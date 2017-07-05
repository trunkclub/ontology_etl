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
from command_executor import CommandExecutor

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
        else:
            raise Exception('Tried to add something weird.')
        other.pipeline = self

    def connect_components(self):
        for data_source in self.data_sources:
            print 'connecting data sources:'
            data_source > self.alligator
        (self.alligator > self.logic_validator >
         self.dependency_checker > self.command_executor)


if __name__ == '__main__':
    etl_pipeline = ETLPipeline()
    ontology.instantiate_data_sources()
    alligator = Alligator()
    logic_validator = LogicValidator()
    dependency_checker = DependencyChecker()
    command_executor = CommandExecutor()
    
    etl_pipeline.add(alligator)
    etl_pipeline.add(logic_validator)
    etl_pipeline.add(dependency_checker)
    etl_pipeline.add(command_executor)
    for data_source in ontology.SOURCES_STORE.itervalues():
        etl_pipeline.add(data_source)
  
    etl_pipeline.connect_components()
   
    snippet_dict = {}
    for entity_name, entity_configuration in (
            etl_pipeline.alligator.entities_configuration.iteritems()):
        snippet_list = entity_configuration['command_snippets']
        for snippet_name in snippet_list:
            snippet_function = load_snippet(*snippet_name.split('.'))
            snippet_dict[snippet_name] = snippet_function

    etl_pipeline.snippet_dict = snippet_dict

    etl_pipeline.logic_validator_thread = logic_validator.start()
    etl_pipeline.dependency_checker_thread = dependency_checker.start()
    etl_pipeline.data_source_thread_dict = ontology.start_data_sources()
    etl_pipeline.command_executor_thread = command_executor.start()

    for message in alligator.raw_entities():
        print message.payload
        print message.origin.__dict__
        data_source_name = message.origin.name
        relevant_entities = alligator.source_to_entity_dict[data_source_name]
        print 'Relevant entities:', relevant_entities
        print 'Data source:      ', data_source_name
        for entity in relevant_entities:
            entity_attribute_dict = alligator.entities_configuration[entity][
                'attributes']
            attribute_dict = {}
            for attribute, attribute_config in entity_attribute_dict.iteritems():
                data_source_config = [
                    i for i in attribute_config['sources']
                    if data_source_name in i.keys()][0][data_source_name]
                required = data_source_config['required']
                keypath = data_source_config['keypath']  # Is keypath general enough?
                attribute_value = etl_utils.get_key_path(message.payload, keypath)
                attribute_dict[attribute] = attribute_value
            thing = alligator.entities_dict[entity](**attribute_dict)
            alligator.output_queue.put(thing)
