from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from renai.cli import app, rename

runner = CliRunner()


def test_cli_help():
    """Test that CLI help is available."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Image file or directory to process" in result.output


def test_cli_version():
    """Test that --version outputs version info."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "renai version" in result.output


def test_cli_rename_help():
    """Test that rename command help is available."""
    result = runner.invoke(app, ["rename", "--help"])
    assert result.exit_code == 0
    assert "Image file or directory to process" in result.output


def test_cli_rename_dry_run():
    """Test that rename command passes dry_run to process_path."""
    with (
        patch("renai.cli.find_config_file") as mock_find_config,
        patch("renai.cli.load_config") as mock_load_config,
        patch("renai.cli.process_path") as mock_process,
    ):
        from renai.config import Config

        config = Config()
        mock_load_config.return_value = config
        mock_find_config.return_value = None

        rename(Path("test.jpg"), dry_run=True)

        mock_process.assert_called_once()
        _, _, _, dry_run = mock_process.call_args[0]
        assert dry_run is True
