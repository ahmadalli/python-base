# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Installation

```bash
poetry install
```

## Configuration

This project uses a flexible configuration system that loads settings from multiple sources with the following priority:

1. Command-line arguments (highest priority)
2. Environment variables (format: `APP_SECTION_KEY`, e.g., `APP_DATABASE_HOST`)
3. `secret.ini` (for sensitive data, not committed to version control)
4. `config.<env>.ini` (environment-specific settings)
5. `config.ini` (base settings, lowest priority)

### Example Usage

```python
from {{ cookiecutter.package_name }}.config import Config

# Load configuration with default environment
config = Config()

# Load configuration with specific environment
config = Config(env="prod")

# Load configuration with command-line overrides
config = Config(config_overrides=[("database.host", "localhost"), ("api.timeout", "60")])

# Get configuration values
db_host = config.get_config("database.host")
api_settings = config.get_config("api")  # Returns entire section as dict
```

## Usage

You can run the application in several ways:

### Using Poetry

```bash
poetry run {{ cookiecutter.project_slug }}
```

### Using the main script

```bash
python main.py
```

### Command-line arguments

```bash
# Run with a specific environment
python main.py --env prod

# Override configuration values
python main.py --config database.host localhost --config api.timeout 60
```

## Development

{% if cookiecutter._template and cookiecutter._commit -%}
### Update project from template

```bash
poetry run cruft-update
```

{% endif -%}

{% if cookiecutter.use_pre_commit == 'y' -%}
### Set up pre-commit hooks

```bash
poetry run pre-commit install
```

{% endif -%}

{% if cookiecutter.use_pytest == 'y' -%}
### Run tests

```bash
poetry run pytest
```

{% endif -%}

{% if cookiecutter.use_black == 'y' -%}
### Format code

```bash
poetry run black .
```

{% endif -%}

{% if cookiecutter.use_flake8 == 'y' -%}
### Lint code

```bash
poetry run flake8
```

{% endif -%}

{% if cookiecutter.use_mypy == 'y' -%}
### Type check

```bash
poetry run mypy {{ cookiecutter.package_name }}
```

{% endif -%}
