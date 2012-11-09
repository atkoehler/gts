import modules.compilation
import os

# acquire from configuration file or script
WORKING_DIR = "working"

# received from test initialization
where_am_i = "/home/csgrads/akoeh001/git/gts/test" 
file_loc = "/home/csgrads/akoeh001/gts-test/students/akoehler" 
includes_loc = "/home/csgrads/akoeh001/gts-test/system/includes"

# system commands
rm_cmd = "rm"
mkdir_cmd = "mkdir"

# create a working directory
work_loc = where_am_i + "/" + WORKING_DIR
make_work = mkdir_cmd + " " + work_loc
rm_cmd = rm_cmd + " " + work_loc
os.system(make_work)

# call compilation
return_value = comp((file_loc, work_loc, includes_loc), False)

# Within Main Script
section_name = " Compilation "
score = -25 * return_value[0]
marking_write = (section_name, score, return_value[1])

# Within Deduction Print Script
print '{:=^70}'.format(marking_write[0])
if marking_write[1] != 0:
    print "Deduction assessed:", marking_write[1], "points\n"
print "".join(marking_write[2])

os.system(rm_cmd)
