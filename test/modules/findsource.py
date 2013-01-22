## 
# @author Adam Koehler
# @date January 22, 2013
#
#

SOURCE_EXT = ".cpp"


## 
# @brief findsource module determines whether source file exists for testing
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object that is a dictionary defining the test
# @param allow_multiple allow multiple source files in directory, will 
#           choose main with extension if exists otherwise first alphabetical
#
# @return the file name of the source file otherwise an empty string
def test(locations, test_obj, allow_multiple):
    NOT_FOUND = ""
    
    source_name = "main" + SOURCE_EXT

    import os
    
    # attempt for main + extension first
    main_path = os.path.join(locations[0], source_name)
    if os.path.isfile(main_path):
        test_obj.message = "Found main file with extension " + SOURCE_EXT + ", testing " + source_name
        return source_name
    else:
        file_name = [item for item in os.listdir(locations[0]) if item.endswith(SOURCE_EXT)]
        if len(file_name) == 1: 
            test_obj.message = "Found file with extension " + SOURCE_EXT + ", testing " + file_name[0]
            return file_name[0]
        elif (allow_multiple and len(file_name) > 0):   
            test_obj.message = "Found multiple files with extension " + SOURCE_EXT + ", testing " + file_name[0]
            return file_name[0]
        else:
            test_obj.message = "No file found with extension " + SOURCE_EXT
            return NOT_FOUND
        
     
    test_obj.message = "No file found with extension " + SOURCE_EXT
    return NOT_FOUND

