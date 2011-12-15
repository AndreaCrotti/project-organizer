"""
Workflow:
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

from os import getcwd
from organizer.commander import ShellCommandRunner


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
        return "lp" in url


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


class ShellCommandFailed(Exception):
    def __init__(self, message, retcode):
        super(ShellCommandFailed, self).__init__(message)
        self.retcode = retcode

    def __str__(self):
        return "Shell command failed %s: %d" % (self.message, self.retcode)


class MalformedEntry(Exception):
    #TODO: this should take some information about the actual object
    #analysed
    pass


class NoStorageFound(MalformedEntry):
    def __init__(self, message):
        super(NoStorageFound, self).__init__(message)



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
        if not found in match:
            raise NoStorageFound("no valid storage found in %s" % url)

        assert found in match
        # where should be the user/password couple?
        # probably in some sort of encrypted database, or in a standard format
        return match[found](found, url)


class Plain(Storage):
    pass


class SCM(Storage):
    """
    contains the interface that has to be implemented by each of the
    scm classes, and some functions which are similar for all of them.

    Does it make sense to make a distinction between centralised and
    non centralised models

    We need to have a very easy way to declare new aliases in a smart way.
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
            self.update(self.path)

    def create_repository(self, hosting):
        pass


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