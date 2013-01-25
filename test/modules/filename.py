## 
# @file modules/filename.py
# @author Adam Koehler
# @date January 22, 2013
#
# @brief Provides the means to check the file name. It uses a proper file name
#        for comparison and updates the provided test object with a scoring 
#        penalty if one should be assessed.
#

# TODO: figure out the configuration system to get this item from their
PROPER_FILE_NAME = "main.cpp"
PENALTY = 25


## 
# @brief test function checks file name against a required name
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj):
    OK = 0

    import os    
    main_path = os.path.join(locations[0], "main.cpp")
    if not os.path.isfile(main_path):
        test_obj.score = -1 * PENALTY
        test_obj.message = "File name not " + PROPER_FILE_NAME

    return OK

