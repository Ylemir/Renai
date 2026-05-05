import logging
from unittest.mock import patch

from renai.logger import (
    ColoredFormatter,
    print_debug,
    print_error,
    print_highlight,
    print_info,
    print_process,
    print_separator,
    print_success,
    print_warning,
    setup_logger,
)


def test_setup_logger_debug():
    """Test that setup_logger calls basicConfig with DEBUG level."""
    with patch("renai.logger.logging.basicConfig") as mock_basic_config:
        setup_logger(debug=True)
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args.kwargs
        assert call_kwargs.get("level") == logging.DEBUG


def test_setup_logger_default():
    """Test that setup_logger calls basicConfig with CRITICAL level."""
    with patch("renai.logger.logging.basicConfig") as mock_basic_config:
        setup_logger(debug=False)
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args.kwargs
        assert call_kwargs.get("level") == logging.CRITICAL


def test_colored_formatter_info():
    """Test ColoredFormatter.info returns a string."""
    result = ColoredFormatter.info("test message")
    assert isinstance(result, str)
    assert "test message" in result


def test_colored_formatter_success():
    """Test ColoredFormatter.success returns a string."""
    result = ColoredFormatter.success("success message")
    assert isinstance(result, str)
    assert "success message" in result


def test_colored_formatter_warning():
    """Test ColoredFormatter.warning returns a string."""
    result = ColoredFormatter.warning("warning message")
    assert isinstance(result, str)
    assert "warning message" in result


def test_colored_formatter_error():
    """Test ColoredFormatter.error returns a string."""
    result = ColoredFormatter.error("error message")
    assert isinstance(result, str)
    assert "error message" in result


def test_colored_formatter_debug():
    """Test ColoredFormatter.debug returns a string."""
    result = ColoredFormatter.debug("debug message")
    assert isinstance(result, str)
    assert "debug message" in result


def test_colored_formatter_process():
    """Test ColoredFormatter.process returns a string."""
    result = ColoredFormatter.process("process message")
    assert isinstance(result, str)
    assert "process message" in result


def test_colored_formatter_highlight():
    """Test ColoredFormatter.highlight returns a string."""
    result = ColoredFormatter.highlight("highlight message")
    assert isinstance(result, str)
    assert "highlight message" in result


def test_print_functions_exist():
    """Smoke test that all print functions are callable."""
    # These print to stdout/stderr; we just verify they don't raise.
    print_info("info")
    print_success("success")
    print_warning("warning")
    print_debug("debug")
    print_process("process")
    print_highlight("highlight")
    print_separator()
    print_separator(char="=", length=10)
    # print_error goes to stderr, so we test it separately
    print_error("error")
