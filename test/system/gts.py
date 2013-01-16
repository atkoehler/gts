class HarnessConfig:
    def __init__(self, late_penalty=0, tests=[]):
        self.late_penalty = late_penalty
        self.tests = tests

class HarenessTestPart:
    def __init__(self, name="", score=0, max_score=0, message=""):
        self.name = name
        self.score = score
        self.max_score = max_score
        self.message = message

class HarenessTest:
    def __init__(self, name="", score=0, max_score=0, message="", parts=[], deduct=False):
        self.name = name
        self.score = score
        self.max_score = max_score
        self.message = message
        self.parts = parts
        self.deduction = deduct
    

