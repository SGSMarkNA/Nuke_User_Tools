import operator
from difflib import SequenceMatcher

TrimsList = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']
base_folders = ['Base_Red', 'Base_Green', 'Base_Blue', 'Base_SL_Red', 'Base_SL_Green', 'Base_SL_Blue', 'Base_XL_Red', 'Base_XL_Green', 'Base_XL_Blue', 'Limited_Red', 'Limited_Green', 'Limited_Blue', 'Limited_Tech_Red', 'Limited_Tech_Green', 'Limited_Tech_Blue', 'Sport_Red', 'Sport_Green', 'Sport_Blue', 'Sport_Z_Red', 'Sport_Z_Green', 'Sport_Z_Blue']

def build_sorted_trim_scores(folder, TrimsList):
	scores_dict = {}
	for trim in TrimsList:
		##print 'trim -----> ', trim
		ratio = SequenceMatcher(None, folder, trim).ratio()
		##print str(ratio) +  '--->   ' + trim
		# Make a dict of the matching trims and their match scores...
		scores_dict[trim] = ratio
		##print scores_dict
		Sorted_Scores = sorted(list(scores_dict.items()), key=lambda key_value: key_value[1], reverse=True)
	##print Sorted_Scores
	BestScoresList = []
	for TrimScore in Sorted_Scores:
		if TrimScore[0] in folder:
			BestScoresList.append(TrimScore[0])
		else:
			pass
	if BestScoresList: 
		Match = max(BestScoresList)
		trim_dir = Match
		print(trim_dir)
		print(folder)
		print('')
		# Return the trim_dir name in TrimsList that best matches the folder name.
		return trim_dir


## EXAMPLE USAGE:
for folder in base_folders:
	build_sorted_trim_scores(folder, TrimsList)

