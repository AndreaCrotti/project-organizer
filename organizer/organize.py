"""
Workflow:
1. read and validate the configuration
2. parse arguments to see what should be done
3. report nicely some results
4. if possible to create a DB of programs and their usual positions

Some good information to show
- last time updated
- last time modified
- time spent on the project
- rating of the project
- differences between original and cloned repository

After the first validation we should also check if all the commands we
need are actually found in the path, using the
ShellCommandRunner.resolve function

Try to use metaclasses and create a nice DSL.
Try to use as little side-effects as possible.

Add a build hook mechanism, with some kind of defaults.
"""

import logging

from os import getcwd
from organizer.commander import ShellCommandRunner

logger = logging.getLogger(__name__)


class Hosting(object):
    """
    Every different hosting service might provide different features,
    such as mailing lists, different bug tracking mechanisms and so on.
    """
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return type(self).__name__

    @classmethod
    def detect(cls, url):
        # try to automatically go through the list of classes, possibly
        # without really listing them again
        hostings = (BitBucket, Github, LaunchPad)
        for scm in hostings:
            if scm.match(url):
                return scm(url)

        return Customised(url)


class Github(Hosting):

    @classmethod
    def match(cls, url):
        return "github" in url


class Dropbox(Hosting):

    @classmethod
    def match(cls, url):
        return "Dropbox" in url


class BitBucket(Hosting):

    @classmethod
    def match(cls, url):
        return "bitbucket" in url


class LaunchPad(Hosting):

    @classmethod
    def match(cls, url):
        #FIXME: might lead to false positives
        return "lp:" in url


class Customised(Hosting):
    # this should always pass
    pass


# todo: check if this is a good idea, since it's mutable
def run_cmd(command, args, cwd=getcwd()):
    """shortcut to execute a command in an easier way
    """
    sh = ShellCommandRunner(command, args)

# taken from hgapi.py
# def hg_command(self, *args):
#     """Run a hg command in path and return the result.
#     Throws on error."""
#     proc = Popen(["hg", "--cwd", self.path, "--encoding", "UTF-8"] + list(args), stdout=PIPE, stderr=PIPE)

#     out, err = [x.decode("utf-8") for x in  proc.communicate()]

#     if proc.returncode:
#         cmd = (" ".join(["hg", "--cwd", self.path] + list(args)))
#         raise Exception("Error running %s:\n\tErr: %s\n\tOut: %s\n\tExit: %s"
#                         % (cmd,err,out,proc.returncode))
#     return out

class Project(object):

    def __init__(self, name, opts):
        self.name = name
        # is this really necessary??
        self.storage = None
        self.type = None
        self.hosting = None
        self.opts = opts
        self.create_project()

    def __str__(self):
        return " | ".join(map(str, (self.name, self.storage, self.type, self. hosting)))

    def create_project(self):
        logger.debug("creating project %s" % self.name)
        self.storage = Storage.detect(self.opts)
        self.type = ProjectType.detect(self.name)
        # pass the url which we just derived above
        self.hosting = Hosting.detect(self.storage.url)

    @classmethod
    def parse(self, conf_dic):
        """Parse
        """
        PRIVATE = ("profiles", "default")
        for sec in conf_dic:
            if sec not in PRIVATE:
                sub_entry = conf_dic[sec]
                assert 'url' in sub_entry
                yield Project(sec, sub_entry)
