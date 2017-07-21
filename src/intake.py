"""
First pass at ETL ingestion

The goal of `intake.py` is to define classes and methods for taking
raw data sources, loading them, and serializing them.

The serialized forms of these will be sent to constructors for the
appropriate entity classes.
"""

import yaml
import json
from watchdog.observers import Observer
from watchdog.events import (
    LoggingEventHandler, RegexMatchingEventHandler, FileCreatedEvent,
    FileModifiedEvent)
from global_configs import *
from etl_utils import Queueable

class QueuedData(object):

    def __init__(self, payload, origin):
        self.payload = payload
        self.origin = origin


class DataSource(Queueable):

    def __init__(self, name=None):
        self.name = name
        super(DataSource, self).__init__()

    def start(self):
        raise Exception('`start` method should be overridden by child class.')
    
    def stop(self):
        raise Exception('`stop` method should be overridden by child class.')

    def attach(self, alligator):
        self.output_queue = alligator.input_queue
        alligator.data_sources[self.name] = self


class FileSource(DataSource):
    """
    Class for ingesting from files as they are detected by watchdog.
    """
    
    def __init__(self, directory=None, name=None):
        print 'initializing FileSource'
        self.directory = directory
        super(FileSource, self).__init__(name=name)
    
    def start(self):
        """
        Starts watchdog thread to monitor for incoming files. Calls the
        child class's `read` method when a new file appears.
        """

        print 'FileSource start method called...', self.directory
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
        print 'observer started.'
        #observer.join()  # Check this
        #print 'observer joined'

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
        print 'initializing JSONFileSource'
        super(JSONFileSource, self).__init__(*args, **kwargs)

    def read(self, path):
        """
        Read the incoming file and load it as JSON object.
        """
        print path
        if isinstance(path, (FileCreatedEvent, FileModifiedEvent,)):
            path = path.src_path
        else:
            return
        with open(path, 'r') as incoming_file:
            incoming = json.load(incoming_file)
        incoming = QueuedData(incoming, self)
        self.output_queue.put(incoming)


if __name__ == '__main__':
    json_file_source = JSONFileSource(directory=WATCHDOG_DIR)
    json_file_source.start()
