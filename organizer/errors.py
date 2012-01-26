class MalformedEntry(Exception):
    pass


class NoStorageFound(MalformedEntry):
    def __init__(self, message):
        super(NoStorageFound, self).__init__(message)
