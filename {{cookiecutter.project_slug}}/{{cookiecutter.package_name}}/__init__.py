"""{{ cookiecutter.project_name }} package."""
import logging

__version__ = "0.1.0"

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Create a logger for this package
logger = logging.getLogger(__name__)
