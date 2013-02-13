## 
# @file modules/unittest.py
# @author Adam Koehler
# @date February 8, 2013
#
# @brief Provides rudimentary means to unit test
#

##
# @brief a class container for a unit test
# @requires requires the altersource module to replace source code
#
class UnitTest:
    def __init__(self, include_stmts=None, test_file=None, 
                             unit_harness=None, merged_file=None):
        self.include_stmts = include_stmts
        self.test_file = test_file
        self.unit_harness = unit_harness
        self.merged_file = merged_file
    
    def create_unit(self, inc_stmts, unit_harness, merge_loc, source, harness):
        self.include_stmts = inc_stmts
        self.test_file = source.file_loc
        self.unit_harness = unit_harness
       
        # grab contents of files 
        includes = open(inc_stmts).read().split('\n')
        harness_contents = open(unit_harness).read().split('\n')

        # indent contents of test file prior to getting contents
        # TODO: re-enable once indent command exists on the system
        #from modules.indent import indent_file
        #ret_val = indent_file(source.file_loc, harness, "BSD", ["-cdw","-nut"])
        #if ret_val["success"]:
        #    stud_contents = ret_val["message"].split('\n')
        #else:
        #    return False
        stud_contents = open(source.file_loc).read().split('\n')
        
        # eliminate "int main" from test file
        # TODO: eliminate module to module dependency
        import modules.altersource as altersource
        altersource.replace_source(stud_contents, "int main", "int testfile_main")
        
        # output all the files to a merged file
        with open(merge_loc, 'w') as merge_file:
            for line in includes:
                merge_file.write(line+"\n")
            merge_file.write("\n")
            
            for line in stud_contents:
                merge_file.write(line+"\n")
            merge_file.write("\n")
            
            for line in harness_contents:
                merge_file.write(line+"\n")
            merge_file.write("\n")
        
        self.merged_file = merge_loc
        
        return True        


import os
import shutil
from modules.compilation import compile_single
from system.utils import *
from galah.interact import *
from modules.unittest import *

WORKING_DIR_NAME = "working"
EXE_NAME = "test_program"
UNIT_TEST_DIR = "unit_tests"
INCLUDE_LINES = "includes.txt"
TEST_FILE_NM = "testfile.cpp"
UNIT_DIR_NAME = "unit_tests"

## 
# @brief test function runs the unit test
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param source the source object containing name, location and content splits
# @param fn_name name of the function to run unit test for
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, source, fn_name):
    import re
    OK = 0
    ERROR = -1
    
    harness_dir = locations[1]
    files_to_remove = []

    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, WORKING_DIR_NAME)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    # set up path to executable rename
    exe_path = os.path.join(working_dir, EXE_NAME)
    files_to_remove.append(exe_path)

    # attempt compilation
    ret_val = compile_single(source.file_loc, exe_path, harness_dir)
    if not ret_val["success"]:
        test_obj.score = 0
        test_obj.message = "File did not compile, cannot execute tests."
        
        # clean up
        if made_working:
            shutil.rmtree(working_dir)
        elif len(files_to_remove) > 0:
            for f in files_to_remove:
                if os.path.isfile(f):
                    os.remove(f)
        
        return OK
    
    # create unit testing file
    unit = UnitTest()
   
    # TODO: make sure all the paths and files exist before accessing/using 
    # set up path to unit tests directory
    unit_dir = os.path.join(harness_dir, UNIT_DIR_NAME)
    
    # set up path to #include lines
    inc_stmt_path = os.path.join(unit_dir, INCLUDE_LINES)
    
    # set up path to harness C++ file
    unit_filename = fn_name + ".cpp"
    unit_harness = os.path.join(unit_dir, unit_filename)
    unit_harness_path = os.path.join(unit_dir, unit_harness)
    
    # set up path to testing file
    merged_path = os.path.join(working_dir, TEST_FILE_NM)
    files_to_remove.append(merged_path)
    
    # create the unit
    ret = unit.create_unit(inc_stmt_path, unit_harness_path, merged_path, 
                     source, harness_dir)
    
    # set up paths for unit test output
    unit_out = os.path.join(working_dir, "unit_test_output.txt")
    errf = os.path.join(working_dir, "test_program_err.txt")   
    outf = os.path.join(working_dir, "test_program_out.txt")   
    files_to_remove.append(unit_out)
    files_to_remove.append(errf)
    files_to_remove.append(outf)
        
    message = []
    suggestions = []
    compiler_messages = []
    output_messages = []
    # merge success
    if ret:
        # attempt compilation
        ret_val = compile_single(merged_path, exe_path, harness_dir)
        if not ret_val["success"]:
            test_obj.score = 0
            header = markup_create_header("Notice\n", 2)
            m = "The unit test did not compile."
            message.append(header + m)
            
            header = markup_create_header("Compile Errors\n", 4)
            m = markup_create_indent(ret_val["message"], 2)
            message.append(markup_create_indent(header + m, 1))
            
            header = markup_create_header("Suggestions\n", 2)
            s = "If you have not yet implmented the " + fn_name + " function, "
            s += " you may ignore the fact that this test did not compile."
            suggestions.append(s)
            s = "If you have started implementing your function " + fn_name
A
            s += " and are attempting to test it, make sure it has a proper "
            s += "definition. Be sure to check its:\n"
            l = ["return type", "function name", 
                 "parameter types", "number of parameters"] 
            l_m = markup_create_indent(markup_create_unlist(l), 2)
            s += l_m
            suggestions.append(s)
            message.append(header + markup_create_unlist(suggestions))
            
            # join all the messages and put in test object message
            test_obj.message = "\n".join(message)
            
            if made_working:
                shutil.rmtree(working_dir)
            elif len(files_to_remove) > 0:
                for f in files_to_remove:
                    if os.path.isfile(f):
                        os.remove(f)
            return OK
        
        
        # run the unit test 
        try:
            with open(outf, 'w') as out_file:
                with open(errf, 'w') as err_file:
                    check_call([exe_path, unit_out], stdout=out_file, stderr=err_file)
        except SystemError as e:
            # create a notice about the abort throw and put in message
            m = markup_create_header("Notice\n", 2)
            m += "The " + fn_name + " unit test was aborted during execution. "
            m += "If errors were output they will be displayed below and they "
            m += "are a good starting point to determine why your code "
            m += "crashed."
A
            message.append(m)
            
            # create a suggestion about abort and put in suggestions
            s = "The abort may have been caused by this function or any "
            s += "function that it calls. If the functions that are called "
            s += "are passing their respective tests then make sure " + fn_name
            s += " is not calling another function with a bad value as one of "
            s += "the parameters or not returning an improper value."
            suggestions.append(s)
            
            # if seg fault was detected
A
            # TODO: this access is ugly and should be cleaned up
            if e[0][0] == -11:
                cl = ["return value", "values of each parameter"]
                s = "A segmentation fault was detected when invoking your "
                s += "function. Make sure you check the following for "
                s += fn_name + " as well as any functions it invokes.\n"
                s += markup_create_indent(markup_create_unlist(cl), 1)
                suggestions.append(s)
        
        # put standard error in the message
        if len(open(errf).read()) > 0: 
            m = fn_name + " standard error\n"
            m = markup_create_indent(markup_create_header(m, 4), 1)
            lines = open(errf).read().rstrip("\n").split("\n")
            combine = []
            for fail_test in lines:
                splits = fail_test.split("\t")
                header = splits[0]
                results = splits[1:]
                rlist = markup_create_unlist(results)
                single_result = markup_create_header(header, 3)
                single_result += rlist
                single_result = markup_create_indent(single_result, 2)
                combine.append(single_result)  
            message.append(m + "\n".join(combine))
            for exception in combine:
                if exception.find("Out of Range") != -1:
                    if exception.find("basic_string::at") != -1:
                        s = "At least one exception was thrown by calling "
                        s += "the at() "
                        s += "member function of a string with a value that "
                        s += "is either negative or greater than or equal to "
                        s += "the size of the string. Check the value "
                        s += "passed with each "
                        s += "invocation of the function at() in " + fn_name
                        s += " as well as any functions " + fn_name + " calls."
                        at_exception_sug_exists = False
                        for current_suggestion in suggestions:
                            if current_suggestion == s:
                                at_exception_sug_exists = True
                                break
                        if not at_exception_sug_exists:
                            suggestions.append(s)
        
        # put standard output in the message
        if len(open(outf).read()) > 0: 
            m = fn_name + " standard output\n"
            m = markup_create_indent(markup_create_header(m, 4), 1)
            line = open(outf).read().rstrip("\n")
            split_on = "Calling "
            pattern = re.compile(split_on)
            per_call = pattern.split(line)
            combine = []
            for output in per_call:
                lines = output.rstrip("\n").split("\n")
                header = lines[0] + "\n"
                if len(lines) > 1:
                    act_output = "\n".join(lines[1:])
                
                    single_result = markup_create_header(header, 3)
                    single_result = markup_create_indent(single_result, 2)
                    single_result += markup_create_indent(act_output, 3)
                    combine.append(single_result)
            message.append(m + "\n".join(combine)) 
         
        # if the unit test had any output then add them to message 
        if os.path.isfile(unit_out):
            unit_out_contents = open(unit_out).read().rstrip('\n')
        else:
            unit_out_contents = ""       
        
        if len(unit_out_contents) > 0:
            m = fn_name + " unit test output\n"
            m = markup_create_header(m, 4)
            con_list = unit_out_contents.split("\n")            
            combine = []
            for fail_test in con_list:
                splits = fail_test.split("\t")
                header = splits[0] + "\n"
                results = splits[1:]
                rlist = markup_create_unlist(results)
                single_result = markup_create_header(header, 3)
                single_result += markup_create_indent(rlist, 2)
                combine.append(single_result)  
                      
            for (i, item) in enumerate(combine):
                combine[i] = markup_create_indent(item, 2)
            
            m = m + "\n".join(combine)
            message.append(m)
        
        # create a suggestion about the existence of output if some exists
        if len(open(outf).read()) > 0: 
            s = "The " + fn_name + " function should not contain any output."
            suggestions.append(s)
       
        # create suggestion if any unit tests failed 
        if len(unit_out_contents) > 0:
            s = "You failed " + str(len(unit_out_contents.split('\n')))
            s += " test cases. Start with the first test case in the unit test "
            s += "output and try to fix it. Then look at the next. If you are "
            s += "confident with your fixes submit your latest work."
            suggestions.append(s)
        
        # add suggestions section to message
        if len(suggestions) > 0:
            m =  markup_create_header("Suggestions\n", 2)
            m += markup_create_unlist(suggestions)
            message.append(m)

        
        # if the message for this part is empty then it passes
        if len(message) == 0:
            test_obj.score = test_obj.max_score
        else:
            test_obj.score = 0
            if test_obj.message == "":
                test_obj.message += "\n".join(message)
            else:
                test_obj.message += "\n" + "\n".join(message)
    else:
        test_obj.message = "Could not create unit test"        
    
    # clean up
    if made_working:
        shutil.rmtree(working_dir)
    elif len(files_to_remove) > 0:
        for f in files_to_remove:
            if os.path.isfile(f):
                os.remove(f)
        
    return OK

