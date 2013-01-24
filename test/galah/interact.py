class GalahTestPart:
    def __init__(self, name="", score=0, max_score=0):
        self.name = name
        self.score = score
        self.max_score = max_score
    

class GalahTest:
    def __init__(self, name="", score=0, max_score=0, message="", parts=[]):
        self.name = name
        self.score = score
        self.max_score = max_score
        self.message = message
        self.parts = parts
    

class GalahResult:
    def __init__(self, score=0, max_score=0, tests=[]):
        self.score = score;
        self.max_score = max_score
        self.tests = tests
    
    def to_json(self):
        return {"score": self.score, 
                "max_score": self.max_score, 
                "tests": self.tests}

    def add_test(self, t):
        # convert the parts if the exist
        part_trans = []
        for part in t.parts:
            part_trans.append({"name": part.name, "score": part.score, 
                               "max_score": part.max_score})
        
        # convert and add the test
        self.tests.append({"name": t.name, "score": t.score, 
                           "max_score": t.max_score, "message": t.message,
                           "parts": t.parts})
    
    def calculate_scores(self):
        self.score = 0
        self.max_score = 0
        for test in self.tests:
            self.score += test["score"]
            self.max_score += test["max_score"]
    
    def send(self):
        r = {"score": self.score, "max_score": self.max_score, 
             "tests": self.tests}
        import json
        import sys
        json.dump(r, sys.stdout)
    

class GalahConfig:
    def __init__(self, testables_dir="", harness_dir="", submission={}, actions=[]):
        self.testables_dir = testables_dir
        self.harness_dir = harness_dir
        self.submission = submission
        self.actions = actions
    
    def init_json(self):
        import json
        import sys

        values = json.load(sys.stdin)
        self.testables_dir = values["TESTABLES_DIRECTORY"]
        self.harness_dir = values["TEST_DRIVER_DIRECTORY"]
        self.submission = values["SUBMISSION"]
        self.actions = values["ACTIONS"]
    

