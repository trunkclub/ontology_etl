"""
A `Command` is something that causes a change of state to
a persistant store.
"""

from etl_utils import hexhash


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

    def __repr__(self):
        """
        We'll replace this. Just here to get hashes.
        """

        return self.__class__.__name__ + ' ' + '|'.join(
            [str(getattr(self, attribute)) for attribute in
             sorted(self.__dict__.keys())])


class RecalculateCommand(Command):
    """
    Command to recalculate a specific value, triggered by ingesting
    information that could change its value.
    """

    def __init__(self, snippet=None, snippet_function=None,
                 triggering_entity=None, updating_entity=None,
                 updating_attribute=None):
        self.snippet = snippet
        self.snippet_function = snippet_function
        self.triggering_entity = triggering_entity
        self.updating_entity = updating_entity
        self.updating_attribute = updating_attribute


class UpsertCommand(Command):
    """
    An `UpsertCommand` will take an entity and upsert a row (or
    whatever) into storage which contains all the represented
    attributes about that entity.
    """

    def __init__(self, entity):
        self.entity = entity
        super(UpsertCommand, self).__init__()
