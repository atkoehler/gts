# TODO: Flags should be in some sort of configuration file?
BEGIN_HDR_FLAG = "BEGIN ASSIGNMENT HEADER"
END_HDR_FLAG = "END ASSIGNMENT HEADER"
DEFAULT_SPACING = 3
MIN_SPACING = 2
MAX_SPACING = 6

class SourceFile:
    def __init__(self, file_loc="", code="", header=[], comments=[], name="", indent_size=0, style_halt=False):
        self.code = code
        self.header = header
        self.comments = comments
        self.file_loc = file_loc # code path joined with source file name
        self.name = name
        self.indent_size = indent_size
        
        # Some style checking is depending on others passing
        # This will be True if a dependent test should immediately fail
        self.style_halt = style_halt 
    
    # TODO: implement try block for opening file
    def split_file(self):
        source_file = open(self.file_loc)
        source = source_file.read()
        source_file.close()
        allcomments = []
        
        import re
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                allcomments.append(s)
                return ""
            else:
                return s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        self.code = re.sub(pattern, replacer, source)
         
        inHeader = False
        for i in allcomments:
            if i.lower().find(BEGIN_HDR_FLAG.lower()) != -1:
                inHeader = True
                self.header.append(i)
                continue
            
            if i.lower().find(END_HDR_FLAG.lower()) != -1:
                inHeader = False
                self.header.append(i)
                continue
            
            if inHeader:
                self.header.append(i)
            else:
                self.comments.append(i)
    
    # TODO: implement try block for opening file
    def comment_remover(self):
        source_file = open(self.file_loc)
        text = source_file.read()
        source_file.close()
        
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return ""
            else:
                return s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        self.code = re.sub(pattern, replacer, text)
    
    def determine_indent_size(self):
        from system.utils import expand_all_tabs
        
        # TODO: try block shouldn't return False on exception
        try:
            source_file = open(self.file_loc)
            contents = source_file.read()
            source_file.close()
        except:
            return False
        
        def indent_amount(lines, i, prev_indent_amt):
            "Determine the amount a line is indented"

            if i < len(lines) and len(lines[i].strip()) > 0:
                return lines[i].find(lines[i].strip()[0]) - prev_indent_amt
            else:
                return  -prev_indent_amt
        
        def next_nonblank(lines, i):
            "Find index of first non blank line starting at i"

            while i < len(lines) and len(lines[i].strip()) == 0:
                i = i+1
            return i
        
        self.indent_size = 0
        lines = contents.split("\n")
        expand_all_tabs(lines, DEFAULT_SPACING)
        for (i, line) in enumerate(lines):
            if line.find("{") != -1:
                if (line.lstrip().find("{") == 0):
                    first_index = line.find("{")
                else:
                    first_index = line.find(line.lstrip()[0])
                
                if line.find("}") == -1:
                    non_blank = next_nonblank(lines, i+1)
                    spacer = indent_amount(lines, non_blank, first_index)
                    if spacer >= MIN_SPACING and spacer <= MAX_SPACING:
                        self.indent_size = spacer
                        break
        
        if self.indent_size < MIN_SPACING or self.indent_size > MAX_SPACING:
            self.indent_size = DEFAULT_SPACING


