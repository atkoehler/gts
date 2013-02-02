## 
# @file modules/stylecheck.py
# @author Adam Koehler
# @date January 24, 2013
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
    name = "Global variable existence check"
    sub_test = GalahTestPart()
    sub_test.name = name
    globals = globals_exist(sub_test, locations[1], source)
    m = ""
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
    name = "Program contains comments"
    sub_test = GalahTestPart()
    sub_test.name = name
    if len(source.comments) == 0:
        sub_test.score = -1 * DEDUCTION_PER_GAFFE
    test_obj.parts.append(sub_test)

    # check for long lines in code
    name = "Lines over " + str(LONG_LINE_COUNT) + " characters"
    sub_test = GalahTestPart()
    sub_test.name = name
    nums = long_lines_check(sub_test, source)
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
    
    # comments exist sub test
    name = "Check indentation on scopes"
    sub_test = GalahTestPart()
    sub_test.name = name
    (space_val, nums) = scope_indent_check(sub_test, source)
    m = ""
    for i in nums:
        m += str(i) + ", "
    if len(nums) > 0:
        m = m.strip().rstrip(',')
        if len(nums) == 1:
            m = "Incorrect scope indentation using " + str(space_val) + " spaces, scope begins on line: " + m
        elif len(nums) > 1:
            m = "Incorrect scope indentation using " + str(space_val) + " spaces, scopes begin on lines: " + m
        if test_obj.message == "":
            test_obj.message += m
        else:
            test_obj.message += "\n\n" + m
    test_obj.parts.append(sub_test)
   
    
    # go over test parts to calculate the style penalty
    for test in test_obj.parts:
        test_obj.score += test.score
    
    # cap style deduction
    if abs(test_obj.score) > STYLE_PENALTY_MAX:
        test_obj.score = -1 * STYLE_PENALTY_MAX
    
    return OK




## 
# @brief sub test to check whether global variables exist in the program
# 
# @param test the test part object to update with score
# @param harness_dir directory containing the test harness
# @param source the source object containing name, location and content splits
#
# @return a list containing all the names of global variables
#
def globals_exist(test, harness_dir, source):
    import os
    import shutil
    from system.functions import which
    
    # make sure the commands exist
    nm = which("nm")
    grep = which("grep")
    cut = which("cut")
    gpp = which(COMPILER)
    if nm == None or grep == None or cut == None or gpp == None:
        return
    
    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, WORKING_DIR_NAME)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    vars = [] 
    FNULL = open(os.devnull, 'w')
    try:
        import subprocess

        # compile the object file
        object_file = source.name[0:source.name.find(".")] + ".o"
        obj_loc = os.path.join(working_dir, object_file)
        subprocess.check_call([gpp, "-o", obj_loc, source.file_loc], 
                              stdout=FNULL, stderr=subprocess.STDOUT)
        
        # get object symbols
        symf = os.path.join(working_dir, "symbols.txt")
        with open(symf, 'w') as sym_file:
            subprocess.check_call([nm, obj_loc], stdout=sym_file, stderr=FNULL)
        
        # grep for proper symbols relating to global variables
        grepf = os.path.join(working_dir, "grep.txt")
        with open(symf, 'r') as sym_file:
            with open(grepf, 'w') as grep_file:
                subprocess.check_call([grep, "[0-9A-Fa-f]* [BCDGRS]"], 
                               stdin=sym_file, stdout=grep_file, stderr=FNULL)
        
        # cut off the variable names
        cutf = os.path.join(working_dir, "cut.txt")
        with open(grepf, 'r') as grep_file:
            with open(cutf, 'w') as cut_file:
                del_opt = "-d ' '"
                subprocess.check_call([cut, "-d", " ", "-f" "3"],
                               stdout=cut_file, stdin=grep_file, stderr=FNULL)
        
        # split the global variables into a list, exclude vars starting with _
        contents = open(cutf).read().rstrip().rstrip('\n').split("\n")
        for (i, val) in enumerate(contents):
            if val[0] != '_':
                vars.append(val)
    
    except subprocess.CalledProcessError:
    # TODO: determine what to do in except clause, outputing error cause issue?
        FNULL.close()
        shutil.rmtree(working_dir)
        test.score = -1 * DEDUCTION_PER_GAFFE * len(vars)
        return vars
    
    # remove working directory
    shutil.rmtree(working_dir)
    FNULL.close() 
    test.score = -1 * DEDUCTION_PER_GAFFE * len(vars)
    return vars


## 
# @brief sub test to check whether long lines exist in the program
# 
# @param test the test part object to update with score
# @param source the source object containing name, location and content splits
#
def long_lines_check(test, source):
    line_nums = []
    
    # TODO implement try block
    file = open(source.file_loc)
    contents = file.read()
    file.close()
    
    lines = contents.split("\n")
    for (i, line) in enumerate(lines):
        if len(line) > LONG_LINE_COUNT:
            line_nums.append(i)
    
    test.score = -1 * DEDUCTION_PER_GAFFE * len(line_nums)
    return line_nums


## 
# @brief sub test to check whether scopes are indented
# 
# @param test the test part object to update with score
# @param source the source object containing name, location and content splits
#
def scope_indent_check(test, source):
    line_nums = []
    curlies = []
    scopes = {}
    
    # global scope
    scopes[0] = []

    # TODO implement try block
    file = open(source.file_loc)
    contents = file.read()
    file.close()
    
    # attempt to determine the spacing used for indenting new scopes
    spacing = determine_scope_space_count(source)
    if spacing == 0:
        spacing = DEFAULT_SPACING
    
    lines = contents.split("\n")
    for (i, line) in enumerate(lines):
        # discover open curly?
        if line.find("{") != -1:
            # column number of first char is either { or something before {
            if (line.lstrip().find("{") == 0):
                first_index = line.find("{")
            else:
                first_index = line.find(line.lstrip()[0])
            
            # discovered open curly is on col num less than last discovered
            if len(curlies) > 0:
                if first_index <= curlies[-1][1]:
                    line_nums.append(i+1)
            
            # add discovered open curly to stack (line # in file, column #)
            curlies.append((i+1, first_index))
            
            # create a list in scopes dictionary with key of this line number
            scopes[i+1] = []
        
        # discover closing curly?
        if line.find("}") != -1:
            # column number of first char is either } or something before }
            if line.find("{") != -1:
                # if open curly found on same line determine first char
                # as did prior, first char is either { or something before it
                if (line.lstrip().find("{") == 0):
                    first_index = line.find("{")
                else:
                    first_index = line.find(line.lstrip()[0])           
                
                # if both curlies on one line
                # treat as if closing curly is only character on line
                alone = True
            else:
                # no open on same line, determine if closing curly is alone
                alone = (len(line.strip()) == 1)
                first_index = line.find("}")
            
            # check col of last item in stack against closing column
            if len(curlies) > 0:
                if first_index != curlies[-1][1]:
                    line_nums.append(curlies[-1][0])
                elif (first_index == curlies[-1][1]) and (not alone):
                    line_nums.append(curlies[-1][0])
            
            # check to ensure spacing of lines in discovered scope is correct 
            for i in scopes[curlies[-1][0]]:
                if i != spacing:
                    line_nums.append(curlies[-1][0])
                    break
            
            # pop most recent left curly brace off stack
            if len(curlies) > 0: 
                curlies.pop()
        
        # determine scope to use as key, and amount of indent based on scope
        if len(curlies) > 0: 
            if line.find("{") != -1 and line.find("}") == -1:
                # opened a new scope then line with open is of previous scope
                if len(curlies) > 1:
                    key = curlies[-2][0]
                    amount = indent_amount(lines, i, curlies[-2][1])
                else:
                    # only one curly, previous scope is global scope
                    key = 0
                    amount = indent_amount(lines, i, 0)
            else:
                # didn't open new scope on this line, use latest scope
                key = curlies[-1][0]
                amount = indent_amount(lines, i, curlies[-1][1])
        else:
            # use global scope if curly stack is empty
            key = 0
            amount = indent_amount(lines, i, 0)
           
        if len(line.strip()) != 0:
            scopes[key].append(amount)
            if key == 37: #TODO: line 56, curly brace not in indentation list?
                print line
  
    print scopes 
    # elimate duplicates and sort
    line_nums = list(set(line_nums))
    line_nums.sort()
    
    # apply per gaffe deduction 
    test.score = -1 * DEDUCTION_PER_GAFFE * len(line_nums)
    
    # return the list of line numbers
    return (spacing, line_nums)


## 
# @brief helper function that attempts to determine the indentation spacing
#        used within source code (such as 2 spaces for items in a new scope)
# 
# @param source the source object containing name, location and content splits
#
def determine_scope_space_count(source):
    spacer = 0
    mismatched = []
    line_nums = []

    # TODO implement try block
    file = open(source.file_loc)
    contents = file.read()
    file.close()
    
    lines = contents.split("\n")
    for (i, line) in enumerate(lines):
        if line.find("{") != -1:
            if (line.lstrip().find("{") == 0):
                first_index = line.find("{")
            else:
                first_index = line.find(line.lstrip()[0])
           
            if line.find("}") == -1: 
                non_blank = next_non_blank(lines, i+1)
                spacer = indent_amount(lines, non_blank, first_index)
                if spacer > 0:
                    break   
                else:
                     spacer = 0
        
    
    return spacer

## 
# @brief helper function to determine the indent spacing of provided line
# 
# @param lines a list of lines
# @param i the line to start looking at
# @param prev_indent_amt the amount the previous line was indented
#
def indent_amount(lines, i, prev_indent_amt):
    if i < len(lines) and len(lines[i].strip()) > 0:
        indent_amt = lines[i].find(lines[i].strip()[0])
    else:
        indent_amt = 0
   
    return indent_amt - prev_indent_amt

## 
# @brief helper function to determine index of next non-blank line
# 
# @param lines a list of lines
# @param i the line to start looking at
#
def next_non_blank(lines, i):
    while i < len(lines) and len(lines[i].strip()) == 0:
        i = i + 1
    return i

