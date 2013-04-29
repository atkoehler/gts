# TODO: Flags should be in some sort of configuration file?

class SourceFile:
    def __init__(self, file_loc="", code="", header=[], comments=[], name="", extension="", indent_size=0, style_halt=False):
        self.code = code
        self.header = header
        self.comments = comments
        self.file_loc = file_loc # code path joined with source file name
        self.name = name
        self.extension = extension
        self.indent_size = indent_size
        
        # Some style checking is depending on others passing
        # This will be True if a dependent test should immediately fail
        self.style_halt = style_halt 
    
    ##
    #   @brief split the file in pieces: header, comments and code
    #   @param hdr_begin the string to signal assessment header start
    #   @param hdr_end the string to signal assessment header end
    #
    def split_file(self, hdr_begin, hdr_end):
        def fix_ctrlm(file_loc):
            contents = open(file_loc, 'rb').read()
            s = contents.replace("\r\n", "\n")
            if -1 != s.find("\r"):
                s = contents.replace("\r", "\n")
            open(file_loc, 'wb+').write(s)
        
        # TODO: implement try block for opening file
        fix_ctrlm(self.file_loc)
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
            if i.decode('utf-8').lower().find(hdr_begin.lower()) != -1:
                inHeader = True
                self.header.append(i)
                continue
            
            if i.decode('utf-8').lower().find(hdr_end.lower()) != -1:
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
    
    ##
    #   @brief attempt to determine the indentation block size utilized
    #   @param default the default spacing to utilize if nothing good is found
    #   @param min the minimum amount of spaces allowed for 1 indent level
    #   @param max the maximum amount of spaces allowed for 1 indent level
    #
    def determine_indent_size(self, default, min, max):
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
        expand_all_tabs(lines, default)
        for (i, line) in enumerate(lines):
            if line.find("{") != -1:
                if (line.lstrip().find("{") == 0):
                    first_index = line.find("{")
                else:
                    first_index = line.find(line.lstrip()[0])
                
                if line.find("}") == -1:
                    non_blank = next_nonblank(lines, i+1)
                    spacer = indent_amount(lines, non_blank, first_index)
                    if spacer >= min and spacer <= max:
                        self.indent_size = spacer
                        break
        
        if self.indent_size < min or self.indent_size > max:
            self.indent_size = default


    

