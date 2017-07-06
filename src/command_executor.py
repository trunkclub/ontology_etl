"""
The `CommandExecutor` reads `Command` objects from a queue and
calls their `run` methods.
"""

from Queue import Queue
from etl_utils import QueueableThreadable
from ontology import Entity
from command import UpsertCommand

class CommandExecutor(QueueableThreadable):

    def __init__(self):
        self.outgoing_command_queue = Queue()
        super(CommandExecutor, self).__init__()

    def process_thing(self, thing, *args, **kwargs):
        if isinstance(thing, Entity):
            command = UpsertCommand(thing)
        else:
            command = thing
        
        print 'CommandExecutor:', command
        if isinstance(command, UpsertCommand):
            for data_store in self.pipeline.data_store_dict.itervalues():
                data_store.upsert(command.entity)
