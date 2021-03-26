
import operator
from difflib import SequenceMatcher

view_name = 'Base_XL_Green'
List = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']

def _find_best_match(view_name, List):
	''''''
	scores_dict = {}
	for x in List:
		print 'x -----> ', x
		ratio = SequenceMatcher(None, view_name, x).ratio()*100
		##ratio = SequenceMatcher(lambda z: z == " ", view_name, x).ratio()
		print str(ratio) +  '--->   ' + x
		# Make a dict of the matching trims and their match scores...
		scores_dict[x] = ratio
	# Get the dir. with the best matching score...
	MaxScore = max(scores_dict.iteritems(), key=operator.itemgetter(1))[0]
	print 'MaxScore =================>>>>>> ', MaxScore
	return MaxScore	


_find_best_match(view_name, List)


