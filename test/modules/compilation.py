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

# TODO: figure out the configuration system, to hold these values
# TODO: once complete, utilize import or whatever is needed
TYPE = ".cpp"
COMPILER = "g++"
WORKING_DIR_NAME = "working"
EXE_NAME = "test_program"
COMPILER_ERR_FNAME = "compiler_errors.txt"
PENALTY = 25
INCLUDES_DIR = "system/includes"

## 
# @brief test function checks various style parts for the program
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param source the source object containing name, location and content splits
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, source):
    import os
    OK = 0
    ERROR = -1
    
    harness_dir = locations[1]
    
    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, WORKING_DIR_NAME)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    
    # set up compiler error text file path
    compile_err_path = os.path.join(working_dir, COMPILER_ERR_FNAME)
    
    # set up path to executable rename
    exe_path = os.path.join(working_dir, EXE_NAME)

    # attempt compilation
    ret_val = compile_single(source.file_loc, exe_path, harness_dir)
    
    # set test object message to message of compilation return value
    test_obj.message = ret_val["message"]
   
    # enforce penalty if needed 
    if not ret_val["success"]:
        test_obj.score = -1 * PENALTY
    
    # remove the working directory
    import shutil
    shutil.rmtree(working_dir)    
    
    return OK


## 
# @brief the compile_single function compiles a single file
# 
# @param file_wpath source file with full path
# @param output_wpath output file name with full path
# @param harness_dir full path to harness directory
#
# @return a dictionary with two values. The first boolean with key success.
#         The second key of message containing a message of compilation success
#         or failure containing any errors produced by compilation call.
#
# @precondition all included files must be at base level of includes directory
#
def compile_single(file_wpath, output_wpath, harness_dir):
    import os
    import subprocess
    from system.utils import which
   
    # grab proper g++ command 
    gpp = which("g++")

    # set up successful message
    message = "Compiled successfully"     

    # pull out file path to trim any error messages to just name or local path
    file_path = file_wpath[0:file_wpath.rfind("/")+1]
    
    # set up path to includes directory
    include_path = os.path.join(harness_dir, INCLUDES_DIR)

    # attempt compilation
    try:
        m = subprocess.check_output([gpp, "-o", output_wpath, 
                                          "-I", include_path, 
                                          file_wpath], 
                                    stderr=subprocess.STDOUT)
        compiled = True 
    
    except subprocess.CalledProcessError as e:
        message = e.output.replace(file_path, "")
        compiled = False
    
    return {"success": compiled, "message": message}


## 
# @brief strips the comments from a provided source file using g++ and flags
# 
# @param file_wpath source file with full path
# @param harness_dir full path to harness directory
#
# @return a dictionary with two values. The first boolean with key success.
#         The second key of message containing either the source code 
#         processed and without comments or error messages from compilation
#
# @precondition all included files must be at base level of includes directory
#
def strip_comments(file_wpath, harness_dir):
    import os
    import subprocess
    from system.utils import which
   
    # grab proper g++ command 
    gpp = which("g++")

    if gpp is None:
        message = "g++ compiler not found, could not strip comments"
        compiled = False
        return {"success": compiled, "message": message}
    
    # pull out file path to trim any error messages to just name or local path
    file_path = file_wpath[0:file_wpath.rfind("/")+1]
    
    # set up path to includes directory
    include_path = os.path.join(harness_dir, INCLUDES_DIR)

    # attempt compilation
    try:
        message = subprocess.check_output([gpp, "-fpreprocessed", "-E", 
                                          "-I", include_path, 
                                          file_wpath], 
                                    stderr=subprocess.STDOUT)
        compiled = True 
    
    except subprocess.CalledProcessError as e:
        message = "Stripping comments from file failed"
        compiled = False
    
    if compiled:
        message = message[message.find("\n"):] 
    
    return {"success": compiled, "message": message}

