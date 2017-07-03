"""
The `CommandExecutor` reads `Command` objects from a queue and
calls their `run` methods.
"""

from etl_utils import MissingQueue


class CommandExecutor(object):

    def __init__(self):
        self.input_queue = MissingQueue()

    def start(self):
        pass
