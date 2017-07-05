"""
The `CommandExecutor` reads `Command` objects from a queue and
calls their `run` methods.
"""

from Queue import Queue
from etl_utils import QueueableThreadable


class CommandExecutor(QueueableThreadable):

    def __init__(self):
        self.outgoing_command_queue = Queue()
        super(CommandExecutor, self).__init__()

    def process_thing(self, thing, *args, **kwargs):
        print 'CommandExecutor passthrough:', thing
