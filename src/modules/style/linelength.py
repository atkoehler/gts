## 
# @file modules/style/linelength.py
# @author Adam Koehler
# @date February 4, 2013
#
# @brief Provides a checks on line length
#

## 
# @brief sub test to check whether long lines exist in the program
# 
# @param test the test part object to update with score
# @param source the source object containing name, location and content splits
# @param max_len maximum length of a line
# @param deduction the deduction to take off per discovered problem
#
def long_check(test, source, max_len, deduction):
    from system.utils import expand_all_tabs
    
    line_nums = []
    
    # TODO implement try block
    file = open(source.file_loc)
    contents = file.read()
    file.close()

    lines = contents.split("\n")
    expand_all_tabs(lines, source.indent_size)
    for (i, line) in enumerate(lines):
        if len(line.rstrip()) > max_len:
            line_nums.append(i+1)

    test.score = -1 * deduction * len(line_nums)
    return line_nums

