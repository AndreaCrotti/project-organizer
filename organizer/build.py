"""
Parse the type of project, given the build system
"""

from os import path

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
