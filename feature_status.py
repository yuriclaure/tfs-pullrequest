from enum import Enum

class FeatureStatus(Enum):
	COULDNT_DEFINE = 1
	BEHIND = 2
	UPTODATE = 3
	AHEAD = 4
	LOCAL = 5

	
