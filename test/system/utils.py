##
# @file system/utils.py
# @author Adam Koehler
# @date January 24, 2013
#
# @brief several useful functions that can be utilized in test harnesses
#

# credit to jay and harmv from stackoverflow:
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
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

def expand_all_tabs(lines, tab_size):
    "Expand all tabs in all lines provided, updates provided lines"
    
    for (i, line) in enumerate(lines):
        lines[i] = line.expandtabs(tab_size)

