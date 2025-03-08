#!/usr/bin/env python3
"""Main entry point for the application."""
import sys
import argparse
import logging
from {{ cookiecutter.package_name }}.config import Config

# Get the package logger
logger = logging.getLogger("{{ cookiecutter.package_name }}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="{{ cookiecutter.project_description }}")

    # Add environment argument
    parser.add_argument(
        "--env", default="dev", help="Environment to use (dev, prod, etc.)"
    )

    # Add config override arguments
    parser.add_argument(
        "--config",
        action="append",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Override config values (can be used multiple times)",
    )

    # Add your specific command-line arguments here
    # parser.add_argument("--example", help="Example argument")

    return parser.parse_args()


def setup_logging(config):
    """Set up logging based on configuration."""
    log_level = config.get_config("logging.level", "INFO")
    log_format = config.get_config(
        "logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        logger.warning(f"Invalid log level: {log_level}, defaulting to INFO")
        numeric_level = logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format
    )
    
    # Set level for external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def main():
    """Main entry point for the application."""
    args = parse_args()

    # Load configuration
    config = Config(args.env, args.config)
    
    # Set up logging based on configuration
    setup_logging(config)
    
    # Log startup information
    logger.info(f"Starting {{ cookiecutter.project_name }} in {args.env} environment")
    
    # Your application code here
    # ...
    
    logger.info("Application finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())