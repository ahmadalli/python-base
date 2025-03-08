"""Tests for the configuration management module."""
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import configparser
from {{ cookiecutter.package_name }}.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear environment variables that might interfere with tests
        for env_var in list(os.environ.keys()):
            if env_var.startswith("APP_"):
                del os.environ[env_var]

        # Create temporary config files for testing
        self.config_content = """
[database]
host = localhost
port = 5432
username = default_user

[api]
url = https://api.example.com
timeout = 30
"""

        self.env_config_content = """
[database]
host = dev.example.com
username = dev_user

[logging]
level = DEBUG
"""

        self.secret_config_content = """
[database]
password = secret_password

[api]
key = secret_api_key
"""

        # Create a patcher for the actual file reading method
        # This prevents reading actual files while allowing read_string to work
        self.read_patcher = patch('configparser.ConfigParser.read', return_value=[])
        self.mock_read = self.read_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patcher after each test
        self.read_patcher.stop()

    @patch("os.path.exists")
    @patch("configparser.ConfigParser.read")
    def test_load_config_files(self, mock_read, mock_exists):
        """Test that config files are loaded in the correct order."""
        # Setup mocks
        mock_exists.side_effect = lambda path: path in [
            "config.ini",
            "config.dev.ini",
            "secret.ini",
        ]

        # Create and initialize config
        config = Config(env="dev")

        # Check that all files were checked
        mock_exists.assert_any_call("config.ini")
        mock_exists.assert_any_call("config.dev.ini")
        mock_exists.assert_any_call("secret.ini")

        # Check that all files were read in the correct order
        mock_read.assert_any_call("config.ini")
        mock_read.assert_any_call("config.dev.ini")
        mock_read.assert_any_call("secret.ini")

    def test_config_priority_with_real_files(self):
        """Test that config values are loaded with the correct priority."""
        # Create a real config parser and load the test content
        parser = configparser.ConfigParser()
        parser.read_string(self.config_content)
        parser.read_string(self.env_config_content)
        parser.read_string(self.secret_config_content)

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
                self.assertEqual(
                    config.get_config("database.host"), "dev.example.com"
                )  # From env config
                self.assertEqual(
                    config.get_config("database.port"), "5432"
                )  # From base config
                self.assertEqual(
                    config.get_config("database.password"), "secret_password"
                )  # From secret
                self.assertEqual(
                    config.get_config("api.key"), "secret_api_key"
                )  # From secret
                self.assertEqual(
                    config.get_config("logging.level"), "DEBUG"
                )  # From env config

    def test_environment_variables(self):
        """Test that environment variables are applied correctly."""
        # Set environment variables
        os.environ["APP_DATABASE_HOST"] = "env.example.com"
        os.environ["APP_API_NEWKEY"] = "env_api_key"

        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False  # No config files

            config = Config()

            # Check that environment variables were applied
            self.assertEqual(config.get_config("database.host"), "env.example.com")
            self.assertEqual(config.get_config("api.newkey"), "env_api_key")

    def test_command_line_overrides(self):
        """Test that command line overrides are applied correctly."""
        # Create config with command line overrides
        overrides = [("database.host", "cli.example.com"), ("api.timeout", "60")]

        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False  # No config files

            config = Config(config_overrides=overrides)

            # Check that overrides were applied
            self.assertEqual(config.get_config("database.host"), "cli.example.com")
            self.assertEqual(config.get_config("api.timeout"), "60")

    def test_priority_order(self):
        """Test the full priority order of configuration sources."""
        # Test the full priority order:
        # CLI > Environment > Secret > Env Config > Base Config

        # Create a real config parser and load the test content
        parser = configparser.ConfigParser()
        parser.read_string(self.config_content)
        parser.read_string(self.env_config_content)
        parser.read_string(self.secret_config_content)

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
                self.assertEqual(
                    config.get_config("database.host"), "env.example.com"
                )  # From env var
                self.assertEqual(config.get_config("api.timeout"), "60")  # From CLI
                self.assertEqual(
                    config.get_config("database.password"), "secret_password"
                )  # From secret
                self.assertEqual(
                    config.get_config("logging.level"), "DEBUG"
                )  # From env config
                self.assertEqual(
                    config.get_config("database.port"), "5432"
                )  # From base config

    def test_get_config_with_default(self):
        """Test that get_config returns the default value when key is not found."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False  # No config files

            config = Config()

            # Test with default value
            self.assertEqual(
                config.get_config("nonexistent.key", "default_value"), "default_value"
            )
            self.assertEqual(
                config.get_config("nonexistent", {"default": "value"}),
                {"default": "value"},
            )

    def test_set_config(self):
        """Test that set_config correctly sets a configuration value."""
        config = Config()

        # Set a new value
        config.set_config("test.key", "test_value")

        # Check that it was set
        self.assertEqual(config.get_config("test.key"), "test_value")

    def test_sections(self):
        """Test that sections returns the correct list of sections."""
        # Create a real config parser and load the test content
        parser = configparser.ConfigParser()
        parser.read_string(self.config_content)

        # Now patch the ConfigParser constructor to return our pre-loaded parser
        with patch("configparser.ConfigParser", return_value=parser):
            with patch("os.path.exists") as mock_exists:
                mock_exists.side_effect = lambda path: path in [
                    "config.ini",
                ]

                config = Config()

                # Test sections
                self.assertEqual(set(config.sections()), {"database", "api"})
