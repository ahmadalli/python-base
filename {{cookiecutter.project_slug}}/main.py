#!/usr/bin/env python3
"""Entry point for the application."""
import sys
from {{ cookiecutter.package_name }}.main import main

if __name__ == "__main__":
    sys.exit(main())
