"""Tests for the configuration management module."""

import os
import pytest
from unittest.mock import patch
import configparser
from {{ cookiecutter.package_name }}.config import Config


@pytest.fixture
def config_content():
    """Return sample base config content."""
    return """
[database]
host = localhost
port = 5432
username = default_user

[api]
url = https://api.example.com
timeout = 30
"""


@pytest.fixture
def env_config_content():
    """Return sample environment config content."""
    return """
[database]
host = dev.example.com
username = dev_user

[logging]
level = DEBUG
"""


@pytest.fixture
def secret_config_content():
    """Return sample secret config content."""
    return """
[database]
password = secret_password

[api]
key = secret_api_key
"""


@pytest.fixture
def clean_env():
    """Clear environment variables that might interfere with tests."""
    # Save original environment
    original_env = os.environ.copy()

    # Clear environment variables that might interfere with tests
    for env_var in list(os.environ.keys()):
        if env_var.startswith("APP_"):
            del os.environ[env_var]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_read():
    """Create a patcher for the actual file reading method."""
    with patch("configparser.ConfigParser.read", return_value=[]) as patcher:
        yield patcher


def test_load_config_files(mock_read, clean_env):
    """Test that config files are loaded in the correct order."""
    # Setup mocks
    with patch("os.path.exists") as mock_exists:
        mock_exists.side_effect = lambda path: path in [
            "config.ini",
            "config.dev.ini",
            "secret.ini",
        ]

        # Create and initialize config
        _ = Config(env="dev")

        # Check that all files were checked
        mock_exists.assert_any_call("config.ini")
        mock_exists.assert_any_call("config.dev.ini")
        mock_exists.assert_any_call("secret.ini")

        # Check that all files were read in the correct order
        mock_read.assert_any_call("config.ini")
        mock_read.assert_any_call("config.dev.ini")
        mock_read.assert_any_call("secret.ini")


def test_config_priority_with_real_files(
    config_content, env_config_content, secret_config_content, clean_env
):
    """Test that config values are loaded with the correct priority."""
    # Create a real config parser and load the test content
    parser = configparser.ConfigParser()
    parser.read_string(config_content)
    parser.read_string(env_config_content)
    parser.read_string(secret_config_content)

    # Now patch the ConfigParser constructor to return our pre-loaded parser
    with patch("configparser.ConfigParser", return_value=parser):
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path in [
                "config.ini",
                "config.dev.ini",
                "secret.ini",
            ]

            config = Config(env="dev")

            # Test priority: base config < env config < secret config
            assert (
                config.get_config("database.host") == "dev.example.com"
            )  # From env config
            assert config.get_config("database.port") == "5432"  # From base config
            assert (
                config.get_config("database.password") == "secret_password"
            )  # From secret
            assert config.get_config("api.key") == "secret_api_key"  # From secret
            assert config.get_config("logging.level") == "DEBUG"  # From env config


def test_environment_variables(clean_env):
    """Test that environment variables are applied correctly."""
    # Set environment variables
    os.environ["APP_DATABASE_HOST"] = "env.example.com"
    os.environ["APP_API_NEWKEY"] = "env_api_key"

    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False  # No config files

        config = Config()

        # Check that environment variables were applied
        assert config.get_config("database.host") == "env.example.com"
        assert config.get_config("api.newkey") == "env_api_key"


def test_command_line_overrides(clean_env):
    """Test that command line overrides are applied correctly."""
    # Create config with command line overrides
    overrides = [("database.host", "cli.example.com"), ("api.timeout", "60")]

    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False  # No config files

        config = Config(config_overrides=overrides)

        # Check that overrides were applied
        assert config.get_config("database.host") == "cli.example.com"
        assert config.get_config("api.timeout") == "60"


def test_priority_order(
    config_content, env_config_content, secret_config_content, clean_env
):
    """Test the full priority order of configuration sources."""
    # Test the full priority order:
    # CLI > Environment > Secret > Env Config > Base Config

    # Create a real config parser and load the test content
    parser = configparser.ConfigParser()
    parser.read_string(config_content)
    parser.read_string(env_config_content)
    parser.read_string(secret_config_content)

    # Now patch the ConfigParser constructor to return our pre-loaded parser
    with patch("configparser.ConfigParser", return_value=parser):
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path in [
                "config.ini",
                "config.dev.ini",
                "secret.ini",
            ]

            # Set environment variables
            os.environ["APP_DATABASE_HOST"] = "env.example.com"

            # Create config with command line overrides
            overrides = [("api.timeout", "60")]

            config = Config(env="dev", config_overrides=overrides)

            # Check priority
            assert (
                config.get_config("database.host") == "env.example.com"
            )  # From env var
            assert config.get_config("api.timeout") == "60"  # From CLI
            assert (
                config.get_config("database.password") == "secret_password"
            )  # From secret
            assert config.get_config("logging.level") == "DEBUG"  # From env config
            assert config.get_config("database.port") == "5432"  # From base config


def test_get_config_with_default(clean_env):
    """Test that get_config returns the default value when key is not found."""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False  # No config files

        config = Config()

        # Test with default value
        assert config.get_config("nonexistent.key", "default_value") == "default_value"
        assert config.get_config("nonexistent", {"default": "value"}) == {
            "default": "value"
        }


def test_set_config(clean_env):
    """Test that set_config correctly sets a configuration value."""
    config = Config()

    # Set a new value
    config.set_config("test.key", "test_value")

    # Check that it was set
    assert config.get_config("test.key") == "test_value"


def test_sections(config_content, clean_env):
    """Test that sections returns the correct list of sections."""
    # Create a real config parser and load the test content
    parser = configparser.ConfigParser()
    parser.read_string(config_content)

    # Now patch the ConfigParser constructor to return our pre-loaded parser
    with patch("configparser.ConfigParser", return_value=parser):
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: False

            config = Config()

            # Test sections
            assert set(config.sections()) == {"database", "api"}
