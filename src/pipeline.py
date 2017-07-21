import ontology
import entity_alligator
from logic_validator import LogicValidator
from dependency_checker import DependencyChecker
from global_configs import *
import intake
import etl_utils
from etl_utils import run_in_thread, load_snippet
from intake import DataSource
from entity_alligator import Alligator
from command_generator import CommandGenerator
from command_executor import CommandExecutor
from data_store import DataStore, get_data_stores_dict


class ETLPipeline(object):
    """
    Holds the entire pipeline.
    """

    def __init__(self):
        self.data_sources = []
        self.alligator = None
        self.logic_validator = None
        self.dependency_checker = None
        self.command_executor = None
        self.data_store_dict = {}

        self.logic_validator_thread = None
        self.data_source_thread_dict = None

    def add(self, other):
        if isinstance(other, DataSource):
            self.data_sources.append(other)
        elif isinstance(other, Alligator):
            self.alligator = other
        elif isinstance(other, LogicValidator):
            self.logic_validator = other
        elif isinstance(other, DependencyChecker):
            self.dependency_checker = other
        elif isinstance(other, CommandExecutor):
            self.command_executor = other
        elif isinstance(other, DataStore):
            self.data_store_dict[other.name] = other
        elif isinstance(other, CommandGenerator):
            self.command_generator = other
        else:
            raise Exception('Tried to add something weird.')
        other.pipeline = self

    def connect_components(self):
        for data_source in self.data_sources:
            print 'connecting data sources:'
            data_source > self.alligator
        (self.alligator > self.logic_validator >
         command_generator > self.dependency_checker > self.command_executor)


if __name__ == '__main__':
    etl_pipeline = ETLPipeline()
    ontology.instantiate_data_sources()
    alligator = Alligator()
    logic_validator = LogicValidator()
    dependency_checker = DependencyChecker()
    command_generator = CommandGenerator()
    command_executor = CommandExecutor()
   
    data_stores_dict = get_data_stores_dict()

    etl_pipeline.add(alligator)
    etl_pipeline.add(logic_validator)
    etl_pipeline.add(dependency_checker)
    etl_pipeline.add(command_generator)
    etl_pipeline.add(command_executor)
    etl_pipeline.add(alligator)
    for data_source in ontology.SOURCES_STORE.itervalues():
        etl_pipeline.add(data_source)
    for data_store in data_stores_dict.itervalues():
        etl_pipeline.add(data_store)
  
    etl_pipeline.connect_components()
 
    snippet_dict = {}
    snippet_list = []
    for entity_name, entity_configuration in (
            etl_pipeline.alligator.entities_configuration.iteritems()):
        for source_name, source_config_list in entity_configuration[
                'sources'].iteritems():
            for source_config in source_config_list:
                # Add other types of snippets to load here
                if 'test_snippet' in source_config:
                    snippet_list.append(source_config['test_snippet'])
        
    for snippet_name in snippet_list:
        snippet_function = load_snippet(*snippet_name.split('.'))
        snippet_dict[snippet_name] = snippet_function

    import pdb; pdb.set_trace()

    etl_pipeline.snippet_dict = snippet_dict

    etl_pipeline.logic_validator_thread = logic_validator.start()
    etl_pipeline.dependency_checker_thread = dependency_checker.start()
    etl_pipeline.data_source_thread_dict = ontology.start_data_sources()
    etl_pipeline.command_generator.start()
    etl_pipeline.command_executor_thread = command_executor.start()
    etl_pipeline.alligator.start()
