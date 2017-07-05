"""
Class for interacting with the persistent data storage.
Each subclass must override methods such as `upsert`.

The `get_data_stores_dict()` function returns a dictionary
mapping names of data stores onto their objects. It gets
the configuration from `config/data_stores.yaml` and
dynamically instantiates All The Things.
"""

import MySQLdb
from global_configs import *
from etl_utils import get_yaml_files_from_directory


class DataStore(object):

    def __init__(self):
        pass

    def upsert(self, *args, **kwargs):
        raise Exception(
            'The `upsert` method must be overridden by any class '
            'inheriting from `DataStore`.')


class MySQLDataStore(DataStore):
    """
    MySQL is nice. Why do people say mean things about it?
    """

    def __init__(self, host=None, user=None, password=None, database=None):
        self.host = host or MYSQL_HOST
        self.user = user or MYSQL_USER
        self.password = password or MYSQL_PASSWORD
        self.database = database or MYSQL_DATABASE

        self.db = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.database)
        self.cursor = self.db.cursor()


def instantiate_data_store(data_store_name, data_store_configuration):    
    constructor_keywords = data_store_configuration['constructor_options']
    constructor_keywords = {
        keyword: globals()[value] for keyword, value in
        constructor_keywords.iteritems()}
    data_store_class_name = data_store_configuration['data_store_class']
    data_store_class = globals()[data_store_class_name]
    data_store = data_store_class(**constructor_keywords) 
    return data_store


def get_data_stores_dict():
    data_stores_config = get_yaml_files_from_directory(DATA_STORES_DIR)
    data_store_dict = {}
    for data_store_name, data_store_configuration in (
            data_stores_config.iteritems()):
        data_store_dict[data_store_name] = instantiate_data_store(
            data_store_name, data_store_configuration)
    return data_store_dict


if __name__ == '__main__':
    print get_data_stores_dict()
