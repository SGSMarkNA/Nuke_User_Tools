import nuke
import os
import sys
import shutil
import re
import glob
import subprocess
#------------------------------------------------------------
from .SourceNodeInfo import NodeInfo
#from SourceNodePathRepair import SourceNodePathRepair
from . import PathRepairPanel
## Need this to find the Node_Tools folder, which is relative to this file...
NodeToolsDir = os.path.realpath(os.path.dirname(__file__) + '/..') + '/Node_Tools'
os.sys.path.append(NodeToolsDir)
from Node_Tools.Node_Tools import Node_Tools
#------------------------------------------------------------


class CollectSourceFiles(object):
	'''
	Copies all of the source files for the current script into a new folder and re-links
	the source nodes to the copies. Saves the modified script into the same directory.
	Useful for archiving scripts or transporting them to another computer or location.
	'''

	def __init__(self):
		'''
		Initialize some variables and run the main method.
		'''
		self.scriptName = os.path.basename(nuke.Root().name())
		self.videoExtension = ['mov', 'avi', 'mpeg', 'mpg', 'mp4', 'R3D']
		self.DUPE_NUM = 000
		self.cancelCollect = 0	

	def _set_destination_Panel(self):
		'''
		Build simple panel to select or enter main directory path for all the collected source files...
		'''
		colPanel = nuke.Panel("Collect Source Files")
		colPanel.addFilenameSearch("Output Path:", "")
		colPanel.addButton("Cancel")
		colPanel.addButton("OK")
		colPanel.setWidth(600)
		retVar = colPanel.show()
		pathVar = colPanel.value("Output Path:")
		return (retVar, pathVar)

	def _prompt_for_dest_path(self):
		'''
		Run collectPanel to get the destination targetPath from the user...
		'''
		self.targetPath = ''
		panelResult = self._set_destination_Panel()
		# Some checks for the panelResult value...
		if panelResult[0] == 1 and panelResult[1] != '':
			self.targetPath = panelResult[1]
			# Check to make sure a file path is not passed through
			if os.path.isfile(self.targetPath):
				self.targetPath = os.path.dirname(self.targetPath)
			# Make sure target path ends with a slash (for consistency)
			if not self.targetPath.endswith('/'):
				self.targetPath += '/'
			return self.targetPath
		# If they just hit OK on the default ellipsis...
		elif panelResult[0] == 1 and panelResult[1] == '':
			nuke.message('Select a path or Cancel...')
			# Run it again, in case the user just goofed...
			self.targetPath = self._prompt_for_dest_path()
		# If they hit CANCEL...
		else:
			self.cancelCollect = 1
			return None
		# Return the chosen directory path...
		return self.targetPath

	def _create_target_dir(self, targetPath):
		'''
		Check if destination targetPath directory already exists; ask to create it if it doesn't...
		'''
		self.targetPath = targetPath
		if not os.path.exists(self.targetPath):
			if nuke.ask('Destination Directory does not exist.\nCreate it now?'):
				try:
					os.makedirs(self.targetPath)
				except:
					raise Exception('Cannot create Destination Directory!')
			else:
				nuke.message('Sorry, cannot proceed without valid Destination Directory!')
				return False

	def _create_footage_dir(self):
		'''
		Creates the "footage" subdirectory under the targetPath to copy all the collected source files...
		'''
		self.footagePath = self.targetPath + 'footage/'
		if (os.path.exists(self.footagePath)):
			pass
		else:
			try:
				os.mkdir(self.footagePath)
			except:
				raise Exception('Cannot create footage directory!')

	def _check_for_knob(self, node, checkKnob):
		'''
		Test to see if the node has a particular knob...
		'''
		try:
			node[checkKnob]
		except NameError:
			return False
		else:
			return True

	def _copy_with_robocopy_subprocess(self, cmd):
		'''
		Used in place of shutil for faster Windows file copying for file sequences.

		EXAMPLE arguments to build "cmd":
		    cmd = None
		    dirPath = '"X:\\AW\\ARMW-17-010_AW_Hyundai_E-photo_test\\work\\s01_Hyundai_Ephoto\\img\\ren\\KONA_360_EPHOTO_TEST_002"'
		    prefix = '"order_21517_Beauty_item_*"'
		    ext = '".exr"'
		    newDir = '"U:\\rbobo\\TEST\\COPY_SPEED_TESTING"'
		    robocopy = "robocopy"
		    cmd = [robocopy, dirPath, newDir, prefix]
		    cmd = " ".join(cmd)

		#-----------------------
		#  IMPORTANT NOTES:
		#-----------------------
		# All elements in cmd are protected with single/double quotes, to protect the doubles -- EXCEPT for the robocopy command!
		# Backslashes are escaped.
		# The cmd list of arguments are first ' '.join'ed together into a string to pass to subprocess.call
		# The filename wildcard specification is the THIRD argument, AFTER the source/destination folder arguments. That is proper robocopy syntax.		
		'''
		proc = subprocess.call(cmd)

	##---------------------------------------------------------------------------------------
	##--- Primary Copy and Re-Link Method ---------------------------------------------------

	def _copy_and_relink_source_files(self, sourceNode):
		'''
		Use shutil.copy2 to do the copying from the source node filepath to the new targetPath/footage/ directory...
		'''
		#---- Check to see if the node needs to be copied as a sequence, not a single file...
		try:
			self.seqCheck = NodeInfo().get_info(sourceNode)['seqCheck']
		except:
			pass
		#---- Check to see if the node has a "first" frame knob...
		if self._check_for_knob(sourceNode, 'first'):
			self._get_frame_range(sourceNode)
			#---- If it's one of the movie file types...
			if (self.fileNodePath.endswith(tuple(self.videoExtension))):				
				self._copy_movie_file(sourceNode)
				self._relink_movie_file(sourceNode)			
			#---- If it's a single image...
			if (self.firstFrame == self.lastFrame):
				self._copy_single_frame_file(sourceNode)
				self._relink_single_frame_file(sourceNode)
			#---- If it's a frame sequence...
			elif self.seqCheck:
				self._copy_frame_sequence(sourceNode)
				self._relink_frame_sequence(sourceNode)
		else:
			self._copy_single_source_file(sourceNode)
			self._relink_single_source_file(sourceNode)

	##-----------------------------------------------------------------------------------------------
	##--- Utility Methods used by "_copy_and_relink_source_files" -----------------------------------

	def _get_frame_range(self, sourceNode):
		self.firstFrame = NodeInfo().get_info(sourceNode)['firstFrame']
		self.firstFrame = int(self.firstFrame)
		self.lastFrame = NodeInfo().get_info(sourceNode)['lastFrame']
		self.lastFrame = int(self.lastFrame)
		self.framesDur = NodeInfo().get_info(sourceNode)['length']
		self.framesDur = int(self.framesDur)

	#-----------------------------------------------------------------------------------------------
	def _copy_movie_file(self, sourceNode):
		'''
		Movie file types, defined in self.videoExtension...
		'''
		# Get the evaluated file path...
		self._assign_source_node_path_vars_and_create_new_dir(sourceNode)
		# Assemble the new file output path...
		self.newMovieFilePath = self.newDir + self.Filename
		#print ''
		#print 'self.newMovieFilePath ====>>> ', self.newMovieFilePath
		# Start a new task message...
		task = nuke.ProgressTask('Copy Movie File:')		
		if (os.path.exists(self.fileNodePath)):
			task = nuke.ProgressTask('Copy Movie:')			
			shutil.copy2(self.fileNodePath, self.newMovieFilePath)
			task.setMessage('Copying %s' % self.Filename)
			if (os.path.exists(self.newMovieFilePath)):
				print(self.newMovieFilePath + ' movie file COPIED...')
			else:
				print('ERROR: ' + self.newMovieFilePath + ' movie file MISSING!')

	def _relink_movie_file(self, sourceNode):
		# Store the original raw contents of the source file knob in the label knob. We might need to know where
		# the original files came from or if there were expressions or metadata used in the original pathname...
		rawKnob = NodeInfo().get_info(sourceNode)['rawKnob']
		rawKnob = 'Original Path:\n' + rawKnob
		sourceNode['label'].setValue(rawKnob)		
		self.relinkPath = self.newMovieFilePath
		sourceNode['file'].setValue(self.relinkPath)

	#-----------------------------------------------------------------------------------------------

	def _copy_single_frame_file(self, sourceNode):
		'''
		This is the typical single image file, such as a JPEG file that is not an indexed sequence...
		'''
		self._assign_source_node_path_vars_and_create_new_dir(sourceNode)
		# Assemble the new file output path...
		self.newSingleFrameFilePath = self.newDir + self.Filename
		#print ''
		#print 'self.newSingleFrameFilePath ====>>> ', self.newSingleFrameFilePath
		# Start a new task message...
		task = nuke.ProgressTask('Copy Single Frame File:')
		if (os.path.exists(self.fileNodePath)):		
			shutil.copy2(self.fileNodePath, self.newSingleFrameFilePath)
			# Update the progress bar message...
			task.setMessage('Copying %s' % self.Filename)
			if (os.path.exists(self.newSingleFrameFilePath)):
				print(self.newSingleFrameFilePath + ' single frame file COPIED...')
			else:
				print('ERROR: ' + self.newSingleFrameFilePath + ' single frame file MISSING!')

	def _relink_single_frame_file(self, sourceNode):
		# Store the original raw contents of the source file knob in the label knob. We might need to know where
		# the original files came from or if there were expressions or metadata used in the original pathname...
		rawKnob = NodeInfo().get_info(sourceNode)['rawKnob']
		rawKnob = 'Original Path:\n' + rawKnob
		sourceNode['label'].setValue(rawKnob)		
		self.relinkPath = self.newSingleFrameFilePath
		sourceNode['file'].setValue(self.relinkPath)

	#-----------------------------------------------------------------------------------------------

	def _copy_single_source_file(self, sourceNode):
		'''
		This is likely to be some kind of data file that is part of a node, like a geo file in a ReadGeo node, for example...
		'''
		self._assign_source_node_path_vars_and_create_new_dir(sourceNode)
		# Assemble the new file output path...
		self.newSingleSourceFilePath = self.newDir + self.Filename
		#print ''
		#print 'self.newSingleSourceFilePath ====>>> ', self.newSingleSourceFilePath
		# Start a new task message...
		task = nuke.ProgressTask('Copy Single Source File:')		
		if (os.path.exists(self.fileNodePath)):
			shutil.copy2(self.fileNodePath, self.newSingleSourceFilePath)
			task.setMessage('Copying %s' % self.Filename)
			if (os.path.exists(self.newSingleSourceFilePath)):
				print(self.newSingleSourceFilePath + ' single source file COPIED...')
			else:
				print('ERROR: ' + self.newSingleSourceFilePath + ' single source file MISSING!')

	def _relink_single_source_file(self, sourceNode):
		# Store the original raw contents of the source file knob in the label knob. We might need to know where
		# the original files came from or if there were expressions or metadata used in the original pathname...
		rawKnob = NodeInfo().get_info(sourceNode)['rawKnob']
		rawKnob = 'Original Path:\n' + rawKnob
		sourceNode['label'].setValue(rawKnob)		
		self.relinkPath = self.newSingleSourceFilePath
		try:
			sourceNode['file'].setValue(self.relinkPath)
		except:
			sourceNode['vfield_file'].setValue(self.relinkPath)

	#-----------------------------------------------------------------------------------------------

	def _copy_frame_sequence(self, sourceNode):
		'''
		Copy frame sequences to the new directory...
		'''
		self._assign_source_node_path_vars_and_create_new_dir(sourceNode)
		# Get the first part of the original sequence filename, without the frame number or extension...
		self.prefix = NodeInfo().get_info(sourceNode)['prefix']
		#print 'self.prefix ------------>', self.prefix
		# Get the file extension to use in the glob.iglob path filter. Otherwise we might copy .vrimg files or other things in the folder...
		self.ext = NodeInfo().get_info(sourceNode)['fileExt']
		#print 'self.ext ------------>', self.ext
		# Use a wildcard to search for the sequence files and create an iglob list iterator to use for looping through the list of frames in the sequence...
		self.fileList = glob.iglob(os.path.join(self.dirPath + self.prefix + "*" + self.ext))
		self.fileList = sorted(self.fileList)
		#print 'self.fileList ----------->>>', self.fileList
		# Set up a progress bar task for these longer sequence copy operations...
		self.length = NodeInfo().get_info(sourceNode)['length']
		task = nuke.ProgressTask('%s (%s files)' % ('Copy Frame Sequence', self.length))
		# Copy the frame sequence files to the new directory...
		for i, Frame in enumerate(self.fileList):
			# Windows puts a '\\' separator after the parent directory... 
			if os.name == 'nt':
				Frame = Frame.replace('\\', '/')
			# Allow the user to cancel...
			if task.isCancelled() or self.mainTask.isCancelled():
				self.cancelCollect = 1
				# Clean up the progress bar task, just in case it wants to hang around after it's needed...
				del(task)
				break			
			# Get just the file name portion...
			Filename = Frame.split("/")[-1]
			#print 'Filename ------>', Filename
			# Assemble the filepath for the frame copy...
			NewFrame = self.newDir + Filename
			#print ''
			#print 'NewFrame ====>>> ', NewFrame

			###################################
			# If OS is Windows, do the copy using robocopy in a subprocess...
			if os.name == 'nt':
				cmd = None
				robocopy = "robocopy"
				dirPath = '"' + self.dirPath + '"'
				#print dirPath
				newDir = '"' + self.newDir + '"'
				#print newDir
				prefix = '"' + self.prefix + '"'
				#print prefix
				ext = '"' + self.ext + '"'
				#print ext
				wildcard = prefix + '*' + ext
				#print wildcard
				cmd = [robocopy, dirPath, newDir, wildcard]
				#print cmd
				cmd = " ".join(cmd)
				# Use robocopy in Windows Command Prompt subprocess...
				self._copy_with_robocopy_subprocess(cmd)
			# If OS is macOS, do the copy using shutil...
			elif os.name == 'posix':
				shutil.copy2(Frame, NewFrame)
			###################################
			# Update the progress bar message...
			task.setMessage('Copying %s' % Filename)
			task.setProgress(int(float(i) / self.length * 100))			
			# Check to see if it succeeded...
			#if (os.path.exists(NewFrame)):
				#print NewFrame + ' COPIED...'					
			#else:
				#print 'ERROR: ' + NewFrame + ' MISSING!'

	def _relink_frame_sequence(self, sourceNode):
		# Store the original raw contents of the source file knob in the label knob. We might need to know where
		# the original files came from or if there were expressions or metadata used in the original pathname...
		rawKnob = NodeInfo().get_info(sourceNode)['rawKnob']
		rawKnob = 'Original Path:\n' + rawKnob
		sourceNode['label'].setValue(rawKnob)		
		# Get the unevaluated padded filename (e.g., %04d) from the original raw path in the sourceNode...
		self.FilenameForRelink = NodeInfo().get_info(sourceNode)['FilenameForRelink']
		# Combine the new directory with the padded filename...
		self.relinkPath = self.newDir + self.FilenameForRelink
		# Set the new fileknob value...
		sourceNode['file'].setValue(self.relinkPath)

	#-----------------------------------------------------------------------------------------------

	def _assign_source_node_path_vars_and_create_new_dir(self, sourceNode):
		'''
		Sets up the directory paths for source and destination - and creates the destination directory...
		'''
		################################################################################################
		## TO DO:
		##       - Make a list of all the "used pathnames" for each node.
		##       - Add a check to see if the rawKnob value for the current sourceNode matches.
		##       - If so, don't make a new dir., just relink the node's path to it.
		################################################################################################

		#Check to see if the new directory already exists. If it does, append "___dupe_<DUPE_NUM>" to the parent dir. name, so it is unique...
		if (os.path.exists(self.newDir)):
			#print ''
			#print self.newDir + ' already exists.'
			self.DUPE_NUM +=1
			# Change the value of self.newDir to add the extra "__dupe_" to the name...
			self.newDir = self.footagePath + self.ParentDir + '___dupe_' + str(self.DUPE_NUM) + '/'
			try:
				os.mkdir(self.newDir)
				#print ''
				#print 'Duplicate directory created --> ' + self.newDir
			except Exception as e:
				print(e)
				print("Cannot make directory " + self.newDir)
				raise
		else:
			try:
				os.mkdir(self.newDir)
				#print 'Created --> ' + self.newDir
			except Exception as e:
				print("Cannot make directory " + self.newDir)
				raise

		# This version just copies into the existing directory if it's the same name...
		# 
		#if (os.path.exists(self.newDir)):
			#print ''
			#print self.newDir + ' already exists.'
		#else:
			#try:
				#os.mkdir(self.newDir)
				#print 'Created --> ' + self.newDir
			#except Exception as e:
				#print "Cannot make directory " + self.newDir
				#raise

	###################################################################################
	##    -----------      MAIN METHODS:       ----------
	###################################################################################

	def collect_source_files(self):
		''''''
		# Prompt the user for the destination directory...
		nuke.message('COLLECT SOURCE FILES:\n\nPlease pick a Destination Directory for the Collected Files...')
		self.targetPath = self._prompt_for_dest_path()
		# Init some progress bar starter values...
		self.progress = 0.0
		self.finishedNodes = 1
		# If the user did not Cancel...
		if self.cancelCollect == 0:
			# Gather up all of the source nodes in the script...
			self.AllNodes = Node_Tools()._get_all_nodes(nuke.root())
			if self.AllNodes:
				self.sourceNodes = Node_Tools()._find_all_source_nodes(self.AllNodes)
			else:
				nuke.message('No nodes found!')
				return
			##-----------------------------------------------------
			##--- CHECK FOR AND REPAIR ANY BROKEN LINKS -----------

			# Before copying source files, run PathRepairPanel to see if there any file paths with broken links and offer to repair them...
			check = PathRepairPanel.start_panel()
			#print 'check ===================>>>>> ', check
			if check:
				# Create the new directory for the collected files...
				self._create_target_dir(self.targetPath)
				# Create the footage subdir...
				self._create_footage_dir()				
				# Copy and relink methods, with progress bar...
				if self._run_copy_and_relinking():
					# Clean up the main progress bar task...
					del(self.mainTask)
					# If the user cancelled, we'll end up here...
					if self.cancelCollect == 1:
						print ('Collect Source Files cancelled!')
						nuke.message('Collect Source Files cancelled!')
					else:
						##----------------------------------
						##--- SAVE THE NEW SCRIPT ----------

						self.newScriptPath = self.targetPath + self.scriptName
						nuke.scriptSaveAs(self.newScriptPath)
						print('')
						print('Saved new script to ------>', self.newScriptPath)
						print ('Collect Source Files COMPLETE.')
						nuke.message('Collect Source Files COMPLETE.')
			else:
				if nuke.ask('BROKEN LINKS REMAIN:\n\nDo you still wish to Collect Files now?'):
					# Create the new directory for the collected files...
					self._create_target_dir(self.targetPath)
					# Create the footage subdir...
					self._create_footage_dir()					
					# Copy and relink methods, with progress bar...
					if self._run_copy_and_relinking():
						# Clean up the main progress bar task...
						del(self.mainTask)
						# If the user cancelled, we'll end up here...
						if self.cancelCollect == 1:
							print ('Collect Source Files cancelled!')
							nuke.message('Collect Source Files cancelled!')
						else:
							##----------------------------------
							##--- SAVE THE NEW SCRIPT ----------

							self.newScriptPath = self.targetPath + self.scriptName
							nuke.scriptSaveAs(self.newScriptPath)
							print('')
							print('Saved new script to ------>', self.newScriptPath)
							print ('Collect Source Files COMPLETE.')
							nuke.message('Collect Source Files COMPLETE.')
				else:
					print ('Collect Source Files cancelled.')
					nuke.message('Collect Source Files cancelled.')					
					return
		# If we cancelled the directory input panel, we'll end up here...
		else:
			print ('Collect Source Files cancelled.')
			nuke.message('Collect Source Files cancelled.')	


	def _run_copy_and_relinking(self):
		''''''
		##-----------------------------------------------------
		##--- DO THE COPYING AND RE-LINKING -------------------

		# Start a task progress bar...
		self.totalNodeCount = len(self.sourceNodes)
		self.mainTask = nuke.ProgressTask('Collect Files: ')
		# Start the main loop...
		for sourceNode in self.sourceNodes:
			# Check to see if the sourceNode has an error...
			if sourceNode.hasError():
				# Skip copying and relinking this sourceNode, it still .hasError()...
				#print 'sourceNode ------>>>>', sourceNode.name(), sourceNode.hasError()
				print('')
				print('SKIPPING sourceNode ' + sourceNode.name())
				#pass			
			else:
				if self.mainTask.isCancelled():
					self.cancelCollect = 1
					break
				# Set the progress bar message...
				self.mainTask.setMessage('%s / %s Nodes' % (self.finishedNodes, self.totalNodeCount))
				try:
					# Get the raw file knob filepath...
					self.rawKnob = NodeInfo().get_info(sourceNode)['rawKnob']					
					# Get the file knob value, so we can set the path and do other stuff...
					self.fileNodePath = sourceNode.knob('file').value()
				except:
					# Must be a Vectorfield node and has a 'vfield_file' knob, instead of a 'file' knob...
					# Get the raw file knob filepath...
					self.rawKnob = NodeInfo().get_info(sourceNode)['rawKnob']
					# Get the file knob value, so we can set the path and do other stuff...
					self.fileNodePath = sourceNode.knob('vfield_file').value()
				#print '\n'
				#print sourceNode.name() + ' ----> ' + self.fileNodePath
				# If there's no pathname in the knob, skip this node and continue with the next...
				if self.fileNodePath:
					##-----------------------------------------------------------
					##--- COPY AND RE-LINK THE FILE FOR THIS sourceNode. -------

					# Set the filename for copying the nodes that represent single files or single frames...
					self.Filename = NodeInfo().get_info(sourceNode)['Filename']

					# Get the parent directory of the original file...
					self.dirPath = NodeInfo().get_info(sourceNode)['dirPath']
					#print ''
					#print 'self.dirPath ----------> ', self.dirPath

					# Get the immediate parent directory for the original file...
					self.ParentDir = self.dirPath.split('/')[-2]
					#print ''
					#print 'self.ParentDir ----------> ', self.ParentDir					

					# Set the full newDirPath for copying the collected files...
					self.newDir = self.footagePath + self.ParentDir + '/'
					#print ''
					#print 'self.newDir ====>>> ', self.newDir
					# Do the copying and re-linking...
					self._copy_and_relink_source_files(sourceNode)				
				else:
					pass
				# Update the main progress bar...					
				self.finishedNodes += 1
				self.progress += 1
				self.mainTask.setProgress(int(self.progress / self.totalNodeCount * 100))
		return True



'''
#########################################
##  Auto-runs when Class is initialized
#########################################

# Initialize the Class...
def Run_CollectSourceFiles():
	CSF = CollectSourceFiles()

# Run it...
Run_CollectSourceFiles()

'''





'''
##########################################
## TESTING IN Nuke...
##########################################

import CollectSourceFiles.CollectSourceFiles

## Initialize the Class...
CSF = CollectSourceFiles.CollectSourceFiles

## Run it...
CSF.CollectSourceFiles()

'''