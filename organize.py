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

After the first validation we should also check if all the commands we
need are actually found in the path, using the
ShellCommandRunner.resolve function

Try to use metaclasses and create a nice DSL.
Try to use as little side-effects as possible
"""

import argparse
import logging
from os import path, environ, getcwd, pathsep

from configobj import ConfigObj
from sys import argv
from validate import Validator
from subprocess import Popen, PIPE

# set a simple logging mechanism
logging.basicConfig()
logger = logging.getLogger('organizer')
logger.setLevel(logging.DEBUG)

DEFAULT_CONF = 'projects.ini'
DEFAULT_SPEC = 'projects.spec'
SIMULATE = True


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
    def resolve(cls, cmd):
        """Resolve the full path of the executable, or return None if
        nothing was found
        """
        ps = environ['PATH'].split(pathsep)
        for pt in ps:
            # not checking if also executable here
            full = path.join(pt, cmd)
            if path.isfile(full):
                return full
        # otherwise nothing is clearly found

    def _format_cmd(self):
        # could also be a double join
        # return ' '.join([self.resolve(self.cmd), ] + self.args)
        return [self.resolve(self.cmd), ] + self.args

    #todo: at the moment the exception and the erroneous return code
    #might have to be threat in the same way
    def run(self, relative_cwd=None):
        #todo: what should be the type of relative_cwd, is that os-dependent or not?
        cmd = self._format_cmd()
        logger.info("running command %s" % cmd)
        if SIMULATE:
            logger.debug("only simulating")
            # this return is just to avoid the indentation level
            return

        try:
            #TODO: this part should be made parallel, maybe rewriting
            #with zeromq or a simple threading infrastructure
            proc = Popen(self._format_cmd(),
                         cwd=relative_cwd, stderr=PIPE, stdout=PIPE)
            # communicate also waits for the end of the process
            out, _ = proc.communicate()
        except Exception:
            self.failed = True
        # fixme: make this more robust and reliable, maybe we should
        # also return true or false depending if it's correctly done
        else:
            if proc.returncode != 0:
                self.failed = True
            else:
                # in this case there should be no error
                return out

class Hosting(object):
    """
    Every different hosting service might provide different features,
    such as mailing lists, different bug tracking mechanisms and so on.
    """
    match = None

    def is_hosting_type(self, url):
        # call the function or lookup the string
        if callable(self.match):
            # this is something that pylint can't possibly detect
            self.match(url)
        else:
            return url.find(match)


class Github(Hosting):
    match = "github"


class BitBucket(Hosting):
    match = "bitbucket"


class LaunchPad(Hosting):
    match = "lp"


class Customised(Hosting):
    # this should always pass
    match = lambda _: True


def detect_hosting(url):
    # try to automatically go through the list of classes, possibly
    # without really listing them again
    pass


# todo: check if this is a good idea, since it's mutable
def run_cmd(command, args, cwd=getcwd()):
    """shortcut to execute a command in an easier way
    """
    sh = ShellCommandRunner(command, args)


#TODO: see maybe if we can define the interface in a smarter way
class Profile(object):
    """a Profile declares some extra options which might come handy
    """
    # some commands which should be possible from every profile
    def backup(self):
        raise NotImplementedError


class ConfParser(object):
    PRIVATE = ("profiles", "default")

    def __init__(self, configuration):
        self.configuration = configuration

    def _parse_entry(self, name, opts):
        """
        Parse an entry in the form [scala-mode] url = ...
        and create the correct repository out of it
        """
        match = {
            'git': Git,
            'bzr': BZR,
            'svn': SVN,
            'hg': Mercurial,
            'plain': Plain
        }
        # this should be part of the validation process too
        # import pdb; pdb.set_trace()
        print("analysing %s" % name)
        found, url = opts['url'].split(' ')
        assert found in match
        # where should be the user/password couple?
        # probably in some sort of encrypted database, or in a standard format
        return match[found](found, url, name)

    def parse(self):
        #TODO: refactor this messy thing
        for sec in self.configuration:
            if sec not in self.PRIVATE:
                sub_entry = self.configuration[sec]
                if 'url' not in sub_entry:
                    # load the specific entries
                    for key, val in sub_entry.items():
                        if type(val) == dict:
                            yield self._parse_entry(key, val)
                else:
                    yield self._parse_entry(sec, sub_entry)


class Plain(Profile):
    pass


class SCM(Profile):
    """
    contains the interface that has to be implemented by each of the
    scm classes, and some functions which are similar for all of them
    """

    fetch_cmd = None
    update_cmd = None

    def __init__(self, ex, url, path, user_pwd=None):
        # base executable
        self.ex = ex
        self.url = url
        # if the user and password are none then we should be only
        # able to fetch in theory, otherwise it must be a tuple
        self.user_pwd = user_pwd
        self.path = path
        # for each of the different methods there can be more ways to
        # fetch the data, must be able to set somehow a priority and
        # how to create the different methods (for example ssh/http etc)

    def _validate(self):
        # the resolv can also be done here, so there's no real need of
        # that class ShellCommandRunner
        return ShellCommandRunner.resolve(self.ex) is not None

    def clone(self):
        if not self.user_pwd:
            logger.warn("fetching without authentication, read only repository")
        # put the arguments together
        # if the path already exists maybe we should do a checkout
        if path.isdir(self.path):
            logger.warn("path already existing, trying a checkout instead")
            self.fetch(write=True)
            
        else:
            args = (self.clone, self.path)
            # fetch the repository there
            ShellCommandRunner(self.ex, args).run(self.path)

    #TODO: the ShellCommandRunner is not really helping in this case
    def fetch(self, write=False):
        """
        Fetch new commits, and update the working directory if write= Truex
        """
        # the command used for fetching new commits
        args = [self.fetch_cmd, self.url, self.path]
        ShellCommandRunner(self.ex, args).run()

        if write:
            self.update()

    def update(self):
        args = [self.update, ]
        ShellCommandRunner(self.ex, args).run(self.path)

    def new_commits(self):
        # return a list of new commits, to show in some fancy way
        # not all the SCM can do this really easily
        pass


class Mercurial(SCM):
    fetch_cmd = "fetch"
    update_cmd = "pull"


#todo: should i also be able to create new repositories?
class Git(SCM):
    fetch_cmd = "fetch"
    update_cmd = "pull"


class SVN(SCM):
    checkout_cmd = "update"
    fetch_cmd = "checkout"


class GitSvn(SCM):
    pass


class Project(object):
    pass


class BZR(SCM):
    cmd = "bzr"
    


class Conf(object):
    # the conf is just a list of projects
    def __init__(self):
        pass


def load_configuration(config_file):
    val = Validator() 
    conf = ConfigObj(config_file, configspec=DEFAULT_SPEC)
    ret = conf.validate(val)
    #TODO: raise an exception in case it didn't work out
    return conf


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entry point to manage projects')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='list all the projects')

    parser.add_argument('-c', '--config',
                        default=DEFAULT_CONF,
                        help='additional configuration')

    parser.add_argument('action',
                        nargs=1,
                        choices=['fetch', 'update'],
                        help='action to execute')

    parser.add_argument('projects',
                        metavar='PROJECT',
                        nargs='*',
                        help='which projects to run the command')

    ns = parser.parse_args(argv[1:])

    conf = load_configuration(ns.config)
    c = ConfParser(conf)
    for found in c.parse():
        getattr(found, ns.action[0])()
