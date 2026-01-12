import base64
import logging
import time

from openai import (
    APIError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from renai.config import Config, load_config
from renai.logger import print_error, print_process, print_success, print_warning
from renai.prompt import SYSTEM_PROMPT, USER_PROMPT

log = logging.getLogger(__name__)


class ContentFilteredError(Exception):
    """Exception raised when AI content is filtered due to policy violation."""

    pass


def generate_name(
    image_bytes: bytes, mime: str, model: str, config: Config | None = None
) -> str:
    """
    Generate a name for an image using AI.

    Args:
        image_bytes: Image data as bytes
        mime: MIME type of the image
        model: AI model to use
        config: Configuration object (optional, will load default if not provided)

    Returns:
        Generated name for the image

    Raises:
        Exception: If API call fails or returns invalid response
    """
    # Use provided config or load default config
    if config is None:
        config = load_config()

    # Initialize OpenAI client with base URL and API key if provided
    client_params = {}
    base_url = config.get_openai_base_url()
    if base_url:
        client_params["base_url"] = base_url

    api_key = config.get_openai_api_key()
    if api_key:
        client_params["api_key"] = api_key
    else:
        raise ValueError(
            "OpenAI API key is required but not provided in config or environment"
        )

    client = OpenAI(**client_params)

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    log.debug(f"Calling AI for model: {model}")
    print_process(
        f"  Calling AI model: {model} (Image size: {len(image_bytes) / (1024 * 1024):.2f} MB, MIME: {mime})"
    )

    # Use configured prompts if available, otherwise use defaults
    system_prompt = (
        config.system_prompt if config.system_prompt is not None else SYSTEM_PROMPT
    )
    user_prompt = config.user_prompt if config.user_prompt is not None else USER_PROMPT

    max_retries = config.max_retries
    retry_delay = config.retry_delay

    for attempt in range(max_retries):
        attempt_start_time = time.time()
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                            },
                        ],
                    },
                ],
                temperature=0.2,
            )

            response_time = time.time() - attempt_start_time
            log.debug(
                f"AI response received for model: {model} (attempt {attempt + 1}) in {response_time:.2f}s"
            )
            content = resp.choices[0].message.content.strip()

            if not content:
                raise ValueError("AI returned an empty response")

            print_success(f"  AI response received in {response_time:.2f}s")
            return content

        except AuthenticationError:
            print_error("Authentication failed. Please check your API key.")
            raise
        except RateLimitError as e:
            response_time = time.time() - attempt_start_time
            print_warning(
                f"Rate limit exceeded on attempt {attempt + 1} after {response_time:.2f}s: {e}"
            )
            print_warning(
                f"  Rate limit exceeded (attempt {attempt + 1}) after {response_time:.2f}s, retrying..."
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2**attempt))  # Exponential backoff
                continue
            else:
                raise
        except APIError as e:
            response_time = time.time() - attempt_start_time
            error_msg = str(e)
            if (
                "ResponsibleAIPolicyViolation" in error_msg
                or "content_filter" in error_msg
            ):
                print_warning(f"Content filtered by AI safety policy: {e}")
                raise ContentFilteredError(
                    f"AI content filtered due to policy violation: {e}"
                ) from e
            print_warning(
                f"API error on attempt {attempt + 1} after {response_time:.2f}s: {e}"
            )
            print_warning(
                f"  API error (attempt {attempt + 1}) after {response_time:.2f}s, retrying..."
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2**attempt))  # Exponential backoff
                continue
            else:
                raise
        except Exception as e:
            response_time = time.time() - attempt_start_time
            print_error(
                f"Unexpected error during API call after {response_time:.2f}s: {e}"
            )
            print_error(f"  Unexpected error after {response_time:.2f}s: {e}")
            raise

    raise Exception(f"Failed to get response from AI after {max_retries} attempts")
