## 
# @file modules/style/globalscheck.py
# @author Adam Koehler
# @date February 4, 2013
#
# @brief Provides a check for whether global variables exist in program
#


## 
# @brief sub test to check whether global variables exist in the program
# 
# @param test the test part object to update with score
# @param harness_dir directory containing the test harness
# @param source the source object containing name, location and content splits
# @param env the environment variables dict from JSON config of test suite
# @param deduction the deduction to take off per discovered problem
#
# @return a list containing all the names of global variables, None if sys err
#
def globals_exist(test, harness_dir, source, env, deduction):
    import os
    import shutil
    import re
    from system.utils import which
    from system.procs import check_call
   
    # intialize to empty list of global variables  
    vars = [] 
    
    files_to_remove = []
    
    # make sure the commands exist
    nm = which("nm")
    gpp = which(env["compiler"])
    if nm == None or gpp == None:
        return None
    
    # check if working directory exists, if not make one
    working_dir = os.path.join(harness_dir, env["working_dir"])
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
        made_working = True
    else:
        made_working = False
    
    FNULL = open(os.devnull, 'w')
    try:
        # compile the object file
        # set up path to includes directory
        include_path = os.path.join(harness_dir, env["includes_dir"])
        object_file = source.name[0:source.name.find(".")] + ".o"
        obj_loc = os.path.join(working_dir, object_file)
        files_to_remove.append(obj_loc)
        check_call([gpp, "-c", "-o", obj_loc, 
                    "-I", include_path, source.file_loc], 
                   stdout=FNULL, stderr=FNULL)
       
        # get object symbols
        symf = os.path.join(working_dir, "symbols.txt")
        files_to_remove.append(symf)
        cmd = " ".join([nm, obj_loc])
        with open(symf, 'w') as sym_file:
            check_call([nm, obj_loc], stdout=sym_file, stderr=FNULL)
        
        # search for global variables line in symbols file
        var_lines = []
        with open(symf, 'r') as sym_file:
            for line in sym_file:
                if re.search('[0-9A-Fa-f]* [BCDGRS]', line):
                    var_lines.append(line)
                
        # append last item (the variable name) to variables list
        for line in var_lines:
            if len(line) > 0:
                vars.append(line.strip().split(" ")[-1])
       
    except SystemError as e:
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
    
    test.score = -1 * deduction * len(vars)
    return vars


