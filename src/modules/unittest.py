## 
# @file modules/unittest.py
# @author Adam Koehler
# @date February 16, 2013
#
# @brief Provides means to unit test
#

##
# @brief a class container for a unit test
# @requires requires the altersource module to replace source code
#
class UnitTest:
    def __init__(self, fn_name, include_stmts=None, test_file=None, 
                             unit_harness=None, unit_main=None,
                             merged_file=None):
        self.fn_name = fn_name
        self.include_stmts = include_stmts
        self.test_file = test_file
        self.unit_harness = unit_harness
        self.unit_main = unit_main
        self.merged_file = merged_file
    
    def create_unit(self, inc_stmts, unit_harness, unit_main,
                    merge_loc, source, harness):
        import os
        self.include_stmts = inc_stmts
        self.unit_harness = unit_harness
        self.unit_main = unit_main
        self.test_file = source.file_loc
       
        if not os.path.isfile(self.include_stmts):
            return False
        if not os.path.isfile(self.unit_harness):
            return False
        if not os.path.isfile(self.unit_main):
            return False
        if not os.path.isfile(merge_loc):
            return False
        
        # grab contents of files        
        includes = open(inc_stmts).read().split('\n')
        harness_contents = open(unit_harness).read().split('\n')
        main_contents = open(unit_main).read().split('\n')

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
        altersource.replace_source(harness_contents, "STUDENT_FUNC_NAME", self.fn_name)
        
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

            for line in main_contents:
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
# @param has_output whether function should have output, default is False
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, source, fn_name, 
                    has_output=False, has_input=False):
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
    unit = UnitTest(fn_name)
   
    # TODO: make sure all the paths and files exist before accessing/using 
    # set up path to unit tests directory
    unit_dir = os.path.join(harness_dir, UNIT_DIR_NAME)
    
    # set up path to #include lines
    inc_stmt_path = os.path.join(unit_dir, INCLUDE_LINES)
    
    # set up path to harness C++ file
    unit_filename = fn_name + ".cpp"
    unit_test_path = os.path.join(unit_dir, unit_filename)
    unit_main_path = os.path.join(unit_dir, "unit_main.cpp")
    
    # set up path to testing file
    merged_path = os.path.join(working_dir, TEST_FILE_NM)
    files_to_remove.append(merged_path)
    
    # create the unit
    ret = unit.create_unit(inc_stmt_path, unit_test_path, unit_main_path,
                           merged_path, source, harness_dir)
    
    # set up paths for unit test output
    unit_out = os.path.join(working_dir, "unit_test_output.txt")
    unit_err = os.path.join(working_dir, "unit_test_errors.txt")
    errf = os.path.join(working_dir, "test_program_err.txt")   
    outf = os.path.join(working_dir, "test_program_out.txt")   
    inpf = os.path.join(working_dir, "test_input.txt")   
    files_to_remove.append(unit_out)
    files_to_remove.append(unit_err)
    files_to_remove.append(errf)
    files_to_remove.append(outf)
    files_to_remove.append(inpf)
       
    # TODO: this probably should go in some sort of external file
    exception_msg = {}
    exception_handled = {}

    # Out of Range exceptions
    # string.at(int)
    exception_msg["Out of Range"] = {}
    s = "At least one exception was thrown by calling the at() member "
    s += " function of a string with a value that is either negative or "
    s += " greater than or equal to the size of the string. Check the value "
    s += " passed with each invocation of the function at() in " + fn_name 
    s += " as well as any functions " + fn_name + " calls."
    exception_msg["Out of Range"]["basic_string::at"] = s
    
    # vector.at(int)
    s = "At least one exception was thrown by calling the at() member "
    s += " function of a vector. The function was provided a value that is "
    s += " greater than or equal to the size of the vector or it was given a "
    s += " negative value. Check the value "
    s += " passed with each invocation of the function at() in " + fn_name 
    s += " as well as any functions " + fn_name + " calls."
    exception_msg["Out of Range"]["vector::_M_range_check"] = s
    
    # initially no exceptions have been handled
    for key in exception_msg:
        exception_handled[key] = {}
        for what_key in exception_msg[key]:
            exception_handled[key][what_key] = False
    
    message = []
    suggestions = []
    run_messages = {}
    notifications = {}
    unit_fail = set()
    contains_output = False
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
            s += " and are attempting to test it: Make sure you fix all "
            s += "compile errors before submission. If yours is compiling, "
            s += "make sure " + fn_name + " has a proper definition "
            s += "as we cannot invoke the function from the specification "
            s += " if you are defining it differently than we expect. "
            s += "Be sure to check its:\n"
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
                    if has_input:
                        inputFile = open(inpf, 'w+')
                        inputFile.write("OverwriteMe")
                        inputFile.close()
                        with open(inpf, 'r') as inp_file:
                            check_call([exe_path, unit_out, unit_err, inpf], 
                               stdout=out_file, stderr=err_file, stdin=inp_file)
                    else:
                        check_call([exe_path, unit_out, unit_err], 
                           stdout=out_file, stderr=err_file)
        
        except SystemError as e:
            unit_fail.add("SystemError")
            
            # create a notice about the abort throw and put in message
            m = "The " + fn_name + " unit test was aborted during execution "
            m += "by the operating system. If any reason or trace was given "
            m += "these may exist in the standard error message of the "
            m += "specific call that was aborted. If the type of abort was "
            m += "recognized there will be guidance in the Suggestions "
            m += "section. The abort may have been caused by this function "
            m += "or one that it calls."
            notifications["abort"] = m
            
           
            # if seg fault was detected
            # TODO: this access is ugly and should be cleaned up
            if e[0][0] == -11:
                cl = ["return value", "values of each parameter"]
                s = "A segmentation fault was detected when invoking your "
                s += "function. Make sure you check the following for "
                s += fn_name + " as well as any functions it invokes.\n"
                s += markup_create_indent(markup_create_unlist(cl), 1)
                suggestions.append(s)
            else:
                s = "The abort may have been caused by " + fn_name + " or any "
                s += "function that it calls. If " + fn_name + " invokes a "
                s += "function and that function passes its unit test then "
                s += "make sure " + fn_name + " passes proper values to the "
                s += "other function."
                suggestions.append(s)
         
        
        # if the unit test had any output then add them to message 
        if os.path.isfile(unit_err):
            unit_err_contents = open(unit_err).read().rstrip('\n')
        else:
            unit_err_contents = ""       
 
        # put unit test errors in the message
        if len(unit_err_contents) > 0: 
            lines = unit_err_contents.rstrip("\n").split("\n")
            for fail_test in lines:
                splits = fail_test.split("\t")
                key = splits[0] 
                errors = "\n".join(splits[1:])
                top = fn_name + " unit test error\n"
                single_result = markup_create_header(top, 4)
                single_result = markup_create_indent(single_result, 2)
                single_result += markup_create_indent(errors, 3)
                single_result += "\n"
                key = key.strip()
                unit_fail.add(key)
                if key not in run_messages:
                    run_messages[key] = single_result
                else:
                    run_messages[key] += single_result
                
                error_split = errors.split("\n")
                if len(error_split) > 0:
                    m = "The " + fn_name + " unit test caught an exception "
                    m += "thrown by " + fn_name + ". If the exception was "
                    m += "recognized by our harness then more information "
                    m += "will exist in the information for the invocation "
                    m += "of the specific unit test that threw the exception. "
                    m += "Additionally, there may be guidance in the "
                    m += "Suggestions section of the feedback."
                    notifications["exception"] = m

                for exception in error_split:
                    for key in exception_msg:
                        if exception.find(key) != -1:
                            for what, sug in exception_msg[key].iteritems():
                                if exception.find(what) != -1:
                                    if not exception_handled[key][what]:
                                        suggestions.append(sug)
                                        exception_handled[key][what] = True
         
        # if the unit test had any output then add them to message 
        if os.path.isfile(unit_out):
            unit_out_contents = open(unit_out).read().rstrip('\n')
        else:
            unit_out_contents = ""       
        
        if len(unit_out_contents) > 0:
            con_list = unit_out_contents.split("\n")            
            combine = []
            for fail_test in con_list:
                splits = fail_test.split("\t")
                key = splits[0] 
                results = splits[1:]
                rlist = markup_create_unlist(results)

                top = fn_name + " unit test output\n"
                single_result = markup_create_header(top, 4)
                single_result = markup_create_indent(single_result, 2)
                single_result += markup_create_indent(rlist, 3)
                single_result += "\n"
                key = key.strip()
                unit_fail.add(key)
                if key not in run_messages:
                    run_messages[key] = single_result
                else:
                    run_messages[key] += single_result
        
        # put standard output in the msg if unit testing had output or error
        if len(open(outf).read()) > 0: 
            line = open(outf).read().rstrip("\n")
            split_on = "Calling "
            pattern = re.compile(split_on)
            per_call = pattern.split(line)
            for output in per_call:
                lines = output.rstrip("\n").split("\n")
                key = "Calling " + lines[0]
                if len(lines) > 1:
                    contains_output = True
                    
                    act_output = "\n".join(lines[1:])
                     
                    top = fn_name + " standard output\n"
                    single_result = markup_create_header(top, 4)
                    single_result = markup_create_indent(single_result, 2)
                    single_result += markup_create_indent(act_output, 3)
                    single_result += "\n"
                    key = key.strip()
                    
                    # if the case hasn't been flagged for failure, do so
                    # if output is not expected for this function
                    if not has_output and contains_output:
                        unit_fail.add(key)
                    
                    # only add output if key already exists since it will
                    # be created by unit_error or unit_out
                    if key in unit_fail:
                        if key in run_messages:
                            run_messages[key] += single_result
                        else:
                            run_messages[key] = single_result
        
        # create a suggestion about the existence of output if some exists
        if not has_output and contains_output: 
            s = "The " + fn_name + " function should not contain any output."
            suggestions.append(s)
        elif has_output and not contains_output:
            s = "The " + fn_name + " function should contain some output."
            suggestions.append(s)
       
        # create suggestion if any unit tests failed 
        if len(run_messages) > 0:
            s = "You failed " + str(len(run_messages))
            s += " test cases. Additionally if any exceptions or aborts were "
            s += "thrown then most likely not all test cases were executed. "
            s += "Start with the first test case that failed and try to fix "
            s += "it. Then look at the next. If you are "
            s += "confident with your fixes submit your latest work to test it."
            suggestions.append(s)
       
        # add individual testing output to the message
        import operator
        m_sorted = sorted(run_messages.iteritems(), key=operator.itemgetter(0))
        for (key, value) in m_sorted:
            header = markup_create_indent(markup_create_header(key+"\n", 3),1)
            message.append(header + value)
         
        # put notifications at top of message if there are any
        if len(notifications) > 0:
            top = markup_create_header("Notifications\n", 2)
            notes = []
            for (key, value) in notifications.iteritems():
                head = markup_create_bold(key.upper())
                head += ": " + value
                notes.append(head)
            m = markup_create_unlist(notes)
            message = [top + m + "\n"] + message
 
        # add suggestions section as last part of message
        if len(suggestions) > 0:
            m =  markup_create_header("Suggestions\n", 2)
            m += markup_create_unlist(suggestions)
            message.append(m)
         
        # if unit fail set is empty
        if len(unit_fail) == 0:
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

