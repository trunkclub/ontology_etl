# Ontology ETL

## Design principles

This is an ETL framework designed to simplify the ingestion of data from a variety of data sources having incompatible formats.

Modern ETL frameworks are designed to handle huge amounts of data and very high throughput. But this isn't nearly the most important ETL problem that the vast majority of organizations face. There is an interconnected set of problems that we typically find in ETL processes:

* Initially, data ingestion happens from a small number of sources, and so a bit of custom code is written that can handle it.
* Over time, the number of sources increases until the amount of custom code is overwhelming.
* With the increase in the number of sources, more complex triggering logic has to occur. New data requires existing data to be updated; for example, the sale of a new widget may require the total number of widgets to be updated. This is typically done in a series of batch processes.
* The number of batch processes increases until the database is strained.
* Furthermore, batch processes depend on upstream batch processes; so a failure in one will cause failures in others.
* These updates are very fragile -- the failure of a single record to update correctly can cause an entire batch process (and all its downstream dependencies) to fail.
* As the number of sources and destinations increases, the number of necessary transformations increases exponentially.

Ontology ETL is designed to alleviate these problems with a few design principles:

* All transformations, data sources, destinations, validations, and triggering logic is encoded in configurations, not in custom code.
* All data is translated to a single, unified data model; and all output is derived from data that adheres to that model. The data model is described in configurations, so it is thereby documented in a single place.
* As the number of sources and destinations increases, the number of transformations increases arithmetically, not exponentially, because the data model is the single basis for every data source and destination.
* All steps of the ETL process are loosely coupled, and are connected to each other by a customizable, swappable queuing mechanism that automatically handles logging and alerting.
* If custom code is required, it can be dynamically loaded at runtime, without necessitating new code deployments. Custom code can be called from configurations, so it is never necessary to modify the ETL pipeline source code directly.
* Batch processing is largely eliminated because new jobs can be dynamically triggered during data ingestion. Rather than doing a mass update of many records (most of which are updates are usually unnecessary), the pipeline updates single records right away, as the updates are necessary. Data is not allowed to go stale before a batch update is executed.

## The ontology

The core concept of the framework is the "ontology", which is a single data model for all your data.

For example, suppose you are an retail business selling widgets to customers. You may ingest data on your customers from your website, from third parties, social media, and so on. Naturally, your customers will be represented by various data formats depending on the data source.

In your ontology (or data model), you would probably have a kind of entity called a "Customer". Each "Customer" would have a variety of different attributes -- e.g. a UUID, name, phone number, number of widgets purchased, social media accounts, and so on. Each data source in the Ontology ETL framework would contain a configuration describing how to translate its data into a "Customer" entity. For example, if one data source ingested from a sequence of CSV files, it might have a column called "CUSTOMER_PHONE_NUMBER", and another data source might have the same information in a JSON file under the key "PHONE". In this framework, both values would be translated immediately into a single attribute in each "Customer" entity, for example, "phone_number".

This way, validation can occur one time instead of two. If it was necessary to store customer data in multiple databases as it was ingested, we would only need to translate from the "Customer" entity to each data source, effectively halving the number of transformations that would have to be defined.

In order to add a new data source, we need only worry about how to translate it into the ontology. Once it is ingested, the rest of the pipeline works exactly as before, with no modifications. Similarly if we need to store the data in a new database. We do not need to worry about the data formats from each of the sources; we only need to design the transformations necessary to go from the ontology to the new database.

## ETL Pipeline

The main class of an ETL pipeline is the `ETLPipeline`. Each `ETLPipeline` comprises several steps, each of which has its own class and runs in its own thread. The `ETLPipeline` glues them together, handles the message passing and threading, loads the configurations, and so on.

The components of each pipeline are the following:

1. `DataSource` This class describes the type and source of data that is ingested. For example, a `DataSource` could be a process that watches a directory for new JSON files to appear. The framework contains a number of custom classes that handle various ways of ingesting data -- for example, ingesting from CSV files that are periodically dropped in a directory, reading from a Kafka topic, etc.
2. `EntityAlligator` This class aggregates data from the sources and allocates it to downstream processes (hence, allocator + aggregator = alligator). It transforms each piece of raw data from the sources into the ontology by dynamically instantiating Python classes that are described in configuration files. In the course of this process, it does the first level of validation: ensuring that data types are correct, that mandatory attributes are defined, and so on.
3. `LogicValidator` This component handles more complex validation requirements. Any validation requiring additional data to be loaded is referred to in this framework as "logic validation". For example, we might want to ensure that the number of widgets sold is not more than the number of widgets manufactured. In order to perform this check each time a widget is sold, we would have to look up (in a different database) the total number of widgets manufactured.
4. `DependencyChecker` When a datum has passed validation, we check whether it should trigger an update to a different entity. For example, we might keep track of the total number of widgets purchased by each customer. So when a customer purchases a widget, that number would have to be incremented. The `DependencyChecker` knows which attributes of which entities depend on others. So when a specific attribute is updated, any downstream dependencies are triggered. This amounts to creating (what we call) a "Job" and placing it in a queue. In practice, this is usually the queue that feeds into the `LogicValidator`. Naturally, this job could itself trigger a cascade of other downstream jobs.
5. `CommandExecutor` Anything that potentially changes the state of a database is called a "Command" in this framework. After all validation steps have been passed and downstream dependencies identified, the actual database updates are queued as "Commands" and sent to the `CommandExecutor`. It is aware of all databases and is configured to translate each attribute in the ontology to a specific field or column (or what-have-you) in each database. Successes and failures are logged by the `CommandExecutor`.

Each of these five stages is connected by a queue, which adds helpful metadata to each item that passes through it. Timing information, warnings, exceptions, data sources, and so on are automatically tracked. Logs of failures include this information to make debugging less painful.

