## 
# @file modules/indent.py
# @author Adam Koehler
# @date January 31, 2013
#
# @brief Provides means to run the indent command with preset argument or 
#        list of arguments.
#

from system.utils import *

## 
# @brief test function checks file name against a required name
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
    OK = 0
    ERROR = -1
    
    harness_dir = locations[1]
    
    # attempt file indent
    ret_val = indent_file(source.file_loc, harness_dir, env, vars["base_style"],
                          vars["add_flags"])
    
    # set message to errors from indent if they exist and enforce penalty
    if not ret_val["errors"] is None:
        test_obj.message = markup_create_indent(ret_val["errors"], 1)
        test_obj.score = -1 * vars["penalty"]
    elif not ret_val["success"]:
        test_obj.message = ret_val["message"]
    else:
        test_obj.message = "indent command executed without errors"
    
    return OK


## 
# @brief indent_file runs the indent command on single file if indent is 
#        present on the system
#
#   Possible values for the preset include strings: "BSD"
# 
# @param source_wpath a file to be indented containing full path to file
# @param preset a string containing a preset style
# @param arguments a list of arguments for indent command if preset is None
# @param env the environment variables dict from JSON config of test suite
#
# @return dictionary containing the keys, success, message, errors. 
#           success contains True if the file could be indented. 
#           message contains the indented file as a string if success is True
#           errors contains stderr output from indent command, otherwise None
#
def indent_file(source_wpath, harness_path, env, preset="", arguments=None):
    if arguments is None:
        arguments = []
    
    if preset == "":
        ret_val = indent_args(source_wpath, harness_path, arguments, env)
    elif preset == "BSD":
        ret_val = preset_bsd(source_wpath, harness_path, arguments, env)
    else:
        message = "Invalid preset value: " + str(preset)
        ret_val = {"success": False, "message": message, "errors": None}
    
    return ret_val


## 
# @brief preset_bsd uses BSD (Allman) Style arguments with the indent command
# 
# @param f a file to be indented containing full path to file
# @param p is the path to the test harness directory
# @param arg_list a list of arguments to be utilized in addition to BSD args
# @param env the environment variables dict from JSON config of test suite
#
# @return dictionary containing the keys, success, message, errors. 
#           success contains True if the file could be indented. 
#           message contains the indented file as a string if success is True
#           errors contains stderr output from indent command, otherwise None
#
def preset_bsd(f, p, arg_list, env):
    bsd_args = ["-bap", "-bli0", "-i4", "-l79", "-ncs", "-npcs", 
                 "-npsl", "-lc79", "-fc1", "-ts4"]
    for i in arg_list:
        bsd_args.append(i)
    
    return indent_args(f, p, bsd_args, env)


## 
# @brief indent_args uses the provided arguments when calling indent command
# 
# @param f a file to be indented containing full path to file
# @param p is the path to the test harness directory
# @param arg_list a list of arguments to be utilized
# @param env the environment variables dict from JSON config of test suite
#
# @return dictionary containing the keys, success, message, errors. 
#           success contains True if the file could be indented. 
#           message contains the indented file as a string if success is True
#           errors contains stderr output from indent command, otherwise None
#
def indent_args(f, p, arg_list, env):
    import os
    import subprocess  
    import shutil
    from system.utils import which
    from system.procs import check_call
    
    files_to_remove = []
    
    indented = False
    message = "Could not indent the file"
    error = None
  
    # send indent output to standard output
    arg_list.append("-st")
    
    # grab the system's indent command
    indent = which("indent")
    if indent is None:
        indented = False
        message = "No indent command found on system"
        error = None
        return {"success": indented, "message": message, "errors": error}
    
    # create a working directory if one doesn't exist
    working_dir = os.path.join(p, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
   
    
    # attempt compilation as compile errors may cause odd indent errors
    # grab proper g++ command 
    gpp = which(env["compiler"])

    # pull out file path to trim any error messages to just name or local path
    file_wpath = f
    file_path = file_wpath[0:file_wpath.rfind("/")+1]
    
    # set up path to includes directory
    include_path = os.path.join(p, env["includes_dir"])
    
    # set up path to output exe
    output_wpath = os.path.join(working_dir, "indent_compile")
    
    # open /dev/null for dismissing output or errors
    nullFile = open(os.devnull, 'w')
    
    # attempt compilation
    try:
        r = check_call([gpp, "-o",output_wpath, "-I", include_path, file_wpath],
                       stdout=nullFile, stderr=nullFile)
        compiled = True 
    except SystemError:
        compiled = False
    
    
    errf = os.path.join(working_dir, "indent_errors.txt")
    files_to_remove.append(errf)
    indentf = os.path.join(working_dir, "indent_out.cpp")
    files_to_remove.append(indentf)
    try:
        command = [indent]
        for arg in arg_list:
            command.append(arg)
        command.append(f)
        
        # run indent command 
        with open(errf, 'w') as err_file:
            with open(indentf, 'w') as indentFile:
                r = check_call(command, stdout=indentFile, stderr=err_file)
        message = open(indentf).read()
    except SystemError:
        message = open(indentf).read()
   
    # Indent always does something even when errors exist
    indented = True

    # determine if error messages exist
    with open(errf, 'r') as err_file:
        error = err_file.read()
    if len(error) == 0:
        error = None
    else:
        error = error.replace(f[0:f.rfind("/")+1], "").replace("indent: ", "")
        error = error.replace("\n\n", "\n")
        error = error.strip()
        
    # didn't compile pre-pend a warning about indent error messages
    if not compiled:
        pre = "WARNING: Failed compilation may result in additional errors from indent command.\n\n"
        error = pre + error
    
    # remove working directory if this process created it otherwise all files
    if made_working:
        shutil.rmtree(working_dir) 
    elif len(files_to_remove) > 0:
        for f in files_to_remove:
            if os.path.isfile(f):
                os.remove(f)
        
    
    return {"success": indented, "message": message, "errors": error}

