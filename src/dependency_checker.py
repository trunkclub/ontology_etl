"""
Checks whether we need to trigger a recalculation because some
attribute could have been affected by some data we just
processed.
"""

import importlib
import sys
from etl_utils import QueueableThreadable, get_yaml_files_from_directory
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
        super(DependencyChecker, self).__init__()

    def process_thing(self, thing, *args, **kwargs):
        output = thing
        entity = thing.entity
        print 'DependencyChecker:', output
        if isinstance(thing, UpsertCommand):
            entity_type = entity.__class__.__name__
        else:
            # Add elif statements for dependencies on other commands
            return
        entity_dependencies = self.dependency_config[entity_type]['upsert']  # Make this parameter later
        for attribute in entity.__dict__.keys():
            attribute_dependencies = entity_dependencies.get(attribute, [])
            for action_dict in attribute_dependencies:
                func = self.pipeline.snippet_dict[action_dict['snippet']]
                new_entity = self.pipeline.alligator.entities_dict[action_dict['entity']]()
                new_entity.name = entity.name
                setattr(new_entity, action_dict['attribute'], func(entity))
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
    print d
