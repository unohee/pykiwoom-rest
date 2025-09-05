#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyKiwoom-REST Setup Configuration
고성능 키움증권 REST API Python 라이브러리 v2.0
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Version
__version__ = "2.0.0"

setup(
    name="pykiwoom-rest",
    version=__version__,
    author="PyKiwoom Team",
    author_email="contact@pykiwoom-rest.org",
    description="고성능 키움증권 REST API Python 라이브러리",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pykiwoom-rest",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "openpyxl>=3.1.0",
    ],
    extras_require={
        "async": [
            "aiohttp>=3.8.0",
        ],
        "performance": [
            "pandas>=2.0.0",
            "numpy>=1.24.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "all": [
            "aiohttp>=3.8.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
        ]
    },
    keywords=[
        "kiwoom", "securities", "api", "trading", "stock", "finance",
        "rest", "async", "rate-limiting", "high-performance"
    ],
    include_package_data=True,
    zip_safe=False,
)