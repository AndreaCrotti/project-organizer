__all__ = [
    'load_configuration'
]

from configobj import ConfigObj


DEFAULT_SPEC = 'projects.spec'
DEFAULT_CONF = 'projects.ini'


def load_configuration(config_file, simple):
    #TODO: rewrite the validation process
    # val = Validator()
    conf = ConfigObj(config_file, configspec=DEFAULT_SPEC)
    return conf
