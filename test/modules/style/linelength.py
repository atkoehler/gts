## 
# @file modules/style/linelength.py
# @author Adam Koehler
# @date February 4, 2013
#
# @brief Provides a checks on line length
#

# TODO: figure out the configuration system to get this item from their
DEDUCTION_PER_GAFFE = 5
LONG_LINE_COUNT = 80


## 
# @brief sub test to check whether long lines exist in the program
# 
# @param test the test part object to update with score
# @param source the source object containing name, location and content splits
#
def long_check(test, source):
    line_nums = []

    # TODO implement try block
    file = open(source.file_loc)
    contents = file.read()
    file.close()

    lines = contents.split("\n")
    for (i, line) in enumerate(lines):
        if len(line) > LONG_LINE_COUNT:
            line_nums.append(i+1)

    test.score = -1 * DEDUCTION_PER_GAFFE * len(line_nums)
    return line_nums

