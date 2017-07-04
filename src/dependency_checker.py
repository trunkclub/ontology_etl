"""
Checks whether we need to trigger a recalculation because some
attribute could have been affected by some data we just
processed.
"""
from etl_utils import MissingQueue, Queueable

class DependencyChecker(Queueable):

    def __init__(self, *args, **kwargs):
        super(DependencyChecker, self).__init__()

     
