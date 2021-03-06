class GalahTestPart:
    def __init__(self, name = "", score = 0, max_score = 0):
        self.name = name
        self.score = score
        self.max_score = max_score
    
    def to_list(self):
        return [self.name, self.score, self.max_score]
    

class GalahTest:
    def __init__(self, name = "", score = 0, max_score = 0, message = "", parts = None):
        if parts is None:
            parts = []

        self.name = name
        self.score = score
        self.max_score = max_score
        self.message = message
        self.parts = parts
    
    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score,
            "max_score": self.max_score,
            "message": self.message,
            "parts": [i.to_list() for i in self.parts]
        }
    

class GalahResult:
    def __init__(self, score = 0, max_score = 0, tests = None):
        if tests is None:
            tests = []

        self.score = score;
        self.max_score = max_score
        self.tests = tests
    
    def to_dict(self):
        return {
            "score": self.score,
            "max_score": self.max_score,
            "tests": [i.to_dict() for i in self.tests]
        }
    
    def calculate_scores(self):
        """
        Sets score and max_score by summing up the scores and maximum scores of
        each test, respectively.
        
        """

        self.score = sum(i.score for i in self.tests)
        self.max_score = sum(i.max_score for i in self.tests)
    
    def add_test(self, test):
        self.tests.append(test)
     
    def send(self):
        import json
        import sys
        json.dump(self.to_dict(), sys.stdout)


import json
import sys
class GalahConfig:
    def __init__(self, testables_dir = None, harness_dir = None,                                 submission = None, assignment = None, harness = None, 
                 actions = None):
        if actions is None:
            actions = []
        self.testables_directory = testables_dir
        self.harness_directory = harness_dir
        self.submission = submission
        self.harness = harness
        self.assignment = assignment
        self.actions = actions
    
    @staticmethod
    def from_file(file_object = sys.stdin):
        values = json.load(file_object)
        
        return GalahConfig(
            testables_dir = values["testables_directory"],
            harness_dir = values["harness_directory"],
            submission = values["raw_submission"],
            assignment = values["raw_assignment"],
            harness = values["raw_harness"],
        )


