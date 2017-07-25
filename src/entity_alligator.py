"""
This aggregates data from the various `DataSource`s and directs them
to the proper `Entity` classes to be instantiated.
"""

import time
import collections
import ontology
from global_configs import *
from etl_utils import get_key_path, get_yaml_files_from_directory, QueueableThreadable


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
            ENTITIES_DIR)  # Move this to __init__?
        for entity_class, entity_config in (
                self.entities_configuration.iteritems()):
            # Insert entity test here; `continue` if False
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

    def process_thing(self, message):
        data_source_name = message.origin.name
        relevant_entities = self.source_to_entity_dict[data_source_name]
        for entity in relevant_entities:
            snippets_dict = self.entities_configuration[entity]['sources'][data_source_name]
            # Test whether this payload should trigger the creation of this entity
            if 'test_snippet' in snippets_dict:
                test_snippet_name = snippets_dict['test_snippet']
                test_function = self.pipeline.snippet_dict[test_snippet_name]
                if not test_function(message.payload):
                    continue
            entity_attribute_dict = self.entities_configuration[entity][
                'attributes']
            attribute_dict = {}
            for attribute, attribute_config in entity_attribute_dict.iteritems():
                data_source_config = [
                    i for i in attribute_config['sources']
                    if data_source_name in i.keys()]
                if len(data_source_config) == 0:
                    continue
                data_source_config = data_source_config[0].get(data_source_name, {})
                required = data_source_config.get('required', None)
                keypath = data_source_config['keypath']  # Is keypath general enough?
                attribute_value = get_key_path(message.payload, keypath)
                attribute_dict[attribute] = attribute_value
            thing = self.entities_dict[entity](**attribute_dict)
            self.output_queue.put(thing)

    def start(self):
        for message in self.raw_entities():
            self.process_thing(message) 
    

if __name__ == '__main__':
    pass
