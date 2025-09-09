"""
Setup script for Night Writer Terminal Automation System

Author: João Panizzutti
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="night-writer-automation",
    version="1.0.0",
    author="João Panizzutti",
    description="Terminal automation system for scheduled task execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "night-writer=night_writer_cli:main",
            "night-writer-automation=terminal_automation:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="automation terminal cli scheduling tasks",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/night-writer/issues",
        "Source": "https://github.com/your-repo/night-writer",
    },
)
