# Ontology ETL
This project is in its early stages.

# Motivation

This is an experimental framework for orchestrating complex ETL jobs in a configurable way.

Here’s an example of a typical ETL problem. WidgetCo sells widgets to customers. Each point of sale triggers a message to be sent with the customer’s ID number and the number of widgets that customer has just purchased. Each transaction is to be recorded into a SQL table. Additionally, WidgetCo has a separate table (possibly in a different database) where customer information is aggregated. It has a column containing customer IDs, and a second column containing the total number of widgets that customer has ever purchased.

In the real world, it’s very unlikely that the two tables represent the same information in the same way. The first table might have a `customer_id` column, whereas the second has the same information in the `id` column, for example. And the event generated at the point of sale might be a JSON document that looks like: `{customer: {id: 123}, purchased: 2}` So a typical ETL pipeline contains logic that’s hard-coded, mapping the structure of the JSON blob to the appropriately named columns in the first table. Then, the customer aggregation table could be batch updated each night to recalculate the number of purchased widgets for each customer. The batch job will have the column names of the aggregation table, as well as any business logic, hard-coded.

The problems with such ETL processes are very well-appreciated. Data goes stale prior to each batch update; hard-coded business logic becomes opaque over time; the number of hard-coded transformations increases (sometimes exponentially) as the number of data sources and data stores increases; and the total number of batch processes only increases as the business requirements become more demanding. The result is a tangle of ETL jobs, inconsistent conventions, slow (and fragile) batch jobs, stale data that slows down the business, and brittle code that’s difficult to understand and even harder to modify.

The Ontology ETL framework advocates a different process that stresses configurability and consistency, while discouraging too much reliance on batch updates. The most important component of the framework is the *ontology*. This is a unified data model that all validation, transformation, and business logic is applied to. All data is immediately transformed, via a simple set of configurations, into the ontology. This way, each validation and transformation can be defined once, regardless of where the data originated. Commands to change the state of the databases are made against the ontology, and each data store is configured to understand how to execute the proper low-level command (e.g. SQL `INSERT INTO`). Additionally, the framework allows you to configure a set of dependencies among the entities and attributes in the ontology. This way, whenever an aggregated value becomes out of date, the framework immediately produces and queues the command to do the proper update for that particular entity (as opposed to doing a batch update for everything, which is usually wasteful).

We can illustrate the process by going back to the WidgetCo example. The major components of the pipeline would be the following:


1. An ontology where we define (e.g.) a `Customer` entity having the attributes `customer_id` and `total_widgets_purchased`. We would also have a `Transaction` entity with the attributes `customer_id` and `widgets_purchased`.
2. A `DataSource` object for the point of sale data stream. It would be configured with a mapping from its JSON structure to the ontology. For example, it would map the nested keypath `customer.id` onto the `Transaction` object’s `customer_id` attribute. The pipeline would then know how to transform each incoming JSON object into canonical `Transaction` object.
3. A dependency rule expressing the condition that whenever there is a new `Transaction`, the pipeline should cause an update to the appropriate `Customer`'s `total_widgets_purchased` attribute.
4. A pair of `DataStore` objects representing the SQL tables that will ultimately store this information. Each `DataStore` is configured with a mapping from the ontology to its (in this case) columns.

There are several advantages to this framework:


1. Aggregated information does not go stale, because small, targeted updates are immediately triggered whenever necessary.
2. New data sources can be added by configuring the mapping from their data structure to the ontology. No additional code is necessary, and any applicable downstream transformations or calculations will be triggered on the new data automatically. 
3. All business logic, validations, transformations, etc. are expressed using the same model (the ontology) and the same names and conventions are used everywhere. This makes the pipeline much cleaner, easier to read, and simpler to modify.
4. The configurations are easy to read, and they document the underlying data model.
5. Many batch jobs are eliminated, resulting in simpler, more robust ETL processes.
6. Any command or event in the ETL pipeline can easily be logged into a commit log (e.g. Kafka). This enables easier debugging; it also enables the ETL process to be “replayed” in case of a failure, or in case it’s necessary to update the data model or any part of the infrastructure.
# High-level workflow

Ontology ETL breaks down the ETL process into several discrete stages. Each stage is connected to the previous one by a queue. When it does its job, the result is placed on the queue for the next stage. Each type of stage corresponds to a Python class that is defined in the `ontology_etl` module.

An ETL process is created by instantiating each class and adding them to a `Pipeline` object, which is in charge of linking them together and coordinating their work. In addition, it is necessary to write configurations defining the underlying data model, as well as all the sources and targets of the data.


1. **Data source listener** Data from a particular source (e.g. file drops, database updates, Kafka messages) is ingested into the pipeline by a `DataSource` object. No specific transformation is done by the `DataSource` — its only responsibility is to pick up the raw data and put it into the pipeline.
2. **Alligator (=allocator + aggregator)** The main responsibility of the `Alligator` is to transform the raw data into the pipeline’s unified data model (more on this later). Each type of entity represented in the data is instantiated into its own (dynamically generated) class, which is defined in a configuration file. The instantiated entity is validated during its construction with respect to attribute types and other “surface level” features. Assuming it passes validation, the entity is placed in the queue for further processing.
3. **Logic validator** The data has already been validated with respect to types and required attributes. We use the term “logic validation” to refer to any further validation that requires a lookup from a data store. For example, if we were ingesting customer data on payments and refunds, we might want to check that a customer’s total refunds don’t exceed her total payments. This would require looking up the customer’s payments in a database. Hence, that validation step would occur here. Entities that do not pass the logic validation step are logged and not processed by the rest of the pipeline.
4. **Command generator** There are a few different types of commands that can be carried out by the ETL pipeline, such as inserting data to a table. When the command generate processes a particular type of entity, it looks up whether this event should trigger (e.g.) an insert to a table, or the modification of an value in the table. The relevant commands are generated here and put into a queue.
5. **Dependency checker** Some commands ought to trigger other commands to be generated. For example, if were tracking the total number of widgets sold to each customer, then a sales transaction for a customer should trigger a recalculation of the total number of widgets that customer has purchased. The `DependencyChecker` inspects each command prior to its being executed, creates any additional commands that are trigger by it, and places those new commands back onto its own incoming queue (so that if necessary, further commands can be generated from it). The original command and any other commands eventually make their way onto the next queue.
6. **Command executor** This is where we finally update our data store. Commands are run by the `CommandExecutor` for each relevant `DataStore` (e.g. a SQL database). These `DataStore` classes must have methods corresponding to each command type. For example, an `UpsertCommand` will cause the command executor to call the `DataStore`'s `upsert` method.

