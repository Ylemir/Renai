import base64
import functools
import logging
import re
import time
from typing import Any

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


@functools.lru_cache(maxsize=8)
def _get_openai_client(base_url: str | None, api_key: str) -> OpenAI:
    client_params = {"api_key": api_key}
    if base_url:
        client_params["base_url"] = base_url
    return OpenAI(**client_params)


class ContentFilteredError(Exception):
    """Exception raised when AI content is filtered due to policy violation."""

    pass


def substitute_prompt_vars(
    prompt: str,
    metadata_context: dict[str, Any] | None = None,
    *,
    strict: bool = False,
) -> str:
    if metadata_context is None:
        return prompt

    return _render_prompt_template(prompt, metadata_context, strict=strict)


def _render_prompt_template(
    template: str, context: dict[str, Any], *, strict: bool
) -> str:
    pattern = re.compile(r"\{([a-zA-Z_][\w\.]*)\}")

    def repl(match: re.Match[str]) -> str:
        expr = match.group(1)
        value = _resolve_context_value(context, expr)
        if value is None:
            if strict:
                raise KeyError(f"Missing prompt variable: {expr}")
            return "unknown"
        return str(value)

    return pattern.sub(repl, template)


def _resolve_context_value(context: dict[str, Any], expr: str) -> Any:
    current: Any = context
    for part in expr.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def format_metadata_block(metadata_context: dict[str, Any]) -> str:
    lines: list[str] = []

    file_ctx = metadata_context.get("file")
    if isinstance(file_ctx, dict):
        for key in [
            "name",
            "stem",
            "suffix",
            "size_bytes",
            "size_mb",
            "abspath",
            "mtime_iso",
        ]:
            if key in file_ctx:
                lines.append(f"file.{key}: {file_ctx[key]}")

    image_ctx = metadata_context.get("image")
    if isinstance(image_ctx, dict):
        for key in [
            "width",
            "height",
            "format",
            "mode",
            "has_alpha",
            "orientation",
            "aspect_ratio",
        ]:
            if key in image_ctx:
                lines.append(f"image.{key}: {image_ctx[key]}")

    exif_ctx = metadata_context.get("exif")
    if isinstance(exif_ctx, dict) and exif_ctx:
        for key in sorted(exif_ctx.keys()):
            lines.append(f"exif.{key}: {exif_ctx[key]}")

    if not lines:
        return ""

    return "Image metadata:\n" + "\n".join(lines)


def generate_name(
    image_bytes: bytes,
    mime: str,
    model: str,
    config: Config | None = None,
    metadata_context: dict[str, Any] | None = None,
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
    base_url = config.get_openai_base_url()
    api_key = config.get_openai_api_key()
    if not api_key:
        raise ValueError(
            "OpenAI API key is required but not provided in config or environment"
        )

    client = _get_openai_client(base_url, api_key)

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    log.debug(f"Calling AI for model: {model}")
    print_process(
        (
            f"  Calling AI model: {model} (Image size: "
            f"{len(image_bytes) / (1024 * 1024):.2f} MB, MIME: {mime})"
        )
    )

    # Use configured prompts if available, otherwise use defaults
    system_prompt = (
        config.system_prompt if config.system_prompt is not None else SYSTEM_PROMPT
    )
    user_prompt = config.user_prompt if config.user_prompt is not None else USER_PROMPT

    strict = bool(getattr(config, "strict_metadata", False))
    system_prompt = substitute_prompt_vars(
        system_prompt, metadata_context=metadata_context, strict=strict
    )
    user_prompt = substitute_prompt_vars(
        user_prompt, metadata_context=metadata_context, strict=strict
    )

    if getattr(config, "auto_append_metadata", False) and metadata_context is not None:
        block = format_metadata_block(metadata_context)
        if block:
            user_prompt = f"{user_prompt}\n\n{block}"

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
                (
                    f"AI response received for model: {model} "
                    f"(attempt {attempt + 1}) in {response_time:.2f}s"
                )
            )
            message_content = resp.choices[0].message.content
            if message_content is None:
                raise ValueError("AI returned a null response")
            content = message_content.strip()

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
