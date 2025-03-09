"""Cruft utilities"""

import subprocess


def update():
    """
    Update the project from its Cookiecutter template.
    This runs:
    1. cruft update - to update from the template
    2. poetry lock - to update dependencies
    3. black - to format code
    4. pre-commit install - to set up git hooks
    """
    commands = [
        ["cruft", "update", "--allow-untracked-files"],
        ["poetry", "lock"],
        ["poetry", "install"],
        ["poetry", "run", "black", "."],
        ["poetry", "run", "pre-commit", "install"],
    ]

    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")
            return result.returncode

    print("Cookiecutter update completed successfully!")
    return 0


if __name__ == "__main__":
    exit(update())
