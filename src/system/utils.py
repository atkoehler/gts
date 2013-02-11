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
    "Essentially subprocess.check_call for compatibility reasons."
    
    import subprocess
    returnValue = subprocess.call(*args, **kwargs)
    if returnValue != 0:
        raise SystemError((returnValue, str(args[0])))
    else:
        return 0

def markup_convert_newline(line):
    "Convert solitary newlines in string to markup format"
    
    line_split = line.split('\n')
    for (i, ind_line) in enumerate(line_split):
        if len(ind_line) > 0:
            if i+1 < len(line_split) and len(line_split[i+1]):
                line_split[i] = ind_line + "  "
    
    return "\n".join(line_split)

def markup_create_header(line, level):
    "Turn the line into a header by inserting proper markdown based on level"
    
    header = "#" * level + " "
    return header + line

def markup_create_indent(line, level):
    "Indent the line by inserting proper markdown based on level"
    
    if line.find('\n') == -1 or line.find('\n') == (len(line) - 1):
        return "> " * level + line
    else:
        lines = line.split('\n')
        for (i, l) in enumerate(lines):
            lines[i] = "> " * level + l
        line = "\n".join(lines)
        return line

def markup_create_unlist(lines):
    "Turn the list of lines into a markdown list"
    
    for (i, line) in enumerate(lines):
        lines[i] = "* " + line

    return "\n".join(lines)

