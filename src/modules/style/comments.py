## 
# @file modules/style/comments.py
# @author Adam Koehler
# @date February 4, 2013
#
# @brief Provides a check for whether comments exist in source file
#

# TODO: figure out the configuration system to get this item from their
DEDUCTION_PER_GAFFE = 5

## 
# @brief sub test to check whether comments exist in source file which are not
#        part of the assignment header
#
# @param test the test part containing properties to fill out
# @param source the source object containing name, location and content splits
#
# @return true if the source contains comments, otherwise false
#
def comments_exist(test, source):
    OK = 0
    ERROR = 1
    
    if len(source.comments) == 0:
        test.score = -1 * DEDUCTION_PER_GAFFE
        return False
     
    return True

