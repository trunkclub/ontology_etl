"""
A place for little helper functions.
"""

import yaml


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
