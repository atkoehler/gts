## 
# @file assessment/madlibs.py
# @author Adam Koehler
# @date April 5, 2013
#
# @brief Provides tests specific to madlibs assignment in various functions
#


from system.utils import *
from system.procs import *
from galah.interact import *
import os

##
# @brief Test to run all the tests specific to madlibs assignment
#
# @param locations tuple (location of code, location of harness)
# @param result the Galah result to add tests to
# @param vars the dictionary of variables for the madlibs test from config JSON
# @param source the object containing all info for the source file
# @param env the environment dictrionary from config JSON
#
def test(locations, result, vars, source, env):
    from modules.compilation import compile_single
    import copy
    import shutil
     
    # files to remove on finish
    files_to_remove = []
    
    harness_dir = locations[1]

    # set up working area
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    # set up exe path for compilation
    exe_path = os.path.join(working_dir, env["exe_name"])
    files_to_remove.append(exe_path)

    # set up path for inputs
    in_path = os.path.join(working_dir, "input_file.txt")
    files_to_remove.append(in_path)

    # set up path for output
    out_path = os.path.join(working_dir, "program_output.txt")
    files_to_remove.append(out_path)

    
    # compile the program
    ret_val = compile_single(source.file_loc, exe_path, harness_dir, env)
    
    # grab / generate items specific to this test
    ins = genIntStrings(100, vars["input_length"], vars["input_seed"])
    with open(in_path, 'w+') as inFile:
        for i in ins:
            inFile.write(i + "\n")
    
    if ret_val["success"]:
        # execute the program grabbing its output
        try:
            t = Task(env["timeout"])
            with open(out_path, 'w') as outFile:
                with open(in_path, 'r') as inFile:
                    t.check_call([exe_path], stdout=outFile, stdin=inFile)
            notification = ""
        except:
            notification = "Program did not execute to completion.\n"
            notification = markup_create_bold(notification)
            notification = markup_create_indent(notification, 1)
        
        # acquire the story portion of the output
        storyOutput = getStory(out_path, vars["separator"],
                               vars["separator_size"])
        
        # run individual tests on the story output
        ind_test = "Inputs Utilized"
        if ind_test in vars:
            t = GalahTest()
            t.name = ind_test
            t.max_score = vars[ind_test]["max_score"] 
            test_vars = copy.deepcopy(vars[ind_test])
            inputsUsed(t, test_vars, storyOutput, in_path)
            t.message = notification + t.message
            result.add_test(t)

        ind_test = "Paragraph Count"
        if ind_test in vars:
            t = GalahTest()
            t.name = ind_test
            t.max_score = vars[ind_test]["max_score"] 
            test_vars = copy.deepcopy(vars[ind_test])
            paragraphCount(t, test_vars, storyOutput)
            t.message = notification + t.message
            result.add_test(t)

        ind_test = "Formatting Check"
        if ind_test in vars:
            t = GalahTest()
            t.name = ind_test
            t.max_score = vars[ind_test]["max_score"] 
            test_vars = copy.deepcopy(vars[ind_test])
            formattingCheck(t, test_vars, storyOutput, env)
            t.message = notification + t.message
            result.add_test(t)
    else:
        # Did not compile
        ind_test = "Inputs Utilized"
        if ind_test in vars:
            t = GalahTest()
            t.name = ind_test
            t.max_score = vars[ind_test]["max_score"] 
            m = "Could not run test due to comiplation failure."       
            t.message = markup_create_indent(m, 1)
            result.add_test(t)
        
        ind_test = "Paragraph Count"
        if ind_test in vars:
            t = GalahTest()
            t.name = ind_test
            t.max_score = vars[ind_test]["max_score"] 
            m = "Could not run test due to comiplation failure."       
            t.message = markup_create_indent(m, 1)
            result.add_test(t)
 
        ind_test = "Formatting Check"
        if ind_test in vars:
            t = GalahTest()
            t.name = ind_test
            t.max_score = vars[ind_test]["max_score"] 
            m = "Could not run test due to comiplation failure."       
            t.message = markup_create_indent(m, 1)
            result.add_test(t)  
        
    # remove the working directory if made it
    if made_working:
        shutil.rmtree(working_dir)    
    elif os.path.isfile(exe_path):
        for f in files_to_remove:
            os.remove(f)


 
##
# @brief Test for the minimum number of paragraphs in story
#
# @param test the test object containing properties to fill out
# @param vars the dictionary of variables for the test from config JSON
# @param storyOutput string containing all the story output (file.read())
#
def paragraphCount(test, vars, storyOutput):
    if len(storyOutput) == 0:
        test.score = 0
        m = "Did not find any story output, cannot count paragraphs. "
        m += "If you expected to have story output, make sure you are "
        m += "outputting a blank line after each question and just prior to "
        m += "the ruler line that denotes the beginning of the story.\n"
        m = markup_create_indent(m, 1)
        test.message = m
        return

    storyLines = storyOutput.strip().split("\n")

    expected_lines = vars["min_paragraphs"] + vars["min_paragraphs"] - 1
    if len(storyLines) < expected_lines:
        if len(storyLines) == 1:
            word = "line"
        else:
            word = "lines"
        
        test.score = 0
        m = "Expected " + str(expected_lines) + " but only found "
        m += str(len(storyLines)) + " " + word + " of story output."
        m = markup_create_indent(m, 1)
        test.message = m
        return
    
    paragraphStart = []
    badParagraph = []  
    inParagraph = False
    sentenceCount = 0
    paragraphCount = 0
    for (i, line) in enumerate(storyLines):
        # determine if current line has any sentence endings
        for word in line.split(" "):
            if word.endswith(".") or word.endswith("!") or word.endswith("?"):
                sentenceCount += 1
   
        # are we at the end of a paragraph
        if len(line.strip()) == 0 or line == storyLines[-1]:
            if inParagraph and sentenceCount >= vars["min_sentences"]:
                paragraphCount += 1
            elif inParagraph and sentenceCount < vars["min_sentences"]:
                badParagraph.append(paragraphStart[-1])
            inParagraph = False
            sentenceCount = 0
            continue
        
        # characters exist on the line and we should start a new paragraph
        if not inParagraph and len(line.strip()) > 0:
            paragraphStart.append(i+1)
            inParagraph = True
        
    # give feedback message if bad paragraphs exist, regardless of score 
    if len(badParagraph) > 0:
        if len(badParagraph) == 1:
            bad_pars = "paragraph"
            lines_word = "line"
        else:
            bad_pars = "paragraphs"
            lines_word = "lines"
        
        if paragraphCount == 1:
            good_pars = "paragraph"            
        else:
            good_pars = "paragraphs"
            
        
        # put the lines into a string
        lines = ""
        for (i, line_num) in enumerate(badParagraph):
            lines += str(line_num)
            if i+1 < len(badParagraph) and i > 0:
                lines += ", "
        
        m = "Discovered " + str(paragraphCount) + " proper " + good_pars + ". "
        m += " Also discovered " + str(len(badParagraph)) + " bad "
        m += bad_pars + ". To be proper, paragraphs must have at least " 
        m += str(vars["min_sentences"])
        m += " sentences. The " + str(len(badParagraph)) + " bad " + bad_pars
        m += " starting at " + lines_word + " " + lines + " "
        m += "of your story did not meet this minimum requisite. A sentence "
        m += "cannot be counted if the punctuation is not followed by a space."

        m = markup_create_indent(m, 1)
        test.message = m
    
    # Determine score
    test.score = vars["max_score"] * paragraphCount / vars["min_paragraphs"]
    
    # Do not allow more than the max possible points
    if test.score > vars["max_score"]:
        test.score = vars["max_score"]


##
# @brief Test for the minimum number of inputs utilized in story
#
# @param test the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
# @param storyOutput string containing all the story output (file.read())
# @param inFile the path to file containing all the inputs possibly utilized
#
def inputsUsed(test, vars, storyOutput, inFile):
    allInputs = open(inFile).read().strip().split("\n")
   
    if len(storyOutput) == 0:
        test.score = 0
        m = "Did not find any story output, cannot check for input usage. "
        m += "If you expected to have story output, make sure you are "
        m += "outputting a blank line after each question and just prior to "
        m += "the ruler line that denotes the beginning of the story.\n"
        m = markup_create_indent(m, 1)
        test.message = m
        return
 
    inputsDiscovered = 0
    for input in allInputs:
        if storyOutput.find(input) != -1:
            inputsDiscovered = inputsDiscovered + 1
    
    # give feedback if minimum was not met
    if inputsDiscovered < vars["min_inputs"]:
        if inputsDiscovered == 1:
            input_word = "input"
        else:
            input_word = "inputs"
        
        m = "Discovered " + str(inputsDiscovered) + " inputs utilized in "
        m += "story. The minimum number of inputs acquired and used is "
        m += str(vars["min_inputs"]) + ". Make sure you are acquiring at "
        m += "least that many inputs as well as utilizing at least that many "
        m += "inputs."
        
        m = markup_create_indent(m, 1)
        test.message = m
   
     
    test.score = vars["max_score"] * inputsDiscovered / vars["min_inputs"]
    
    # Do not allow more than the max possible points
    if test.score > vars["max_score"]:
        test.score = vars["max_score"]


##
# @brief Check the formatting of the story
#
#       Checks whether lines are too long or too short, meaning two words
#       from the following line could have fit on the current one.
#
# @param test the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
# @param storyOutput string containing all the story output (file.read())
# @param env the environment dictrionary from config JSON
#
def formattingCheck(test, vars, storyOutput, env):
    if len(storyOutput) == 0:
        test.score = 0
        m = "Did not find any story output, cannot check formatting. "
        m += "If you expected to have story output, make sure you are "
        m += "outputting a blank line after each question and just prior to "
        m += "the ruler line that denotes the beginning of the story.\n"
        m = markup_create_indent(m, 1)
        test.message = m
        return
    
    storyLines = storyOutput.strip().split("\n")
    longLines = []
    shortLines = []
    messages = []

    expected_lines = vars["min_paragraphs"] + vars["min_paragraphs"] - 1
    if len(storyLines) < expected_lines:
        if len(storyLines) == 1:
            word = "line"
        else:
            word = "lines"
        test.score = 0
        m = "Expected " + str(expected_lines) + " but only found "
        m += str(len(storyLines)) + " " + word + " of story output."
        m = markup_create_indent(m, 1)
        test.message = m
        return
   
    # Expand tab characters in the story to four spaces
    expand_all_tabs(storyLines, 4)
        
    # Check for long lines
    for (i, line) in enumerate(storyLines):
        if len(line.strip()) == 0:
            continue
        if len(line.rstrip()) > vars["max_length"]:
            longLines.append(i+1)
    
    # Check for short lines
    allowance = vars["shortline_word_allowance"]
    for (i, line) in enumerate(storyLines):
        if len(line.strip()) == 0:
            continue
        curLen = len(line.rstrip())
        if i+1 < len(storyLines):
            nextLen = len(" ".join(storyLines[i+1].split()[0:(allowance+1)]))
            if nextLen > 0 and (curLen + nextLen + 1) <= vars["max_length"]:
                shortLines.append(i+1)       
  
    # Present feedback to the user if long lines existed     
    if len(longLines) > 0:
        if len(longLines) == 1:
            line_word = "line"
        else:
            line_word = "lines"
        
        # put the lines into a string
        lines_list = ""
        for (i, line_num) in enumerate(longLines):
            if i+1 < len(longLines) and i > 0:
                lines_list += ", "
            
            if i+1 == len(longLines) and len(longLines) > 1:
                lines_list += " and " + str(line_num)
            else:
                lines_list += str(line_num)
        
        header = "Long Lines\n"
        header = markup_create_header(header, 3)
        header = markup_create_indent(header, 1)
        m = "Discovered " + str(len(longLines)) + " long " + line_word + " on "
        m += line_word + " " + lines_list + " of your story. "
        m += "If a line is long then it went past the maximum of "
        m += str(vars["max_length"]) + " characters for that line."
        m = markup_create_indent(m, 2)
        messages.append(header + m)
 
    # Present feedback to the user if short lines existed     
    if len(shortLines) > 0:
        if len(shortLines) == 1:
            line_word = "line"
        else:
            line_word = "lines"
        
        # put the lines into a string
        lines_list = ""
        for (i, line_num) in enumerate(shortLines):
            if i+1 < len(shortLines) and i > 0:
                lines_list += ", "
            
            if i+1 == len(shortLines) and len(shortLines) > 1:
                lines_list += " and " + str(line_num)
            else:
                lines_list += str(line_num)
        
        header = "Short Lines\n"
        header = markup_create_header(header, 3)
        header = markup_create_indent(header, 1)
        m = "Discovered " + str(len(shortLines)) + " short " + line_word 
        m += " on " + line_word + " " + lines_list + " of your story. "
        m += "If a line is short then at least one word on the line below "
        m += "it could have fit without going over " + str(vars["max_length"]) 
        m += " character limit for a single line."
        m = markup_create_indent(m, 2)
        messages.append(header + m) 

    if len(storyOutput) > 0 and (len(longLines) > 0 or len(shortLines) > 0): 
        header = "Story's Output\n"
        header = markup_create_header(header, 3)
        header = markup_create_indent(header, 1)
        m = markup_create_indent(markup_create_codeblock(storyOutput), 2)
        user_story = header + "\n<small>\n" + m + "\n</small>\n"

    # Place any feedback messages into the test's message    
    if len(messages) > 0:
        potential = user_story + "\n".join(messages)
        if len(potential) < env["max_message_size"]:
            test.message = potential
        else:
            test.message = "\n".join(messages)
    
    # Determine score - simply pass / fail
    if len(shortLines) == 0 and len(longLines) == 0:
        test.score = vars["max_score"]
    elif len(shortLines) + len(longLines) == 1:
        test.score = vars["max_score"] / 2
    else:
        test.score = 0


##
# @brief break off the story output from any other output
# 
# @param outputFile path to file containing all output from program execution
# @param separator the character used as a separator
# @param the size of the separation string
#
def getStory(outputFile, separator, separator_size):
    separatorString = separator * separator_size
    output = open(outputFile).read().split("\n")
    
    storyLines = []
    storyBegan = False
    for line in output:
        if storyBegan and separatorString == line.decode('utf-8').strip():
            break
        if storyBegan:
            storyLines.append(line)
        if separatorString == line.decode('utf-8').strip():
            storyBegan = True  
   
    if len(storyLines) == 0:
        return []
    else: 
        return "\n".join(storyLines)

##
# @brief generate N random strings of size m, utilizing digits 0 through 9
# 
# @param N number of random numbers to generate
# @param m the number of digits each input number should have
# @param minimum the lowest possible random number
# @param maximum the highest possible random number
# @param s the seed for the random number generator to start at
#
# @return a list of size N containing randomly generated numbers in range
#
def genIntStrings(N, m, s):
    import random
    
    random.seed(s)
    
    nums = []
    for i in range(N):
        cur = ""
        for j in range(m):
            cur += str(random.randint(0,9))
        nums.append(cur)
    
    return nums

