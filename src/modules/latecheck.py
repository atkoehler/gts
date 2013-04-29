## 
# @file modules/latecheck.py
# @author Adam Koehler
# @date February 1, 2013
#
# @brief Provides the means to assess a late penalty based 
#        submission date and assignment due date.
#

from system.utils import *

## 
# @brief test function checks the submission date against the due date
# 
# @param locations tuple (location of code, location of harness)
# @param test_obj the test object containing properties to fill out
# @param vars the dictionary of variables for the test from conifuration JSON
# @param submit_date submission date from the provided raw submission
# @param due_date the due date from the provided assignment dictionary 
# @param score currently tabulated score for the result
# @param max_score currently tabulated max_score for the result
#
# @return 0 if test completed successfully, otherwise -1
#
def test(locations, test_obj, vars, submit_date, due_date, score, max_score):
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
        test_obj.message = "Submitted " + markup_create_bold("after") + " the "
        test_obj.message += "deadline."
        if vars["type"] == "flat":
            test_obj.score = -1 * vars["penalty"]
        elif vars["type"] == "cap":
            capped = max_score - vars["penalty"]
            if capped < score and score > 0:
                test_obj.score = -1 * (score - capped)
                test_obj.message += " Applying penalty to attain capped "
                test_obj.message += "maximum score."
            else:
                test_obj.score = 0
                test_obj.message += " Score is not over the capped maximum, "
                test_obj.message += "no penalty is required."
        else:
            test_obj.score = -1 * vars["penalty"]

    return OK

