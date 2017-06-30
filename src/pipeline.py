import ontology
import entity_alligator
from logic_validator import LogicValidator
from global_configs import *
import intake
import etl_utils


if __name__ == '__main__':
    alligator = entity_alligator.Alligator()
    logic_validator = LogicValidator()
    alligator > logic_validator
    ontology.instantiate_data_sources()
    ontology.attach_data_sources_to_alligator(alligator)
    ontology.start_data_sources()
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
            import pdb; pdb.set_trace()

