#!/usr/bin/env python
"""PyKiwoom-REST setup script"""

from setuptools import setup, find_packages
import os

# Read the contents of README
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read the contents of requirements.txt
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='pykiwoom-rest',
    version='2.2.0',
    description='키움증권 REST API Python 래퍼와 CLI, MCP 서버',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='PyKiwoom-REST Development Team',
    author_email='dev@pykiwoom-rest.io',
    url='https://github.com/unohee/pykiwoom-rest',
    project_urls={
        'Bug Reports': 'https://github.com/unohee/pykiwoom-rest/issues',
        'Source Code': 'https://github.com/unohee/pykiwoom-rest',
        'Documentation': 'https://github.com/unohee/pykiwoom-rest/blob/master/README.md',
    },
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'mcp': ["mcp>=1.27,<2; python_version >= '3.10'"],
    },
    entry_points={
        'console_scripts': [
            'kiwoom=pykiwoom_rest.cli.main:main',
            'kiwoom-mcp=pykiwoom_rest.mcp_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords=[
        'kiwoom',
        'trading',
        'stock',
        'api',
        'korea',
        'securities',
    ],
    zip_safe=False,
)
