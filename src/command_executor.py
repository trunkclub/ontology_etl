"""
The `CommandExecutor` reads `Command` objects from a queue and
calls their `run` methods.
"""

from etl_utils import Queueable


class CommandExecutor(Queueable):

    def __init__(self):
        super(CommandExecutor, self).__init__()

    def start(self):
        pass
