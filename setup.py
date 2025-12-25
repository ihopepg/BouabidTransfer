"""
BouabidTransfer Setup Script
Production-ready Windows desktop application installer configuration
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="BouabidTransfer",
    version="1.0.0",
    author="BouabidTransfer Team",
    author_email="support@bouabidtransfer.com",
    description="Professional Windows desktop application for iPhone to PC data transfer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/BouabidTransfer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bouabidtransfer=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ui", "*.qss", "*.png", "*.ico", "*.json", "*.yaml"],
    },
    options={
        "build_exe": {
            "include_files": [
                "assets/",
                "config/",
            ],
            "packages": [
                "PyQt5",
                "pymobiledevice3",
                "libimobiledevice",
            ],
        },
    },
)

