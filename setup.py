"""Setup configuration for Repoman."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="repoman",
    version="0.1.0",
    description="Autonomous repository agent that can read, write, and refactor code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Repoman Contributors",
    python_requires=">=3.8",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.25.0",
        "gitpython>=3.1.40",
        "PyYAML>=6.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "repoman=repoman.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
