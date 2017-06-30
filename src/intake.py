"""
First pass at ETL ingestion

The goal of `intake.py` is to define classes and methods for taking
raw data sources, loading them, and serializing them.

The serialized forms of these will be sent to constructors for the
appropriate entity classes.
"""

import yaml
import json
from Queue import Queue
from watchdog.observers import Observer
from watchdog.events import (
    LoggingEventHandler, RegexMatchingEventHandler, FileCreatedEvent,
    FileModifiedEvent)
from global_configs import *
import etl_utils


class QueuedData(object):

    def __init__(self, payload, origin):
        self.payload = payload
        self.origin = origin


class DataSource(object):

    def __init__(self, name=None):

        self.output_queue = etl_utils.MissingQueue()
        self.name = name

    def attach(self, alligator):
        """
        Attach the `Alligator` input queue to the `DataSource` object.
        """

        alligator.attach_data_source(self)

    def __gt__(self, other):
        """
        Just 'cuz we can be cute and overload operators.
        """

        self.attach(other)

    def start(self):
        raise Exception('`start` method should be overridden by child class.')
    
    def stop(self):
        raise Exception('`stop` method should be overridden by child class.')


class FileSource(DataSource):
    """
    Class for ingesting from files as they are detected by watchdog.
    """
    
    def __init__(self, directory=None, name=None):
        self.directory = directory
        super(FileSource, self).__init__(name=name)
    
    def start(self):
        """
        Starts watchdog thread to monitor for incoming files. Calls the
        child class's `read` method when a new file appears.
        """

        event_handler = RegexMatchingEventHandler(
            regexes=['.*'],
            ignore_regexes=[],
            ignore_directories=False,
            case_sensitive=False)
        event_handler.on_created = self.read  # Call child's `read` method
        event_handler.on_modified = self.read
        watch_path = self.directory
        observer = Observer()
        observer.schedule(event_handler, watch_path, recursive=False)
        observer.start()
        observer.join()  # Check this

    def read(self, *args, **kwargs):
        """
        The `read` method should define how to load the particular type of file
        into memory. It will vary according to the child class, e.g. whether
        we're reading a CSV, parquet, etc.

        This method exists in the `FileSource` class only for informative
        error handling.
        """

        raise Exception('`read` method should be overridden by child class.')


class JSONFileSource(FileSource):
    """
    Class for ingesting JSON files
    """

    def __init__(self, *args, **kwargs):
        super(JSONFileSource, self).__init__(*args, **kwargs)

    def read(self, path):
        """
        Read the incoming file and load it as JSON object.
        """
        if isinstance(path, (FileCreatedEvent, FileModifiedEvent,)):
            path = path.src_path
        with open(path, 'r') as incoming_file:
            incoming = json.load(incoming_file)
        incoming = QueuedData(incoming, self)
        self.output_queue.put(incoming)


if __name__ == '__main__':
    json_file_source = JSONFileSource(directory=DATA_SOURCES_DIR)

