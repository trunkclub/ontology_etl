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
        self.data_store_config = get_yaml_files_from_directory(DATA_STORES_DIR)
        self.data_store_config = self.data_store_config[self.name]
        self.entity_data = self.data_store_config['contains']

    def upsert(self, *args, **kwargs):
        raise Exception(
            'The `upsert` method must be overridden by any class '
            'inheriting from `DataStore`.')

    def get_attribute(self, entity_type, entity_identifier, attribute):
        raise Exception(
            'The `get_attribute` method must be overridden by class '
            'inheriting from `DataStore`.')


class MySQLDataStore(DataStore):
    """
    MySQL is nice. Why do people say mean things about it?
    """

    def __init__(
        self, name=None, host=None, user=None,
            password=None, database=None):
        self.host = host or MYSQL_HOST
        self.user = user or MYSQL_USER
        self.password = password or MYSQL_PASSWORD
        self.database = database or MYSQL_DATABASE
        self.name = name

        self.db = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.database)
        self.cursor = self.db.cursor()

        super(MySQLDataStore, self).__init__()

    def commit(self):
        self.cursor.execute('COMMIT;')

    def upsert(self, entity):
        entity_type = entity.__class__.__name__
        attribute_list = tuple(entity.__dict__.keys())
        attribute_values = tuple(
            [getattr(entity, attribute) for attribute in attribute_list])

        attribute_values_placeholder = ', '.join(['%s'] * len(attribute_values))
        column_list = []
        for attribute in attribute_list:
            table, column = self.entity_data[entity_type][attribute]
            column_list.append(column)
        column_list_string = ', '.join(column_list)
        column_list_string = ''.join(['(', column_list_string, ')'])
        set_clause_list = []
        for column_name, attribute_value in zip(column_list, attribute_values):
            set_clause_list.append(column_name + ' = %s')
        set_clause = ', '.join(set_clause_list)
        query = (
            """INSERT INTO {table} {column_list_string} VALUES """
            """({attribute_values_placeholder}) """
            """ON DUPLICATE KEY UPDATE {set_clause};""").format(
                table=table,
                column_list_string=column_list_string,
                attribute_values_placeholder=attribute_values_placeholder,
                set_clause=set_clause)
        print query
        self.cursor.execute(query, attribute_values + attribute_values)
        self.commit()

    def get_attribute(self, entity_type, entity_identifier, attribute):
        entity_config = self.entity_data[entity_type]
        name_table, name_column = entity_config['name']
        attribute_table, attribute_column = entity_config[attribute]
        query = (
            """SELECT {attribute_column} FROM {attribute_table} """
            """WHERE {name_column} = %s LIMIT 1;""").format(
                attribute_column=attribute_column,
                attribute_table=attribute_table,
                name_column=name_column)
        self.cursor.execute(query, (entity_identifier,))
        result = self.cursor.fetchone()
        return result[0] if len(result) > 0 else None
        

def instantiate_data_store(data_store_name, data_store_configuration):    
    constructor_keywords = data_store_configuration['constructor_options']
    constructor_keywords = {
        keyword: globals()[value] for keyword, value in
        constructor_keywords.iteritems()}
    data_store_class_name = data_store_configuration['data_store_class']
    data_store_class = globals()[data_store_class_name]
    data_store = data_store_class(
        name=data_store_configuration['name'], **constructor_keywords) 
    return data_store


def get_data_stores_dict():
    data_stores_config = get_yaml_files_from_directory(DATA_STORES_DIR)
    data_store_dict = {}
    for data_store_name, data_store_configuration in (
            data_stores_config.iteritems()):
        data_store_configuration['name'] = data_store_name
        data_store_dict[data_store_name] = instantiate_data_store(
            data_store_name, data_store_configuration)
    return data_store_dict


if __name__ == '__main__':
    d = get_data_stores_dict()
    store = d['mysql_test_store']
    entity = 'Person'
    attribute = ['name', 'age']
    value = ['Alice', 97]
    store.upsert(entity, attribute, value)
