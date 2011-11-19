#!/usr/bin/env python2
"""
Workflow
1. read and validate the configuration
2. parse arguments to see what should be done
3. report nicely some results
4. if possible to create a DB of programs and their usual positions

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

# taken from hgapi.py
def hg_command(self, *args):
    """Run a hg command in path and return the result.
    Throws on error."""
    proc = Popen(["hg", "--cwd", self.path, "--encoding", "UTF-8"] + list(args), stdout=PIPE, stderr=PIPE)

    out, err = [x.decode("utf-8") for x in  proc.communicate()]

    if proc.returncode:
        cmd = (" ".join(["hg", "--cwd", self.path] + list(args)))
        raise Exception("Error running %s:\n\tErr: %s\n\tOut: %s\n\tExit: %s"
                        % (cmd,err,out,proc.returncode))
    return out


class ProjectType(object):
    build_cmd = ""
    markers = tuple()  # empty

    @classmethod
    def detect(cls, base):
        """Detect the kind of project and return it
        """
        prj_types = (PythonProject, AutoconfProject, MakefileOnly, ProjectType)
        for p in prj_types:
            markers = p.markers
            if any(path.isfile(path.join(base, x)) for x in markers):
                return p()


class PythonProject(ProjectType):
    build_cmd = "python setup.py develop --user"
    markers = ('setup.py',)


class AutoconfProject(ProjectType):
    #TODO: there should be also a way to configure it
    build_cmd = "./configure && make -j3"
    markers = ('configure.in', 'configure.ac', 'Makefile.am')


class MakefileOnly(ProjectType):
    build_cmd = "make"
    markers = ('Makefile', )


class Project(object):

    def __init__(self, name, opts):
        self.name = name
        self.storage = None
        self.type = None
        self.create_project(opts)

    def __str__(self):
        return self.name

    def create_project(self, opts):
        self.storage = Storage.detect(opts)
        self.type = ProjectType.detect(self.name)


class MultiProject(object):

    def __init__(self, name, conf_dict):
        self.name = name
        self.project_list = self.parse(conf_dict)

    def __iter__(self):
        return iter(self.project_list)

    # # if we don't have the attribute
    # def __getattribute__(self, attr):
    #     try:
    #         getattr(self, attr)
    #     except AttributeError:
    #         for prj in self.project_list:
    #             getattr(prj, attr)

    def parse(self, opts):
        project_list = []
        # load the specific entries
        for key, val in opts.items():
            #TODO: assert maybe is better
            if type(val) == dict:
                project_list.append(Project(key, val))

        return project_list


#TODO: see maybe if we can define the interface in a smarter way
class Storage(object):
    """a Project declares some extra options which might come handy
    """
    def build(self):
        raise NotImplementedError

    # some commands which should be possible from every profile
    def backup(self):
        raise NotImplementedError

    @classmethod
    def detect(cls, opts):
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
        return match[found](found, url)


class ConfParser(object):
    PRIVATE = ("profiles", "default")

    def __init__(self, configuration):
        self.configuration = configuration

    #FIXME: not the right place
    def __str__(self):
        res = []
        for key, val in self.configuration.items():
            res.append("%s -> %s" % (key, str(val)))

        return '\n'.join(res)

    def parse(self):
        conf = {}
        for sec in self.configuration:
            if sec not in self.PRIVATE:
                sub_entry = self.configuration[sec]
                if 'url' not in sub_entry:
                    conf[sec] = MultiProject(sec, sub_entry)
                else:
                    conf[sec] = Project(sec, sub_entry)

        return conf


class Plain(Storage):
    pass


class SCM(Storage):
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

    def __init__(self, ex, url, user_pwd=None):
        # base executable
        self.ex = ex
        self.url = url
        # if the user and password are none then we should be only
        # able to fetch in theory, otherwise it must be a tuple
        self.user_pwd = user_pwd

    def __str__(self):
        return "%s -> %s" % (self.ex, self.url)

    def _validate(self):
        # the resolv can also be done here, so there's no real need of
        # that class ShellCommandRunner
        return ShellCommandRunner.resolve(self.ex) is not None

    def clone(self, dest_dir):
        if not self.user_pwd:
            logger.warn("fetching without authentication, read only repository")
        # put the arguments together
        # if the path already exists maybe we should do a checkout
        if path.isdir(dest_dir):
            logger.warn("path already existing, trying a checkout instead")
            self.fetch(write=True)

        else:
            args = [self.clone_cmd, dest_dir]
            # fetch the repository there
            ShellCommandRunner(self.ex, args).run(dest_dir)

    #TODO: the ShellCommandRunner is not really helping in this case
    def fetch(self, dest_dir, write=False):
        """
        Fetch new commits, and update the working directory if write= Truex
        """
        # the command used for fetching new commits
        args = [self.fetch_cmd, self.url, dest_dir]
        ShellCommandRunner(self.ex, args).run()

        if write:
            self.update()

    def update(self, dest_dir):
        args = [self.update_cmd, ]
        ShellCommandRunner(self.ex, args).run(dest_dir)

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
    update_cmd = "update"
    fetch_cmd = "checkout"


class GitSvn(SCM):
    pass


class BZR(SCM):
    update_cmd = "branch"
    fetch_cmd = "fetch"
    clone_cmd = "checkout"


def load_configuration(config_file):
    val = Validator()
    conf = ConfigObj(config_file, configspec=DEFAULT_SPEC)
    #TODO: FIX the validation process
    # print(conf.validate(val))
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

    parser.add_argument('-a', '--action',
                        choices=['fetch', 'update', 'clone'],
                        help='action to execute')

    # the project can be passed as a choice
    parser.add_argument('projects',
                        metavar='PROJECT',
                        nargs='*',
                        help='which projects to run the command, all of them if not specified')

    return parser.parse_args()


if __name__ == '__main__':
    ns = parse_arguments()
    conf = load_configuration(ns.config)
    c = ConfParser(conf).parse()

    if not ns.projects:
        ns.projects = c.keys()  # scan on everything

    # depending on the object which is actually found we might have
    # different possible actions
    if not ns.action:
        for key, found  in c.items():
            print(found)
            # getattr(found, ns.action[0])()
