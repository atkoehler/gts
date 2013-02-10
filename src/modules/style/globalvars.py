## 
# @file modules/style/globalscheck.py
# @author Adam Koehler
# @date February 4, 2013
#
# @brief Provides a check for whether global variables exist in program
#

# TODO: figure out the configuration system to get this item from their
DEDUCTION_PER_GAFFE = 5
WORKING_DIR_NAME = "working"
COMPILER = "g++"

## 
# @brief sub test to check whether global variables exist in the program
# 
# @param test the test part object to update with score
# @param harness_dir directory containing the test harness
# @param source the source object containing name, location and content splits
#
# @return a list containing all the names of global variables, None if sys err
#
def globals_exist(test, harness_dir, source):
    import os
    import shutil
    from system.utils import which
   
    # intialize to empty list of global variables  
    vars = [] 
    
    files_to_remove = []
    
    # make sure the commands exist
    nm = which("nm")
    grep = which("grep")
    cut = which("cut")
    gpp = which(COMPILER)
    if nm == None or grep == None or cut == None or gpp == None:
        return None
    
    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, WORKING_DIR_NAME)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    FNULL = open(os.devnull, 'w')
    try:
        from system.utils import check_call

        # compile the object file
        object_file = source.name[0:source.name.find(".")] + ".o"
        obj_loc = os.path.join(working_dir, object_file)
        files_to_remove.append(obj_loc)
        cmd = " ".join([gpp, "-o", obj_loc, source.file_loc])
        check_call([gpp, "-o", obj_loc, source.file_loc], 
                   stdout=FNULL, stderr=FNULL)
        
        # get object symbols
        symf = os.path.join(working_dir, "symbols.txt")
        files_to_remove.append(symf)
        cmd = " ".join([nm, obj_loc])
        with open(symf, 'w') as sym_file:
            check_call([nm, obj_loc], stdout=sym_file, stderr=FNULL)
        
        # grep for proper symbols relating to global variables
        grepf = os.path.join(working_dir, "grep.txt")
        files_to_remove.append(grepf)
        cmd = " ".join([grep, "[0-9A-Fa-f]* [BCDGRS]"])
        with open(symf, 'r') as sym_file:
            with open(grepf, 'w') as grep_file:
                check_call([grep, "[0-9A-Fa-f]* [BCDGRS]"], 
                           stdin=sym_file, stdout=grep_file, stderr=FNULL)
        
        # cut off the variable names
        cutf = os.path.join(working_dir, "cut.txt")
        files_to_remove.append(cutf)
        with open(grepf, 'r') as grep_file:
            with open(cutf, 'w') as cut_file:
                check_call([cut, "-d", " ", "-f" "3"], 
                           stdout=cut_file, stdin=grep_file, stderr=FNULL)
        
        # split the global variables into a list, exclude vars starting with _
        contents = open(cutf).read().rstrip().rstrip('\n').split("\n")
        for (i, val) in enumerate(contents):
            if val[0] != '_':
                vars.append(val)
    
    except SystemError:
    # TODO: determine what to do in except clause, outputing error cause issue?
        FNULL.close()
        if made_working:
            shutil.rmtree(working_dir)
        elif len(files_to_remove) > 0:
            for f in files_to_remove:
                if os.path.isfile(f):
                    os.remove(f)
        return None
    
    # remove working directory if created it otherwise remove files created
    if made_working:
        shutil.rmtree(working_dir)
    elif len(files_to_remove) > 0:
        for f in files_to_remove:
            if os.path.isfile(f):
                os.remove(f)
    
    FNULL.close() 
    test.score = -1 * DEDUCTION_PER_GAFFE * len(vars)
    
    return vars


