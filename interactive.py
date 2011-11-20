#!/usr/bin/env python2

from organize import get_default_configuration
from cmd import Cmd

# cmd version

class Prj(Cmd):

    def __init__(self, conf):
        self.c = ConfParser(conf).parse()

    def do_list(self, _):
        """List all the projects, printing out the some properties
        """
        print(self.c.keys())
        

if __name__ == '__main__':
    interpreter = Prj(get_default_configuration())
    interpreter.cmdloop()
