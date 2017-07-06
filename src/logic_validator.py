"""
We will use the term "logic validation" to mean all validation
that requires retrieving other data.

This class is obviously a stub.
"""

from etl_utils import QueueableThreadable
from command import UpsertCommand
import time


class LogicValidator(QueueableThreadable):

    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        super(LogicValidator, self).__init__()

    def __call__(self, entity):
        """
        Return True if entity passes its tests; False otherwise.
        """

        return True  # Obviously just a stub

    def log_validation_failure(self, thing):
        """
        We'll send this to a real log. For now, just a stub.
        """
        
        print 'Failed validation:', thing

    def process_thing(self, thing, *args, **kwargs):
        print 'LogicValidator passed'
        return thing
