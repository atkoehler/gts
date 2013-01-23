import re
import sys

def comment_remover(text):
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
    return re.sub(pattern, replacer, text)

def split_file(text):
    comments = []
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            comments.append(s)
            return "" 
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    noncomments = re.sub(pattern, replacer, text)
    
    return (noncomments, comments)

def extract_header(commentlist):
    header = []
    nonheader = []
    inHeader = False
    for i in commentlist:
        if i.find("BEGIN ASSIGNMENT HEADER") != -1:
            inHeader = True
            header.append(i)
            continue
        
        if i.find("END ASSIGNMENT HEADER") != -1:
            inHeader = False
            header.append(i)
            continue
        
        if inHeader:
            header.append(i)
        else:
            nonheader.append(i)
    
    return (header, nonheader)        

