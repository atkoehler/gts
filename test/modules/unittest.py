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
TEST_FILE_NM = "test_file.cpp"
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

    # merge success
    if ret:
        # attempt compilation
        ret_val = compile_single(merged_path, exe_path, harness_dir)
        if not ret_val["success"]:
            test_obj.score = 0
            test_obj.message = "Unit test did not compile. Make sure your function " + fn_name + " is properly defined.\n\n"
            test_obj.message += "Compile Errors:\n\n" + ret_val["message"]
            if made_working:
                shutil.rmtree(working_dir)
            return OK
        
        # set up paths for unit test output
        unit_out = os.path.join(working_dir, "unit_test_output.txt")
        errf = os.path.join(working_dir, "test_program_err.txt")   
        outf = os.path.join(working_dir, "test_program_out.txt")   
        
    
        # run the unit test 
        with open(outf, 'w') as out_file:
            with open(errf, 'w') as err_file:
                check_call([exe_path, unit_out], stdout=out_file, stderr=err_file)
       
        
        message = "" 
        if len(open(outf).read()) > 0: 
            m = "The " + fn_name + " function should not contain any output."
            if message == "":
                message += m
            else:
                message += "\n\n" + m
        
        if len(open(errf).read()) > 0: 
            m = "The " + fn_name + " function output errors:\n\n"
            m = m + open(errf).read()
            if message == "":
                message += m
            else:
                message += "\n\n" + m
 
        if os.path.isfile(unit_out):
            unit_out_contents = open(unit_out).read()
        else:
            unit_out_contents = ""
        
        if len(unit_out_contents) > 0:
            if message == "":
                message += unit_out_contents
            else:
                message += "\n\n" + unit_out_contents      
        
        
        # if the message for this part is empty then it passes
        if len(message) == 0:
            test_obj.score = test_obj.max_score
        else:
            test_obj.score = 0
            if test_obj.message == "":
                test_obj.message += message
            else:
                test_obj.message += "\n\n" + message
    else:
        test_obj.message = "Could not create unit test"        

    if made_working:
        shutil.rmtree(working_dir)
    
    return OK

