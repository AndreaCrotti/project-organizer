#!/usr/bin/env python2
"""
TODO:
1. read and validate the configuration
2. parse arguments to see what should be done
3. report nicely some results
4. check if possible to create a DB of programs and their usual positions

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
    def __init__(self, cmd, args=None):
        # cmd might have to be validated or found in the system in the
        # path, and this should be done in a OS-independent way
        self.cmd = cmd
        if args:
            self.args = args
        else:
            self.args = []

        self.failed = False

    @classmethod
    def _resolve(cls, cmd):
        #TODO: use a way to resolve the path which avoids running with
        #shell=True which doesn't give enough control on the given machine
        return cmd

    def _format_cmd(self):
        return "%s %s" % (self._resolve(self.cmd), ' '.join(self.args))

    #TODO: at the moment the exception and the erroneous return code
    #might have to be threat in the same way
    def run(self, relative_cwd=None):
        #TODO: what should be the type of relative_cwd, is that os-dependent or not?
        try:
            self.proc = Popen(self._format_cmd(),
                              cwd=relative_cwd, stderr=PIPE, stdout=PIPE, shell=True)
            # communicate also waits for the end of the process
            out, err = self.proc.communicate()
        except Exception:
            self.failed = True
        # FIXME: make this more robust and reliable, maybe we should
        # also return True or False depending if it's correctly done
        else:
            if self.proc.returncode != 0:
                self.failed = True


def run_cmd(command, args, cwd):
    """shortcut to execute a command in an easier way
    """
    sh = ShellCommandRunner(command, args)
    sh.run(cwd)


class Profile(object):
    """A profile declares some extra options which might come handy
    """
    pass


class BugTracker(Profile):
    pass


class Commit(object):
    """
    A commit can be shown in the same way everywhere
    """
    pass


class SCM(Profile):
    """
    Contains the interface that has to be implemented by each of the
    SCM classes, and some functions which are similar for all of them
    """

    def __init__(self, url, path, user_pwd=None):
        self.url = url
        # if the user and password are None then we should be only
        # able to fetch in theory, otherwise it must be a tuple
        self.user_pwd = user_pwd
        self.path = path
        # for each of the different methods there can be more ways to
        # fetch the data, must be able to set somehow a priority and
        # how to create the different methods (for example ssh/http etc)

    def fetch(self):
        # put the arguments together
        run_cmd(self.fetch)

    def checkout(self):
        run_cmd(self.checkout)

    def new_commits(self):
        # return a list of new commits, to show in some fancy way
        pass


#TODO: should I also be able to create new repositories?
class Git(SCM):
    pass


class SVN(SCM):
    pass


class GitSVN(SCM):
    pass


class Project(object):
    pass


class Conf(object):
    # the conf is just a list of projects
    def __init__(self):
        pass


def load_configuration(config_file):
    val = Validator()
    config = ConfigObj(config_file, configspec=DEFAULT_SPEC)
    ret = config.validate(val)
    print(ret)
    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entry point to manage projects')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='list all the projects')

    parser.add_argument('-c', '--config',
                        default=DEFAULT_CONF,
                        help='additional configuration')

    parser.add_argument('projects',
                        metavar='PROJECT',
                        nargs='+',
                        help='which projects to run the command')

    ns = parser.parse_args(argv[1:])

    load_configuration(ns.config)
