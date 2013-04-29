##
# @file system/config.py
# @brief configuration for this assessment
#
#   The configuration class specific to an assessment. Utilizes JSON config 
#   file to load various values.
#

import json
import sys
class GTSConfig:
    def __init__(self, environment=None, tests=None, alterations=None, 
                 units=None):
        if environment is None:
            environment = []
        if alterations is None:
            alterations = []
        if tests is None:
            tests = []
        if units is None:
            units = []
        
        self.environment = environment
        self.tests = tests
        self.alterations = alterations
        self.units = units
    
    @staticmethod
    def from_file(file_object = sys.stdin):
        values = json.load(file_object)
        
        return GTSConfig(
            environment = values["environment"],
            alterations = values["alterations"],
            tests = values["tests"],
            units = values["units"]
        )


