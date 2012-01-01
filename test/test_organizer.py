"""
Test the organizer script
TODO:
- how can the test be independent on the OS which is actually used?
- use heavily StringIO and similar for mocking the filesystem

"""

from StringIO import StringIO
import unittest

#TODO: make it in such a way that it will be easy to move around
import organizer.organize as org
import organizer.conf as conf

#TODO: switch to something smarter

class TestShellCommands(unittest.TestCase):

    def test_not_existing_fails(self):
        sh_commander = org.ShellCommandRunner('ldfs')
        sh_commander.run('dslkfj')

    def test_run_cmds(self):
        sh_commander = org.ShellCommandRunner('ls')
        sh_commander.run()

    def test_resolving_things(self):
        self.assertTrue(org.ShellCommandRunner.resolve('git') is not None)
        print(org.ShellCommandRunner.resolve('bzr'))


class TestValidation(unittest.TestCase):
    # ideally everything which is not specifically declared in the
    # validation file should not be allowed

    # creates a simple string with a configuration
    # might also pass a dictionary maybe (easier to test)
    simple_spec = """
    [default]
    checkout = False
    default = True
    """

    def test_mispelled_option_fails(self):
        io = StringIO(self.simple_spec)
        # print(org.load_configuration(io))
        #TODO: make this work again
        # self.assertTrue(org.load_configuration(io))
