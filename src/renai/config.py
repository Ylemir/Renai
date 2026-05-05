"""Configuration management for renai."""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import toml

from renai.logger import print_warning

log = logging.getLogger(__name__)


class Config:
    """Configuration class for renai."""

    def __init__(self):
        self.max_size_mb: float = 8.0
        self.model: str = "gpt-4o"
        self.dry_run: bool = False
        self.debug: bool = False
        self.strict_metadata: bool = False
        self.auto_append_metadata: bool = False
        self.openai_api_key: str | None = None
        self.openai_base_url: str | None = None
        self.system_prompt: str | None = None
        self.user_prompt: str | None = None
        self.max_retries: int = 3
        self.retry_delay: float = 1.0

    def load_from_dict(self, config_dict: dict[str, Any]) -> None:
        """Load configuration from a dictionary."""
        if "max_size_mb" in config_dict:
            self.max_size_mb = float(config_dict["max_size_mb"])
        if "model" in config_dict:
            self.model = config_dict["model"]
        if "dry_run" in config_dict:
            self.dry_run = config_dict["dry_run"]
        if "debug" in config_dict:
            self.debug = config_dict["debug"]
        if "strict_metadata" in config_dict:
            self.strict_metadata = bool(config_dict["strict_metadata"])
        if "auto_append_metadata" in config_dict:
            self.auto_append_metadata = bool(config_dict["auto_append_metadata"])
        if "openai_api_key" in config_dict:
            self.openai_api_key = config_dict["openai_api_key"]
        if "openai_base_url" in config_dict:
            self.openai_base_url = config_dict["openai_base_url"]
        if "system_prompt" in config_dict:
            self.system_prompt = config_dict["system_prompt"]
        if "user_prompt" in config_dict:
            self.user_prompt = config_dict["user_prompt"]
        if "max_retries" in config_dict:
            self.max_retries = int(config_dict["max_retries"])
        if "retry_delay" in config_dict:
            self.retry_delay = float(config_dict["retry_delay"])

    def get_openai_api_key(self) -> str | None:
        """Get OpenAI API key from config or environment variable."""
        # Check config first, then environment variable
        api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
        return api_key

    def get_openai_base_url(self) -> str | None:
        """Get OpenAI base URL from config or environment variable."""
        # Check config first, then environment variable
        base_url = self.openai_base_url or os.getenv("OPENAI_BASE_URL")
        return base_url


@lru_cache(maxsize=1)
def _find_config_file_cached(start_path_str: str) -> str | None:
    """Cached version of find_config_file to avoid repeated file system operations."""
    start_path = Path(start_path_str)
    current_path = start_path.resolve()

    # Search up the directory tree for config files
    while current_path != current_path.parent:
        # Check for common config file names
        for config_name in [".renai.toml", "renai.toml"]:
            config_path = current_path / config_name
            if config_path.exists():
                return str(config_path)

        # Move up one directory
        current_path = current_path.parent

    # Check home directory
    home_config = Path.home() / ".config" / "renai.toml"
    if home_config.exists():
        return str(home_config)

    return None


def find_config_file(start_path: Path | None = None) -> Path | None:
    """Find configuration file by searching up the directory tree."""
    if start_path is None:
        start_path = Path.cwd()

    config_path_str = _find_config_file_cached(str(start_path))
    return Path(config_path_str) if config_path_str else None


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from file or return default config."""
    config = Config()

    # Find config file if none provided
    if config_path is None:
        config_path = find_config_file()

    if config_path and config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                config_data = toml.load(f)
                if "renai" in config_data:
                    config.load_from_dict(config_data["renai"])
                else:
                    # If no 'renai' section, use the root as config
                    config.load_from_dict(config_data)
        except Exception as e:
            print_warning(f"Could not load config file {config_path}: {e}")

    return config
