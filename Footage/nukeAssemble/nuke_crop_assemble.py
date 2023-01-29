#python

import os;
import sys;
import nuke;
import string;
import fnmatch;
import time;
import math;

frames = []
dimentions = [0,0]
merges = []
outFileName = ""



def test():
	ted = 'bob'

##### find crop numbers by index, add master merge, with B input being a constant node, add write.. execute to full file

def figureOutName(dir):
	name = dir.split('\\')[-1]
# 	outFileName = os.path.join(dir, (name + "_assembled.exr")).replace("\\", "/")
	outFileName = os.path.join(dir, (name + "_assembled.exr")).replace("\\", "/")
	return outFileName




def findEXRS(dir):
	currentDir = dir
	badFiles = ['assembled.exr', 'thumbs.db', 'assemble.nk', 'working.py']
	badExtensions = ['py', 'db', 'vrscene', 'vrimg', 'tmp', 'nk']
	for root, dirs, files in os.walk(dir):
		for file in files:
			if file in badFiles:
				continue
			if file.split('.')[1] in badExtensions:
				continue
			size = file.split("_")
			#whereCrop and make sure the exr has a crop value
			if fnmatch.filter(size, 'crop*'):
				indexValue = fnmatch.filter(size,'crop*')[0]
				placeIndex = size.index(indexValue)
				size = size[placeIndex]
				size = size[5:].split("-")

				frames.append([os.path.join(root,file),size])

				if int(size[2])>dimentions[0]:
					dimentions[0]=int(size[2])
				if int(size[3])>dimentions[1]:
					dimentions[1]=int(size[3])

	frames.sort()


def nukeStuff(dir):
	if dimentions == [0,0]:
		print("WARNING!!! There are no cropped files here")
		return
	outFileName = figureOutName(dir)
	### Set format
	fullImageFormat = str( str(dimentions[0]) + " " + str(dimentions[1]) +" "+ "fullImage")
	nuke.addFormat(fullImageFormat)
	nuke.root()['format'].setValue("fullImage")
	nuke.knobDefault("Root.first_frame", "1")
	nuke.knobDefault("Root.last_frame", "1")
	#### Read in frames, set transforms
	for image in frames:
		new_read = nuke.createNode('Read')
		new_read['file'].fromUserText(image[0])
		new_read['postage_stamp'].setValue(0)     
		reformat = nuke.createNode('Reformat')
		reformat['format'].setValue('fullImage')
		reformat['resize'].setValue('none')
		reformat['center'].setValue(False)
		reformat.connectInput(0, new_read)
		translate = [int(image[1][0]),abs(int(image[1][3])-int(dimentions[1]))]
		new_trans = nuke.createNode('Transform')
		new_trans['center'].setValue([0,0])
		#new_trans['black_outside'].setValue(False)
		new_trans['translate'].setValue(translate) 
		new_trans.connectInput(0, reformat)
		merges.append(new_trans)
		print("merges", len(merges))
	mainMerge = nuke.createNode('Merge2')
	mainMerge['also_merge'].setValue('all')
	mainMerge['metainput'].setValue('All')
	mainMerge.setInput(1, None)
	mainMerge.setInput(2, None)
	mainMerge.setInput(3, None)
	### Merge it all together

	## test if more than one merge can handle
	if len(merges) < 90:
		## do with only one merge
		for elementCount in range(len(merges)):
			mainMerge.connectInput(elementCount+3, merges[elementCount])
	else:
		## do with merging merges
		subMergeCount = int(len(merges)/(int(math.ceil(len(merges)/90.0))))
		subMergeList = [merges[i:i+subMergeCount] for i in range(0, len(merges), subMergeCount)]
		subGroupMerge = []
		for mergeGroup in range(len(subMergeList)):
			subMerge = nuke.createNode('Merge2')
			subGroupMerge.append(subMerge)
			subMerge['also_merge'].setValue('all')
			subMerge['metainput'].setValue('All')
			subMerge.setInput(1, None)
			subMerge.setInput(2, None)
			subMerge.setInput(3, None)
			for elementCount in range(len(subMergeList[mergeGroup])):
				subMerge.connectInput((elementCount+3), subMergeList[mergeGroup][elementCount])

		for groupMerge in range(len(subGroupMerge)):
			mainMerge.connectInput((groupMerge+3), subGroupMerge[groupMerge])        


	### Add the write node
	for node in nuke.allNodes():
		node.setSelected(False)
	outWrite = nuke.createNode('Write')
	outWrite['channels'].setValue('all')
	outWrite.connectInput(1, mainMerge)
	outWrite['file'].setValue(outFileName)
	outWrite['file_type'].setValue('exr')
	outWrite['datatype'].setValue('32-bit float')
	outWrite['metadata'].setValue('all metadata')
	outWrite['interleave'].setValue('channels')
	nuke.selectAll()
	nuke.autoplace_all()
	
def findSize():
	lastImage = frames[:-1]
	#print lastImage

def main(dir):
	findEXRS(dir)
	nukeStuff(dir)

def auto(dir):
	findEXRS(dir)
	nukeStuff(dir)
	nuke.execute (outwrite, 1, 1)

def debug():
	import pydevd
	pydevd.settrace(stdoutToServer=True, stderrToServer=True, suspend=False)
	dir = r"N:\Jobs\Genex\MXXM-14-007_2016_Acura_ILX_Build_and_Price_Stills\work\s01_MY16_ILX_Front_3-4_Accy\img\ren\v03\Bty"
	figureOutName(dir)
# 	main(dir)

