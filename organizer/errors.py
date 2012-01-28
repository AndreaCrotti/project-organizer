class MalformedEntry(Exception):
    pass


class NoStorageFound(MalformedEntry):
    def __init__(self, message):
        super(NoStorageFound, self).__init__(message)

class ShellCommandFailed(Exception):
    def __init__(self, message, retcode):
        super(ShellCommandFailed, self).__init__(message)
        self.retcode = retcode

    def __str__(self):
        return "Shell command failed %s: %d" % (self.message, self.retcode)
