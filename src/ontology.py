"""
This is in charge of taking the output of the `intake` script and
transforming that output into the intermediate representation. The
function of the intermediate representation is to make the ontology
explicit, and provide a unified set of methods for transforming the
data and loading it into a database.
"""

import os
import threading
import collections
from global_configs import *
from intake import *
import yaml
import etl_utils


SOURCES_STORE = {}


class Entity(object):
    """
    This will be a mix-in class for all dynamically-created entity
    classes from the `entities.yaml` configuration file.
    """
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        super(Entity, self).__init__()


def instantiate_data_sources():
    global SOURCES_STORE
    sources_configuration = etl_utils.get_yaml_files_from_directory(
        DATA_SOURCES_DIR)
    for source_name, source_config in sources_configuration.iteritems():
        constructor_kwargs = {
            key: value for key, value in source_config.iteritems()
            if key not in EXCLUDED_FROM_CONSTRUCTORS}
        constructor_kwargs['name'] = source_name
        SOURCES_STORE[source_name] = globals()[
            source_config['source_type']](**constructor_kwargs)

def start_data_sources():
    global SOURCES_STORE
    data_source_workers = collections.defaultdict(dict)
    for data_source_name, data_source in SOURCES_STORE.iteritems():
        data_source_thread = threading.Thread(target=data_source.start)
        data_source_thread.start()

def attach_data_sources_to_alligator(alligator):
    global SOURCES_STORE
    for data_source_name, data_source in SOURCES_STORE.iteritems():
        data_source > alligator

instantiate_data_sources()

if __name__ == '__main__':
    instantiate_entities()
    instantiate_data_sources()
    
    test_json_file_store = SOURCES_STORE['test_json_file_source']
    start_data_sources()
    attach_data_sources_to_alligator(alligator)
    
    for raw_entity in alligator.raw_entities():
        print raw_entity.__dict__
