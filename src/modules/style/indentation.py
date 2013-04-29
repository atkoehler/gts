## 
# @file modules/style/indentation.py
# @author Adam Koehler
# @date February 2, 2013
#
# @brief Provides module for checking indentation and single curly per line
#

class SourceLine:
    "A source line and its associated line number in the file"
    
    def __init__(self, num = 0, content = None):
        if content is None:
            content = ""
        
        self.num = num
        self.content = content


class Block:
    """
    Simple class that contains the properties of a indentation block.
    The level is utilized the calculate the proper amount of spacing for lines
    contained within the indentation block (level * source.indent_size). Lines
    contains all the lines within this indentation block.
    """
    
    def __init__(self, level = 0, start_line = 1, lines = None):
        if lines is None:
            lines = []
        
        self.level = level
        self.start_line = start_line
        self.lines = lines
    

##
# @brief function determines if the spacing of all lines within the various
#        indentation blocks are correct. 
#
#        Currently uses the create_levels function and the one_curly_per_line
#        function as the single curly restraint is necessary at the time for
#        proper block initialization.
#
# @param test the test part object to update with score
# @param source the source object containing name, location and other members
# @param deduction the deduction to take off per discovered problem
#
# @return tuple containing True/False and list of line numbers where each
#         number is the start of an incorrectly spaced indentation block
#
def correct_indent(test, source, deduction):
    """
    Go through the lines in each level and determine if spacing is correct.
    
    """
    
    bad_lines = []

    # Verify one curly brace per line
    l = one_curly_per_line(source)

    # Correct spacing is dependent on other style tests passing
    if source.style_halt:
        return (False, [])
    
    # Create a list of indentation blocks
    (ret, blocks) = create_blocks(source)
    
    # False value indicates error in levels creation, test fails
    if not ret:
        return (False, [])
    
    for cur_block in blocks:
        sp = cur_block.level * source.indent_size
        for (i, line) in enumerate(cur_block.lines):
            strip_len = len(line.content.strip())
            if strip_len > 0:
                indent_amount = line.content.find(line.content.lstrip()[0])
                if sp != indent_amount:
                    if i-1 >= 0:
                        prev = cur_block.lines[i-1].content
                        if not (prev.strip() == "{" or prev.strip() == "}"):
                            if prev.find(";") == -1:
                                if sp+source.indent_size != indent_amount:
                                    bad_lines.append(line.num)
                            else:
                                bad_lines.append(line.num)
                        else:
                            bad_lines.append(line.num)
                    else:
                        bad_lines.append(line.num)
    
    # test completed and return list of incorrectly indented lines
    bad_l = sorted(list(set(bad_lines)))
    test.score = -1 * deduction * len(bad_l)
    return (True, bad_l)


##
# @brief create a list of indentation Block objects from source
#
# @param source the source object containing name, location and other members
# @return a list of levels as defined in the expanded brief
#    
def create_blocks(source):
    """
    Create a list of levels, each level contains all lines in file for that
    level indentation block. 
    
    """
    from system.utils import expand_all_tabs
     
    # Indentation is dependent on other the absence of other style problems
    if source.style_halt:
        return (False, [])
    
    indeces = []
    blocks = []
    
    # TODO implement try block
    f = open(source.file_loc)
    contents = f.read()
    f.close()
   
    # global level 
    level = 0
    begin = 1
    blocks.append(Block(level, begin))
    indeces.append(0)
    
     
    # loop over all the lines in the file splitting up levels
    file_lines = contents.split("\n")
    expand_all_tabs(file_lines, source.indent_size)
    for (i, line) in enumerate(file_lines):
        # determine if end of level exists on line
        if line.find("}") != -1:
            # make sure not to pop global off in case of mismatch braces
            if len(indeces) > 1:
                # only pop if belong within indent level one up
                if line.lstrip().find("}") == 0:
                    indeces.pop()
                    popped = True

        # add line to current level
        cur = indeces[-1]
        blocks[cur].lines.append(SourceLine(i+1, line))

        # determine if new level needs to be created
        if line.find("{") != -1:
            # create a new object for discovered level
            level = blocks[cur].level + 1
            begin = i+1 
            
            # update lists of tuples and indeces
            indeces.append(len(blocks))
            blocks.append(Block(level, begin))
        
        # determine if end of level exists on line and haven't popped
        if line.find("}") != -1 and not popped:
            # make sure not to pop global in case of mismatch braces
            if len(indeces) > 1:
                indeces.pop()                  
        
        popped = False
    
    return (len(blocks) != 0, blocks)

    
def one_curly_per_line(source, test=None, deduction=0):
    """
    Determines if one curly brace exists per line
    
    """
    
    bad_lines = []
    
    # TODO: implement try block
    contents = open(source.file_loc).read()

    # create list of line numbers where multiple braces exist
    lines = contents.split('\n')
    for (i, line) in enumerate(lines):
        num_braces = line.count("{") + line.count("}")
        if num_braces > 1:
            bad_lines.append(i)
   
    # not having a single curly per line halts certain style checks 
    if len(bad_lines) > 0:
        source.style_halt = True
    
    if test is not None:    
        test.score = -1 * deduction * len(bad_lines)
    return bad_lines


