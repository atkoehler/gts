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

# non-threaded version
def check_call(*args, **kwargs):
    "Essentially subprocess.check_call for compatibility reasons."
    
    import subprocess
    returnValue = subprocess.call(*args, **kwargs)
    if returnValue != 0:
        raise SystemError((returnValue, str(args[0])))
    else:
        return 0

