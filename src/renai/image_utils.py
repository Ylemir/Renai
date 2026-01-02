import io
import logging
from pathlib import Path

from PIL import Image

from renai.logger import print_debug

log = logging.getLogger(__name__)

image_mimes = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


def compress_image(path: Path, max_size_mb: float) -> bytes:
    """
    Compress an image to be under the specified size limit while preserving format-specific features.

    Args:
        path: Path to the image file
        max_size_mb: Maximum size in megabytes

    Returns:
        Compressed image as bytes
    """
    img = Image.open(path)

    # Preserve original format
    original_format = img.format
    max_bytes = max_size_mb * 1024 * 1024

    # For formats that support transparency, preserve it
    if img.mode in ("RGBA", "LA", "P") and path.suffix.lower() in [
        ".png",
        ".webp",
        ".gif",
        ".tiff",
        ".tif",
    ]:
        # For transparent images, we can't convert to RGB
        if img.mode == "P":
            # Convert palette mode to RGBA to preserve transparency
            img = img.convert("RGBA")
    # For non-transparent images, convert to RGB if needed
    elif img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")

    # Check if the image is already under the size limit
    buf = io.BytesIO()
    img.save(buf, format=original_format)
    current_size = buf.tell()

    if current_size <= max_bytes:
        log.debug(
            f"Image already under size limit: {current_size / (1024 * 1024):.2f} MB < {max_size_mb} MB"
        )
        return buf.getvalue()

    # Calculate target dimensions to reduce file size
    scale_factor = (max_bytes / current_size) ** 0.5
    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)

    # Resize the image
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Try to compress by adjusting quality if format supports it
    if original_format in ["JPEG", "JPG", "WEBP"]:
        quality = 95
        while quality >= 50:
            buf.seek(0)
            buf.truncate()

            if original_format in ["JPEG", "JPG"]:
                img.save(buf, format=original_format, quality=quality, optimize=True)
            else:  # WEBP
                img.save(buf, format=original_format, quality=quality, optimize=True)

            if buf.tell() <= max_bytes:
                break
            quality -= 5
    else:
        # For formats that don't support quality (like PNG), try different optimization methods
        buf.seek(0)
        buf.truncate()
        img.save(buf, format=original_format, optimize=True)

    final_size = buf.tell()
    if final_size > max_bytes:
        # If still too large, convert to JPEG (lossy) as a last resort
        if path.suffix.lower() not in [
            ".jpg",
            ".jpeg",
        ]:  # Don't convert if already JPEG
            img_rgb = img.convert("RGB")
            buf.seek(0)
            buf.truncate()
            img_rgb.save(buf, format="JPEG", quality=85, optimize=True)
            final_size = buf.tell()

    if final_size > max_bytes:
        print_debug(
            f"Could not compress {path} to under {max_size_mb}MB. Final size: {final_size / 1024 / 1024:.2f}MB"
        )
    else:
        compression_ratio = (current_size - final_size) / current_size * 100
        print_debug(
            f"Image {path} compressed by {compression_ratio:.1f}%, current size: {final_size / 1024 / 1024:.2f} MB"
        )

    return buf.getvalue()


def get_mime(path: Path) -> str:
    """Get the MIME type for an image file."""
    return image_mimes.get(path.suffix.lower(), "image/jpeg")
