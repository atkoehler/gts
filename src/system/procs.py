##
# @file system/process.py
# @author Adam Koehler
# @date February 20, 2013
#
# @brief implemenatation of processes with backwards compatibility as well as
#           kill timers.
#
#           credit to those at stackoverflow for helping me decipher this
#

import subprocess
import threading

##
# @brief A task is a single process that is executed for a given amount of time
#
#       If no time is executed then no timeout will exist and the task will 
#       execute until completion
#
class Task:
    def __init__(self, timeout=None):
        self.timeout = timeout
        self.process = None

    def check_call(self, *args, **kwargs):
        "Essentially subprocess.check_call with kill switch for compatibility."
        
        def target():
            self.process = subprocess.Popen(*args, **kwargs)
            self.process.communicate()
        
        thread = threading.Thread(target=target)
        thread.start()
    
        thread.join(self.timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
    
        if self.process.returncode != 0:
            raise SystemError((self.process.returncode, str(args[0])))
        else:
            return 0

##
# @brief Non-threaded version of check_call.
#
#        This allows items to be easily executed by the harness so that a 
#        task does not always have to be created first. The threaded version
#        should be used in almost all cases when executing non-system programs
#
def check_call(*args, **kwargs):
    "Essentially subprocess.check_call for compatibility reasons."
    
    import subprocess
    returnValue = subprocess.call(*args, **kwargs)
    if returnValue != 0:
        raise SystemError((returnValue, str(args[0])))
    else:
        return 0

