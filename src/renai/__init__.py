"""AI-based image renamer package."""

from importlib.metadata import version

from .config import Config, load_config

__version__ = version("renai")
__all__ = ["Config", "load_config"]
