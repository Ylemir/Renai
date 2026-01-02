from pathlib import Path

import typer

from renai.config import find_config_file, load_config
from renai.logger import print_info, print_separator, setup_logger
from renai.renamer import process_path

app = typer.Typer(
    help="AI-powered image renamer using OpenAI-compatible models.",
    invoke_without_command=True,
    no_args_is_help=True,
)

# def version_callback(value: bool):
#     if value:
#         typer.echo(f"renai version {typer.style(__version__, fg=typer.colors.GREEN, bold=True)}")
#         raise typer.Exit()

# @app.callback()
# def main(
#     version: bool = typer.Option(None, "--version", "-v", callback=version_callback, help="Show version and exit.")
# ):
#     pass


@app.command()
def rename(
    path: Path = typer.Argument(
        ..., exists=True, help="Image file or directory to process."
    ),
    max_size_mb: float = typer.Option(None, help="Maximum size of the image in MB."),
    model: str = typer.Option(None, help="Model to use for image renaming."),
    dry_run: bool = typer.Option(None, help="Run without actually renaming files."),
    debug: bool = typer.Option(None, help="Enable debug logging."),
    config_path: Path = typer.Option(None, help="Path to configuration file."),
):
    # Load configuration
    config = load_config(config_path)

    # Use CLI options if provided, otherwise use config values, otherwise use defaults
    max_size_mb = max_size_mb if max_size_mb is not None else config.max_size_mb
    model = model if model is not None else config.model
    dry_run = dry_run if dry_run is not None else config.dry_run
    debug = debug if debug is not None else config.debug

    # Display configuration information
    print_info(
        f"Configuration loaded from: {config_path or find_config_file() or 'Default'}"
    )
    print_info(f"Model: {model}")
    print_info(f"Max image size: {max_size_mb} MB")
    print_info(f"Dry run: {'Yes' if dry_run else 'No'}")
    print_info(f"Debug mode: {'On' if debug else 'Off'}")
    print_separator()

    setup_logger(debug)
    process_path(path, max_size_mb, model, dry_run)


if __name__ == "__main__":
    app()
