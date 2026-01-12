import logging
import re
from pathlib import Path

from renai.ai_client import ContentFilteredError, generate_name
from renai.config import load_config
from renai.image_utils import compress_image, get_mime, image_mimes
from renai.logger import (
    print_error,
    print_highlight,
    print_info,
    print_process,
    print_separator,
    print_success,
    print_warning,
)

log = logging.getLogger(__name__)


def validate_filename(name: str) -> str:
    """
    Validate and sanitize the AI-generated filename.

    Args:
        name: The AI-generated name

    Returns:
        Sanitized and validated filename
    """
    if not name:
        raise ValueError("Generated name is empty")

    # Remove any path traversal attempts
    name = (
        name.strip()
        .replace("../", "")
        .replace("..\\", "")
        .replace("./", "")
        .replace(".\\", "")
    )

    # According to the prompt, we should:
    # 1. Use user input language (we can't validate this)
    # 2. Don't use spaces - replace with hyphens
    name = name.replace(" ", "-")

    # 3. Don't use punctuation (except hyphens which connect words)
    # Keep only alphanumeric characters and hyphens
    name = re.sub(r"[^\w\-]", "", name)

    # 4. Use `-` to connect words (already handled above)
    # 5. Total length should be under 30 characters
    if len(name) > 30:
        name = name[:30]

    # 6. Don't add explanations, just the filename (this is handled by the AI)

    # Remove any leading/trailing hyphens
    name = name.strip("-")

    # Ensure the name is not empty after sanitization
    if not name:
        raise ValueError("Generated name became empty after sanitization")

    return name


def safe_rename(src: Path, new_name: str) -> Path:
    """Safely create a target path with the new name, handling duplicates."""
    # Validate the new name first
    validated_name = validate_filename(new_name)

    target = src.with_name(f"{validated_name}{src.suffix}")
    idx = 1
    while target.exists():
        target = src.with_name(f"{validated_name}_{idx}{src.suffix}")
        idx += 1
    return target


def process_path(
    path: Path,
    max_size_mb: float,
    model: str,
    dry_run: bool,
):
    # Load config once and reuse for all images
    config = load_config()

    if path.is_file():
        files = [path]
        print_info(f"Processing single file: {path.name}")
    else:
        files = list(path.iterdir())
        print_info(f"Processing directory: {path}")

    files = [item for item in files if item.suffix.lower() in image_mimes]
    print_info(f"Found {len(files)} image(s) to process: {[f.name for f in files]}")

    if not files:
        print_warning("No image files found to process.")
        return

    print_process(f"Starting processing with model: {model}")
    print_separator()

    processed_count = 0
    skipped_count = 0
    error_count = 0

    for i, img in enumerate(files, 1):
        log.debug(f"Processing: {img.name}")
        size_mb = img.stat().st_size / (1024 * 1024)
        print_process(
            f"[{i}/{len(files)}] Processing: {img.name} (Size: {size_mb:.2f} MB)"
        )
        try:
            image_bytes = compress_image(img, max_size_mb)
            mime = get_mime(img)
        except Exception as e:
            print_error(f"Failed to prepare image {img.name}: {str(e)}")
            error_count += 1
            continue

        # Show compression info if compression occurred
        original_size = img.stat().st_size
        compressed_size = len(image_bytes)
        if original_size != compressed_size:
            orig_mb = original_size / (1024 * 1024)
            comp_mb = compressed_size / (1024 * 1024)
            print_info(f"  Compressed from {orig_mb:.2f} MB to {comp_mb:.2f} MB")

        try:
            name = generate_name(image_bytes, mime, model, config)
        except ContentFilteredError:
            print_warning(f"  Skipping {img.name} due to AI content filtering")
            error_count += 1
            continue
        except Exception as e:
            print_error(f"Failed to generate name for {img.name}: {str(e)}")
            raise

        try:
            # Validate the generated name
            validated_name = validate_filename(name)

            target = safe_rename(img, validated_name)

            if dry_run:
                print_warning(f"  [DRY RUN] Would rename: {img.name} -> {target.name}")
                skipped_count += 1
            else:
                img.rename(target)
                print_success(f"  Renamed: {img.name} -> {target.name}")
                processed_count += 1
        except Exception as e:
            print_error(f"Failed to rename {img.name}: {str(e)}")
            error_count += 1

    # Print summary
    print_separator()
    print_highlight("Processing Summary:")
    print_info(f"  Total files processed: {len(files)}")
    print_success(f"  Successfully renamed: {processed_count}")
    print_warning(f"  Skipped (dry run): {skipped_count}")
    print_error(f"  Errors: {error_count}")
