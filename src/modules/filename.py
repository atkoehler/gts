## 
# @file modules/filename.py
# @author Adam Koehler
# @date January 22, 2013
#
# @brief Provides the means to check the file name. It uses a proper file name
#        for comparison and updates the provided test object with a scoring 
#        penalty if one should be assessed.
#


## 
# @brief test function checks file name against a required name
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, vars):
    OK = 0

    import os    
    main_path = os.path.join(locations[0], vars["proper_name"])
    if not os.path.isfile(main_path):
        test_obj.score = -1 * vars["penalty"]
        test_obj.message = "The submitted file name is not "+vars["proper_name"] 
    
    return OK

