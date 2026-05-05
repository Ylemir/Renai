from pathlib import Path

import pytest

from renai.renamer import safe_rename, validate_filename


def test_validate_filename_basic():
    """Test basic filename validation."""
    result = validate_filename("beautiful-sunset-view")
    assert result == "beautiful-sunset-view"


def test_validate_filename_with_spaces():
    """Test that spaces are replaced with hyphens."""
    result = validate_filename("beautiful sunset view")
    assert result == "beautiful-sunset-view"


def test_validate_filename_removes_punctuation():
    """Test that punctuation is removed."""
    result = validate_filename("hello, world!")
    assert result == "hello-world"


def test_validate_filename_too_long():
    """Test that long filenames are truncated to 30 chars."""
    long_name = "a" * 50
    result = validate_filename(long_name)
    assert len(result) <= 30
    assert result == "a" * 30


def test_validate_filename_strips_hyphens():
    """Test leading/trailing hyphens are stripped."""
    result = validate_filename("-hello-world-")
    assert result == "hello-world"


def test_validate_filename_empty():
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError, match="Generated name is empty"):
        validate_filename("")


def test_validate_filename_becomes_empty():
    """Test that sanitization resulting in empty string raises ValueError."""
    with pytest.raises(
        ValueError, match="Generated name became empty after sanitization"
    ):
        validate_filename("!!!")


def test_validate_filename_path_traversal():
    """Test that path traversal attempts are sanitized."""
    result = validate_filename("../etc/passwd")
    assert ".." not in result
    assert "/" not in result


def test_safe_rename(tmp_path: Path):
    """Test safe_rename generates expected target path."""
    src = tmp_path / "original.jpg"
    src.write_text("dummy")
    target = safe_rename(src, "new-name")
    assert target == tmp_path / "new-name.jpg"


def test_safe_rename_duplicate(tmp_path: Path):
    """Test safe_rename handles duplicate filenames."""
    src1 = tmp_path / "original1.jpg"
    src1.write_text("dummy1")
    # Pre-create the expected target
    (tmp_path / "new-name.jpg").write_text("exists")

    target = safe_rename(src1, "new-name")
    assert target == tmp_path / "new-name_1.jpg"


def test_safe_rename_multiple_duplicates(tmp_path: Path):
    """Test safe_rename handles multiple duplicate filenames."""
    src = tmp_path / "original.jpg"
    src.write_text("dummy")
    (tmp_path / "new-name.jpg").write_text("exists")
    (tmp_path / "new-name_1.jpg").write_text("exists")

    target = safe_rename(src, "new-name")
    assert target == tmp_path / "new-name_2.jpg"
