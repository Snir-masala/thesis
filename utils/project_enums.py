from enum import Enum

class BoneQuality(Enum):
    GOOD = "Good"
    MEDIUM = "Medium"
    POOR = "Poor"

class MuscleStrength(Enum):
    STRONG = "Strong"
    MEDIUM = "Medium"
    WEAK = "Weak"

class DiseaseStage(Enum):
    I = 1
    II = 2
    III = 3
    IV = 4

class SurgeryStatus(Enum):
    NO = "No"
    YES = "Yes"

class Complications(Enum):
    NO = "No"
    YES = "Yes"

class FractureEvent(Enum):
    NO = "No"
    YES = "Yes"

class DecisionOption(Enum):
    WAIT = "Wait"
    SURGERY = "Surgery"
    ADDITIONAL_TESTS = "Additional Tests"