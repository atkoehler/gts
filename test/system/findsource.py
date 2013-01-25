##
# @file system/findsource.py 
# @author Adam Koehler
# @date January 23, 2013
# 
# @brief finds the source file within testing directory if one exists
#

# TODO: this probably should come from config file
SOURCE_EXT = ".cpp"


## 
# @brief findsource module determines whether source file exists for testing
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param source the source file object to store file name and location into
# @param allow_multiple allow multiple source files in directory, will 
#           choose main with extension if exists otherwise first alphabetical
#
# @return True if source file is discovered otherwise False
#
def test(locations, test_obj, source, allow_multiple):
    
    source_name = "main" + SOURCE_EXT

    import os
    
    # attempt for main + extension first
    main_path = os.path.join(locations[0], source_name)
    if os.path.isfile(main_path):
        test_obj.message = "Found main file with extension " + SOURCE_EXT + ", testing " + source_name
        source.name = source_name
        source.file_loc = main_path
        return True
    else:
        file_name = [item for item in os.listdir(locations[0]) if item.endswith(SOURCE_EXT)]
        if len(file_name) == 1: 
            test_obj.message = "Found file with extension " + SOURCE_EXT + ", testing " + file_name[0]
            source.name = file_name[0]
            source.file_loc = os.path.join(locations[0], file_name[0])
            return True
        elif (allow_multiple and len(file_name) > 0):   
            test_obj.message = "Found multiple files with extension " + SOURCE_EXT + ", testing " + file_name[0]
            source.name = file_name[0]
            source.file_loc = os.path.join(locations[0], file_name[0])
            return True
        else:
            test_obj.message = "No file found with extension " + SOURCE_EXT
            return False
        
     
    test_obj.message = "No file found with extension " + SOURCE_EXT
    return False

