## 
# @author Adam Koehler
# @date January 22, 2013
#
# @brief this module provides the means to check the file name
#        against a specified name in configuration file
#
#        this module updates the test dictionary provided with the score
#

# TODO: figure out the configuration system to get this item from their
PROPER_FILE_NAME = "main.cpp"
PENALTY = 25


## 
# @brief the filename module checks file name against a required name
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object that is a dictionary defining the test
#
# @return 0 if test completed successfully, otherwise -1
def test(locations, test_obj):
    OK = 0

    import os    
    main_path = os.path.join(locations[0], "main.cpp")
    print main_path
    if not os.path.isfile(main_path):
        test_obj.score = -1 * PENALTY
        test_obj.message = "File name not " + PROPER_FILE_NAME

    return OK

