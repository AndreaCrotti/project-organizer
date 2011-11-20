from configobj import ConfigObj
from validate import Validator


DEFAULT_SPEC = 'projects.spec'
DEFAULT_CONF = 'projects.ini'

# from organize import MultiProject, Project


class ConfParser(object):
    PRIVATE = ("profiles", "default")

    def __init__(self, configuration):
        self.configuration = configuration

    #FIXME: not the right place
    def __str__(self):
        res = []
        for key, val in self.configuration.items():
            res.append("%s -> %s" % (key, str(val)))

        return '\n'.join(res)

    def parse(self):
        """Parse 
        """
        conf = {}
        for sec in self.configuration:
            if sec not in self.PRIVATE:
                sub_entry = self.configuration[sec]
                if 'url' not in sub_entry:
                    #TODO: project and multiproject should be passed from the outside
                    conf[sec] = MultiProject(sec, sub_entry)
                else:
                    conf[sec] = Project(sec, sub_entry)

        return conf


def load_configuration(config_file):
    val = Validator()
    conf = ConfigObj(config_file, configspec=DEFAULT_SPEC)
    #TODO: FIX the validation process
    # print(conf.validate(val))
    #TODO: raise an exception in case it didn't work out
    return ConfParser(conf).parse()
