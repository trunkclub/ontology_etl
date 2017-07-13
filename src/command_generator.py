"""
The `CommandExecutor` reads `Command` objects from a queue and
calls their `run` methods.
"""

from Queue import Queue
from etl_utils import QueueableThreadable
from ontology import Entity
from command import UpsertCommand

class CommandGenerator(QueueableThreadable):

    def __init__(self):
        self.outgoing_command_queue = Queue()
        super(CommandGenerator, self).__init__()

    def process_thing(self, thing, *args, **kwargs):
        print 'in the CommandGenerator'
        if isinstance(thing, Entity):
            command = UpsertCommand(thing)
        else:
            command = thing
        
        return command 
