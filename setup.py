"""Setup configuration for Gender Detection package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
readme_file = this_directory / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else "Gender Detection from Togolese Names"

# Read requirements (use production requirements if available, fallback to requirements.txt)
requirements_file = this_directory / "requirements-prod.txt"
if not requirements_file.exists():
    requirements_file = this_directory / "requirements.txt"
requirements = requirements_file.read_text().splitlines()
requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="gender-detection-togo",
    version="1.0.0",
    author="Ambroise KOUWADAN",
    author_email="ambroisekouwadan52@gmail.com",
    description="Machine learning system for gender detection from Togolese names",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gender-detection",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.990',
            'pylint>=2.15.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'gender-detect=gender_detection.cli:main',
            'gender-train=gender_detection.model:train_model',
        ],
    },
    include_package_data=True,
    package_data={
        'gender_detection': ['templates/*.html', 'static/*'],
    },
)
