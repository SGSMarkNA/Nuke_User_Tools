import nuke
import nukescripts
import fnmatch
import os
import time
from difflib import SequenceMatcher
import operator
from SourceNodeInfo import NodeInfo
## Need this to find the Node_Tools folder, which is relative to this file...
NodeToolsDir = os.path.realpath(os.path.dirname(__file__) + '/..') + '/Node_Tools'
os.sys.path.append(NodeToolsDir)
from Node_Tools.Node_Tools import Node_Tools



class SourceNodePathRepair(object):
	''''''

	def __init__(self):
		'''Constructor'''
		self.start_time = time.time()
		self.cancel = False
		self.SourceNodesWithErrors = []		

	##---------------------------------------------------------------------------------------
	##---------------------------------------------------------------------------------------

	def _prompt_for_search_path(self, sourceNode):
		'''
		Run nuke.getFilename to ask for the search path from the user...
		'''
		self.searchPath = ''
		self.dirPath = NodeInfo().get_info(sourceNode)['dirPath']
		self.basePath = nuke.getFilename('ORIGINAL PATH ---> %s' % self.dirPath, " ", type = 'open')
		if self.basePath != None:
			self.searchPath = os.path.join(self.basePath)
			return True
		else:
			return False


	def _assemble_search_path(self, sourceNode):
		''''''
		self.pattern = ''
		# If it's a file sequence path, we need to assemble a wildcard search path...
		if NodeInfo().get_info(sourceNode)['seqCheck']:
			self.prefix = NodeInfo().get_info(sourceNode)['prefix']
			self.fileExt = NodeInfo().get_info(sourceNode)['fileExt']
			# Need to build the path differently, depending on the number of dot separators in the orig. path...
			self.rawKnob = NodeInfo().get_info(sourceNode)['rawKnob']
			if self.rawKnob.count('.') == 1:
				self.pattern = self.prefix + '*' + self.fileExt
			elif self.rawKnob.count('.') == 2:
				self.pattern = self.prefix + '.' + '*' + self.fileExt
		# If it's not a file sequence, just use the original file name in the file knob...
		else:
			self.pattern = NodeInfo().get_info(sourceNode)['Filename']
		return self.pattern


	def _find_dir_match(self, pattern, searchPath):
		''''''
		result = []
		length = .01
		found = None
		dirs_found = []
		MatchedDir = ''
		# Start search progress task...
		self.task = nuke.ProgressTask('Matching: %s \n' % pattern)
		progress = 0.0
		for root, dirs, files in os.walk(searchPath):
			# Windows has '\' separators in some parts of the root dir. path...
			if os.name == 'nt':
				root = root.replace("\\", "/")			
			# Progress bar message updates with new root dir. search...
			self.task.setMessage(root)
			# Allow for cancellation by user...
			if self.task.isCancelled():
				found = set([])		## Empty set
				break		
			# Loop through the files in the root dir....
			for name in files:
				length = len(files)+1
				# Allow the user to cancel...
				if self.task.isCancelled():
					found = set([])		## Empty set
					break
				# Find the matches...
				if fnmatch.fnmatch(name, pattern):
					result.append(root)
					# Collect only unique directories...
					found = set(result)
			# Update the progress bar...
			progress += 1
			self.task.setProgress(int(float(progress) / length * 100))
		if found:
			# Turn the set into a list...
			dirs_found = list(found)
		else:
			dirs_found = []
		# If we found at least one directory match...
		if dirs_found:
			# Use difflib.SequenceMatcher.ratio() to find the best match between the original node's dirPath and the list of found directories...
			MatchedDir = self._find_best_ratio_match(self.dirPath, dirs_found)
		# Cleanup progress bar...
		del self.task
		return MatchedDir


	def _find_best_ratio_match(self, dir_to_match_to, dirs_list):
		''''''
		scores_dict = {}
		for path_to_match in dirs_list:
			path_to_match = path_to_match + '/'
			ratio = SequenceMatcher(None, dir_to_match_to, path_to_match).ratio()
			print str(ratio) +  '--->   ' + path_to_match
			# Make a dict of the matching dirs and their match scores...
			scores_dict[path_to_match] = ratio
		# Get the dir. with the best matching score...
		MaxScoreDir = max(scores_dict.iteritems(), key=operator.itemgetter(1))[0]
		return MaxScoreDir


	def _relink_node(self, sourceNode):
		''''''
		# Assemble the new link path...
		self.FilenameForRelink = NodeInfo().get_info(sourceNode)['FilenameForRelink']
		####self.ReLinkPath = os.path.join(self.FoundDir + '/' + self.FilenameForRelink)
		self.ReLinkPath = os.path.join(self.FoundDir + self.FilenameForRelink)
		# Re-link the file path to the newfound directory path...
		try:
			sourceNode['file'].setValue(self.ReLinkPath)
		except:
			sourceNode['vfield_file'].setValue(self.ReLinkPath)

	##------------------------------------------------------
	##---------- The main method to run --------------------

	def repair_path(self):
		''''''
		# Gather up all of the source nodes in the script...
		self.AllNodes = Node_Tools()._get_all_nodes()
		self.sourceNodes = Node_Tools()._find_all_source_nodes(self.AllNodes)
		print 'self.SourceNodes -->', [item.fullName() for item in self.sourceNodes]
		# Do an initial check to see if any of the sourceNodes have errors...
		self.SourceNodesWithErrors = Node_Tools()._find_nodes_with_errors(self.sourceNodes)
		print 'self.SourceNodesWithErrors -->', [item.fullName() for item in self.SourceNodesWithErrors]
		# While there are errors, continue to run...
		while self.SourceNodesWithErrors:		
			# Ask the user if he wants to try to repair the broken links...
			error_message = 'BROKEN FILE PATH LINKS:\n\nAt least one of the source nodes in this script has a broken file path.\n\nWould you like to try to repair them now?'
			if nuke.ask(error_message):
				# Initialize a holder variable for the final status message after we're done...
				self.finalmessage = ''
				# Toggle for using the same search path for any remaining nodes with error...
				self.recycle_search_path = False
				# Go through the list of source nodes with errors and try to repair the filename links  by searching in the self.searchPath directory the user has selected...
				# Initialize some progress bar starter values...
				NodeNumber = 1
				if len(self.SourceNodesWithErrors):
					TotalNodeCount = len(self.SourceNodesWithErrors)
				# Loop though the list of source nodes with errors...
				for node in self.SourceNodesWithErrors:
					print node.name()
					# Initialize some progress bar starter values...
					Progress = 0.0						
					# Start a task progress bar...
					self.MainTask = nuke.ProgressTask('Repair Node Paths: ')						
					# Set the progress bar message...
					self.MainTask.setMessage('%s / %s Nodes: %s' % (NodeNumber, TotalNodeCount, node.name()))
					# Let the user bail out...
					if self.MainTask.isCancelled():
						self.cancel = True
						break
					if self.recycle_search_path == False:
						nuke.message('Checking %s \n\nPLEASE PICK A DIRECTORY TO SEARCH:\n\nNote: The original path will be shown at the top of the next window for reference.' % node.name())
						# Run a nuke.getFilename panel to ask the user for the directory in which to start searching...
						check = self._prompt_for_search_path(node)
						# If check is True, it means the user actually picked a directory to search and did not hit Cancel. So, prompt for re-using the same search path or not...
						if check:
							# Check to see if the user wants to re-use the same search path for any/all remaining nodes with errors...
							if nuke.ask('Do you want to use the same Search Path for any remaining nodes with broken file path links?'):
								self.recycle_search_path = True
						else:
							# The user canceled picking a search path. Maybe they only want to skip one node or maybe they want to just quit everything. Better ask...
							if nuke.ask('DO YOU WANT TO CANCEL ALL...?'):
								self.cancel = True
								break
					# If the user has not cancelled...
					if self.searchPath:
						# Create the masked (*) pathnames to search for...
						self._assemble_search_path(node)
						# Find the directories that have pattern matches and use the one with the best ratio score...
						self.FoundDir = self._find_dir_match(self.pattern, self.searchPath)
						if self.FoundDir:
							print 'self.FoundDir---------->', self.FoundDir
							# If we found a match, relink the node's file knob to the new path...
							self._relink_node(node)
							self.finalmessage = self.finalmessage + node.name() + " - " + " Found Successfully!\n"
						else:
							print 'self.FoundDir---------->' + 'NOT FOUND.'
							self.finalmessage = self.finalmessage + node.name() + " - " +  " Not Found!\n"
					else:
						# User cancelled directory selection, so mark the node as not found...
						self.finalmessage = self.finalmessage + node.name() + " - " +  " Not Found!\n"
					# Update the main progress bar...
					Progress += 1
					self.MainTask.setProgress(int(Progress / TotalNodeCount * 100))
					NodeNumber += 1
					# Check to see if any of the sourceNodes still have errors...
					self.SourceNodesWithErrors = Node_Tools()._find_nodes_with_errors(self.sourceNodes)
				# If the user cancelled, bail out.
				if self.cancel:
					# Cleanup progress bar task...
					if self.MainTask:
						del self.MainTask
					print ('Source Node Path Repair cancelled.')
					nuke.message('Source Node Path Repair cancelled.')
					return
				# If there are still errors, ask the user if he wants to run the repair again...
				elif self.SourceNodesWithErrors:
					if nuke.ask('There are still nodes with broken file path links. Do you want to run repair nodes again...?'):
						NodeNumber = 1
						continue
					else:
						# The user doesn't mind leaving some broken path links... Clean up and return.
						# Cleanup progress bar task...
						if self.MainTask:
							del self.MainTask
						# Calculate how long it took...
						self.elapsed = (time.time() - self.start_time)
						print "Time elapsed:", self.elapsed, "seconds"
						self.finalmessage = self.finalmessage + ('\nTime elapsed: %s seconds' % self.elapsed)
						nuke.message(self.finalmessage)
						return			
				# If there are no more nodes with errors, clean up and return.
				else:
					# Cleanup progress bar task...
					if self.MainTask:
						del self.MainTask
					# Calculate how long it took...
					self.elapsed = (time.time() - self.start_time)
					print "Time elapsed:", self.elapsed, "seconds"
					self.finalmessage = self.finalmessage + ('\nTime elapsed: %s seconds' % self.elapsed)
					nuke.message(self.finalmessage)
					return
			else:
				# The user wants to skip the repair of broken links. Just return...
				self.SourceNodesWithErrors = []
				return
		else:
			# Yay - here are no source nodes with errors! Just return...
			nuke.message('No broken links found.')
			return

'''
##########################################
## TESTING IN Nuke...
##########################################

sourceNodes = nuke.selectedNodes()

import CollectSourceFiles.SourceNodePathRepair
reload(CollectSourceFiles.SourceNodePathRepair)

SNR = CollectSourceFiles.SourceNodePathRepair.SourceNodePathRepair()

SNR.repair_path(sourceNodes)

'''
