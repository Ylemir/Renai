import logging

import typer


# Define color constants
class Colors:
    RESET = typer.colors.RESET
    BLACK = typer.colors.BLACK
    RED = typer.colors.RED
    GREEN = typer.colors.GREEN
    YELLOW = typer.colors.YELLOW
    BLUE = typer.colors.BLUE
    MAGENTA = typer.colors.MAGENTA
    CYAN = typer.colors.CYAN
    WHITE = typer.colors.WHITE
    BRIGHT_BLACK = typer.colors.BRIGHT_BLACK
    BRIGHT_RED = typer.colors.BRIGHT_RED
    BRIGHT_GREEN = typer.colors.BRIGHT_GREEN
    BRIGHT_YELLOW = typer.colors.BRIGHT_YELLOW
    BRIGHT_BLUE = typer.colors.BRIGHT_BLUE
    BRIGHT_MAGENTA = typer.colors.BRIGHT_MAGENTA
    BRIGHT_CYAN = typer.colors.BRIGHT_CYAN
    BRIGHT_WHITE = typer.colors.BRIGHT_WHITE


def setup_logger(debug: bool = False) -> None:
    """Set up the logger with the specified debug level."""
    # Only keep DEBUG level, all other levels will be disabled
    level = (
        logging.DEBUG if debug else logging.CRITICAL
    )  # Use CRITICAL to effectively disable non-debug logs
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


class ColoredFormatter:
    """A formatter that adds colors to different types of messages."""

    @staticmethod
    def info(message: str) -> str:
        """Format info messages with blue color."""
        return typer.style(message, fg=Colors.BRIGHT_BLUE, bold=True)

    @staticmethod
    def success(message: str) -> str:
        """Format success messages with green color."""
        return typer.style(message, fg=Colors.BRIGHT_GREEN, bold=True)

    @staticmethod
    def warning(message: str) -> str:
        """Format warning messages with yellow color."""
        return typer.style(message, fg=Colors.BRIGHT_YELLOW, bold=True)

    @staticmethod
    def error(message: str) -> str:
        """Format error messages with red color."""
        return typer.style(message, fg=Colors.BRIGHT_RED, bold=True)

    @staticmethod
    def debug(message: str) -> str:
        """Format debug messages with magenta color."""
        return typer.style(message, fg=Colors.MAGENTA, bold=False)

    @staticmethod
    def process(message: str) -> str:
        """Format process messages with cyan color."""
        return typer.style(message, fg=Colors.CYAN, bold=True)

    @staticmethod
    def highlight(message: str) -> str:
        """Format highlighted messages with white bold."""
        return typer.style(message, fg=Colors.BRIGHT_WHITE, bold=True)


def print_info(message: str):
    """Print info message with color."""
    typer.echo(ColoredFormatter.info(message))


def print_success(message: str):
    """Print success message with color."""
    typer.echo(ColoredFormatter.success(message))


def print_warning(message: str):
    """Print warning message with color."""
    typer.echo(ColoredFormatter.warning(message))


def print_error(message: str):
    """Print error message with color."""
    typer.echo(ColoredFormatter.error(message), err=True)


def print_debug(message: str):
    """Print debug message with color."""
    typer.echo(ColoredFormatter.debug(message))


def print_process(message: str):
    """Print process message with color."""
    typer.echo(ColoredFormatter.process(message))


def print_highlight(message: str):
    """Print highlighted message with color."""
    typer.echo(ColoredFormatter.highlight(message))


def print_separator(char: str = "-", length: int = 50, color: str = Colors.BRIGHT_BLUE):
    """Print a colored separator line."""
    separator = char * length
    typer.echo(typer.style(separator, fg=color))
