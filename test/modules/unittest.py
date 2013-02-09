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
    OK = 0
    ERROR = -1
    
    harness_dir = locations[1]

    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, WORKING_DIR_NAME)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    
    # set up path to executable rename
    exe_path = os.path.join(working_dir, EXE_NAME)

    # attempt compilation
    ret_val = compile_single(source.file_loc, exe_path, harness_dir)
    if not ret_val["success"]:
        test_obj.score = 0
        test_obj.message = "File did not compile, cannot execute tests."
        if made_working:
            shutil.rmtree(working_dir)
        return OK
    
    # create unit testing file
    unit = UnitTest()
   
    # TODO: make sure all the paths and files exist before accessing/using 
    # set up path to unit tests directory
    unit_dir = os.path.join(harness_dir, UNIT_DIR_NAME)
    unit_filename = fn_name + ".cpp"
    unit_harness = os.path.join(unit_dir, unit_filename)
    
    # set up path to testing file
    merged_path = os.path.join(working_dir, TEST_FILE_NM)
    
    # set up path to #include lines
    inc_stmt_path = os.path.join(unit_dir, INCLUDE_LINES)
    
    # set up path to harness C++ file
    unit_harness_path = os.path.join(unit_dir, unit_harness)
    
    # create the unit
    ret = unit.create_unit(inc_stmt_path, unit_harness_path, merged_path, 
                     source, harness_dir)

    message = []
    suggestions = []
    # merge success
    if ret:
        # attempt compilation
        ret_val = compile_single(merged_path, exe_path, harness_dir)
        if not ret_val["success"]:
            test_obj.score = 0
            test_obj.message = markup_create_header("Compile Errors\n", 4)
            test_obj.message += markup_create_indent(ret_val["message"], 1)
            test_obj.message += markup_create_header("Suggestions\n", 2)
            test_obj.message += "The unit test did not compile. If you have not yet implemented this function, you may ignore this. If you have started implementing your function " + fn_name + " and are attempting to test it, make sure it has a proper definition. Check its:\n" + markup_create_indent(markup_create_unlist(["return type", "function name", "parameter types", "number of parameters"]), 1)
            if made_working:
                shutil.rmtree(working_dir)
            return OK
        
        # set up paths for unit test output
        unit_out = os.path.join(working_dir, "unit_test_output.txt")
        errf = os.path.join(working_dir, "test_program_err.txt")   
        outf = os.path.join(working_dir, "test_program_out.txt")   
        
    
        # run the unit test 
        try:
            with open(outf, 'w') as out_file:
                with open(errf, 'w') as err_file:
                    check_call([exe_path, unit_out], stdout=out_file, stderr=err_file)
        except SystemError as e:
            # create a notice about the abort throw and put in message
            m = markup_create_header("Notice\n", 1)
            m += "The " + fn_name + " unit test was aborted during execution. "
            m += "If errors were output they will be displayed below and they "
            m += "are a good starting point to determine why your code "
            m += "crashed."
            message.append(m)
            
            # create a suggestion about abort and put in suggestions
            s = "The abort may have been caused by this function or any "
            s += "function that it calls. If the functions that are called "
            s += "are passing their respective tests then make sure " + fn_name
            s += " is not calling another function with a bad value as one of "
            s += "the parameters."
            suggestions.append(s)

        # put standard error in the message
        if len(open(errf).read()) > 0: 
            m = fn_name + " standard error\n"
            m = markup_create_header(m, 4)
            m = m + markup_create_indent(open(errf).read(), 1)
            message.append(m)
        
        # put standard output in the message
        if len(open(outf).read()) > 0: 
            m = fn_name + " standard output\n"
            m = markup_create_header(m, 4)
            m = m + markup_create_indent(open(outf).read(), 1)
            message.append(m)
 
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
                single_result = markup_create_header(header, 5)
                single_result += markup_create_indent(rlist, 1)
                combine.append(single_result)  
                      
            for (i, item) in enumerate(combine):
                combine[i] = markup_create_indent(item, 1)
            
            m = m + "\n".join(combine)
            message.append(m)
        
        # create a suggestion about the existence of output if some exists
        if len(open(outf).read()) > 0: 
            s = "The " + fn_name + " function should not contain any output."
            suggestions.append(s)
        

        
        if len(unit_out_contents) > 0:
            s = "You failed " + str(len(unit_out_contents.split('\n')))
            s += " test cases. Start with the first test case in the unit test "
            s += "output and try to fix it. Then look at the next. If you are "
            s += "confident with your fixes submit your latest work."
            suggestions.append(s)
        
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

    if made_working:
        shutil.rmtree(working_dir)
    
    return OK

