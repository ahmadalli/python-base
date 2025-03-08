"""Configuration management module."""

import os
import configparser
from typing import Dict, Any, Optional, List, Tuple, Union


class Config:
    """
    Configuration manager that loads settings from multiple sources with priority:
    1. Command-line arguments (highest priority)
    2. Environment variables
    3. secret.ini
    4. config.<env>.ini
    5. config.ini (lowest priority)
    """

    def __init__(
        self, env: str = "dev", config_overrides: Optional[List[Tuple[str, str]]] = None
    ):
        """
        Initialize the configuration manager.

        Args:
            env: Environment name (dev, prod, etc.)
            config_overrides: List of (key, value) tuples from command line args
        """
        self._env = env
        self._config = configparser.ConfigParser()
        self._load_config_files()
        self._apply_environment_variables()
        self._apply_overrides(config_overrides)

    def _load_config_files(self):
        """Load configuration from files in priority order."""
        # Load base configuration (lowest priority)
        if os.path.exists("config.ini"):
            self._config.read("config.ini")

        # Load environment-specific configuration
        env_config_file = f"config.{self._env}.ini"
        if os.path.exists(env_config_file):
            self._config.read(env_config_file)

        # Load secrets configuration
        if os.path.exists("secret.ini"):
            self._config.read("secret.ini")

    def _apply_environment_variables(self):
        """Apply environment variables to configuration."""
        # Format: APP_SECTION_KEY (e.g., APP_DATABASE_HOST)
        for env_var, env_value in os.environ.items():
            if env_var.startswith("APP_"):
                parts = env_var.split("_", 2)
                if len(parts) == 3:
                    _, section, key = parts
                    section = section.lower()
                    key = key.lower()

                    if section not in self._config:
                        self._config[section] = {}
                    self._config[section][key] = env_value

    def _apply_overrides(self, config_overrides: Optional[List[Tuple[str, str]]]):
        """Apply command-line overrides to configuration."""
        if config_overrides:
            for key, value in config_overrides:
                # Expect format: section.key
                if "." in key:
                    section, option = key.split(".", 1)
                    if section not in self._config:
                        self._config[section] = {}
                    self._config[section][option] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with a default fallback.

        Args:
            key: Configuration key in format "section.option" or just "option"
            default: Default value if key is not found

        Returns:
            The configuration value or default if not found
        """
        if "." in key:
            section, option = key.split(".", 1)
            if section in self._config and option in self._config[section]:
                return self._config[section][option]
        elif key in self._config:
            return dict(self._config[key])
        return default

    def set_config(self, key: str, value: Any):
        """
        Set a configuration value.
        """
        if "." in key:
            section, option = key.split(".", 1)
            if section not in self._config:
                self._config[section] = {}
            self._config[section][option] = str(value)

    def sections(self) -> List[str]:
        """Get all configuration sections."""
        return self._config.sections()
