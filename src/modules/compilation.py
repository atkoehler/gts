## 
# @file compilation.py
# @author Adam Koehler
# @date November 4, 2012
#
# @brief this module provides the means to compile a single or series
#        of files with or without a makefile.
#
#        the module returns a tuple of length 2 containing a binary
#        value representing compilation success and any messages
#        attached to compilation for feedback such as error messages
#

# TODO: figure out the configuration system, to hold these values
# TODO: once complete, utilize import or whatever is needed
TYPE = ".cpp"
COMPILER = "g++"

# TODO: split non-makefile and makefile compilation into functions

## 
# @brief the compilation module compiles a single or series of files
# 
# @precondition if an includes directory is used, the files must exist 
#               in that directory or within an immediate sub-directory 
#
# @param locations tuple (location of files, working dir[, includes dir])
# @param makefile boolean, defaults to False, should makefile be used
# @param rmexe boolean, defaults to True, should executable be deleted
#
# @return a tuple with two values. The first is the boolean of whether the 
#          file compiled successfully. The second is a list of strings to 
#          print to feedback: either errors or successful compilation.
def compile(locations, rmexe=True, makefile=False):
    
    # need for os specific calls such 
    import os
    
    # for string replace
    import string
    
    # working directory location
    working_dir = locations[1]
    
    # testing executable
    test_program = working_dir + "/test_program"
    
    # compiler errors file
    compile_err = working_dir + "/compile.err"
    
    # remove command
    remove_str = "rm"
    
    # initial value for compilation (assume failure)
    compile_return = 1
    
    
    # Formulate the linux command line call
    if makefile == False:
        # determine all the files to compile
        file_loc = locations[0]
        
        # append ending slash if needed
        if file_loc[-1] != "/":
            file_loc = file_loc + "/"
        
        compile_str = COMPILER + " -o " + test_program + " "
       
        #add include dir to includes path if needed
        if len(locations) == 3:
            compile_str = compile_str + "-I " + locations[2] + " "
            compile_str = compile_str + "-I " + locations[2] + "/* "
        
        found_file = False
        
        # loop over all files in directory
        for file in os.listdir(file_loc):
            if file.endswith(TYPE):
                found_file = True
                
                # add file name to compilation string
                compile_str = compile_str + file_loc + file + " "
        
        if found_file == True:
            compile_str = compile_str + " 2>" + compile_err                
            
            # compile the files and add errors to error file
            compile_return = os.system(compile_str)
            remove_str = remove_str + " " + compile_err
    else:
        donothing = "" 
        # case where makefile is utilized 
        # TODO: should use student makefile?  or a solution?   
    
    # Initialize a string for returning feedback
    feedback = ""
    
    # Check if compilation was a success
    if compile_return == 0:
        module_return = 0
        feedback = "Compilation completed successfully.\n"
        
        if rmexe == True:
            remove_str = remove_str + " " + test_program
        
    # Compilation failure, capture compile errors 
    else:
        module_return = 1
        f = open(compile_err,'r')
        # loop over the lines in error file, split off the base dir
        for line in f:
            feedback = feedback + string.replace(line, file_loc, "")
        f.close()
    
    # Clean up generated files
    os.system(remove_str)
    
    # Form tuple of the module return value and compilation errors
    return_value = (module_return, feedback)
    
    return return_value


