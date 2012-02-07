from cmd import Cmd
from sys import exit

from organizer.conf import DEFAULT_CONF

# cmd version

class Prj(Cmd):

    def __init__(self, conf):
        self.conf = conf
        Cmd.__init__(self)

    def do_list(self, _):
        """List all the projects, printing out the some properties
        """
        print(self.conf.keys())

    def do_quit(self):
        """Exit the interpreter
        """
        exit(0)


def loop(conf):
    interpreter = Prj(conf)
    interpreter.cmdloop()
