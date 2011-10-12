from setuptools import setup, find_packages

package = 'project_organizer'
#TODO: get the revision number from git revparse
version = '0.1'

INSTALL_REQUIRES = []

try:
    import argparse
except ImportError:
    INSTALL_REQUIRES.append('argparse')

try:
    import configobj
except ImportError:
    INSTALL_REQUIRES.append('configobj')

setup(
    name=package,
    version=version,
    packages=find_packages(),
    description="organize multiple projects",
    author='Andrea Crotti',
    author_email='andrea.crotti.0@gmail.com',
    scripts=['src/organize.py']
    )
