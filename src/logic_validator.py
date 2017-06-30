"""
We will use the term "logic validation" to mean all validation
that requires retrieving other data.

This class is obviously a stub.
"""

import time
from Queue import Queue


class LogicValidator(object):

    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        self.input_queue = etl_utils.MissingQueue()
        self.output_queue = Queue()

    def __call__(self, entity):
        """
        Return True if entity passes its tests; False otherwise.
        """

        return True

    def log_validation_failure(self, thing):
        """
        We'll send this to a real log. For now, just a stub.
        """
        
        print 'Failed validation:', thing

    def start(self):
        while 1:
            while self.input_queue.empty():
                time.sleep(self.check_interval)
            thing = self.input_queue.get()
            if self(thing):
                self.output_queue.put(thing)
            else:
                self.log_validation_failure(thing)
