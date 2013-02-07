##
# @file system/utils.py
# @author Adam Koehler
# @date January 24, 2013
#
# @brief several useful functions that can be utilized in test harnesses
#

##
# @brief grabs the full path to the system program
#
#   credit to jay and harmv from stackoverflow:
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
#
# @param program a string containing the name of program within the system
# @return the full system path to the executable of the program
#
def which(program):
    # windows compatibility
    import sys
    if sys.platform == "win32" and not program.endswith(".exe"):
        program += ".exe"
    
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    
    return None


##
# @brief expand all tabs within the provided lines using provided tab size
#
#       Changes the provided line directly instead of return new string or list
#
# @param lines a string or list of strings to expand tabs on
# @param tab_size the number of spaces to utilize when expanding tabs
#
def expand_all_tabs(lines, tab_size):
    "Expand all tabs in all lines provided, updates provided lines"
    
    # TODO: determine if lines is a list or not   
    for (i, line) in enumerate(lines):
        lines[i] = line.expandtabs(tab_size)


def check_call(*args, **kwargs):
    """
    Essentially subprocess.check_call for compatibility reasons.
    Common usage: check_call(command, stdout = file_obj, stderr = file_obj).
    
    """

    returnValue = subprocess.call(*args, **kwargs)
    if returnValue != 0:
        raise SystemError((returnValue, str(args[0])))
    else:
        return 0
