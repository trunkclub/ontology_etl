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
        output = UpsertCommand(thing)
        print 'DependencyChecker passthrough:', output
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
