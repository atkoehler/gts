## 
# @file modules/compilation.py
# @author Adam Koehler
# @date January 30, 2013
#
# @brief this module provides the means to compile a single or series
#        of files with or without a makefile.
#
#        the module returns a tuple of length 2 containing a binary
#        value representing compilation success and any messages
#        attached to compilation for feedback such as error messages
#

from system.utils import *
from system.procs import *

## 
# @brief test function checks compilation of the program
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
# @param source the source object containing name, location and content splits
# @param env the environment variables dict from JSON config of test suite
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, vars, source, env):
    import os
    import shutil
    OK = 0
    ERROR = -1
    
    harness_dir = locations[1]
    
    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    
    # set up compiler error text file path
    compile_err_path = os.path.join(working_dir, env["errors_file"])
    
    # set up path to executable rename
    exe_path = os.path.join(working_dir, env["exe_name"])

    # attempt compilation
    ret_val = compile_single(source.file_loc, exe_path, harness_dir, env)
    
    # set test object message to message of compilation return value
    test_obj.message = markup_create_indent(ret_val["message"], 1)
   
    # enforce penalty if needed 
    if not ret_val["success"]:
        test_obj.score = -1 * vars["penalty"]
    
    # remove the working directory if made it
    if made_working:
        shutil.rmtree(working_dir)    
    elif os.path.isfile(exe_path):
        os.remove(exe_path) 
    
    return OK


## 
# @brief the compile_single function compiles a single file
# 
# @param file_wpath source file with full path
# @param output_wpath output file name with full path
# @param harness_dir full path to harness directory
# @param env the environment variables dict from JSON config of test suite
#
# @return a dictionary with two values. The first boolean with key success.
#         The second key of message containing a message of compilation success
#         or failure containing any errors produced by compilation call.
#
# @precondition all included files must be at base level of includes directory
#
def compile_single(file_wpath, output_wpath, harness_dir, env):
    import os
    import subprocess
    import shutil
    from system.utils import which

    # Open /dev/null for dismissing errors or output    
    nullFile = open(os.devnull, 'w+')

    # grab proper g++ command 
    gpp = which(env["compiler"])

    # set up successful message
    message = "Compiled successfully"     

    # pull out file path to trim any error messages to just name or local path
    file_path = file_wpath[0:file_wpath.rfind("/")+1]
    
    # set up path to includes directory
    include_path = os.path.join(harness_dir, env["includes_dir"])
    
    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    
    err_file_path = os.path.join(working_dir, "errors.txt")
    
    # attempt to compile any provided source code
    obj_files = []
    compiled = True
    if env["code_provided"]:
        prov_dir = os.path.join(harness_dir, env["provided_dir"])
        files = os.listdir(prov_dir)        
        for file in files:
            if file.endswith(".o"):
                dest_path = os.path.join(working_dir, file)
                file_path = os.path.join(prov_dir, file)
                copyfile(file_path, dest_path)
            elif file.endswith(".cpp"):
                obj_name = file[0:file.find(".cpp")] + ".o"
                obj_path = os.path.join(working_dir, obj_name)
                file_path = os.path.join(prov_dir, file)
                try:
                    r = check_call([gpp, "-c", "-o", obj_path, 
                                    "-I", include_path, file_path], 
                                   stdout=nullFile, stderr=nullFile)
                    compiled = True
                    obj_files.append(obj_path)
                except SystemError:
                    compiled = False
                    break
        

    # attempt compilation
    if compiled:
        try:
            cmd = [gpp, "-o", output_wpath, "-I", include_path]
            for f in obj_files:
                cmd.append(f)
            cmd.append(file_wpath)
            with open(err_file_path, 'w+') as errFile:
                r = check_call(cmd, stdout=nullFile, stderr=errFile)
            compiled = True 
        
        except SystemError:
            # grab the errors from the error file then eliminate it
            message = open(err_file_path).read().replace(file_path, "")
            compiled = False
        
    # remove the working directory if function created it
    if made_working:
        shutil.rmtree(working_dir)    
    elif os.path.isfile(err_file_path):
        os.remove(err_file_path)
    
    return {"success": compiled, "message": message}


## 
# @brief strips the comments from a provided source file using g++ and flags
# 
# @param file_wpath source file with full path
# @param harness_dir full path to harness directory
# @param env the environment variables dict from JSON config of test suite
#
# @return a dictionary with two values. The first boolean with key success.
#         The second key of message containing either the source code 
#         processed and without comments or error messages from compilation
#
# @precondition all included files must be at base level of includes directory
#
def strip_comments(file_wpath, harness_dir, env):
    import os
    import subprocess
    import shutil
    from system.utils import which
   
    # grab proper g++ command 
    gpp = which(env["compiler"])

    if gpp is None:
        message = "g++ compiler not found, could not strip comments"
        compiled = False
        return {"success": compiled, "message": message}
    
    # pull out file path to trim any error messages to just name or local path
    file_path = file_wpath[0:file_wpath.rfind("/")+1]
    
    # set up path to includes directory
    include_path = os.path.join(harness_dir, env["includes_dir"])
    
    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
 
    # attempt to compiler preprocessor to strip comments
    out_file_path = os.path.join(working_dir, "out.txt")
    try:
        with open(out_file_path, 'w') as outFile:
            r = check_output([gpp, "-fpreprocessed", "-E", 
                               "-I", include_path, file_wpath], 
                               stdout=outFile, stderr=nullFile)
        compiled = True 
        message = open(out_file_path).read() 
    except SystemError:
        message = "Stripping comments from file failed"
        compiled = False
    
    if compiled:
        message = message[message.find("\n"):] 
    
    # remove the working directory if function created it
    if made_working:
        shutil.rmtree(working_dir)   
    elif os.path.isfile(out_file_path):
        os.remove(out_file_path)
    
    return {"success": compiled, "message": message}

