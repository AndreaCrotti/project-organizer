"""
Test the organizer script
"""

import unittest
#TODO: make it in such a way that it will be easy to move around
from src.organize import ShellCommandRunner

#TODO: switch to something smarter

class TestShellCommands(unittest.TestCase):
    #TODO: how can the test be independent on the OS which is actually used

    def test_not_existing_fails(self):
        self.sh_commander = ShellCommandRunner('ldfs')
        self.sh_commander.run('dslkfj')
        # is it really a good idea to create a FSM for this thing
        self.assertTrue(self.sh_commander.failed)
