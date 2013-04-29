## 
# @file modules/outputcheck.py
# @author Adam Koehler
# @date February 25, 2013
#
# @brief Provides the means to a program's output to solution
#

from system.utils import *
from system.procs import *


DISPLAY_NAME_ONLY = False
DISPLAY_EXPECTED = True

## 
# @brief check the last item on line starting with key against solution
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param source the source object containing name, location and content splits
# @param file_paths the paths to all input files to utilize for this test
# @param env the environment variables dict from JSON config of test suite
# @param alterations dict of lists of alterations to source before testing it
# @param keyval the key value to look for in output
# @param n the number of failed cases to output
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, source, file_paths, 
             env, alterations, keyval, n):
    OK = 0
    from modules.compilation import compile_single
    import modules.altersource as altersource
    import difflib
    import os
    import shutil

    harness_dir = locations[1]
    files_to_remove = []

    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False

    # solution path
    sol_dir = os.path.join(harness_dir, env["solution_dir"])
    sol_path = os.path.join(sol_dir, env["solution_name"])
    sol_work = os.path.join(working_dir, env["solution_name"])
    
    # student working file
    testing_file = env["src_name"] + env["src_extension"]
    stud_file = os.path.join(working_dir, testing_file)
    files_to_remove.append(stud_file)

    # executables
    exe_path = os.path.join(working_dir, env["exe_name"])
    files_to_remove.append(exe_path)
    sol_exe = os.path.join(working_dir, env["solution_exe"])
    files_to_remove.append(sol_exe)

    # attempt alterations to code
    stud_contents = open(source.file_loc).read().split('\n')
    sol_contents = open(sol_path).read().split('\n')
    for (i, value) in enumerate(alterations["from"]):
        replaced = altersource.replace_source(stud_contents, value, 
                                              alterations["to"][i])
        if not replaced:
            test_obj.score = 0
            test_obj.message = "Could not find " + value + " in source code."
        
            # clean up
            if made_working:
                shutil.rmtree(working_dir)
            elif len(files_to_remove) > 0:
                for f in files_to_remove:
                    if os.path.isfile(f):
                        os.remove(f)
            return OK           
        
        # apply same alterations to solution
        replaced = altersource.replace_source(sol_contents, value, 
                                              alterations["to"][i])
        if not replaced:
            test_obj.score = 0
            test_obj.message = "Could not find " + value + " in solution."
        
            # clean up
            if made_working:
                shutil.rmtree(working_dir)
            elif len(files_to_remove) > 0:
                for f in files_to_remove:
                    if os.path.isfile(f):
                        os.remove(f)
            return OK           
    
    # open the student working file and write the altered source
    open(stud_file, 'wb+').write("\n".join(stud_contents))
    
    # open the solution working file and write the altered source
    open(sol_work, 'wb+').write("\n".join(sol_contents))

    # attempt compilation of both working files
    ret_val = compile_single(stud_file, exe_path, harness_dir, env)
    sol_ret_val = compile_single(sol_work, sol_exe, harness_dir, env)
    if not ret_val["success"]:
        test_obj.score = 0
        test_obj.message = "File did not compile, cannot compare output."
        
        # clean up
        if made_working:
            shutil.rmtree(working_dir)
        elif len(files_to_remove) > 0:
            for f in files_to_remove:
                if os.path.isfile(f):
                    os.remove(f)
        
        return OK
    if not sol_ret_val["success"]:
        test_obj.score = 0
        test_obj.message = "Solution did not compile, cannot compare output."
        
        # clean up
        if made_working:
            shutil.rmtree(working_dir)
        elif len(files_to_remove) > 0:
            for f in files_to_remove:
                if os.path.isfile(f):
                    os.remove(f)
        
        return OK   
    
    # compilation successful proceed with testing
    outf = os.path.join(working_dir, "test_program.out")   
    files_to_remove.append(outf)
    solution_outf = os.path.join(working_dir, "solution.out")   
    files_to_remove.append(solution_outf)
 
    FNULL = open(os.devnull, 'w')
    messages = []
    suggestions = []
    notifications = {}
    if len(file_paths) > 0: 
        status = {}
        for input in file_paths:
            with open(input, 'r') as inp_file:
                try:
                    # create a task for execution
                    t = Task(env["timeout"])
                    with open(outf, 'w+') as out_file:
                        t.check_call([exe_path], stdout=out_file, stderr=FNULL, 
                                     stdin=inp_file)
                    status[testing_file] = True                
                except SystemError as e:
                    status[testing_file] = False
                    # create a notice about the abort throw and put in message
                    m = "Your program's execution was aborted."
                    notifications["abort"] = m
                    
                   
                    # TODO: this access is ugly and should be cleaned up
                    # if seg fault was detected
                    if e[0][0] == -11:
                        cl = ["return value", "values of each parameter"]
                        s = "A segmentation fault occurred when running your "
                        s += "program."
                        suggestions.append(s)
                    # termination of thread due to timeout
                    elif e[0][0] == -15:
                        cl = ["infinite loops (check your conditions)", 
                              "attempting to get input when no input exists"]
                        s = "Your program failed to execute "
                        s += "to completion in the time allotted to it. "
                        s += "This may have been caused by several things "
                        s += "including:\n"
                        s += markup_create_indent(markup_create_unlist(cl), 1)
                        suggestions.append(s)
             
            # grab standard output if test was not aborted
            if len(open(outf).read()) > 0: 
                testfile_output = open(outf).readlines()
            else:
                testfile_output = ""

            # format the lines:
            # eliminate blank lines, strip trail/lead whitespace
            # convert all to lowercase
            tf_output = []
            testfile_output_string = ""
            for line in testfile_output:
                if len(line.strip()) != 0:
                    if line.lower().find(keyval.lower()) != -1:
                        key_loc = line.lower().find(keyval.lower())
                        space_aft = line.lower().find(" ", key_loc)
                        if len(testfile_output_string) > 0:
                            testfile_output_string += "\n"
                        if space_aft != -1:
                            testfile_output_string += line[space_aft+1:].strip()
                            tf_output.append(testfile_output_string+'\n')

            # now execute solution 
            with open(input, 'r') as inp_file:
                try:
                    # create a task for execution
                    t = Task(env["timeout"])
                    with open(outf, 'w+') as out_file:
                        t.check_call([sol_exe], stdout=out_file, stderr=FNULL, 
                                     stdin=inp_file)
                    status[env["solution_name"]] = True                     
                except SystemError as e:
                    status[env["solution_name"]] = False
                    key = "abort"
                    if key not in notifications:
                        notifications["abort"] = "Solution was aborted!"
                    else:
                        notifications["abort"] += "\nSolution was aborted!"
 
            # grab standard output if test wasn't aborted
            if len(open(outf).read()) > 0: 
                solution_output = open(outf).readlines()
            else:
                solution_output = ""
 
            # format the lines:
            # eliminate blank lines, strip trail/lead whitespace
            # convert all to lowercase
            sol_output = []
            solution_output_string = ""
            for line in solution_output:
                if len(line.strip()) != 0:
                    if line.lower().find(keyval.lower()) != -1:
                        key_loc = line.lower().find(keyval.lower())
                        space_aft = line.lower().find(" ", key_loc)
                        if len(solution_output_string) > 0:
                            solution_output_string += "\n"
                        if space_aft != -1:
                            solution_output_string += line[space_aft+1:].strip()
                            sol_output.append(solution_output_string+'\n')
            
            lines = []
            difflines = difflib.unified_diff(tf_output, sol_output, 
                            fromfile=source.name, tofile='solution.cpp', n=1)
            unique = []
            for (i, line) in enumerate(difflines):
                if i > 1 and len(line) > 0:
                    if line[0] == '+':
                        unique.append(line)
                lines.append(line)
            diffoutput = "".join(lines)
            
            if not status[env["solution_name"]] or not status[testing_file]:
                diffoutput = "Output comparison was skipped because the program"
                diffoutput += " was terminated due to an abort "
                diffoutput += "signal."

            # make the list of unique lines
            unique = list(set(unique))
          
            if len(diffoutput.strip()) > 0:
                if len(testfile_output_string.strip()) > 0:
                    m = "Weighted sum value for digit number "
                    m += sol_output[0].strip("\n") 
                    m += " is incorrect, where the first digit is the "
                    m += "farthest left."
                else:
                    m = "Could not find a value to utilize. Attempted to find "
                    m += " value using a case agnostic key value of: "
                    m += keyval
                    s = "The test harness could not find an output value for "
                    s += "these tests. Check the specification and make sure "
                    s += "you are following the stipulated output requirements."
                    suggestions.append(s)
                messages.append(m)
            else:
                test_obj.score += float(test_obj.max_score) / len(file_paths)
    
    # limit the messages if warranted
    if len(messages) > 0:
        m = "You failed " + str(len(messages)) + " cases. "
        m += "When you fix one of the cases, it should disappear from the "
        m += "feedback on your next submission." 
        suggestions.append(m)

        # turn current messages into bullet point list
        header = markup_create_header("Bad Values\n", 2)
        q = list(set(messages))
        q.sort()
        mlist = markup_create_unlist(q)
        messages = []
        messages.append(header + mlist)
 
    # put notifications at top of message if there are any
    if len(notifications) > 0:
        top = markup_create_header("Notifications\n", 2)
        notes = []
        for (key, value) in notifications.iteritems():
            head = markup_create_bold(key.upper())
            head += ": " + value
            notes.append(head)
        m = markup_create_unlist(notes)
        messages = [top + m + "\n"] + messages

    # add suggestions section as last part of message
    if len(suggestions) > 0:
        m =  markup_create_header("Suggestions\n", 2)
        m += markup_create_unlist(list(set(suggestions)))
        messages.append(m)
    
    # add messages
    if len(messages) != 0:
        if test_obj.message == "":
            test_obj.message += "\n".join(messages)
        else:
            test_obj.message += "\n" + "\n".join(messages)
 
    # clean up
    if made_working:
        shutil.rmtree(working_dir)
    elif len(files_to_remove) > 0:
        for f in files_to_remove:
            if os.path.isfile(f):
                os.remove(f)
   
    test_obj.score = int(round(test_obj.score))
    return OK

