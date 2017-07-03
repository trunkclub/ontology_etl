"""
A `Command` is something that causes a change of state to
a persistant store.
"""


class Command(object):
    """
    Inherit `Command` for specific commands that cause a chage
    of state in a persisted database.
    """

    def __init__(self, *args, **kwargs):
        pass

    def run(self):
        """
        Override `run` in each subclass; this is called by the
        `JobExecutor`. It must be defined for each subclass
        """

        raise NotImplementedError(
            'Override the `run` method in every subclass of `Job`.')


class UpsertCommand(Command):
    """
    An `UpsertCommand` will take an entity and upsert a row (or
    whatever) into storage which contains all the represented
    attributes about that entity.
    """

    def __init__(self, entity):
        super(UpsertCommand, self).__init__()
        self.entity = entity
