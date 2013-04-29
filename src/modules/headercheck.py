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
#   whether the lines that signal beginning and ending of the assesment 
#   header exist.
#

from galah.interact import *
from system.utils import *

## 
# @brief the header check module is composed of several parts that verify
#        the assessment header exists and is properly filled in
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param vars the dictionary of yyvariables for the test from conifuration JSON
# @param source the source object containing name, location and content splits
#
# @return 0 if test completed, otherwise -1
#
# @precondition the source contents have been split into source object fields
#
def test(locations, test_obj, vars, source, submission):
    OK = 0
    ERROR = -1

        
    # failed to located header on split of source
    if len(source.header) == 0:
        header_link = markup_create_link("Header Example", 
                                         vars["header_example"])
        m = "A proper assessment header is expected for each submission. "
        m += "Please utilize our " + header_link + " as a guide.\n\n"
        test_obj.score = -1 * vars["penalty"]
        test_obj.message = m + "Header not found: Either it does not exist or the test harness could not find " + markup_create_italic(vars["begin_flag"]) + " line. If you believe you have a proper header, please also verify that you submitted a proper C++ source file."
        return OK
    
    # loop over parts of header and run specific sub tests
    found_end = found_begin = False
    tags = {}
    tags[vars["author_tag"]] = False
    tags[vars["plagiarism_tag"]] = False

    messages = []
    for (i, line) in enumerate(source.header):
        # author email check
        if line.decode('utf-8').lower().find(vars["author_tag"].lower()) != -1:
            if not verify_email(submission["user"], line, vars):
                m = "Email in author line does not match submission email"
                test_obj.score = -1 * vars["penalty"]
                messages.append(m)
                tags[vars["author_tag"]] = True
            else:
                tags[vars["author_tag"]] = True
        
         
        # anti-plagiarism lines check
        if line.decode('utf-8').lower().find(vars["plagiarism_tag"].lower()) != -1:
            if i+1 >= len(source.header):
                m = "Could not find anti-plagiarism lines"
                test_obj.score = -1 * vars["penalty"]
                messages.append(m)
            else:
                if i+2 < len(source.header):
                    plag_lines = [source.header[i+1], source.header[i+2]]
                else:
                    plag_lines = [source.header[i+1]]
                if not check_plagiarism(plag_lines, vars):
                    m = "Incorrect wording for anti-plagiarism lines"
                    test_obj.score = -1 * vars["penalty"]
                    messages.append(m)
                    tags[vars["plagiarism_tag"]] = True
                else:
                    tags[vars["plagiarism_tag"]] = True
        
            
        # flags for beginning and ending of assessment header 
        if line.decode('utf-8').lower().find(vars["begin_flag"].lower()) != -1:
            found_begin = True
        
        if line.decode('utf-8').lower().find(vars["end_flag"].lower()) != -1:
            found_end = True

    # assessment header begin line        
    if not found_begin:
        test_obj.score = -1 * vars["penalty"]
        m = "Did not find " + markup_create_italic(vars["begin_flag"]) + " line in the assessment header."
        messages.append(m)
    
    # assessment header end line        
    if not found_end:
        test_obj.score = -1 * vars["penalty"]
        m = "Did not find " + markup_create_italic(vars["end_flag"]) + " line in the assessment header."
        messages.append(m)
    
    if not tags[vars["author_tag"]]:
        test_obj.score = -1 * vars["penalty"]
        m = "Did not find " + markup_create_italic(vars["author_tag"])
        m + " anywhere in the assessment header."
        messages.append(m)

    if not tags[vars["plagiarism_tag"]]:
        test_obj.score = -1 * vars["penalty"]
        m = "Did not find " + markup_create_italic(vars["plagiarism_tag"])
        m += " anywhere in the assessment header or the plagiarism section has "
        m += "an improper layout of its contents."
        messages.append(m)


    if len(messages) > 0:
        header_link = markup_create_link("Header Example", 
                                         vars["header_example"])
        m = "A proper assessment header is expected for each submission. "
        m += "Please utilize our " + header_link + " as a guide.\n\n"
        test_obj.message = m + markup_create_unlist(messages)
     
    return OK


## 
# @brief sub test for the header check to verify email in header against the
#        the email of the submitter
# 
# @param email the email from the submission object provided to test harness
# @param line the line in header to acquire an email from use for comparison
# @param vars the dictionary of yyvariables for the test from conifuration JSON
#
# @return True if the emails match, otherwise False
#
def verify_email(email, line, vars):
    line_email = ""
    
    # attempt to discover email using @ symbol
    fields = line.decode('utf-8').lower().split()
    for val in fields:
        if val.find(vars["author_tag"].lower()) == -1 and val.find("@") != -1:
            line_email = val.replace("[","").replace("]","").replace("<","").replace(">","").strip()
        
    return line_email.lower() == email.lower()


## 
# @brief sub test for the header check to verify contents of the 
#        anti-plagiarism lines
# 
# @param lines a list of lines in the header that contain anti-plagiarism lines
# @param vars the dictionary of yyvariables for the test from conifuration JSON
#
# @return True if the anti-plagiarism wording matches, otherwise False
#
def check_plagiarism(lines, vars):
    for (i, line) in enumerate(lines):
        lines[i] = line.decode('utf-8').replace("/","").lstrip().rstrip()
    check_line = " ".join(lines)

    return check_line.lower() == vars["plagiarism_quote"].lower()


