import argparse
import logging

from organizer.conf import load_configuration, DEFAULT_CONF
from organizer.organize import Project

# set a simple logging mechanism
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    conf = load_configuration(ns.config, MultiProject, Project)

    if not ns.projects:
        ns.projects = conf.keys()  # scan on everything

    # depending on the object which is actually found we might have
    # different possible actions
    if not ns.action:
        for key, found  in conf.items():
            print(found)
            # getattr(found, ns.action[0])()
