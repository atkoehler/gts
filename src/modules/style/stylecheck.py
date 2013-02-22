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

from galah.interact import *
from system.utils import *

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
    
    messages = []
    
    # global variables existence sub test
    import modules.style.globalvars as globalvars
    name = "Global variable existence check"
    sub_test = GalahTestPart()
    sub_test.name = name
    globals = globalvars.globals_exist(sub_test, locations[1], source)
    m = ""
    header = markup_create_bold("Global Variables") + ": "
    if globals is None:
        m = "The check for global variables could not be executed due to compilation error. Passing for now."
        messages.append(header + m)
    else:
        for i in globals:
            m += i + ", "
        if len(globals) > 0:
            m = m.strip().rstrip(',')
            if len(globals) == 1:
                m = "Global variable found: " + m
            elif len(globals) > 1:
                m = "Global variables found: " + m
            messages.append(header + m)
    test_obj.parts.append(sub_test)
    
    
    # comments exist sub test
    import modules.style.comments as comments
    name = "Comments exist in source code"
    sub_test = GalahTestPart()
    sub_test.name = name
    ret = comments.comments_exist(sub_test, source)    
    if not ret:
        m = "Did not find any comments in source code."
        header = markup_create_bold("Comments") + ": "
        messages.append(header + m)
    test_obj.parts.append(sub_test)
    
    
    # check for long lines in code
    import modules.style.linelength as linelength
    name = "No lines over " + str(LONG_LINE_COUNT) + " characters"
    sub_test = GalahTestPart()
    sub_test.name = name
    nums = linelength.long_check(sub_test, source)
    m = ""
    header = markup_create_bold("Long Lines") + ": "
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Exceeded " +str(LONG_LINE_COUNT)+ " characters on line: " + m
        elif len(nums) > 1:
            m = "Exceeded " +str(LONG_LINE_COUNT)+ " characters on lines: " + m
        messages.append(header + m)
    test_obj.parts.append(sub_test)
    
    
    # check for tab characters useage as indentation of code
    import modules.style.tabs as tabs
    name = "No tabs used in source"
    sub_test = GalahTestPart()
    sub_test.name = name
    nums = tabs.find_tabs(sub_test, source)
    m = ""
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        header = markup_create_bold("Tabs in Source") + ": "
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Discovered at least one tab character on line: " + m
        elif len(nums) > 1:
            m = "Discovered at least one tab character on lines: " + m
        messages.append(header + m)
    test_obj.parts.append(sub_test)
    
        
    # improper boolean conditionals exist sub test
    import modules.style.conditionals as conditionals
    name = "No improper conditional statements"
    sub_test = GalahTestPart()
    sub_test.name = name
    nums = conditionals.improper_bool(sub_test, source)
    m = ""
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        header = markup_create_bold("Improper Conditionals") + ": "
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            s = "Found improper boolean conditional expression. Such as one "
            s += "which compares to true: "
            s += markup_create_inlinecode("(var_name == true)") + ", instead " 
            s += " of simply using the boolean value: " 
            s += markup_create_inlinecode("(var_name)") + ". At least one "
            s += "improper conditional statement discovered on line: "
            m = s + m
        else: 
            s = "Found improper boolean conditional expression. Such as one "
            s += "which compares to true: "
            s += markup_create_inlinecode("(var_name == true)") + ", instead " 
            s += " of simply using the boolean value: " 
            s += markup_create_inlinecode("(var_name)") + ". At least one "
            s += "improper conditional statement discovered on lines: "
            m = s + m
        messages.append(header + m)
    test_obj.parts.append(sub_test)
    
    
    # One curly brace per line sub test
    from modules.style import indentation as indentation
    name = "Source has a single curly brace per line"
    sub_test = GalahTestPart()
    sub_test.name = name
    
    m = ""
    nums = indentation.one_curly_per_line(source)
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        header = markup_create_bold("Curly Brace Issues") + ": "
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Found multiple curly braces on line: " + m
        elif len(nums) > 1:
            m = "Found multiple curly braces on lines: " + m
        messages.append(header + m)
    sub_test.score = -1 * DEDUCTION_PER_GAFFE * len(nums)
    test_obj.parts.append(sub_test)
    
    
    # Proper spacing within indentation blocks sub test
    from modules.style import indentation as indentation
    name = "Indentation blocks spaced properly"
    sub_test = GalahTestPart()
    sub_test.name = name
    
    m = ""
    (ret, nums) = indentation.correct_indent(source)
    
    header = markup_create_bold("Improper Indentation") + ": "
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Incorrect indentation using " + str(source.indent_size) + " spaces per indent level on line: " + m
        elif len(nums) > 1:
            m = "Incorrect indentation using " + str(source.indent_size) + " spaces per indent level on lines: " + m
        messages.append(header + m)
    elif not ret:
        m = "Could not execute indentation check due to prior style errors."
        messages.append(header + m)
     
    # impose maximum penalty if test completely failed 
    if ret:
        sub_test.score = -1 * DEDUCTION_PER_GAFFE * len(nums)
    else:
        sub_test.score = -1 * STYLE_PENALTY_MAX
    test_obj.parts.append(sub_test)   
    
    
     
    # go over test parts to calculate the style penalty
    for test in test_obj.parts:
        test_obj.score += test.score
    
    m = ""
    # cap style deduction
    if abs(test_obj.score) > STYLE_PENALTY_MAX:
        m = "Penalty of " + str(abs(test_obj.score)) + " exceeds maximum " 
        m += "penalty of " + str(STYLE_PENALTY_MAX) + ", assessing maximum.\n\n"
        test_obj.score = -1 * STYLE_PENALTY_MAX
   
    # add any messages to test object
    if len(messages) > 0:
        test_obj.message = m + markup_create_unlist(insert_blanks(messages))
    else:
        test_obj.message = m 
   
    return OK


