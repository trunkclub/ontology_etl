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

ENTITIES_STORE = {}
SOURCES_STORE = {}


class Entity(object):
    """
    This will be a mix-in class for all dynamically-created entity
    classes from the `entities.yaml` configuration file.
    """

    pass


def get_yaml_files_from_directory(target_directory):
    """
    This loads all the yaml configuration files from `target_directory`
    and returns a dictionary that combines them.
    """

    configuration = {}
    for file_name in os.listdir(target_directory):
        if not file_name.endswith('.yaml'):
            continue
        file_name = '/'.join([target_directory, file_name])
        with open(file_name, 'r') as config_file:
            configuration.update(yaml.load(config_file))
    return configuration


def instantiate_entities():
    global ENTITIES_STORE
    entities_configuration = get_yaml_files_from_directory(ENTITIES_DIR)
    for entity_class, entity_config in entities_configuration.iteritems():
        ENTITIES_STORE[entity_class] = type(entity_class, (Entity,), {})
        ENTITIES_STORE[entity_class].sources_dict = entity_config['sources']


def instantiate_data_sources():
    global SOURCES_STOR
    sources_configuration = get_yaml_files_from_directory(DATA_SOURCES_DIR)
    for source_name, source_config in sources_configuration.iteritems():
        constructor_kwargs = {
            key: value for key, value in source_config.iteritems()
            if key not in EXCLUDED_FROM_CONSTRUCTORS}
        SOURCES_STORE[source_name] = globals()[
            source_config['source_type']](**constructor_kwargs)

def start_data_sources():
    global SOURCES_STORE
    data_source_workers = collections.defaultdict(dict)
    for data_source_name, data_source in SOURCES_STORE.iteritems():
        print data_source_name, data_source
        data_source_thread = threading.Thread(target=data_source.start)
        data_source_thread.start()

if __name__ == '__main__':
    instantiate_entities()
    instantiate_data_sources()
    start_data_sources()
