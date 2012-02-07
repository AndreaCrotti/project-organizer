from setuptools import setup, find_packages

package = 'project_organizer'
#TODO: get the revision number from git revparse
version = '0.1'

INSTALL_REQUIRES = []

REQUIRED_DATA = {
    'conf': ['sample.ini', 'projects.spec']
}

try:
    import argparse
except ImportError:
    INSTALL_REQUIRES.append('argparse')

try:
    import configobj
except ImportError:
    INSTALL_REQUIRES.append('configobj')

# TODO: use console-entry points instead to make it more multi-platform
setup_cfg = {
    'name': package,
    'version': version,
    'packages': find_packages(),
    'package_data': REQUIRED_DATA,
    'include_package_data': True,
    'description': "organize multiple projects",
    'install_requires': INSTALL_REQUIRES,
    'test_requires': ['nose', 'mock'],
    'test_suite': 'nose.collector',
    'author': 'Andrea Crotti',
    'author_email': 'andrea.crotti.0@gmail.com',
    'scripts': ['bin/organizer.py']
}

setup(**setup_cfg)
