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



def markup_convert_newline(line):
    "Convert solitary newlines in string to markup format"
    
    line_split = line.split('\n')
    for (i, ind_line) in enumerate(line_split):
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

def markup_create_bold(line):
    "Turn the line into markdown emboldened string"
    
    return "**" + line + "**" 

def markup_create_italic(line):
    "Turn the line into markdown italicized string"
    
    return "*" + line + "*" 

def markup_create_codeblock(text):
    "Place 5 spaces in the front of each line in text, to get pre effect"
     
    if text.find('\n') == -1 or text.find('\n') == (len(text) - 1):
        return " " * 5 + text
    else:
        lines = text.split('\n')
        for (i, line) in enumerate(lines):
            lines[i] = " " * 5 + line
        return "\n".join(lines)

def markup_create_inlinecode(word):
    "Create an inline code block using back ticks for markup reading"
        
    return "`` " + word + " ``" 

def markup_create_link(text, url):
    "Create a link using markdown syntax with the specified text-url combo"
        
    return "[" + text + "](" + url + ")"


def insert_blanks(text):
    "Insert newline after each list item or if not list after every newline"
    
    if isinstance(text, list):
        for (i, line) in enumerate(text):    
           text[i] = line + "\n"
        return text
    else: 
        return text.replace("\n", "\n\n")

