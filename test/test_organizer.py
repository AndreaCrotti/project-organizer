"""
Test the organizer script
TODO:
- how can the test be independent on the OS which is actually used?
- use heavily StringIO and similar for mocking the filesystem

"""

from StringIO import StringIO
import unittest

#TODO: make it in such a way that it will be easy to move around
import src.organize as org

#TODO: switch to something smarter

class TestShellCommands(unittest.TestCase):

    def test_not_existing_fails(self):
        self.sh_commander = org.ShellCommandRunner('ldfs')
        self.sh_commander.run('dslkfj')
        # is it really a good idea to create a FSM for this thing
        self.assertTrue(self.sh_commander.failed)

    def test_run_cmds(self):
        self.sh_commander = org.ShellCommandRunner('ls')
        self.sh_commander.run()
        # the command should in theory pass
        self.assertFalse(self.sh_commander.failed)


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
        self.io = StringIO(self.simple_spec)
        print(org.load_configuration(self.io))
        #TODO: make this work again
        # self.assertTrue(org.load_configuration(self.io))
