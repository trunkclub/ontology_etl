"""
This aggregates data from the various `DataSource`s and directs them
to the proper `Entity` classes to be instantiated.
"""

import time
import collections
import ontology
from global_configs import *
from etl_utils import get_yaml_files_from_directory, QueueableThreadable


class Alligator(QueueableThreadable):
    """
    Steps:
    1. Load the configs for the ontology.
    2. Cycle through the input queue.
    3. For each data payload in the queue, find the appropriate entity class.
    4. Instantiate the entity and place on output queue.
    """

    def __init__(self, check_interval=1, state_dict=None):
        self.state_dict = state_dict or {}
        self.check_interval = check_interval
        self.entities_dict = {}
        self.entities_configuration = {}
        self.data_sources = {}
        self.source_to_entity_dict = collections.defaultdict(list)
        self.instantiate_entities()  # Entities_dict and entities_configuration
        self.data_source_to_entity_config()  # Reverse mapping
        super(Alligator, self).__init__()
    
    def raw_entities(self):
        """
        Iterate over this method to access all incoming data.
        """

        while 1:
            while self.input_queue.empty():
                time.sleep(self.check_interval)
            # There's something in the input_queue. How exciting!
            thing = self.input_queue.get()
            yield thing

    def instantiate_entities(self):
        self.entities_configuration = get_yaml_files_from_directory(
            ENTITIES_DIR)
        for entity_class, entity_config in (
                self.entities_configuration.iteritems()):
            self.entities_dict[entity_class] = type(
                entity_class, (ontology.Entity,), {})
            self.entities_dict[entity_class].sources_dict = entity_config[
                'sources']
            self.entities_dict[entity_class].attributes = entity_config[
                'attributes'].keys()

    def data_source_to_entity_config(self):
        """
        Creates a mapping from each entity to a list of data sources that
        can be used to construct it.
        """

        for entity_name, config in self.entities_configuration.iteritems():
            for source_name, _ in config['sources'].iteritems():
                self.source_to_entity_dict[source_name].append(entity_name)
    

if __name__ == '__main__':
    pass
