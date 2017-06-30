"""
This aggregates data from the various `DataSource`s and directs them
to the proper `Entity` classes to be instantiated.
"""

import time
from Queue import Queue
from global_configs import *
import etl_utils
import copy


def get_key_path(some_dict, list_of_keys, in_place=False):
    if not isinstance(list_of_keys, list):
        list_of_keys = [list_of_keys]
    tmp_dict = some_dict
    for key in list_of_keys:
        tmp_dict = tmp_dict[key]
    return copy.deepcopy(tmp_dict) if not in_place else tmp_dict 


class Alligator(object):
    """
    Steps:
    1. Load the configs for the ontology.
    2. Cycle through the input queue.
    3. For each data payload in the queue, find the appropriate entity class.
    4. Instantiate the entity and place on output queue.
    """

    def __init__(self, check_interval=1, state_dict=None):
        self.input_queue = Queue()
        self.state_dict = state_dict or {}
        self.check_interval = check_interval
        self.entities_dict = {}
        self.entities_configuration = {}
        self.instantiate_entities()  # entities_dict and entities_configuration

    def attach_data_source(self, data_source):
        data_source.output_queue = self.input_queue

    def __lt__(self, other):
        self.attach_data_source(other)

    def raw_entities(self):
        while 1:
            while self.input_queue.empty():
                time.sleep(self.check_interval)
            # There's something in the input_queue. How exciting!
            thing = self.input_queue.get()
            yield thing

    def instantiate_entities(self):
        self.entities_configuration = etl_utils.get_yaml_files_from_directory(
            ENTITIES_DIR)
        for entity_class, entity_config in (
                self.entities_configuration.iteritems()):
            self.entities_dict[entity_class] = type(entity_class, (Entity,), {})
            self.entities_dict[entity_class].sources_dict = entity_config[
                'sources']


if __name__ == '__main__':
    alligator = Alligator()
