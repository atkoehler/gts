## 
# @file modules/style/indentation.py
# @author Adam Koehler
# @date February 2, 2013
#
# @brief Provides class for checking indentation on a file
#

# TODO: figure out the configuration system to get this item from their
DEFAULT_SPACING = 3

class Indent:
    def __init__(self, levels = [], spacing = DEFAULT_SPACING, one_per = False):
        """
        Indentation class allows set up of lines for calculating multiple
        tests. First test that propes all curly braces are on own lines
        is a prerequisite for all indentation tests.
         
        Levels contains a list of tuples with each tuple contain three items.
        ([1, 2, 3], [1, 2, 3]...) 
            '1' is the level of indentation, level * spacing is column 0 offset
            '2' is the line number the level begins on
            '3' is a list of lines contained within the level       

        Spacing is the spacing increase per level and one_per is a boolean flag
        stating whether the one curly brace per line test was passed.
        
        """
        
        self.levels = levels
        self.spacing = spacing
        self.one_per = one_per
    
    def init_from_file(self, file_loc):
        """
        Initializes the member variables from a file. 
        
        """
        
        if not self.one_per:
            return False
        
        indeces = []
        
        # TODO implement try block
        f = open(file_loc)
        contents = f.read()
        f.close()
       
        # global level 
        level = 0
        begin = 1
        self.levels.append((level, begin, []))
        indeces.append(0)
        
        # attempt to determine the spacing per level
        spaces = self.per_level_spacing(contents)
        if spaces == 0:
            self.spacing = DEFAULT_SPACING
        else:
            self.spacing = spaces
       
        # loop over all the lines in the file splitting up levels
        file_lines = contents.split("\n")
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
            self.levels[cur][2].append(line)

            # determine if new level needs to be created
            if line.find("{") != -1:
                # create a new object for discovered level
                level = self.levels[indeces[-1]][0] + 1
                begin = i+1 #self.levels[cur][1] + self.spacing
                
                # updated lists of objects and indeces
                indeces.append(len(self.levels))
                self.levels.append((level, begin, []))
            
            # determine if end of level exists on line and haven't popped
            if line.find("}") != -1 and not popped:
                # make sure not to pop global in case of mismatch braces
                if len(indeces) > 1:
                    indeces.pop()                  
            
            popped = False
        
        return len(self.levels) != 0
    
    
    def print_levels(self):
        for level in self.levels:
            print "Contained in level", level[0], "starting at line", level[1]
            for line in level[2]:
                print line
        
    def per_level_spacing(self, contents):
        """
        Attempts to determine the spacing per indentation level from contents
        of file.read().
        
        """
        
        spacer = 0
        
        lines = contents.split("\n")
        for (i, line) in enumerate(lines):
            if line.find("{") != -1:
                if (line.lstrip().find("{") == 0):
                    first_index = line.find("{")
                else:
                    first_index = line.find(line.lstrip()[0])
               
                if line.find("}") == -1: 
                    non_blank = self.next_non_blank(lines, i+1)
                    spacer = self.indent_amount(lines, non_blank, first_index)
                    if spacer > 0:
                        break   
                    else:
                         spacer = 0
        
        return spacer
    
    def indent_amount(self, lines, i, prev_indent_amt):
        """
        Determines the indentation amount in comparison to previous amount.
        
        """
        
        if i < len(lines) and len(lines[i].strip()) > 0:
            indent_amt = lines[i].find(lines[i].strip()[0])
        else:
            indent_amt = 0
       
        return indent_amt - prev_indent_amt
    
    def next_non_blank(self, lines, i):
        """
        Acquires the index of the next non-blank line.
        
        """
        
        while i < len(lines) and len(lines[i].strip()) == 0:
            i = i + 1
        return i
    
    def one_per_level(self, file_loc):
        """
        Determines if one curly brace exists per line
        
        """
        
        bad_lines = []
        
        # TODO: implement try block
        contents = open(file_loc).read()

        # create list of line numbers where multiple braces exist
        lines = contents.split('\n')
        for (i, line) in enumerate(lines):
            if (line.count("{") > 1) or (line.count("}") > 1):
                bad_lines.append(i)
            elif (line.count("{") == 1) and (line.count("}") == 1):
                bad_lines.append(i)

        if len(bad_lines) > 0:
            self.one_per = False
        else:
            self.one_per = True
        
        return bad_lines
    
    def correct_spacing(self):
        """
        Go through the lines on each level and determine if spacing is correct.
        
        """
        
        bad_lines = []
        if self.spacing == 0 or len(self.levels) == 0:
            return (False, [])
        
        for level in self.levels:
            sp = level[0] * self.spacing
            for line in level[2]:
                if len(line.strip()) > 0 and sp != line.find(line.lstrip()[0]):
                    bad_lines.append(level[1])
           
        return (True, sorted(list(set(bad_lines))))
    

