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
# @param penalty the absolute value of the penalty to be applied
#
# @return 0 if test completed successfully, otherwise -1
#
def dicttest(locations, test_obj, source, file_paths, 
             env, alterations, keyval, n, penalty):
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
    open(stud_file, 'w+').write("\n".join(stud_contents))
    
    # open the solution working file and write the altered source
    open(sol_work, 'w+').write("\n".join(sol_contents))

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
                    if line.decode('utf-8').lower().find(keyval.lower()) != -1:
                        key_loc = line.decode('utf-8').lower().find(keyval.lower())
                        if len(testfile_output_string) > 0:
                            testfile_output_string += "\n"
                        if key_loc != -1:
                            testfile_output_string += line[key_loc:].strip()
                        else:
                            testfile_output_string = ""
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
                    if line.decode('utf-8').lower().find(keyval.lower()) != -1:
                        key_loc = line.decode('utf-8').lower().find(keyval.lower())
                        if len(solution_output_string) > 0:
                            solution_output_string += "\n"
                        if key_loc != -1:
                            solution_output_string += line[key_loc:].strip()
                        else:
                            solution_output_string = ""
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
            
            if len(diffoutput) > 0:
                top = markup_create_header(input[input.rfind("/")+1:]+"\n", 3)
                top = markup_create_indent(top, 1)
 
                input_hdr = markup_create_bold("Input Contents:") + "\n"
                input_hdr = markup_create_indent(input_hdr, 2)
                input_cont = markup_create_codeblock(open(input).read())
                input_cont = markup_create_indent(input_cont, 3)
                input_cont += "\n"
                
                # different markdown based on execution of diff or not
                # put diff output in codeblock to avoid bad markdown 
                if status[env["solution_name"]] and status[testing_file]:
                    header = "Differences (" + str(len(unique)) + " unique)\n"
                    diffoutput = markup_create_codeblock(diffoutput)
                else:
                    header = "Differences\n"
                
                results = markup_create_header(header, 4)
                results = markup_create_indent(results, 2)
                results_cont = markup_create_indent(diffoutput, 3)

                rec_hdr = markup_create_bold("Output Value: ")
                rec_hdr = markup_create_indent(rec_hdr, 2)
                if len(testfile_output_string) > 0:
                    rec_contents = markup_create_codeblock(testfile_output_string)
                else:
                    rec_contents = "\n"

                sol_hdr = markup_create_bold("Expected Value: ")
                sol_hdr = markup_create_indent(sol_hdr, 2)
                if len(solution_output_string) > 0:
                    sol_contents = markup_create_codeblock(solution_output_string)
                else:
                    sol_contents = "No output is expected for this operation "
                    sol_contents += "and category combination.\n"
               

                if DISPLAY_NAME_ONLY:
                    single = top + "\n"
                    single += error_hdr + error_cont
                elif DISPLAY_EXPECTED:
                    single = top + "\n"
                    single += input_hdr + input_cont + "\n"
                    single += rec_hdr + rec_contents + "\n"
                    single += sol_hdr + sol_contents + "\n"
                else:
                    single = top + "\n"
                    single += error_hdr + error_cont + "\n"
                    single += input_hdr + input_cont + "\n"
                    single += results + results_cont


                if len(testfile_output_string.strip()) == 0:
                    single = top + "\n"
                    single += input_hdr + input_cont + "\n"
                    m = "Could not find a value to utilize. Attempted "
                    m += "to find value using a case agnostic key value "
                    m += "of: " + keyval
                    m = markup_create_indent(m, 2)
                    single += m
                    s = "The test harness could not find an output value for "
                    s += "these tests. Check the specification and make sure "
                    s += "you are following the stipulated output requirements."
                    suggestions.append(s)
                messages.append(single)
                test_obj.score += -1
            else:
                test_obj.score += 0
    else:
        # no input files just run program and solution and compare output
        try:
            # create a task for execution
            t = Task(env["timeout"])
            with open(outf, 'w+') as out_file:
                t.check_call([exe_path], stdout=out_file, stderr=FNULL)
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
        if status[testing_file] and len(open(outf).read()) > 0: 
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
                if line.decode('utf-8').lower().find(keyval.lower()) != -1:
                    key_loc = line.decode('utf-8').lower().find(keyval.lower())
                    if len(testfile_output_string) > 0:
                        testfile_output_string += "\n"
                    if key_loc != -1:
                        testfile_output_string += line[key_loc:].strip()
                    else:
                        testfile_output_string = ""
                    tf_output.append(testfile_output_string+'\n')

        try:
            # create a task for execution
            t = Task(env["timeout"])
            with open(outf, 'w+') as out_file:
                t.check_call([sol_exe], stdout=out_file, stderr=FNULL)
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
                if line.decode('utf-8').lower().find(keyval.lower()) != -1:
                    key_loc = line.decode('utf-8').lower().find(keyval.lower())
                    if len(solution_output_string) > 0:
                        solution_output_string += "\n"
                    if key_loc != -1:
                        solution_output_string += line[key_loc:].strip()
                    else:
                        solution_output_string = ""
                    sol_output.append(solution_output_string+'\n')
           
        lines = []
        difflines = difflib.unified_diff(tf_output, sol_output, 
                        fromfile=source.name, tofile=env["solution_name"], n=1)
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
        
        if len(diffoutput) > 0:
            top = markup_create_header("Math Equations\n", 3)
            top = markup_create_indent(top, 1)
            if len(testfile_error) > 0:
                error_hdr = markup_create_header("Standard Error\n", 4)
                error_hdr = markup_create_indent(error_hdr, 2)
                error_cont = markup_create_codeblock(testfile_error)
                error_cont = markup_create_indent(error_cont, 3)
            else:
                error_hdr = ""
                error_cont = ""

            input_hdr = markup_create_header("Input Contents\n", 4)
            input_hdr = markup_create_indent(input_hdr, 2)
            input_cont = markup_create_codeblock(open(in_path).read())
            
            # different markdown based on execution of diff or not
            # put diff output in codeblock to avoid bad markdown 
            if status[env["solution_name"]] and status[testing_file]:
                header = "Differences (" + str(len(unique)) + " unique)\n"
                diffoutput = markup_create_codeblock(diffoutput)
            else:
                header = "Differences\n"
            
            results = markup_create_header(header, 4)
            results = markup_create_indent(results, 2)
            results_cont = markup_create_indent(diffoutput, 3)

            rec_hdr = markup_create_header("Output Found:\n", 4)
            rec_hdr = markup_create_indent(rec_hdr, 2)
            if len(testfile_output_string) > 0:
                rec_contents = markup_create_codeblock(testfile_output_string)
            else:
                rec_contents = "\n"

            sol_hdr = markup_create_header("Expected Output:\n", 4)
            sol_hdr = markup_create_indent(sol_hdr, 2)
            if len(solution_output_string) > 0:
                sol_contents = markup_create_codeblock(solution_output_string)
            else:
                sol_contents = "\n"
           

            if DISPLAY_NAME_ONLY:
                single = top + "\n"
                single += error_hdr + error_cont
            elif DISPLAY_EXPECTED:
                single = top + "\n"
                single += input_hdr + input_cont + "\n"
                single += rec_hdr + rec_contents + "\n"
                single += sol_hdr + sol_contents + "\n"
            else:
                single = top + "\n"
                single += input_hdr + input_cont + "\n"
                single += results + results_cont
            messages.append(single)
            test_obj.score += -1
        else:
            test_obj.score = 0

    

    # limit the messages if warranted
    
    m = "You failed " + str(len(messages)) + " cases. "
    if len(messages) > n:
        m += "We are limiting the " 
        m += "number of failed output cases to " + str(n) + " to avoid output "
        m += "clutter and help you concentrate on fixing items in a "
        m += "step-wise manner. When you fix one of the displayed cases "
        m += "it may be replaced by a new one on the next submission."
    else: 
        m += "When you fix one of the cases, it should disappear from the "
        m += "feedback on your next submission." 

    if len(messages) > 0:
        messages = messages[0:n]
        header = markup_create_header("Failed Cases\n", 2)
        messages = [header] + messages
        suggestions.append(m)
 
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
    if test_obj.score < 0:
        test_obj.score = -1 * penalty
    return OK

