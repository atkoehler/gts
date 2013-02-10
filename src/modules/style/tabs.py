## 
# @file modules/style/tabs.py
# @author Adam Koehler
# @date February 5, 2013
#
# @brief Provides check for tab characters within code (instead of spaces)
#

# TODO: figure out the configuration system to get this item from their
DEDUCTION_PER_GAFFE = 5


## 
# @brief sub test to check whether tabs exist in code as we always use spaces
#
# @param test the test part object to update with score
# @param source the source object containing name, location and content splits
# 
# @return a list contain the lines file that contain at least one tab character
#
def find_tabs(test, source):
    line_nums = []
    
    # TODO implement try block
    file = open(source.file_loc)
    contents = file.read()
    file.close()

    lines = contents.split("\n")
    for (i, line) in enumerate(lines):
        # determine if a tab exists on the line
        if line.find('\t') != -1:
            line_nums.append(i+1) 
    
    test.score = -1 * DEDUCTION_PER_GAFFE * len(line_nums)
    return line_nums

