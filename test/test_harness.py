##
# @file test_harness.py
# @brief the launching script for any test harness
#
#   This script should be updated to launch whichever assignment specific
#   test harness has been created. This is simply a defined launching point
#   for the test suite. As such, this should be included with every 
#   assignment's test harness.
#
# @author Adam Koehler
# @date November 8, 2012
# @udpated January 13, 2013
#

import json
import sys
from galah.interact import *

# create configuration object from Galah provided JSON file
config = GalahConfig()
config.init_json()


# set up the code path - single C++ file 
import os
source_file = True
main_path = os.path.join(config.testables_dir, "main.cpp")
if os.path.isfile(main_path):
    code_path = main_path
else:
    file_name = [item for item in os.listdir(config.testables_dir) if item.endswith('.cpp')]
    if len(file_name) > 0:       
        code_path = os.path.join(config.testables_dir, file_name[0])
    else:
        source_file = False

# create result object 
result = GalahResult()

# nothing can be done if C++ file was discovered
if source_file: 
    # run test if it is within the configuration actions
    name = "File Name Check"
    if name in config.actions:
        # create test object
        t = GalahTest()
        t.name = name
         
        # run test
        import modules.filename as filename
        filename.test((config.testables_dir, config.harness_dir), t)
        
        # add test to result
        result.add_test(t)


# update score of result based on tests
result.update_score()

# min score of 0
if result.score < 0:
    result.score = 0


# output result as JSON
result.send()
print ""
print ""
print "Final score: ", result.score, " out of ", result.max_score
