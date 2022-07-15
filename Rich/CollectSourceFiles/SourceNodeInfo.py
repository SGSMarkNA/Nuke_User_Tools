import glob
import os
import nuke


class NodeInfo(object):
	'''
	Given a Nuke node "Source" object (a node that has a "file" knob),
	returns a dictionary of key/value pairs. The information returned
	includes things like the dirPath, fileType, whether or not it's an
	indexed sequence of frames ['seqCheck'], etc.

	################## EXAMPLE USAGE: #########################

	import CollectSourceFiles.SourceNodeInfo

	# RUN THE CLASS... (as the name "Source", in this example):
	Source = CollectSourceFiles.SourceNodeInfo.NodeInfo()

	# SELECT A SOURCE NODE AS THE INPUT...
	Node = nuke.selectedNode()

	# RETURN THE ENTIRE DICTIONARY:
	Source.get_info(Node)

	# RETURN THE INDIVIDUAL KEY VALUES:
	Source.get_info(Node)['rawKnob']
	Source.get_info(Node)['filePath']
	Source.get_info(Node)['dirPath']
	Source.get_info(Node)['Filename']
	Source.get_info(Node)['seqCheck']
	Source.get_info(Node)['padding']
	Source.get_info(Node)['FilenameForRelink']
	Source.get_info(Node)['firstFrame']
	Source.get_info(Node)['lastFrame']
	Source.get_info(Node)['length']
	Source.get_info(Node)['FrameRange']
	Source.get_info(Node)['prefix']
	Source.get_info(Node)['fileType']
	Source.get_info(Node)['fileExt']
	Source.get_info(Node)['firstFile']
	Source.get_info(Node)['lastFile']

	# RETURN THE FIRST AND LAST FRAME NUMBERS:
	keys = ['firstFrame', 'lastFrame']
	for key in keys:
	    print Source.get_info(Node).get(key)

	# PRINT ALL OF THE KEY/VALUE PAIRS:
	sorted = Source.get_info(Node).items()
	sorted.sort()
	print '\n'
	for k, v in sorted:
	    print k, '---->', v
	'''

	def __init__(self):
		'''Constructor'''

		# Set the keys we can get info from...
		self.InfoKeys = ['rawKnob',
		                 'filePath',
		                 'dirPath',
		                 'Filename',
		                 'seqCheck',
		                 'padding',
		                 'FilenameForRelink',
		                 'firstFrame',
		                 'lastFrame',
		                 'length',
		                 'FrameRange',
		                 'prefix',
		                 'fileType',
		                 'fileExt',
		                 'firstFile',
		                 'lastFile']

		# Set the default values...
		self.rawKnob = ''
		self.filePath = ''
		self.dirPath = ''
		self.Filename = ''
		self.seqCheck = False
		self.padding = ''
		self.FilenameForRelink = ''
		self.firstFrame = None
		self.lastFrame = None
		self.length = 1
		self.FrameRange = None
		self.prefix = ''
		self.fileType = ''
		self.fileExt = ''
		self.firstFile = ''
		self.lastFile = ''        

		# Create the dictionary to hold the key/value pairs...
		self.SourceInfoDict = {}

	##------------------------------------------------------
	##---------- The main method to run --------------------

	def get_info(self, node):
		''''''
		# First, make sure we've got a nuke.Node as an input...
		if not type(node) == nuke.Node:
			raise TypeError('Argument must be a nuke.Node object.')

		# Check if the node has a 'file' knob or a 'vfield_file' knob...
		self.knobs_to_check = ['file', 'vfield_file']
		self.SourceCheck = [k for k in self.knobs_to_check if k in node.knobs()]
		if self.SourceCheck:
			pass
		else:
			raise ValueError('Wrong Input: Nuke node must have a "file" knob or a "vfield_file" knob.')

		try:
			# If the node has a 'file' knob, get the path...
			self.rawKnob = node.knob('file').value()

			# Evaluate/expand any expressions, metadata, etc...
			# This will evaluate to the current frame number for the current frame for an indexed sequence... 
			self.filePath = node.knob('file').evaluate()
			
			# Make sure that an empty file knob that evaluates to None gets set back to the empty string...
			if self.filePath == None:
				self.filePath = ''

			# Check to see if the file path represents a file sequence...
			self.seq_chars = ['%', '#']
			for char in self.rawKnob:
				if char in self.seq_chars:
					self.seqCheck = True

			# Get the first and last frame numbers, and the duration of the sequence...
			# Note: Some nodes that have file knobs do not have frame number knobs, so
			# we need to try, rather than blow everything up...
			# Example node with no "first" and "last" knobs: OCIOCDLTransform
			try:
				self.firstFrame = node.knob('first').value()
				self.lastFrame = node.knob('last').value()
				if self.firstFrame == self.lastFrame:
					self.length = 1
				else:
					self.length = (self.lastFrame - self.firstFrame) + 1
			except AttributeError:
				pass            
		except:
			# If the node has a 'vfield_file' knob, get the path...
			self.rawKnob = node.knob('vfield_file').value()
			# Evaluate/expand any expressions, metadata, etc...
			# This will evaluate to the current frame number for the current frame for an indexed sequence... 
			self.filePath = node.knob('vfield_file').evaluate()

		# Get the parent directory...
		self.dirPath = os.path.dirname(self.filePath) + '/'

		# Get just the file name portion...
		self.Filename = os.path.basename(self.filePath)

		# Get the file type, self.fileType - with no dot --> e.g., png, exr, jpg, etc.
		self.fileType = os.path.basename(self.filePath).rpartition('.')[2]

		# Get the file extension, self.fileExt - with the dot --> '.exr'
		self.fileExt = os.path.splitext(self.rawKnob)[1]

		# Whittle down to the base file name prefix...
		basepath = os.path.splitext(self.rawKnob)[0]
		basename = os.path.basename(basepath)
		filename = os.path.splitext(basename)[0]
		self.prefix = filename
		self.prefix = self.prefix.split('%')[0]

		# Set the raw filename to use for the re-link...
		self.FilenameForRelink = os.path.basename(self.rawKnob)

		# If the raw file path - rawKnob - represents a padded image sequence, set these values...
		if self.seqCheck:
			# Create the file sequence list iterator to use for looping through the list of frames in the sequence...
			self.fileList = glob.iglob(os.path.join(self.dirPath + self.prefix + "*"))
			self.FileList = list(self.fileList)
			self.FileList.sort()
			# Get the padding...
			paddedStart = os.path.basename(self.FilenameForRelink).rpartition('.')[0]
			#print 'paddedStart', paddedStart
			if '%' in paddedStart:
				pad_seg = paddedStart.split('_')[-1]
				self.padding = pad_seg + "."
				#print 'self.padding', self.padding
			# Set the first and last filepaths, if valid...
			try:
				self.firstFile = self.FileList[0]
				self.lastFile = self.FileList[-1]
				self.firstFile = self.firstFile.replace('\\', '/')
				self.lastFile = self.lastFile.replace('\\', '/')
			except IndexError:
				pass

		# FrameRange tuple - first, last, increment - used for functions such as nuke.execute() and nuke.executeMultiple()...
		try:
			self.FrameRange = [(int(self.firstFrame), int(self.lastFrame), 1)]
		except TypeError:
			# Vectorfield nodes do not have first/last frames and cause this to fail with a TypeError...
			pass

		# Assemble a list of the values...
		self.InfoValues = [self.rawKnob,
		                   self.filePath,
		                   self.dirPath,
		                   self.Filename,
		                   self.seqCheck,
		                   self.padding,
		                   self.FilenameForRelink,
		                   self.firstFrame,
		                   self.lastFrame,
		                   self.length,
		                   self.FrameRange,
		                   self.prefix,
		                   self.fileType,
		                   self.fileExt,
		                   self.firstFile,
		                   self.lastFile]        

		# Combine the key and value lists as a paired sequence...
		self.zipped = list(zip(self.InfoKeys, self.InfoValues))

		# Populate the SourceInfoDict dictionary with the keys and values from the zipped sequence...
		for Key, Value in self.zipped:
			self.SourceInfoDict[Key] = Value

		return self.SourceInfoDict