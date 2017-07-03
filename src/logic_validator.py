"""
We will use the term "logic validation" to mean all validation
that requires retrieving other data.

This class is obviously a stub.
"""

from etl_utils import MissingQueue
import time
from Queue import Queue


class LogicValidator(object):

    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        self.input_queue = MissingQueue()
        self.output_queue = Queue()

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

    def start(self):
        while 1:
            while self.input_queue.empty():
                time.sleep(self.check_interval)
            thing = self.input_queue.get()
            if self(thing):  # If it passes
                self.output_queue.put(thing)
                print 'LogicValidator passed'
            else:
                self.log_validation_failure(thing)

    def attach_dependency_checker(self, dependency_checker):
        dependency_checker.input_queue = self.output_queue

    def __gt__(self, other):
        self.attach_dependency_checker(other)


