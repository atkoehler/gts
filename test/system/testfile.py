# TODO: Flags should be in some sort of configuration file?
BEGIN_HDR_FLAG = "BEGIN ASSIGNMENT HEADER"
END_HDR_FLAG = "END ASSIGNMENT HEADER"

class SourceFile:
    def __init__(self, file_loc="", code="", header=[], comments=[], name=""):
        self.code = code
        self.header = header
        self.comments = comments
        self.file_loc = file_loc # code path joined with source file name
        self.name = name
    
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
    

