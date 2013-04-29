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
                             unit_harness=None, unit_main=None, sol_funcs=None,
                             merged_file=None):
        self.fn_name = fn_name
        self.include_stmts = include_stmts
        self.test_file = test_file
        self.unit_harness = unit_harness
        self.unit_main = unit_main
        self.sol_funcs = sol_funcs
        self.merged_file = merged_file
    
    def create_unit(self, inc_stmts, unit_harness, unit_main,
                    merge_loc, source, harness, sol_funcs, alterations):
        import os
        self.include_stmts = inc_stmts
        self.unit_harness = unit_harness
        self.unit_main = unit_main
        self.test_file = source.file_loc
        self.sol_funcs = sol_funcs
       
        if not os.path.isfile(self.include_stmts):
            return False
        if not os.path.isfile(self.unit_harness):
            return False
        if not os.path.isfile(self.unit_main):
            return False

        for sol_fn in self.sol_funcs:
            if not os.path.isfile(sol_fn):
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
        
        # TODO: eliminate module to module dependency
        import modules.altersource as altersource
        
        stud_contents = open(source.file_loc).read().split('\n')
        # replace the student's main with new name
        altersource.replace_source(stud_contents, 
                                   "int main", "int _studVer_main")

        # perform any replacements from configuration file
        for (i, value) in enumerate(alterations["from"]):
            altersource.replace_source(stud_contents, value, 
                                       alterations["to"][i])

        # update the test harness call to student's main if testing main
        if self.fn_name == "main":        
            altersource.replace_source(harness_contents, 
                                       "STUDENT_FUNC_NAME", "_studVer_main")
        else:
            altersource.replace_source(harness_contents, 
                                       "STUDENT_FUNC_NAME", self.fn_name)
        
        # output all the files to a merged file
        with open(merge_loc, 'w') as merge_file:
            for line in includes:
                merge_file.write(line+"\n")
            merge_file.write("\n")
      
            for p in self.sol_funcs:
                p_lines = open(p).read().split('\n')
                for line in p_lines:
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
from system.procs import *
from galah.interact import *
from modules.unittesting import *

## 
# @brief test function runs the unit test
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
# @param source the source object containing name, location and content splits
# @param fn_name name of the function to run unit test for
# @param has_output whether function should have output
# @param has_input whether the function should have input
# @param files list of files that store unit tests
# @param inc_sol the solution functions to include in test harness assembly
# @param env the environment variables dict from JSON config of test suite
# @param alterations dict of lists of alterations to source before testing it
#
# @return 0 if test completed successfully, otherwise -1
#
def logictest(locations, test_obj, vars, source, fn_name, 
              has_output, has_input, files, inc_sol, env, alterations):
    import re
    OK = 0
    ERROR = -1


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

    
    harness_dir = locations[1]
    files_to_remove = []

    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    # set up path to executable rename
    exe_path = os.path.join(working_dir, env["exe_name"])
    files_to_remove.append(exe_path)

    # attempt compilation
    ret_val = compile_single(source.file_loc, exe_path, harness_dir, env)
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
    
   
    # TODO: make sure all the paths and files exist before accessing/using 
    # set up path to unit tests directory
    unit_dir = os.path.join(harness_dir, env["unittest_dir"])
    
    # set up path to #include lines
    inc_stmt_path = os.path.join(unit_dir, vars["library_includes"])
    
    # set up path to harness C++ file
    unit_test_path = []
    if files is None:
        unit_filename = fn_name + env["src_extension"]
        unit_test_path.append(os.path.join(unit_dir, unit_filename))
    else:
        for i in files:
            unit_test_path.append(os.path.join(unit_dir, i))
    unittest_module_dir = os.path.join(harness_dir, "modules/unittesting")
    unit_main_path = os.path.join(unittest_module_dir, "unit_main.cpp")
    
    # set up path to testing file
    merged_path = []
    if files is None:
        merged_path.append(os.path.join(working_dir, vars["file_name"]))
        files_to_remove.append(merged_path[-1])
    else:
        for (i, test) in enumerate(unit_test_path):
            file_nm = vars["file_name"][0:vars["file_name"].find(env["src_extension"])] +str(i)+ env["src_extension"]
            merged_path.append(os.path.join(working_dir, file_nm))
            files_to_remove.append(merged_path[-1])
  
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
    
   
    solution_func_dir = os.path.join(harness_dir, env["solution_func_dir"])
    sol_incs = []
    for func in inc_sol:
        file = func + ".cpp"
        file_path = os.path.join(solution_func_dir, file)
        sol_incs.append(file_path)
        
    # create unit testing file
    units = []
    for (i, unit_test) in enumerate(unit_test_path):
        unit = UnitTest(fn_name)
        ret = unit.create_unit(inc_stmt_path, unit_test, unit_main_path,
                           merged_path[i], source, harness_dir, sol_incs,
                           alterations)
        if ret:
            units.append(unit)
    
    message = []
    suggestions = []
    run_messages = {}
    notifications = {}
    unit_fail = set()
    contains_output = False
    contains_input = False
    # merge success
    if len(units) == 0:
        test_obj.message = "<font color='red'>Could not create unit test.</font>"
    else:
        for merge_p in merged_path:
            # attempt compilation
            ret_val = compile_single(merge_p, exe_path, harness_dir, env)
            if ret_val["success"]:
                break

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
        # TODO: implement termination of process if it takes too long
        try:
            # create a task for execution
            t = Task(env["timeout"])
            with open(outf, 'w') as out_file:
                with open(errf, 'w') as err_file:
                    inputFile = open(inpf, 'w+')
                    inputFile.write("1 a holy cow")
                    inputFile.close()
                    with open(inpf, 'r') as inp_file:
                        if has_input:
                            t.check_call([exe_path, unit_out, unit_err, inpf], 
                               stdout=out_file, stderr=err_file, stdin=inp_file)
                        else:
                            t.check_call([exe_path, unit_out, unit_err], 
                               stdout=out_file, stderr=err_file, stdin=inp_file)
                        
                        # all tests are sent an input file, read remainder
                        remains = inp_file.read()
                        
            # read entire input file for comparison
            with open(inpf, 'r') as inp_file:
                entire = inp_file.read()
            
            # if function was not meant to have input and it
            # consumed something then make note of it
            # TODO: if process has_input then remains length is always 0
            # this does not imply that it did or didn't take input
            if len(remains) != len(entire):
                contains_input = True
            else:
                contains_input = False
    
        except SystemError as e:
            unit_fail.add("SystemError")
            
            # create a notice about the abort throw and put in message
            m = "The " + fn_name + " unit test was aborted during execution. "
            m += "If any reason or trace was given "
            m += "these may exist in the error message of the "
            m += "specific call that was aborted. If the type of abort was "
            m += "recognized there will be guidance in the Suggestions "
            m += "section. The abort may have been caused by this function "
            m += "or one that it calls."
            notifications["abort"] = m
            
           
            # TODO: this access is ugly and should be cleaned up
            # if seg fault was detected
            if e[0][0] == -11:
                cl = ["return value", "values of each parameter"]
                s = "A segmentation fault was detected when invoking your "
                s += "function. Make sure you check the following for "
                s += fn_name + " as well as any functions it invokes.\n"
                s += markup_create_indent(markup_create_unlist(cl), 1)
                suggestions.append(s)
            # termination of thread due to timeout
            elif e[0][0] == -15:
                cl = ["infinite loops (check your conditions)", 
                      "attempting to get input when no input exists"]
                s = "The unit test for your function, " + fn_name + " failed "
                s += "to execute to completion in the time allotted to it. "
                s += "This may have been caused by several things including:\n"
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
                    pref_output = markup_create_codeblock(act_output)
                     
                    top = fn_name + " standard output\n"
                    single_result = markup_create_header(top, 4)
                    single_result = markup_create_indent(single_result, 2)
                    single_result += markup_create_indent(pref_output, 3)
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
                            if run_messages[key][-1] == "\n":
                                run_messages[key] += single_result
                            else:
                                run_messages[key] += "\n" + single_result
                        else:
                            run_messages[key] = single_result
        
        # create a suggestion about the existence of output if some exists
        if not has_output and contains_output: 
            s = "The " + fn_name + " function should not contain any output."
            suggestions.append(s)
        elif has_output and not contains_output:
            s = "The " + fn_name + " function should contain some output."
            suggestions.append(s)
            unit_fail.add("OutputProblem")

        # create a suggestion about the existence of input
        if not has_input and contains_input: 
            s = "The " + fn_name + " function should not consume any input."
            suggestions.append(s)
            unit_fail.add("InputProblem")
        elif has_input and not contains_input:
            s = "The " + fn_name + " function should consume some input."
            suggestions.append(s)
            unit_fail.add("InputProblem")

       
        # create suggestion if any unit tests failed 
        if len(run_messages) > 0:
            s = "In total, you failed " + str(len(run_messages)) + " test "
            s += "cases which executed to completion. "
            if vars["cases_output"] != 0 and vars["cases_output"] < len(run_messages):
                s += "To avoid clutter we have provided information on " 
                s += str(min(len(run_messages), vars["cases_output"])) + " of "
                s += "these cases. Please utilize this information when "
                s += "attempting to fix your function, " +fn_name + ". "
                s += "When you submit again, if you pass one "
                s += "of the displayed cases it will disappear and may be "
                s += "replaced by information for another of the cases you "
                s += "failed."
            elif vars["cases_output"] == 0:
                s += "Please attempt to fix your code for your function, "
                s += fn_name + ". We have opted to not "
                s += "display information for any of the failed cases to "
                s += "encourage development of proper testing skills when "
                s += "designign a program or function. This includes coming "
                s += "up with the cases."
            else:
                s += "Information on these test cases has been provided. "
                s += "Please utilize this information when "
                s += "attempting to fix your function, " +fn_name + ". "
                s += "When you submit again, if you pass one "
                s += "of the displayed cases it will disapppear."
            suggestions.append(s)
       
        # add individual testing output to the message
        import operator
        m_sorted = sorted(run_messages.iteritems(), key=operator.itemgetter(0))
        count = 0
        for (key, value) in m_sorted:
            if count >= vars["cases_output"]:
                break
            count = count + 1
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
    
    # clean up
    if made_working:
        shutil.rmtree(working_dir)
    elif len(files_to_remove) > 0:
        for f in files_to_remove:
            if os.path.isfile(f):
                os.remove(f)
        
    return OK


## 
# @brief outputtest function runs the unit test and compares output to solution
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
# @param source the source object containing name, location and content splits
# @param solution object containing name, location, etc of solution
# @param fn_name name of the function to run unit test for
# @param has_output whether function should have output
# @param has_input whether the function should have input
# @param files list of files that store unit tests
# @param inc_sol the solution functions to include in test harness assembly
# @param env the environment variables dict from JSON config of test suite
# @param alterations dict of lists of alterations to source before testing it
#
# @return 0 if test completed successfully, otherwise -1
#
def outputtest(locations, test_obj, vars, source, solution, fn_name, has_output,
               has_input, files, inc_sol, env, alterations):
    import difflib
    import re
    OK = 0
    ERROR = -1


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

    
    harness_dir = locations[1]
    files_to_remove = []

    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    # set up path to executable rename
    exe_path = os.path.join(working_dir, env["exe_name"])
    sol_exe = os.path.join(working_dir, env["solution_exe"])
    files_to_remove.append(exe_path)
    files_to_remove.append(sol_exe)

    # attempt compilation
    ret_val = compile_single(source.file_loc, exe_path, harness_dir, env)
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
 
    # attempt compilation of solution
    ret_val = compile_single(solution.file_loc, sol_exe, harness_dir, env)
    if not ret_val["success"]:
        test_obj.score = 0
        test_obj.message = "Solution did not compile, cannot execute tests."
        
        # clean up
        if made_working:
            shutil.rmtree(working_dir)
        elif len(files_to_remove) > 0:
            for f in files_to_remove:
                if os.path.isfile(f):
                    os.remove(f)
        
        return OK   
   
    # TODO: make sure all the paths and files exist before accessing/using 
    # set up path to unit tests directory
    unit_dir = os.path.join(harness_dir, env["unittest_dir"])
    
    # set up path to #include lines
    inc_stmt_path = os.path.join(unit_dir, vars["library_includes"])
    
    # set up path to harness C++ file
    unit_test_path = []
    if files is None:
        unit_filename = fn_name + env["src_extension"]
        unit_test_path.append(os.path.join(unit_dir, unit_filename))
    else:
        for i in files:
            unit_test_path.append(os.path.join(unit_dir, i))
    unittest_module_dir = os.path.join(harness_dir, "modules/unittesting")
    unit_main_path = os.path.join(unittest_module_dir, "unit_main.cpp")
    
    # set up path to testing file
    merged_path = []
    sol_merged_path = []
    if files is None:
        merged_path.append(os.path.join(working_dir, vars["file_name"]))
        sol_merged_path.append(os.path.join(working_dir, solution.name))
        files_to_remove.append(merged_path[-1])
        files_to_remove.append(sol_merged_path[-1])
    else:
        for (i, test) in enumerate(unit_test_path):
            file_nm = vars["file_name"][0:vars["file_name"].find(env["src_extension"])] +str(i)+ env["src_extension"]
            merged_path.append(os.path.join(working_dir, file_nm))
            files_to_remove.append(merged_path[-1])
            file_nm = solution.name[0:solution.name.find(env["src_extension"])] +str(i)+ env["src_extension"]
            sol_merged_path.append(os.path.join(working_dir, file_nm))
            files_to_remove.append(sol_merged_path[-1])
   
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
    
    
    solution_func_dir = os.path.join(harness_dir, env["solution_func_dir"])
    sol_incs = []
    for func in inc_sol:
        file = func + env["src_extension"]
        file_path = os.path.join(solution_func_dir, file)
        sol_incs.append(file_path)
 
    # create unit testing file
    units = []
    for (i, unit_test) in enumerate(unit_test_path):
        unit = UnitTest(fn_name)
        ret = unit.create_unit(inc_stmt_path, unit_test, unit_main_path,
                           merged_path[i], source, harness_dir, sol_incs,
                           alterations)
        if ret:
            units.append(unit)

    # create unit solution files
    sol_units = []
    for (i, unit_test) in enumerate(unit_test_path):
        unit = UnitTest(fn_name)
        ret = unit.create_unit(inc_stmt_path, unit_test, unit_main_path,
                           sol_merged_path[i], solution, harness_dir, sol_incs,
                           alterations)
        if ret:
            sol_units.append(unit)   
   
    message = []
    suggestions = []
    run_messages = {}
    sol_messages = {}
    notifications = {}
    unit_fail = set()
    contains_output = False
    contains_input = False
    # merge success
    if len(units) == 0 or len(sol_units) == 0:
        test_obj.message = "Could not create unit test."
    else:
        for merge_p in merged_path:
            # attempt compilation
            ret_val = compile_single(merge_p, exe_path, harness_dir, env)
            if ret_val["success"]:
                break

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
 
        for sol_p in sol_merged_path:
            # attempt compilation
            ret_val = compile_single(sol_p, sol_exe, harness_dir, env)
            if ret_val["success"]:
                break

        if not ret_val["success"]:
            test_obj.score = 0
            header = markup_create_header("Notice\n", 2)
            m = "The solution's unit test did not compile."
            message.append(header + m)
            
        
        # run the unit test 
        try:
            # create a task for execution
            t = Task(env["timeout"])
            with open(outf, 'w+') as out_file:
                with open(errf, 'w+') as err_file:
                    inputFile = open(inpf, 'w+')
                    inputFile.write("1 a holy cow")
                    inputFile.close()
                    with open(inpf, 'r') as inp_file:
                        if has_input:
                            t.check_call([exe_path, unit_out, unit_err, inpf], 
                               stdout=out_file, stderr=err_file, stdin=inp_file)
                        else:
                            t.check_call([exe_path, unit_out, unit_err], 
                               stdout=out_file, stderr=err_file, stdin=inp_file)
        except SystemError as e:
            unit_fail.add("SystemError")
            
            # create a notice about the abort throw and put in message
            m = "The " + fn_name + " unit test was aborted during execution. "
            notifications["abort"] = m
            
           
            # TODO: this access is ugly and should be cleaned up
            # if seg fault was detected
            if e[0][0] == -11:
                cl = ["return value", "values of each parameter"]
                s = "A segmentation fault was detected when invoking your "
                s += "function. Make sure you check the following for "
                s += fn_name + " as well as any functions it invokes.\n"
                s += markup_create_indent(markup_create_unlist(cl), 1)
                suggestions.append(s)
            # termination of thread due to timeout
            elif e[0][0] == -15:
                cl = ["infinite loops (check your conditions)", 
                      "attempting to get input when no input exists"]
                s = "The unit test for your function, " + fn_name + " failed "
                s += "to execute to completion in the time allotted to it. "
                s += "This may have been caused by several things including:\n"
                s += markup_create_indent(markup_create_unlist(cl), 1)
                suggestions.append(s)
            else:
                s = "The abort may have been caused by " + fn_name + " or any "
                s += "function that it calls. If " + fn_name + " invokes a "
                s += "function and that function passes its unit test then "
                s += "make sure " + fn_name + " passes proper values to the "
                s += "other function."
                suggestions.append(s)
         
        
        # put standard output in the msg if unit testing had output or error
        if len(open(outf).read()) > 0: 
            line = open(outf).read().rstrip("\n")
            split_on = "Calling "
            pattern = re.compile(split_on)
            per_call = pattern.split(line)
            for output in per_call:
                lines = output.rstrip("\n").split("\n")
                # if something beyond the call line exists, output exists
                if len(lines) > 1:
                    key = "Calling " + lines[0]
                    act_output = "\n".join(lines[1:])
                    run_messages[key] = act_output
        
         
        # run the solution unit test 
        try:
            # create a task for execution
            t = Task(env["timeout"])
            with open(outf, 'w+') as out_file:
                with open(errf, 'w+') as err_file:
                    inputFile = open(inpf, 'w+')
                    inputFile.write("1 a holy cow")
                    inputFile.close()
                    with open(inpf, 'r') as inp_file:
                        if has_input:
                            t.check_call([sol_exe, unit_out, unit_err, inpf], 
                               stdout=out_file, stderr=err_file, stdin=inp_file)
                        else:
                            t.check_call([sol_exe, unit_out, unit_err], 
                               stdout=out_file, stderr=err_file, stdin=inp_file)
        except SystemError as e:
            unit_fail.add("SystemError")
            
            # creatk a notice about the abort throw and put in message
            m = "The " + fn_name + " unit test for solution was aborted."
            notifications["abort"] = m
       
                    
        # put standard output in the msg if unit testing had output or error
        if len(open(outf).read()) > 0: 
            line = open(outf).read().rstrip("\n")
            split_on = "Calling "
            pattern = re.compile(split_on)
            per_call = pattern.split(line)
            for output in per_call:
                lines = output.rstrip("\n").split("\n")
                # if something beyond the call line exists, output exists
                if len(lines) > 1:
                    key = "Calling " + lines[0]
                    sol_output = "\n".join(lines[1:])
                    sol_messages[key] = sol_output
        
        diff_messages = {}
        for (key, value) in sol_messages.iteritems():
            if key not in run_messages:
                run_messages[key] = ""
            
            # split the solution output into lines and eliminate blanks
            output_temp = value.split('\n')
            sol_output = []
            for line in output_temp:
                if len(line.strip()) != 0:
                    sol_output.append(line.strip().lower()+'\n')

            # split the test file output into lines and eliminate blanks
            output_temp = run_messages[key].split('\n')
            tf_output = []
            for line in output_temp:
                if len(line.strip()) != 0:
                    tf_output.append(line.strip().lower()+'\n')
            lines = []
            difflines = difflib.unified_diff(tf_output, sol_output,
                            fromfile=source.name, tofile=solution.name, n=1)
            
            unique = []
            for (i, line) in enumerate(difflines):
                if i > 1 and len(line) > 0:
                    if line[0] == '+':
                        unique.append(line)
                lines.append(line)
            diffoutput = "".join(lines)
                
            # make the list of unique lines
            unique = list(set(unique))

            if len(diffoutput) > 0:
                header = "Differences (" + str(len(unique)) + " unique)\n"
                diffoutput = markup_create_codeblock(diffoutput)
                diffoutput = markup_create_indent(diffoutput, 3)
                diff_messages[key] = header + diffoutput

       
        # create suggestion if any unit diff tests failed 
        if len(diff_messages) > 0:
            s = "In total, you failed " + str(len(run_messages)) + " test "
            s += "cases which executed to completion. "
            if vars["cases_output"] != 0 and vars["cases_output"] < len(run_messages):
                s += "To avoid clutter we have provided information on " 
                s += str(min(len(run_messages), vars["cases_output"])) + " of "
                s += "these cases. Please utilize this information when "
                s += "attempting to fix your function, " +fn_name + ". "
                s += "When you submit again, if you pass one "
                s += "of the displayed cases it will disappear and may be "
                s += "replaced by information for another of the cases you "
                s += "failed."
            elif vars["cases_output"] == 0:
                s += "Please attempt to fix your code for your function, "
                s += fn_name + ". We have opted to not "
                s += "display information for any of the failed cases to "
                s += "encourage development of proper testing skills when "
                s += "designign a program or function. This includes coming "
                s += "up with the cases."
            else:
                s += "Information on these test cases has been provided. "
                s += "Please utilize this information when "
                s += "attempting to fix your function, " +fn_name + ". "
                s += "When you submit again, if you pass one "
                s += "of the displayed cases it will disapppear."
            suggestions.append(s)
       
        # add individual testing output to the message
        import operator
        m_sorted = sorted(diff_messages.iteritems(), key=operator.itemgetter(0))
        count = 0
        for (key, value) in m_sorted:
            if count >= vars["cases_output"]:
                break
            count = count + 1
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
         
        # if no messages have been added to list to display, all tests passed
        if len(message) == 0:
            test_obj.score = test_obj.max_score
        else:
            test_obj.score = 0
            if test_obj.message == "":
                test_obj.message += "\n".join(message)
            else:
                test_obj.message += "\n" + "\n".join(message)
    
    # clean up
    if made_working:
        shutil.rmtree(working_dir)
    elif len(files_to_remove) > 0:
        for f in files_to_remove:
            if os.path.isfile(f):
                os.remove(f)
        
    return OK

