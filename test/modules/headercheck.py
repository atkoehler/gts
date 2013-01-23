## 
# @author Adam Koehler
# @date January 22, 2013
#
# @brief this module provides the means to check the header of source file
#        the header is standardized using doxygen tags
#



## 
# @brief the header check module is composed of several parts that verify
#        the assignment header exists and is properly filled in
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object that is an object with properties to fill out
# @param source the source object contain name, location and content splits
#
# @return 0 if test completed successfully, otherwise -1
def test(locations, test_obj, source):
    OK = 0
    ERROR = -1

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

