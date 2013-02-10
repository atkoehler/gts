## 
# @file modules/altersource.py
# @author Adam Koehler
# @date February 8, 2013
#
# @brief Provides the means to alter the source code of a file
#


## 
# @brief replace_source changes all instances of a string to  
#        a different string
# 
# @param lines a list of lines to search for string
# @param look_for the string to search for
# @param replace_with the string to serve as replacement
# @param count if set, the first count instances of look_for will be replaced
#
# @return True if replace succeeded, otherwise False
#
def replace_source(lines, look_for, replace_with, count = -1):
    n = 0
    for (i, line) in enumerate(lines):
        if count != -1 and n >= count:
            break
        if line != line.replace(look_for, replace_with):
            lines[i] = line.replace(look_for, replace_with)
            n = n + 1
    
    if (count == -1 and n > 0) or (count != -1 and n == count):
        return True
    else:
        return False

