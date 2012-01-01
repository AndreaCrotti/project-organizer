from configobj import ConfigObj
from validate import Validator


DEFAULT_SPEC = 'projects.spec'
DEFAULT_CONF = 'projects.ini'


def load_configuration(config_file, multi, simple):
    #TODO: rewrite the validation process
    # val = Validator()
    conf = ConfigObj(config_file, configspec=DEFAULT_SPEC)
    return ConfParser(conf).parse(multi, simple)
