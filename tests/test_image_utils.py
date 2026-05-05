from pathlib import Path

from renai.image_utils import get_mime


def test_get_mime_jpg():
    """Test getting MIME type for JPG files."""
    path = Path("test.jpg")
    result = get_mime(path)
    assert result == "image/jpeg"


def test_get_mime_png():
    """Test getting MIME type for PNG files."""
    path = Path("test.png")
    result = get_mime(path)
    assert result == "image/png"


def test_get_mime_webp():
    """Test getting MIME type for WEBP files."""
    path = Path("test.webp")
    result = get_mime(path)
    assert result == "image/webp"


def test_get_mime_unknown():
    """Test getting MIME type for unknown extension."""
    path = Path("test.unknown")
    result = get_mime(path)
    assert result == "image/jpeg"  # Should default to JPEG


def test_get_mime_case_insensitive():
    """Test that MIME type detection is case insensitive."""
    path = Path("test.JPG")
    result = get_mime(path)
    assert result == "image/jpeg"

    path = Path("test.Png")
    result = get_mime(path)
    assert result == "image/png"
