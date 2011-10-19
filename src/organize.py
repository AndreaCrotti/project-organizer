#!/usr/bin/env python2
"""
TODO:
1. read and validate the configuration
2. parse arguments to see what should be done
3. report nicely some results

Some good information to show
- last time updated
- last time modified
- time spent on if possible
- differences between original and cloned repository

"""
import argparse
import logging

from configobj import ConfigObj
from glob import glob
from sys import argv
from validate import Validator
from subprocess import Popen, PIPE

logger = logging.getLogger('organizer')

DEFAULT_CONF = 'projects.ini'
DEFAULT_SPEC = 'projects.spec'


class ShellCommandRunner(object):
    """
    This class is in charge of executing shell commands, capture
    output and so on
    """
    def __init__(self, cmd, args):
        # cmd might have to be validated or found in the system in the
        # path, and this should be done in a OS-independent way
        self.cmd = cmd
        self.args = args

    def run(self, relative_cwd=None):
        if relative_cwd:
            pass


class Profile(object):
    """A profile declares some extra options which might come handy
    """
    pass


class Project(object):
    pass


class Conf(object):
    # the conf is just a list of projects
    def __init__(self):
        pass


def load_configuration():
    val = Validator()
    config = ConfigObj(DEFAULT_CONF, configspec=DEFAULT_SPEC)
    print config.validate(val)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entry point to manage projects')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='list all the projects')

    parser.add_argument('-c', '--config',
                        help='additional configuration')

    parser.add_argument('projects',
                        metavar='PROJECT',
                        nargs='+',
                        help='which projects to run the command')

    ns = parser.parse_args(argv[1:])
