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
