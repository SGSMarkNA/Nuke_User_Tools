
import operator
from fuzzywuzzy import fuzz

Trims_List = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']
View_Names = ['Base_Red', 'Base_Green', 'Base_Blue', 'Base_SL_Red', 'Base_SL_Green', 'Base_SL_Blue', 'Base_XL_Red', 'Base_XL_Green', 'Base_XL_Blue', 'Limited_Red', 'Limited_Green', 'Limited_Blue', 'Limited_Tech_Red', 'Limited_Tech_Green', 'Limited_Tech_Blue', 'Sport_Red', 'Sport_Green', 'Sport_Blue', 'Sport_Z_Red', 'Sport_Z_Green', 'Sport_Z_Blue']

def _find_best_match(view, Trims_List):
	scores_dict = {}
	for trim in Trims_List:
		##print 'trim -----> ', trim
		ratio = fuzz.ratio(trim, view)
		##print str(ratio) +  '--->   ' + trim
		# Make a dict of the matching trims and their match scores...
		scores_dict[trim] = ratio
	# Get the dir. with the best matching score...
	MaxScore = max(iter(scores_dict.items()), key=operator.itemgetter(1))[0]
	##print 'MaxScore =================>>>>>> ', MaxScore
	return MaxScore,  scores_dict   


## EXAMPLE USAGE:
for view in View_Names:
	MaxScore, scores_dict = _find_best_match(view, Trims_List)
	if Match:
		print('')
		print(view)
		print(MaxScore)
		print('')
		print(scores_dict)


############################################################################################	

import operator
from fuzzywuzzy import fuzz

Trims_List = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']
View_Names = ['Base_Red', 'Base_Green', 'Base_Blue', 'Base_SL_Red', 'Base_SL_Green', 'Base_SL_Blue', 'Base_XL_Red', 'Base_XL_Green', 'Base_XL_Blue', 'Limited_Red', 'Limited_Green', 'Limited_Blue', 'Limited_Tech_Red', 'Limited_Tech_Green', 'Limited_Tech_Blue', 'Sport_Red', 'Sport_Green', 'Sport_Blue', 'Sport_Z_Red', 'Sport_Z_Green', 'Sport_Z_Blue']

def _find_best_match(view, Trims_List):
	scores_dict = {}
	for trim in Trims_List:
		##print 'trim -----> ', trim
		ratio = fuzz.ratio(trim, view)
		##print str(ratio) +  '--->   ' + trim
		# Make a dict of the matching trims and their match scores...
		scores_dict[trim] = ratio
	# Get the dir. with the best matching score...
	MaxScore = max(iter(scores_dict.items()), key=operator.itemgetter(1))[0]
	##print 'MaxScore =================>>>>>> ', MaxScore
	return MaxScore,  scores_dict   


## EXAMPLE USAGE:
for view in View_Names:
	MaxScore, scores_dict = _find_best_match(view, Trims_List)
print(sorted(list(scores_dict.values()), reverse=True))
if MaxScore not in view:
	print('Nope.')

	if Match:
		print('')
		print(view)
		print(MaxScore)
		print('')
		print(scores_dict)

############################################################################################

import operator
from fuzzywuzzy import fuzz

Trims_List = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']
View_Names = ['Base_Red', 'Base_Green', 'Base_Blue', 'Base_SL_Red', 'Base_SL_Green', 'Base_SL_Blue', 'Base_XL_Red', 'Base_XL_Green', 'Base_XL_Blue', 'Limited_Red', 'Limited_Green', 'Limited_Blue', 'Limited_Tech_Red', 'Limited_Tech_Green', 'Limited_Tech_Blue', 'Sport_Red', 'Sport_Green', 'Sport_Blue', 'Sport_Z_Red', 'Sport_Z_Green', 'Sport_Z_Blue']

def _find_best_match(view, Trims_List):
	scores_dict = {}
	for trim in Trims_List:
		##print 'trim -----> ', trim
		ratio = fuzz.ratio(trim, view)
		##print str(ratio) +  '--->   ' + trim
		# Make a dict of the matching trims and their match scores...
		scores_dict[trim] = ratio
	# Get the dir. with the best matching score...
	MaxScore = max(iter(scores_dict.items()), key=operator.itemgetter(1))[0]
	##print 'MaxScore =================>>>>>> ', MaxScore
	return MaxScore,  scores_dict   

## EXAMPLE USAGE:
for view in View_Names:
	MaxScore, scores_dict = _find_best_match(view, Trims_List)
	Sorted_Scores = sorted(list(scores_dict.items()), key=lambda key_value2: key_value2[1], reverse=True)
print(Sorted_Scores)

############################################################################################

import operator
from fuzzywuzzy import fuzz

Trims_List = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']
View_Names = ['Base_Red', 'Base_Green', 'Base_Blue', 'Base_SL_Red', 'Base_SL_Green', 'Base_SL_Blue', 'Base_XL_Red', 'Base_XL_Green', 'Base_XL_Blue', 'Limited_Red', 'Limited_Green', 'Limited_Blue', 'Limited_Tech_Red', 'Limited_Tech_Green', 'Limited_Tech_Blue', 'Sport_Red', 'Sport_Green', 'Sport_Blue', 'Sport_Z_Red', 'Sport_Z_Green', 'Sport_Z_Blue']

def _find_best_match(view, Trims_List):
	scores_dict = {}
	for trim in Trims_List:
		##print 'trim -----> ', trim
		ratio = fuzz.ratio(trim, view)
		##print str(ratio) +  '--->   ' + trim
		# Make a dict of the matching trims and their match scores...
		scores_dict[trim] = ratio
		Sorted_Scores = sorted(list(scores_dict.items()), key=lambda key_value: key_value[1], reverse=True)
		##print Sorted_Scores
	for TrimScore in Sorted_Scores:
		if TrimScore[0] not in view:
			pass
		else:
			Match = TrimScore[0]
			print(Match)
			print(view)
			print('')

view = 'Base_Red'
_find_best_match(view, Trims_List)

############################################################################################

import operator
from fuzzywuzzy import fuzz

Trims_List = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']
View_Names = ['Base_Red', 'Base_Green', 'Base_Blue', 'Base_SL_Red', 'Base_SL_Green', 'Base_SL_Blue', 'Base_XL_Red', 'Base_XL_Green', 'Base_XL_Blue', 'Limited_Red', 'Limited_Green', 'Limited_Blue', 'Limited_Tech_Red', 'Limited_Tech_Green', 'Limited_Tech_Blue', 'Sport_Red', 'Sport_Green', 'Sport_Blue', 'Sport_Z_Red', 'Sport_Z_Green', 'Sport_Z_Blue']

def build_sorted_trim_scores(view, Trims_List):
	scores_dict = {}
	for trim in Trims_List:
		##print 'trim -----> ', trim
		ratio = fuzz.ratio(trim, view)
		##print str(ratio) +  '--->   ' + trim
		# Make a dict of the matching trims and their match scores...
		scores_dict[trim] = ratio
		Sorted_Scores = sorted(list(scores_dict.items()), key=lambda key_value1: key_value1[1], reverse=True)
		##print Sorted_Scores
		return Sorted_Scores

def find_best_match(Sorted_Scores):
	BestScoresList = []
	for TrimScore in Sorted_Scores:
		if TrimScore[0] in view:
			BestScoresList.append(TrimScore[0])
		else:
			pass
	if BestScoresList: 
		Match = max(BestScoresList)
		print(Match)
		print(view)
		print('')


## EXAMPLE USAGE:
for view in View_Names:
	build_sorted_trim_scores(view, Trims_List)
	find_best_match(Sorted_Scores)



