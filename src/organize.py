"""
1. read and validate the configuration
2. parse arguments to see what should be done
3. report nicely some results
"""
import argparse
import logging

from configobj import ConfigObj
from glob import glob
from sys import argv
from validate import Validator

logger = logging.getLogger('organizer')

DEFAULT_CONF = 'projects.ini'
DEFAULT_SPEC = 'projects.spec'


class Profile(object):
    """A profile declares some extra options which might come handy
    """
    pass


def load_configuration():
    val = Validator()
    config = ConfigObj(DEFAULT_CONF, configspec=DEFAULT_SPEC)
    print config.validate(val)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entry point to manage projects')

    parser.add_argument('-c', '--config',
                        help='additional configuration')

    parser.add_argument('projects',
                        metavar='PROJECT',
                        nargs='+',
                        help='which projects to run the command')

    ns = parser.parse_args(argv[1:])
