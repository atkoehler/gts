## 
# @file modules/style/stylecheck.py
# @author Adam Koehler
# @date February 4, 2013
#
# @brief Provides a check for whether global variables exist in program
#

# TODO: figure out the configuration system to get this item from their
STYLE_PENALTY_MAX = 10
DEDUCTION_PER_GAFFE = 5
LONG_LINE_COUNT = 80
WORKING_DIR_NAME = "working"
COMPILER = "g++"
DEFAULT_SPACING = 3

from galah.interact import *

## 
# @brief test function checks various style parts for the program
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param source the source object containing name, location and content splits
#
# @return 0 if test completed successfully, otherwise -1
#
# @precondition the source contents have been split into source object fields
#
def test(locations, test_obj, source):
    OK = 0
    ERROR = -1
    
    # global variables existence sub test
    import modules.style.globalvars as globalvars
    name = "Global variable existence check"
    sub_test = GalahTestPart()
    sub_test.name = name
    globals = globalvars.globals_exist(sub_test, locations[1], source)
    m = ""
    
    if globals is None:
        m = "Global variables check not executed. Either the program does not compile or a required system program could not be found."
        sub_test.score = -1 * DEDUCTION_PER_GAFFE
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    else:
        for i in globals:
            m += i + ", "
        if len(globals) > 0:
            m = m.strip().rstrip(',')
            if len(globals) == 1:
                m = "Global variable found: " + m
            elif len(globals) > 1:
                m = "Global variables found: " + m
            if test_obj.message == "":
                test_obj.message += m
            else:
                test_obj.message += "\n\n" + m
    test_obj.parts.append(sub_test)

    # comments exist sub test
    import modules.style.comments as comments
    name = "Program contains comments"
    sub_test = GalahTestPart()
    sub_test.name = name
    ret = comments.comments_exist(sub_test, source)
    test_obj.parts.append(sub_test)

    # check for long lines in code
    import modules.style.linelength as linelength
    name = "Lines over " + str(LONG_LINE_COUNT) + " characters"
    sub_test = GalahTestPart()
    sub_test.name = name
    nums = linelength.long_check(sub_test, source)
    m = ""
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Exceeded " +str(LONG_LINE_COUNT)+ " characters on line: " + m
        elif len(nums) > 1:
            m = "Exceeded " +str(LONG_LINE_COUNT)+ " characters on lines: " + m
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    test_obj.parts.append(sub_test)
    
    # check for tab characters in code
    import modules.style.tabs as tabs
    name = "Tabs used in source"
    sub_test = GalahTestPart()
    sub_test.name = name
    nums = tabs.find_tabs(sub_test, source)
    m = ""
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Discovered at least one tab character on line: " + m
        elif len(nums) > 1:
            m = "Discovered at least one tab character on lines: " + m
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    test_obj.parts.append(sub_test)
        
    # improper boolean conditionals exist sub test
    import modules.style.conditionals as conditionals
    name = "Improper conditional statements"
    sub_test = GalahTestPart()
    sub_test.name = name
    nums = conditionals.improper_bool(sub_test, source)
    m = ""
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Found improper boolean conditional expression. Such as one that compares to true--(var_name == true)--instead of simply using the boolean value--(var_name). Improper conditionals discovered on line: " + m
        elif len(nums) > 1:
            m = "Found improper boolean conditional expressions. Such as one that compares to true--(var_name == true)--instead of simply using the boolean value--(var_name). Improper conditionals discovered on lines: " + m
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    test_obj.parts.append(sub_test)

    
    
    # TODO: Clean up.  Indentation object not really needed.  
    # Can be used internally by individual tests if required. 
    # Initialize Indentation Object
    import modules.style.indentation as indentation
    ind = indentation.Indent()

    # One curly brace per line sub test
    name = "Single curly brace per line"
    sub_test = GalahTestPart()
    sub_test.name = name
    
    m = ""
    nums = ind.one_per_level(source.file_loc)
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Found multiple curly braces on line: " + m
        elif len(nums) > 1:
            m = "Found multiple curly braces on lines: " + m
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    sub_test.score = -1 * DEDUCTION_PER_GAFFE * len(nums)
    test_obj.parts.append(sub_test)
    
    # Proper indentation sub test
    name = "Proper indentation and spacing"
    sub_test = GalahTestPart()
    sub_test.name = name
    
    m = ""
    ret = ind.init_from_file(source.file_loc)
    (ret, nums) = ind.correct_spacing()
    
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Incorrect indentation using " + str(ind.spacing) + " spaces, block begins on line: " + m
        elif len(nums) > 1:
            m = "Incorrect indentation using " + str(ind.spacing) + " spaces, blocks begin on lines: " + m
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    elif not ret:
        m = "Could not execute indentation checking due to prior style errors."
        if test_obj.message == "":
            test_obj.message += m
        elif m != "":
            test_obj.message += "\n\n" + m
    
     
    # impose maximum penalty if test completely failed 
    if ret:
        sub_test.score = -1 * DEDUCTION_PER_GAFFE * len(nums)
    else:
        sub_test.score = -1 * STYLE_PENALTY_MAX
    test_obj.parts.append(sub_test)   
     
    # go over test parts to calculate the style penalty
    for test in test_obj.parts:
        test_obj.score += test.score
    
    # cap style deduction
    if abs(test_obj.score) > STYLE_PENALTY_MAX:
        test_obj.score = -1 * STYLE_PENALTY_MAX

    if test_obj.score == 0:
        m = "Did not discover any style errors."
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    
    return OK


