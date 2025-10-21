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
    version='2.1.0',
    description='Kiwoom Securities REST API Python Wrapper',
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
