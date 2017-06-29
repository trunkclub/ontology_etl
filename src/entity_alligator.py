"""
This aggregates data from the various `DataSource`s and directs them
to the proper `Entity` classes to be instantiated.
"""

class Alligator(object):
    """
    Steps:
    1. Load the configs for the ontology.
    2. Attach the relevant `DataSource` objects.
    3. Cycle through the source output queues.
    4. For each data source, locate a list of entities
       and instantiate them accordingly.
    """

    def __init__(self):
        pass
