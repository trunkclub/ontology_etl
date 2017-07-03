"""
Checks whether we need to trigger a recalculation because some
attribute could have been affected by some data we just
processed.
"""
from etl_utils import MissingQueue

class DependencyChecker(object):

    def __init__(self, *args, **kwargs):
        self.input_queue = MissingQueue()
        self.output_queue = MissingQueue()

     
