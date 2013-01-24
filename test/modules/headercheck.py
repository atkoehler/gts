## 
# @author Adam Koehler
# @date January 22, 2013
#
# @brief this module provides the means to check the header of source file
#        the header is standardized using doxygen tags
#

PENALTY = 25
AUTHOR_TAG = "@author"
PLAGIARISM_TAG = ""

## 
# @brief the header check module is composed of several parts that verify
#        the assignment header exists and is properly filled in
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object that is an object with properties to fill out
# @param source the source object contain name, location and content splits
#
# @return 0 if test completed, otherwise -1
#
# @precondition the source contents have been split into source object fields
#
def test(locations, test_obj, source, submission):
    OK = 0
    ERROR = -1

        
    # failed to located header on split of source
    if len(source.header) == 0:
        test_obj.score = -1 * PENALTY
        test_obj.message = "Header not found: Either it does not exist or could not find beginning of assignment header."
        return OK
    
    # loop over parts of header and run specific sub tests
    from galah.interact import *
    for line in source.header:
        if line.find(AUTHOR_TAG):
            sub_test = GalahTest()
            sub_test.name = "Compare author and submit email"
            
            if not verify_email(sub_test, submission["user"], line):
                if test_obj.message == "":
                    test_obj.message = "Could not verify email with submission email"
                else:
                    test_obj.message = "\nCould not verify email with submission email"
            
            test_obj.parts.append(sub_test)
    
    
    # go over test parts, if one failed apply penalty
    for test in test_obj.parts:
        if test.score != test.max_score:
            test_obj.score = -1 * PENALTY
            break
        
    
    
    import re
    p = "(?<=@author)\\s*(\\w+)\\s*(\\w+)\\s*\\[(\\w+)\\@(\\w+).(\\w+)\\]"
    pattern = re.compile(p)
    search_space = "\\\\\\ @author      Adam    Koehler     [akoeh001@ucr.edu]" 
    m = re.search(pattern, search_space)
    m.group(0)
    email_address = m.group(3) + "@" + m.group(4) + "." + m.group(5) 

    # TODO: how to match partial such as below which leaves email off:
    # search_space = "\\\\\\ @author      Adam    Koehler    " 
    return OK


def verify_email(test, email, line):
    
    return True
