"""
A place for little helper functions.
"""

import threading
import os
import sys
import yaml
import Queue
import time
import hashlib
import importlib
from global_configs import *


def load_snippet(module_name, function_name):
    if SNIPPETS_DIR not in sys.path:
        sys.path.append(SNIPPETS_DIR)
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return function


def hexhash(thing):
    return hashlib.md5(thing.__repr__()).hexdigest()


class Threadable(object):
    """
    Mixin class for things that run in their own thread.
    """

    def __init__(self, check_interval=1):
        self.thread = None
        self.check_interval = check_interval

    def thread_loop(self, *args, **kwargs):
        while 1:
            while self.input_queue.empty():
                time.sleep(self.check_interval)
            thing = self.input_queue.get()
            thing_result = self.process_thing(thing, *args, **kwargs)
            if isinstance(self, Queueable):
                self.output_queue.put(thing_result)

    def process_thing(self, *args, **kwargs):
        raise Exception(
            '`process_thing` method must be overridden in any '
            'child inheriting from `Threadable`.')

    def start(self, *args, **kwargs):
        self.thread = threading.Thread(
            target=self.thread_loop,
            args=args,
            kwargs=kwargs)
        self.thread.start()
        return self.thread


class Queueable(object):
    """
    Mixin class for things that have input and output queues.
    """

    def __init__(self):
        self.input_queue = Queue.Queue()
        self.output_queue = Queue.Queue()

    def attach(self, other):
        self.output_queue = other.input_queue

    def __gt__(self, other):
        self.attach(other)
        return other

    def __lt__(self, other):
        other.attach(self)


class QueueableThreadable(Queueable, Threadable):
    """
    Convenience class for inheriting from both classes and calling
    their constructors in one place.
    """

    def __init__(self, *args, **kwargs):
        Queueable.__init__(self, *args, **kwargs)
        Threadable.__init__(self, *args, **kwargs)


class MissingQueue(object):
    """
    This is a dummy class whose only purpose is to indicate that a queue
    hasn't been defined for a `DataSource` object; the exception would
    be raised if we forgot to attach the `DataSource` to an `Alligator`.
    """

    def put(self, *args, **kwargs):
        raise Exception(
            'Trying to put something onto a queue '
            'that has not been defined.')

    def get(self, *args, **kwargs):
        raise Exception(
            'Trying to get an item off a queue that has not '
            'been defined.')


def get_yaml_files_from_directory(target_directory):
    """
    This loads all the yaml configuration files from `target_directory`
    and returns a dictionary that combines them.
    """

    configuration = {}
    for file_name in os.listdir(target_directory):
        if not file_name.endswith('.yaml'):
            continue
        file_name = '/'.join([target_directory, file_name])
        with open(file_name, 'r') as config_file:
            configuration.update(yaml.load(config_file))
    return configuration


def get_key_path(some_dict, list_of_keys, in_place=True):
    if not isinstance(list_of_keys, list):
        list_of_keys = [list_of_keys]
    tmp_dict = some_dict
    for key in list_of_keys:
        tmp_dict = tmp_dict[key]
    return copy.deepcopy(tmp_dict) if not in_place else tmp_dict 


def run_in_thread(target, *args, **kwargs):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    thread.start()
    return thread
