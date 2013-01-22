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


# generic return values
OK = 0
ERROR = -1

# create result object 
result = GalahResult()


# determine if source file exists
name = "Source File Exist"
if name in config.actions:
    # create test object
    t = GalahTest()
    t.name = name
     
    # run test
    import modules.findsource as findsource
    src = findsource.test((config.testables_dir, config.harness_dir), t, True)
    source_exist = (src != "")
    
    # add test to result
    result.add_test(t)
    del(t)
    

# nothing can be done if no source file was discovered
if source_exist: 
    # run test if it is within the configuration actions
    name = "File Name Check"
    if name in config.actions:
        # create test object
        t = GalahTest()
        t.name = name
         
        # run test
        import modules.filename as filename
        completed = filename.test((config.testables_dir, config.harness_dir), t)
        
        # add test to result
        if completed == OK:
            result.add_test(t)
        
        del(t)


# calculate the scores associated with result based on tests
result.calculate_scores()


# min score of 0
if result.score < 0:
    result.score = 0


# output result as JSON
result.send()
print ""
print ""
print "Final score: ", result.score, " out of ", result.max_score
