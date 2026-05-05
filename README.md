# renai

AI-powered image renamer using OpenAI-compatible models. Automatically analyzes your images and generates descriptive, SEO-friendly filenames based on their content.

## Features

- **AI-Powered Analysis**: Uses OpenAI-compatible models to understand image content and generate meaningful names
- **Batch Processing**: Rename single images or entire directories at once
- **Configurable**: Customize behavior through command-line options or configuration files
- **Safe Operation**: Validates generated names and handles duplicate filenames automatically
- **Compression Support**: Automatically compresses large images to stay within API limits
- **Dry Run Mode**: Preview changes before applying them
- **Flexible Configuration**: Supports custom prompts and API endpoints

## Installation

Download the latest release from the [releases page](https://github.com/Ylemir/Renai/releases).

Or install via uv:

```bash
uv tool install git+https://github.com/Ylemir/Renai
```

## Usage

### Command Line

```bash
# Basic usage - rename a single image
renai path/to/image.jpg

# Rename all images in a directory
renai path/to/images/

# With options
renai path/to/images/ --max-size-mb 10.0 --model gpt-4o --dry-run
```

### Configuration File

The application supports configuration files in TOML format. Configuration files are searched for in this order:

1. `.renai.toml` in the current directory
2. `renai.toml` in the current directory
3. `renai.toml` in the home `.config` directory

Example `renai.toml` file:

```toml
[renai]
max_size_mb = 10.0
model = "gpt-4o"
dry_run = false
debug = false
strict_metadata = false
auto_append_metadata = false
openai_api_key = "your-api-key-here"  # Optional: can also be set via OPENAI_API_KEY environment variable
openai_base_url = "https://api.openai.com/v1"  # Optional: for custom OpenAI-compatible endpoints
max_retries = 1
retry_delay = 3.0
system_prompt = "Custom system prompt for AI"
user_prompt = "Custom user prompt for AI"
```

### Options

- `path`: Image file or directory to process (required)
- `--max-size-mb`: Maximum size of the image in MB (default: 8.0)
- `--model`: Model to use for image renaming (default: "gpt-4o")
- `--dry-run`: Run without actually renaming files (default: false)
- `--debug`: Enable debug logging (default: false)
- `--config` / `-c`: Path to configuration file (optional)

## Configuration Priority

Configuration values are applied in this priority order:
1. Command line options (highest priority)
2. Configuration file values
3. Default values (lowest priority)

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (alternative to config file)
- `OPENAI_BASE_URL`: Custom OpenAI-compatible API endpoint (alternative to config file)

## Supported Image Formats

The tool supports all image formats supported by Pillow (JPEG, PNG, GIF, BMP, TIFF, WebP, etc.).

## Customization

You can customize the AI prompts used for generating names by setting the `system_prompt` and `user_prompt` in your configuration file. This allows you to tailor the naming style to your preferences.

### Prompt Template Variables (Image Metadata)

When building the prompt, renai extracts basic metadata from the current image and makes it available for substitution in `system_prompt` and `user_prompt`.

Variables use the `{section.key}` syntax.

Common variables:

- `file.name`, `file.stem`, `file.suffix`
- `file.size_bytes`, `file.size_mb`
- `file.abspath`, `file.mtime_iso`, `file.ctime_iso`
- `image.width`, `image.height`, `image.format`, `image.mode`
- `image.has_alpha`, `image.orientation`, `image.aspect_ratio`
- `exif.datetime_original`, `exif.make`, `exif.model`, `exif.iso`

Example:

```toml
[renai]
user_prompt = "请根据图片内容命名。当前文件: {file.name}，分辨率: {image.width}x{image.height}"
```

If `auto_append_metadata = true`, renai will automatically append a readable metadata block to the end of the `user_prompt` before sending it to the model.

If `strict_metadata = true`, missing template variables (or metadata read failures) will cause the current image to fail instead of silently using `unknown`.


## Development

To set up the development environment:

### Using pip:
```bash
# Clone the repository
git clone https://github.com/Ylemir/renai.git
cd renai

# Install dependencies
pip install -e .
```

### Using uv (recommended):
```bash
# Clone the repository
git clone https://github.com/Ylemir/renai.git
cd renai

# Install dependencies with uv
uv sync

# Run the project in development mode
uv run renai path/to/image.jpg

# Run linter
uv run ruff check src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.