import os

from renai.config import Config


def test_config_defaults():
    """Test that Config has correct default values."""
    config = Config()
    assert config.max_size_mb == 8.0
    assert config.model == "gpt-4o"
    assert config.dry_run is False
    assert config.debug is False
    assert config.strict_metadata is False
    assert config.auto_append_metadata is False
    assert config.openai_api_key is None
    assert config.openai_base_url is None
    assert config.max_retries == 3
    assert config.retry_delay == 1.0


def test_config_load_from_dict():
    """Test loading config from dictionary."""
    config = Config()
    config_dict = {
        "max_size_mb": 10.0,
        "model": "gpt-4o",
        "dry_run": True,
        "debug": True,
        "strict_metadata": True,
        "auto_append_metadata": True,
        "openai_api_key": "test-key",
        "openai_base_url": "https://api.test.com",
        "max_retries": 5,
        "retry_delay": 2.0,
    }

    config.load_from_dict(config_dict)

    assert config.max_size_mb == 10.0
    assert config.model == "gpt-4o"
    assert config.dry_run is True
    assert config.debug is True
    assert config.strict_metadata is True
    assert config.auto_append_metadata is True
    assert config.openai_api_key == "test-key"
    assert config.openai_base_url == "https://api.test.com"
    assert config.max_retries == 5
    assert config.retry_delay == 2.0


def test_config_load_from_dict_partial():
    """Test loading partial config from dictionary."""
    config = Config()
    config_dict = {"model": "gpt-4o", "debug": True}

    config.load_from_dict(config_dict)

    assert config.model == "gpt-4o"
    assert config.debug is True
    # Other values should remain as defaults
    assert config.max_size_mb == 8.0
    assert config.dry_run is False


def test_config_get_openai_api_key():
    """Test getting OpenAI API key from config or environment."""
    config = Config()

    # Test when API key is in config
    config.openai_api_key = "config-key"
    assert config.get_openai_api_key() == "config-key"

    # Test when API key is in environment
    config.openai_api_key = None
    os.environ["OPENAI_API_KEY"] = "env-key"
    assert config.get_openai_api_key() == "env-key"

    # Test when no API key is available
    del os.environ["OPENAI_API_KEY"]
    assert config.get_openai_api_key() is None


def test_config_get_openai_base_url():
    """Test getting OpenAI base URL from config or environment."""
    config = Config()

    # Test when base URL is in config
    config.openai_base_url = "https://api.config.com"
    assert config.get_openai_base_url() == "https://api.config.com"

    # Test when base URL is in environment
    config.openai_base_url = None
    os.environ["OPENAI_BASE_URL"] = "https://api.env.com"
    assert config.get_openai_base_url() == "https://api.env.com"

    # Test when no base URL is available
    del os.environ["OPENAI_BASE_URL"]
    assert config.get_openai_base_url() is None
