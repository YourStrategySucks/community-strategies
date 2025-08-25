#!/usr/bin/env python3
"""Setup script for yss-strategies package."""

import os
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="yss-strategies",
    version="1.0.0",
    author="YSS Community",
    author_email="community@yss-strategies.org",
    description="Community-contributed roulette strategies for the YSS framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/YOUR_REPO_NAME",
    project_urls={
        "Bug Reports": "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/issues",
        "Source": "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME",
        "Documentation": "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/wiki",
        "Strategy Submission": "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/issues/new?template=strategy-submission.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "pylint>=2.15.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "twine>=4.0.0",
            "build>=0.8.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.5.0",
            "mkdocstrings[python]>=0.19.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="roulette gambling strategy simulation gaming community",
    entry_points={
        "console_scripts": [
            "yss-validate=yss_strategies.scripts.validate:main",
            "yss-benchmark=yss_strategies.scripts.benchmark:main",
            "yss-list=yss_strategies.scripts.list_strategies:main",
        ],
    },
)
