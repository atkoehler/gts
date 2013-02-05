## 
# @file modules/style/conditionals.py
# @author Adam Koehler
# @date February 4, 2013
#
# @brief Provides checks such as checking for "== true"
#

# TODO: figure out the configuration system to get this item from their
DEDUCTION_PER_GAFFE = 5


## 
# @brief sub test to check whether improper conditionals exist
#
#       Improper conditions are "x == true", "true == x", 
#       "x == false", "false == x".
# 
# @param test the test part object to update with score
# @param source the source object containing name, location and content splits
#
# @return a list containing line numbers in file that have improper conditional
#
def improper_bool(test, source):
    line_nums = []
    improper = ["== true", "true ==", "== false", "false =="]
    
    # TODO implement try block
    file = open(source.file_loc)
    contents = file.read()
    file.close()

    lines = contents.split("\n")
    for (i, line) in enumerate(lines):
        found_improper = False
        
        # determine if line number contains an improper condition
        for cond in improper:
            if line.replace(" ", "").find(cond.replace(" ", "")) != -1:
                found_improper = True
                break
        
        # add line number of improper conditional expression
        if found_improper:
            line_nums.append(i+1)
        
    
    test.score = -1 * DEDUCTION_PER_GAFFE * len(line_nums)
    return line_nums

