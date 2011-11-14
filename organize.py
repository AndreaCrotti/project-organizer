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
Try to use as little side-effects as possible.

Add a build hook mechanism, with some kind of defaults.
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
    def __init__(self, url):
        self.url = url


class Github(Hosting):

    @classmethod
    def match(cls, url):
        return "github" in url


class BitBucket(Hosting):

    @classmethod
    def match(cls, url):
        return "bitbucket" in url


class LaunchPad(Hosting):

    @classmethod
    def match(cls, url):
        return "lp" in url


class Customised(Hosting):
    # this should always pass
    pass


def detect_hosting(url):
    # try to automatically go through the list of classes, possibly
    # without really listing them again
    hostings = (BitBucket, Github, LaunchPad)
    for scm in hostings:
        if scm.match(url):
            return scm(url)

    return Customised(url)


# todo: check if this is a good idea, since it's mutable
def run_cmd(command, args, cwd=getcwd()):
    """shortcut to execute a command in an easier way
    """
    sh = ShellCommandRunner(command, args)


class ProjectType(object):
    build_cmd = ""

    @classmethod
    def match(cls, _):
        return True


class PythonProject(ProjectType):
    build_cmd = "python setup.py develop --user"

    @classmethod
    def match(cls, base):
        return path.isfile(path.join(base, 'setup.py'))


class AutoconfProject(ProjectType):
    #TODO: there should be also a way to configure it
    build_cmd = "./configure && make -j3"

    @classmethod
    def match(cls, base):
        markers = ('configure.in', 'configure.ac', 'makefile.am')
        return any(path.isfile(path.join(base, x)) for x in markers)


class MakefileOnly(ProjectType):
    build_cmd = "make"

    @classmethod
    def match(cls, base):
        # if we can count on the order the first check is not useful
        return (not AutoconfProject.match(base)) and \
            (path.isfile(path.join(base, 'Makefile')))


def detect_project_type(path):
    prj_types = (PythonProject, AutoconfProject, MakefileOnly, ProjectType)
    for p in prj_types:
        if p.match(path):
            return p()


#TODO: see maybe if we can define the interface in a smarter way
class Project(object):
    """a Project declares some extra options which might come handy
    """
    def build(self):
        raise NotImplementedError

    # some commands which should be possible from every profile
    def backup(self):
        raise NotImplementedError

    @classmethod
    def parse_entry(cls, name, opts):
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
        found, url = opts['url'].split(' ')
        assert found in match
        # where should be the user/password couple?
        # probably in some sort of encrypted database, or in a standard format
        return match[found](found, url, name)


class ConfParser(object):
    PRIVATE = ("profiles", "default")

    def __init__(self, configuration):
        self.configuration = configuration

    def parse(self):
        for sec in self.configuration:
            if sec not in self.PRIVATE:
                sub_entry = self.configuration[sec]
                if 'url' not in sub_entry:
                    yield MultiProject.parse_multi_entry(sec, sub_entry)
                else:
                    yield Project.parse_entry(sec, sub_entry)


class Plain(Project):
    pass


class MultiProject(object):

    def __init__(self, project_list=None):
        self.project_list = project_list

    def __iter__(self):
        return iter(self.project_list)

    @classmethod
    def parse_multi_entry(cls, name, opts):
        # load the specific entries
        for key, val in opts.items():
            if type(val) == dict:
                yield Project.parse_entry(key, val)
        

class SCM(Project):
    """
    contains the interface that has to be implemented by each of the
    scm classes, and some functions which are similar for all of them.

    Does it make sense to make a distinction between centralised and
    non centralised models
    """

    # some more or less sane defaults
    fetch_cmd = 'fetch'
    update_cmd = 'pull'
    clone_cmd = 'clone'

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
        self.project_type = detect_project_type(self.path)

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
            args = [self.clone_cmd, self.path]
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
        args = [self.update_cmd, ]
        ShellCommandRunner(self.ex, args).run(self.path)

    def new_commits(self):
        # return a list of new commits, to show in some fancy way
        # not all the SCM can do this really easily
        pass


#TODO: we might use attributes when it's a simple command and
#properties if something more complex, to give always exactly the same
#interface
class Mercurial(SCM):
    fetch_cmd = "fetch"
    update_cmd = "pull"


#todo: should i also be able to create new repositories?
class Git(SCM):
    fetch_cmd = "fetch"
    update_cmd = "pull"


class SVN(SCM):
    update_cmd = "update"
    fetch_cmd = "checkout"


class GitSvn(SCM):
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


def parse_arguments():
    parser = argparse.ArgumentParser(description='Entry point to manage projects')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='list all the projects')

    parser.add_argument('-c', '--config',
                        default=DEFAULT_CONF,
                        help='additional configuration')

    parser.add_argument('action',
                        nargs=1,
                        choices=['fetch', 'update', 'clone'],
                        help='action to execute')

    parser.add_argument('projects',
                        metavar='PROJECT',
                        nargs='*',
                        help='which projects to run the command, all of them if not specified')

    return parser.parse_args()
    

if __name__ == '__main__':
    ns = parse_arguments()
    conf = load_configuration(ns.config)
    c = ConfParser(conf)

    for found in c.parse():
        getattr(found, ns.action[0])()
