import sys
from setuptools import setup, find_packages

requires = [
    'argparse',
    'bs4'
]

setup(
    name='Recursive Mail Scraper',
    description=("Finds emails through recursive search from a given URL."),
    version='1.0',
    install_requires=requires,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['remas=RecursiveMailScraper.app:main'],
    },
    long_description=open('README.md').read(),
    keywords=['email', 'scraper']
)
