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
import json
import yaml
import hashlib
from global_configs import *
import cPickle as pickle
import etl_utils
from intake import JSONFileSource

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

    def __getstate__(self):
        output = ''
        for attribute, value in self.__dict__.iteritems():
            try:
                output += pickle.dumps(attribute)
                output += pickle.dumps(value)
            except:
                pass
        return output

    @classmethod
    def instantiate(cls, data_store, identifier):
        """
        Just experimenting with dynamic instantiation magic.
        """
        pass

    def list_attributes(self):
        return sorted(self.__dict__.keys())

    def to_json(self):
        attributes = {
            attribute: getattr(self, attribute) for
            attribute in self.list_attributes()}
        return json.dumps(attributes, sort_keys=True)

    def hash(self):
        s = self.__class__.__name__ + self.to_json()
        return hashlib.md5(s).hexdigest()


def instantiate_data_sources():
    print 'instantiate_data_sources()'
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
    data_source_thread_dict = {}
    data_source_workers = collections.defaultdict(dict)
    for data_source_name, data_source in SOURCES_STORE.iteritems():
        data_source_thread = threading.Thread(target=data_source.start)
        data_source_thread_dict[data_source_name] = data_source_thread
        data_source_thread.start()
    return data_source_thread_dict

def attach_data_sources_to_alligator(alligator):
    global SOURCES_STORE
    for data_source_name, data_source in SOURCES_STORE.iteritems():
        data_source > alligator

# instantiate_data_sources()

if __name__ == '__main__':
    
    test_json_file_store = SOURCES_STORE['test_json_file_source']
    start_data_sources()
    attach_data_sources_to_alligator(alligator)
    
    for raw_entity in alligator.raw_entities():
        print raw_entity.__dict__
