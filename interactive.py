#!/usr/bin/env python2

import organize as org
from conf import DEFAULT_CONF
from cmd import Cmd

from sys import exit

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
        

pif __name__ == '__main__':
    interpreter = Prj(org.load_configuration(org.DEFAULT_CONF, org.MultiProject,
                                             org.Project))
    interpreter.cmdloop()
