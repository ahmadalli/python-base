#!/usr/bin/env python
import os
import requests
import subprocess

LICENSE_URLS = {
    "MIT": "https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt",
    "BSD-3-Clause": "https://raw.githubusercontent.com/licenses/license-templates/master/templates/bsd3.txt",
    "GPL-3.0": "https://raw.githubusercontent.com/licenses/license-templates/master/templates/gpl3.txt",
    "Apache": "https://raw.githubusercontent.com/licenses/license-templates/master/templates/apache.txt",
}


def download_license():
    """Download the selected license after project generation."""
    license_choice = "{{ cookiecutter.open_source_license }}"

    if license_choice == "None":
        # If no license is selected, remove the LICENSE file
        license_file = os.path.join(os.getcwd(), "LICENSE")
        if os.path.exists(license_file):
            os.remove(license_file)
        return

    # Get the license URL
    license_url = LICENSE_URLS.get(license_choice)
    if not license_url:
        print(
            f"Warning: Unknown license '{license_choice}'. No license file will be created."
        )
        return

    # Download the license
    try:
        response = requests.get(license_url)
        response.raise_for_status()

        # Replace placeholders in the license text
        license_text = response.text
        license_text = license_text.replace(
            "{% raw %}{{ year }}{% endraw %}", "{% now 'utc', '%Y' %}"
        )
        license_text = license_text.replace(
            "{% raw %}{{ organization }}{% endraw %}",
            "{{ cookiecutter.author_name }}",
        )
        license_text = license_text.replace(
            "{% raw %}{{ project }}{% endraw %}",
            "{{ cookiecutter.project_name }}",
        )

        # Write the license file
        with open(os.path.join(os.getcwd(), "LICENSE"), "w") as f:
            f.write(license_text)

        print(f"Successfully downloaded {license_choice} license.")

    except Exception as e:
        print(f"Error downloading license: {e}")


def init_git():
    """Initialize git repository with initial commit."""
    try:
        # Check if git is installed
        subprocess.run(
            ["git", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Skip if .git directory exists
        if os.path.exists(".git"):
            print("Git repository already exists. Skipping initialization.")
            return

        # Initialize git repository
        subprocess.run(["git", "init"], check=True)

        # Add all files
        subprocess.run(["git", "add", "."], check=True)

        # Create initial commit
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

        print("Git repository initialized with initial commit.")
    except subprocess.CalledProcessError:
        print("Failed to initialize git repository. Make sure git is installed.")
    except Exception as e:
        print(f"An error occurred while initializing git: {e}")


if __name__ == "__main__":
    download_license()

    # Initialize git repository
    init_git()
