"""
A place for little helper functions.
"""

import os
import yaml


class MissingQueue(object):
    """
    This is a dummy class whose only purpose is to indicate that a queue
    hasn't been defined for a `DataSource` object; the exception would
    be raised if we forgot to attach the `DataSource` to an `Alligator`.
    """

    def put(self, *args, **kwargs):
        raise Exception(
            'Trying to put something onto a queue '
            'that has not been defined.')

    def get(self, *args, **kwargs):
        raise Exception(
            'Trying to get an item off a queue that has not '
            'been defined.')


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


def get_key_path(some_dict, list_of_keys, in_place=True):
    if not isinstance(list_of_keys, list):
        list_of_keys = [list_of_keys]
    tmp_dict = some_dict
    for key in list_of_keys:
        tmp_dict = tmp_dict[key]
    return copy.deepcopy(tmp_dict) if not in_place else tmp_dict 


