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
from system.testfile import *

# create configuration object from Galah provided JSON file
config = GalahConfig()
config.init_json()


# generic return values
OK = 0
ERROR = -1

##
# create Galah result object 
#
result = GalahResult()


##
# create source file object and initialize values
# this test is required as set up to all other tests and thus cannot be
# removed from within the configurable actions list
#
source = SourceFile()

# determine if source file exists
name = "Source File Exist"

# create test object
t = GalahTest()
t.name = name
 
# run test
import system.findsource as findsource
source_exist = findsource.test((config.testables_dir, config.harness_dir), t, source, True)

# split the file into code, header and comments
if source_exist:
    source.split_file()

# add test to result so feedback exists stating which file was tested if any
result.add_test(t)
del(t)
    

# nothing can be done if no source file was discovered
if source_exist: 
    ##
    # run test if it is within the configuration actions
    #
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
    
    name = "File Header Check"
    if name in config.actions:
        # create test object
        t = GalahTest()
        t.name = name
         
        # run test
        import modules.headercheck as headercheck
        completed = headercheck.test((config.testables_dir, config.harness_dir), t, source, config.submission)
        
        # add test to result
        if completed == OK:
            result.add_test(t)
        del(t)

    name = "Coding Style Check"
    if name in config.actions:
        # create test object
        t = GalahTest()
        t.name = name
         
        # run test
        import modules.stylecheck as stylecheck
        completed = stylecheck.test((config.testables_dir, config.harness_dir), t, source)
        
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
