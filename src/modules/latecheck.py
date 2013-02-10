## 
# @file modules/latecheck.py
# @author Adam Koehler
# @date February 1, 2013
#
# @brief Provides the means to assess a late penalty based 
#        submission date and assignment due date.
#

# TODO: figure out the configuration system to get this item from their
LATE_PENALTY = 20


## 
# @brief test function checks the submission date against the due date
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param submit_date submission date from the provided raw submission
# @param due_date the due date from the provided assignment dictionary 
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, submit_date, due_date):
    OK = 0
    from datetime import datetime

    # format string from datetime.isoformat() may be without microseconds
    if submit_date.find('.') == -1:
        sdf = "%Y-%m-%dT%H:%M:%S"
    else:
        sdf = "%Y-%m-%dT%H:%M:%S.%f"
    if due_date.find('.') == -1:
        ddf = "%Y-%m-%dT%H:%M:%S"
    else:
        ddf = "%Y-%m-%dT%H:%M:%S.%f"

    # check if submission took place prior to deadline    
    if datetime.strptime(submit_date, sdf) < datetime.strptime(due_date, ddf):
        test_obj.message = "Submitted before the deadline."
    else:
        test_obj.score = -1 * LATE_PENALTY
        test_obj.message = "Submitted after the deadline."

    return OK

