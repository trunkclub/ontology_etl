"""
We will put all global, immutable variables here and do a `from blahblah import *`.
"""

import os


BASE_DIR = os.environ['BASE_DIR']
CONFIG_DIR = os.environ['CONFIG_DIR']
DATA_SOURCES_DIR = os.environ['DATA_SOURCES_DIR']
WATCHDOG_DIR = os.environ['WATCHDOG_DIR']
TRANSFORMS_DIR = os.environ['TRANSFORMS_DIR']
DEPENDENCIES_DIR = os.environ['DEPENDENCIES_DIR']
ENTITIES_DIR = os.environ['ENTITIES_DIR']
SNIPPETS_DIR = os.environ['SNIPPETS_DIR']
SRC_DIR = os.environ['SRC_DIR']

EXCLUDED_FROM_CONSTRUCTORS = ['source_type']
