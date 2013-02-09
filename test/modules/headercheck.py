## 
# @file modules/headercheck.py
# @author Adam Koehler
# @date January 24, 2013
#
# @brief this module provides the means to check the header of source file
#        the header is standardized using doxygen tags
#
#   This module checks three things. First, it verifies the author's email on 
#   the @author line against the email of the submitter. Second, it checks the 
#   existence and wording of the anti-plagiarism lines. Lastly, it checks 
#   whether the lines that signal beginning and ending of the assignment 
#   header exist.
#

# TODO: these should possibly come from some configuration file
PENALTY = 25
AUTHOR_TAG = "@author"
PLAGIARISM_TAG = "@par Plagiarism Section"
PLAGIARISM_LINE = "I hereby certify that the code in this file is ENTIRELY my own original work."
BEGIN_HDR_FLAG = "BEGIN ASSIGNMENT HEADER"
END_HDR_FLAG = "END ASSIGNMENT HEADER"


from galah.interact import *

## 
# @brief the header check module is composed of several parts that verify
#        the assignment header exists and is properly filled in
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param source the source object containing name, location and content splits
#
# @return 0 if test completed, otherwise -1
#
# @precondition the source contents have been split into source object fields
#
def test(locations, test_obj, source, submission):
    OK = 0
    ERROR = -1

        
    # failed to located header on split of source
    if len(source.header) == 0:
        test_obj.score = -1 * PENALTY
        test_obj.message = "Header not found: Either it does not exist or the test harness could not find begin header line."
        return OK
    
    # loop over parts of header and run specific sub tests
    found_end = found_begin = False
    messages = []
    for (i, line) in enumerate(source.header):
        # author email check
        if line.lower().find(AUTHOR_TAG.lower()) != -1:
            if not verify_email(submission["user"], line):
                m = "Email in author line does not match submission email"
                test_obj.score = -1 * PENALTY
                messages.append(m)
        
         
        # anti-plagiarism lines check
        if line.lower().find(PLAGIARISM_TAG.lower()) != -1:
            if i+2 >= len(source.header):
                m = "Could not find anti-plagiarism lines"
                test_obj.score = -1 * PENALTY
                messages.append(m)
            else:
                plag_lines = [source.header[i+1], source.header[i+2]]
                if not check_plagiarism(plag_lines):
                    m = "Incorrect wording for anti-plagiarism lines"
                    test_obj.score = -1 * PENALTY
                    messages.append(m)
        
            
        # flags for beginning and ending of assignment header 
        if line.lower().find(BEGIN_HDR_FLAG.lower()) != -1:
            found_begin = True
        
        if line.lower().find(END_HDR_FLAG.lower()) != -1:
            found_end = True

    # assignment header begin line        
    if not found_begin:
        test_obj.score = -1 * PENALTY
        m = "Did not find begin assignment header line the assignment header."
        messages.append(m)
    
    # assignment header end line        
    if not found_end:
        test_obj.score = -1 * PENALTY
        m = "Did not find end assignment header line the assignment header."
        messages.append(m)
   
    if len(messages) > 0:
        test_obj.message = "\n".join(messages)
     
    return OK


## 
# @brief sub test for the header check to verify email in header against the
#        the email of the submitter
# 
# @param email the email from the submission object provided to test harness
# @param line the line in header to acquire an email from use for comparison
#
# @return True if the emails match, otherwise False
#
def verify_email(email, line):
    line_email = ""
    
    # attempt to discover email using @ symbol
    fields = line.lower().split()
    for val in fields:
        if val.find(AUTHOR_TAG.lower()) == -1 and val.find("@") != -1:
            line_email = val.replace("[","").replace("]","").replace("<","").replace(">","")
        
    return line_email.lower() == email.lower()


## 
# @brief sub test for the header check to verify contents of the 
#        anti-plagiarism lines
# 
# @param lines a list of lines in the header that contain anti-plagiarism lines
#
# @return True if the anti-plagiarism wording matches, otherwise False
#
def check_plagiarism(lines):
    for (i, line) in enumerate(lines):
        lines[i] = line.replace("/","").lstrip().rstrip()
    check_line = " ".join(lines)
    
    return check_line.lower() == PLAGIARISM_LINE.lower()


