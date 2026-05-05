from unittest.mock import MagicMock, patch

import pytest
from openai import BadRequestError
from PIL import Image

from renai.ai_client import (
    ContentFilteredError,
    _get_openai_client,
    format_metadata_block,
    generate_name,
    substitute_prompt_vars,
)
from renai.config import Config


def _clear_openai_client_cache():
    """Clear the OpenAI client LRU cache before tests that patch the client."""
    _get_openai_client.cache_clear()


def test_generate_name_with_config():
    """Test that generate_name accepts a config parameter."""
    _clear_openai_client_cache()
    mock_config = Config()
    mock_config.openai_api_key = "test-key"

    with patch("renai.ai_client.OpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "test-name"

        mock_client.chat.completions.create.return_value = mock_response

        result = generate_name(b"fake_image_data", "image/jpeg", "gpt-4o", mock_config)
        assert result == "test-name"
        mock_client.chat.completions.create.assert_called_once()


def test_generate_name_without_config():
    """Test that generate_name works without explicit config (loads default)."""
    _clear_openai_client_cache()
    with patch("renai.ai_client.load_config") as mock_load_config:
        mock_config = Config()
        mock_config.openai_api_key = "test-key"
        mock_load_config.return_value = mock_config

        with patch("renai.ai_client.OpenAI") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "default-name"

            mock_client.chat.completions.create.return_value = mock_response

            result = generate_name(b"fake_image_data", "image/jpeg", "gpt-4o")
            assert result == "default-name"
            mock_load_config.assert_called_once()
            mock_client.chat.completions.create.assert_called_once()


def test_generate_name_content_filtered_error():
    """Test that generate_name raises ContentFilteredError for policy violations."""
    _clear_openai_client_cache()
    mock_config = Config()
    mock_config.openai_api_key = "test-key"
    mock_config.max_retries = 1

    with patch("renai.ai_client.OpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        error_response = {
            "error": {
                "inner_error": {
                    "code": "ResponsibleAIPolicyViolation",
                    "content_filter_results": {
                        "sexual": {"filtered": True, "severity": "high"},
                        "violence": {"filtered": False, "severity": "safe"},
                        "hate": {"filtered": False, "severity": "safe"},
                        "self_harm": {"filtered": False, "severity": "safe"},
                    },
                },
                "code": "content_filter",
            }
        }
        mock_client.chat.completions.create.side_effect = BadRequestError(
            message=str(error_response),
            body=error_response,
            response=MagicMock(status_code=400),
        )

        with pytest.raises(ContentFilteredError):
            generate_name(b"fake_image_data", "image/jpeg", "gpt-4o", mock_config)


def test_substitute_prompt_vars_no_image_info():
    """Test that prompt vars are returned unchanged when no image info provided."""
    prompt = "Analyze this image and generate a filename."
    result = substitute_prompt_vars(prompt)
    assert result == prompt


def test_substitute_prompt_vars_with_image_info(tmp_path):
    """Test that prompt vars are substituted with image info."""
    test_file = tmp_path / "test_image.png"
    img = Image.new("RGB", (800, 600), color="red")
    img.save(test_file)

    prompt = (
        "Analyze {file.name} ({image.width}x{image.height}, {image.format}) "
        "and generate a filename."
    )
    metadata_context = {
        "file": {"name": "test_image.png"},
        "image": {"width": 800, "height": 600, "format": "PNG"},
    }
    result = substitute_prompt_vars(prompt, metadata_context=metadata_context)

    assert "test_image.png" in result
    assert "800" in result
    assert "600" in result
    assert "PNG" in result


def test_substitute_prompt_vars_full_info(tmp_path):
    """Test that missing variables remain 'unknown' in non-strict mode."""
    test_file = tmp_path / "vacation_photo.jpg"
    img = Image.new("RGB", (1920, 1080), color="green")
    img.save(test_file, quality=95)

    prompt = "Given the following image info: {image_info}"
    result = substitute_prompt_vars(prompt, metadata_context={"image": {}})
    assert result.endswith("unknown")


def test_format_metadata_block_basic():
    metadata_context = {
        "file": {"name": "a.jpg", "size_bytes": 123},
        "image": {"width": 10, "height": 20, "format": "JPEG"},
        "exif": {"make": "Canon"},
    }

    block = format_metadata_block(metadata_context)
    assert "Image metadata:" in block
    assert "file.name: a.jpg" in block
    assert "image.width: 10" in block
    assert "exif.make: Canon" in block
