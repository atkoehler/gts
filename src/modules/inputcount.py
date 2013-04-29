## 
# @file modules/inputcount.py
# @author Adam Koehler
# @date April 12, 2013
#
# @brief Provides the means to assess a score/penalty based 
#        number of inputs versus in source versus expected number of inputs.
#

from system.utils import *

## 
# @brief test function checks the submission date against the due date
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
# @param source the source object containing name, location and content splits
# @param score currently tabulated score for the result
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, vars, source, score):
    OK = 0
    ERROR = -1
    counted = 0

    contents = source.code.split("\n")
    open_cin = False
    line_nums = []
    for (i, line) in enumerate(contents):
        end = 0       
        if line.lower().find("cin", end) != -1 or open_cin:
            while len(line) > 0 and end < len(line):
                # verify if cin statement was left open
                if not open_cin:
                    start = line.lower().find("cin", end)
                else:
                    start = 0
                
                # ending semicolon has to be after opening point
                end = line.lower().find(";", start)
                
                # determine whether cin statement is terminated
                if end == -1:
                    open_cin = True
                    end = len(line)
                else:
                    open_cin = False
                
                # count the number of inputs in substring
                before = counted
                counted += line.count(">>", start, end)
                
                if before != counted:
                    line_nums.append(i+1)
                
                # move along 
                end = end + 1
                   
    # make list unique and sorted
    line_nums = list(set(line_nums))
    line_nums.sort()
    
    # construct message to utilize on failure
    lines_string = ""
    for i in line_nums:
        if i == line_nums[-1] and len(line_nums) > 1:
            lines_string += " and " + str(i)
        elif i == line_nums[0]:
            lines_string += str(i)
        else:
            lines_string += ", " + str(i)
    
    if counted == 1:
        c_word = "input"
    else:
        c_word = "inputs"
    if vars["expected_inputs"] == 1:
        e_word = "input"
    else:
        e_word = "inputs"
    if len(line_nums) == 1:
        l_word = "line"
    else:
        l_word = "lines"
    
    m = "Expecting " + str(vars["expected_inputs"]) + " " + e_word
    m += ". "
    m += "Discovered " + str(counted) + " " + c_word + " on " + l_word
    m += " " + lines_string + "."

    # assess a score
    if vars["type"].lower() == "penalty":
        if counted != vars["expected_inputs"]:            
            test_obj.score = -1 * score
            test_obj.message = markup_create_indent(m, 1)
        else:
            test_obj.score = 0
    else:
        if counted != vars["expected_inputs"]:
            test_obj.score = 0
            test_obj.message = markup_create_indent(m, 1)
        else:
            test.obj.score = vars["max_score"]

    return OK

