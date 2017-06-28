"""
First pass at ETL ingestion
"""

import os
import yaml
import json
from watchdog.observers import Observer
from watchdog.events import (
    LoggingEventHandler, RegexMatchingEventHandler, FileCreatedEvent)


BASE_DIR = os.environ['BASE_DIR']
CONFIG_DIR = os.environ['CONFIG_DIR']
DATA_SOURCES_DIR = os.environ['DATA_SOURCES_DIR']
TRANSFORMS_DIR = os.environ['TRANSFORMS_DIR']
ENTITIES_DIR = os.environ['ENTITIES_DIR']
SNIPPETS_DIR = os.environ['SNIPPETS_DIR']
SRC_DIR = os.environ['SRC_DIR']


class DataSource(object):

    def __init__(self, name=None):
        self.name = name

    def start(self):
        raise Exception('`start` method should be overridden by child class.')
    
    def stop(self):
        raise Exception('`stop` method should be overridden by child class.')


class FileSource(DataSource):
    """
    Class for ingesting from files as they are detected by watchdog.
    """
    
    def __init__(self, directory=None):
        self.directory = directory
        super(FileSource, self).__init__()
    
    def run_watchdog(self):
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
    Class for ingesting CSV files -- serializes them by row, to be transformed
    into the intermediate representation downstream.
    """

    def __init__(self, dialect=None):
        self.dialect = dialect
        super(JSONFileSource, self).__init__()

    def read(self, path):
        """
        Read the incoming file and load it as JSON object.
        """

        with open(path, 'r') as incoming_file:
            incoming = json.load(incoming_file)
        return incoming
