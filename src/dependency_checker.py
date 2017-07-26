"""
Checks whether we need to trigger a recalculation because some
attribute could have been affected by some data we just
processed.
"""

import importlib
import sys
from etl_utils import (
    find_key_value, QueueableThreadable,
    get_yaml_files_from_directory, load_snippet)
from global_configs import *
from command import UpsertCommand, RecalculateCommand


class DependencyRule(object):

    def __init__(
        self, triggering_entity=None, triggering_attribute=None,
        snippet=None, snippet_function=None, updating_entity=None,
            updating_attribute=None):
        
        self.triggering_entity = triggering_entity
        self.triggering_attribute = triggering_attribute
        self.snippet = snippet
        self.updating_entity = updating_entity
        self.updating_attribute = updating_attribute


class DependencyChecker(QueueableThreadable):

    def __init__(self, *args, **kwargs):

        self.dependency_config = get_yaml_files_from_directory(DEPENDENCIES_DIR)
        # Insert snippets from dependency_config dictionary here
        all_snippet_names = []
        for snippet_key in [
                'calculating_snippet', 'identifier_function_snippet']:
            snippet_names = find_key_value(
                self.dependency_config, snippet_key)
            all_snippet_names += snippet_names
        self.snippet_dict = {
            snippet_name: load_snippet(*snippet_name.split('.')) for
            snippet_name in all_snippet_names}

        super(DependencyChecker, self).__init__()

    def process_thing(self, thing, *args, **kwargs):
        output = thing
        entity = thing.entity
        if isinstance(thing, UpsertCommand):
            entity_type = entity.__class__.__name__
        else:
            # Add elif statements for dependencies on other commands
            return
        
        # Make `upsert` a parameter later
        if entity_type not in self.dependency_config:
            return output

        entity_dependencies = self.dependency_config[entity_type]['upsert']
        for attribute in entity.__dict__.keys():
            attribute_dependencies = entity_dependencies.get(attribute, [])
            for action_dict in attribute_dependencies:
                calculating_func = self.pipeline.snippet_dict[
                    action_dict['calculating_snippet']]
                identifier_func = self.pipeline.snippet_dict[
                    action_dict['identifier_function_snippet']]
                new_entity = self.pipeline.alligator.entities_dict[
                    action_dict['entity']]()
                new_entity.name = identifier_func(entity)
                setattr(
                    new_entity,
                    action_dict['attribute'],
                    calculating_func(entity))

                self.pipeline.logic_validator.input_queue.put(new_entity)
        return output


if __name__ == '__main__':

    if SNIPPETS_DIR not in sys.path:
        sys.path.append(SNIPPETS_DIR)
    dependency_checker = DependencyChecker()
    d = dependency_checker.dependency_config
    for entity, config in d.iteritems():
        for attribute, dependency_list in config.iteritems():
            for dependency in dependency_list:
                snippet, snippet_function = dependency['snippet'].split('.')
                triggering_entity = entity
                triggering_attribute = attribute
                updating_entity = dependency['entity']
                updating_attribute = dependency['attribute']
                command = RecalculateCommand(
                    snippet=snippet,
                    snippet_function=snippet_function,
                    triggering_entity=triggering_entity,
                    updating_entity=updating_entity,
                    updating_attribute=updating_attribute)
    module = importlib.import_module('mean_age_snippet')
