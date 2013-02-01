## 
# @file modules/indent.py
# @author Adam Koehler
# @date January 31, 2013
#
# @brief Provides means to run the indent command with preset argument or 
#        list of arguments.
#

# TODO: grab this from configuration object/file when implemented
WORKING_DIR_NAME = "working"
PENALTY = 25


## 
# @brief test function checks file name against a required name
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, source):
    import os
    import shutil
    OK = 0
    ERROR = -1
    
    harness_dir = locations[1]
    
    # create a working directory if one doesn't exist
    working_dir = os.path.join(harness_dir, WORKING_DIR_NAME)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    # cuddle do-while, no tabs
    add_args = ["-cdw", "-nut"] 
    
    # attempt file indent
    ret_val = indent_file(source.file_loc, harness_dir, "BSD", add_args)
    
    # set message to errors from indent if they exist and enforce penalty
    if not ret_val["errors"] is None:
        test_obj.message = ret_val["errors"]
        test_obj.score = -1 * PENALTY
    else:
        test_obj.message = "indent executed without errors"
    
    # remove the working directory if this function created it
    if made_working:
        shutil.rmtree(working_dir) 
    
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
#
# @return dictionary containing the keys, success, message, errors. 
#           success contains True if the file could be indented. 
#           message contains the indented file as a string if success is True
#           errors contains stderr output from indent command, otherwise None
#
def indent_file(source_wpath, harness_path, preset = None, arguments = None):
    if arguments is None:
        arguments = []
    
    if preset is None:
        ret_val = indent_args(source_wpath, harness_path, arguments)
    elif preset == "BSD":
        ret_val = preset_bsd(source_wpath, harness_path, arguments)
    else:
        indented = False
        message = "Invalid preset value: " + str(preset)
        error = None
        ret_val = {"success": indented, "message": message, "errors": error}
    
    return ret_val


## 
# @brief preset_bsd uses BSD (Allman) Style arguments with the indent command
# 
# @param f a file to be indented containing full path to file
# @param p is the path to the test harness directory
# @param arg_list a list of arguments to be utilized in addition to BSD args
#
# @return dictionary containing the keys, success, message, errors. 
#           success contains True if the file could be indented. 
#           message contains the indented file as a string if success is True
#           errors contains stderr output from indent command, otherwise None
#
def preset_bsd(f, p, arg_list):
    bsd_args = ["-bap", "-bli0", "-i4", "-l79", "-ncs", "-npcs", 
                 "-npsl", "-lc79", "-fc1", "-ts4"]
    for i in arg_list:
        bsd_args.append(i)
    
    return indent_args(f, p, bsd_args)


## 
# @brief indent_args uses the provided arguments when calling indent command
# 
# @param f a file to be indented containing full path to file
# @param p is the path to the test harness directory
# @param arg_list a list of arguments to be utilized
#
# @return dictionary containing the keys, success, message, errors. 
#           success contains True if the file could be indented. 
#           message contains the indented file as a string if success is True
#           errors contains stderr output from indent command, otherwise None
#
def indent_args(f, p, arg_list):
    import os
    import subprocess  
    import shutil
    from system.functions import which
    
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
    working_dir = os.path.join(p, WORKING_DIR_NAME)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    # run indent command with subprocess module
    try:
        command = ["indent"]
        for arg in arg_list:
            command.append(arg)
        command.append(f)
        
        errf = os.path.join(working_dir, "indent_errors.txt")
        with open(errf, 'w') as err_file:
            message = subprocess.check_output(command, stderr=err_file)
    except subprocess.CalledProcessError as e:
        message = e.output
    
    # determine if error messages exist
    with open(errf, 'r') as err_file:
        error = err_file.read()
    if len(error) == 0:
        error = None
    else:
        error = error.replace(f[0:f.rfind("/")+1], "").replace("indent: ", "")
        error = error.replace("\n\n", "\n")
        error = error.strip()
        
    # set the return value stating the command completed   
    indented = True
 
    # remove the working directory if this process created it
    if made_working:
        shutil.rmtree(working_dir) 
    else:
        os.remove(errf)

    return {"success": indented, "message": message, "errors": error}
