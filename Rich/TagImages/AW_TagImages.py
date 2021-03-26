try:
	import nuke
except ImportError:
	nuke = None

import os
if os.environ.has_key("AW_GLOBAL_SYSTEMS"):
	if not os.environ["AW_GLOBAL_SYSTEMS"] in os.sys.path:
		os.sys.path.append(os.environ["AW_GLOBAL_SYSTEMS"])
from Environment_Access import System_Settings

import sys
import errno
import shutil
import operator
import re
from difflib import SequenceMatcher

import tag_data_file
# Rename the imported utils class from the tag_data_file...
TagsFileUtils = tag_data_file.TagsFileUtils

# Make a global variable for self.args_file_path in the main module.
# This is necessary because we create an instance of the class twice: once for the beforeRender callback - the create_args_file method - but it gets destroyed afterward, along with any self.xxxxx variables we created.
# Then, we create another instance of the class for the afterFrameRender callback - the tag_images method. When we run the second instance, it doesn't know about the "self.args_file_path" variable we already created.
# So, by storing it in the module at the end of the first method, we can retrieve it before running the second method...
_Global_args_file_path = None


class AW_TagImages(object):
	''' The TagImages class uses the exiftool metadata utility to add XMP style metadata to images. These data tags may be viewed in Photoshop.
	Two methods are used as callbacks in a Nuke Write node's Python tab: The first method, create_args_file(), operates as a beforeRender
	callback and generates a text file containing tag arguments for exiftool to use. On a Nuke Write node, add "TagImages.TagImages().create_args_file()"
	in the Write node's Python tab in the "before render" field. The second method, tag_images(), operates as an afterFrameRender callback.
	On the same Nuke Write node, add "TagImages.TagImages().tag_images()" in the Write node's Python tab in the "after each frame" field.
	For further info on exiftool, go to --> http://www.sno.phy.queensu.ca/~phil/exiftool/

	WARNING: Use with TIF files only! IPTC metadata tagging of PNG files does *not* work with Photoshop. 
	'''	
	def __init__(self):
		''''''
		##print System_Settings.EXIF_TOOL
		# Build exiftool executable path for Windows...
		if os.name == 'nt':
			try:	
				self.EXECUTABLE = System_Settings.EXIF_TOOL
			except:
				print "ERROR: Cannot find path to exiftool executable! Exiting now."
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return
		# Build exiftool executable path for MacOS...
		elif os.name == 'posix':
			try:
				self.EXECUTABLE = '/usr/local/bin/exiftool'
			except:
				print "ERROR: Cannot find path to exiftool executable! Exiting now."
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return

		# Rename the imported utils class for clarity...
		self.args = TagsFileUtils()
		# Rename the write_args_file function for simplicity...
		self.write_args_file = self.args.write_args_file		
		# Get the Write node's render output pathname from the file knob...
		self.node_file_path = nuke.filename(nuke.thisNode())
		# Get OS-corrected slashes in the pathname - forward vs. backward...
		self.node_file_path = os.path.realpath( self.node_file_path )
		# This is the directory for the rendered images...
		self.render_dir = os.path.dirname(self.node_file_path)
		# Get the name of the Nuke script and use it as part of the temp file name...
		self.script_name = os.path.basename(nuke.root().name())
		self.name_parts = os.path.splitext(self.script_name)
		self.name = self.name_parts[0]
		# Name of the args file has the Nuke script name appended to avoid different renders writing to the same filename...
		self.args_filename = "TagImages" + "_" + self.name

		# Initialize various lists and dictionaries...
		self.TrimsList = None
		self.ColorsList = None
		self.trim_dirs_dict = None
		self.base_folders_dict = None
		self.ViewNamesList = []

		for View in (nuke.views()):
			self.ViewNamesList.append(View)
		self.base_dir_folders = self.ViewNamesList	

		'''Initialize the list for holding all of the trim and color data...'''
		self._get_lists_of_stored_trims_and_colors()


	def create_args_file(self):
		''' Function that writes the temp file containing metadata tag arguments for the exiftool command.'''
		global _Global_args_file_path
		# Get the returned file path from the saved file...
		self.args_file_path = self.write_args_file(file_name=self.args_filename, args_list=self.args)
		# Sanity check to see if we got anything back from the tags file...
		if self.args_file_path:
			##print "Args file saved to: ", self.args_file_path
			pass
		else:
			print "ERROR: Tags file not saved!"
			if nuke.GUI:	
				nuke.critical("Tags file not saved!\n Something went wrong with the image metadata tagging!")
			return	
		# Store the value in a global variable, so we can retrieve it when tag_images runs.
		_Global_args_file_path = self.args_file_path
		##print "CREATED ARGS FILE...."


	def get_current_frame_info(self):
		# Get the frame path from the Write node...
		self.current_frame_path = nuke.filename(nuke.thisNode(),nuke.REPLACE)
		##print 'current_frame_path --->', self.current_frame_path
		# Basename for current_frame_path...
		self.current_frame_file = os.path.basename(self.current_frame_path)
		##print 'current_frame_file --->', self.current_frame_file
		# Find the view_name subdirectory portion...
		self.dir_view_name = os.path.dirname(self.current_frame_path).split("/").pop()
		##print 'dir_view_name --->', self.dir_view_name		
		# Remove the view_name subdirectory portion of the path and set the base_dir...
		self.base_dir = os.path.dirname(self.current_frame_path).replace(self.dir_view_name,"")
		##print 'base_dir --->', self.base_dir


	def _get_lists_of_stored_trims_and_colors(self):
		''''''
		# Some temp. local finction vars...
		Trims = []
		Colors = []
		TrimsColorsList = []

		# Get the label data from the Nuke Project Settings/comment panel...
		data = nuke.Root().knob('label').value()
		# If there's nothing there, return None for the trim and color values, so we can handle that properly in the tag_images method...
		if data == "":
			trim, color = None, None
			return trim, color
		else:
			# Remove the empty lines and store the others...
			for d in str.splitlines(data):
				if d != '':
					TrimsColorsList.append(d)
			# Remove the first item, which is just a "do not modify" note to the user...
			# Check to be sure we have the exact header line that the ConfigCombuilder.TrimViewGenerator.storeTrimColorViews() method writes...			
			header_test = TrimsColorsList.pop(0)
			if header_test == "** DO NOT DELETE OR MODIFY THIS LIST! **":

				# Iterate through the self.TrimsColorsList and separate into a trims list and a colors list...
				for x in TrimsColorsList:
					if x != "COLORS:":
						Trims.append(x)
					else:
						break
				Colors = list(set(TrimsColorsList) - set(Trims))				
				Trims.remove('TRIMS:')
				Colors.remove('COLORS:')
				# Make these lists available to the whole Class...
				self.TrimsList = Trims
				self.ColorsList = Colors			
		##print "GOT STORED TRIMS AND COLORS...."


	def _get_trim_and_color_for_view(self, TrimsList):
		''''''
		# Get the current view's trim and color parts by comparing to the current view name...
		color = ''
		trim = ''

		# Get trim part of the view name...
		if self.TrimsList:
			# Find the best match for the base trim folder to put it in...
			trim = self.find_best_match(self.dir_view_name, self.TrimsList)
			##print trim
		else:
			trim = None
		# Get color part of the view name...
		if self.ColorsList:
			# Find the best match for the base trim folder to put it in...
			color = self.find_best_match(self.dir_view_name, self.ColorsList)
			##print color
		else:
			color = None
		##print 'trim --> ', trim
		##print 'color --> ', color		
		return trim, color


	def find_best_match(self, name, List):
		scores_dict = {}
		for item in List:
			##print 'item -----> ', item
			ratio = SequenceMatcher(None, name, item).ratio()
			##print str(ratio) +  '--->   ' + item
			# Make a dict of the matching items and their match scores...
			scores_dict[item] = ratio
			##print scores_dict
			Sorted_Scores = sorted(scores_dict.items(), key=lambda (key,value): value, reverse=True)
		##print Sorted_Scores
		BestScoresList = []
		for Item_Score in Sorted_Scores:
			if Item_Score[0] in name:
				BestScoresList.append(Item_Score[0])
			else:
				pass
		if BestScoresList: 
			Match = max(BestScoresList)
			##print item_dir
			##print name
			##print ''
			# Return the item_dir name in TrimsList that best matches the name name.
			return Match


	def tag_images(self):
		'''
		Uses exiftool to add Photoshop metadata to TIF images with Armstrong White identifier info.
		Gets data from the temp file containing metadata tag arguments created by create_args_file.
		'''
		global _Global_args_file_path
		# Retrieve the stored value that was created when create_args_file ran...
		self.args_file_path =_Global_args_file_path		
		##print 'self.args_file_path -->', self.args_file_path
		
		# Update variables for the current frame...
		self.get_current_frame_info()
		##print 'self.current_frame_path -->', self.current_frame_path
		
		##print 'self.EXECUTABLE -->', self.EXECUTABLE

		# Operates on a single frame. This works well on the farm.
		exec_string = self.EXECUTABLE + ' -@ ' + self.args_file_path + " " + self.current_frame_path
		##print 'exec_string ---------->', exec_string
		# Run the exiftool executable command on the rendered file, with arguments supplied by self.args_file_path...
		try:
			os.system(exec_string)
		except:
			print "ERROR: Metadata Tagging Failed!\n Something went wrong with the image metadata tagging!"
			if nuke.GUI:	
				nuke.critical("Metadata Tagging Failed!\n Something went wrong with the image metadata tagging!")
			return
		# Remove the duplicate xxxxxx.xxx_original" file that exiftool creates as a backup...
		dup_frame = self.current_frame_path + "_original"
		if os.path.isfile(dup_frame):
			try:
				os.remove(dup_frame)
				# Check to see if we removed the file...And, if not....
				if os.path.isfile(dup_frame):
					print "INFO: Tagging probably suceeded, but the removal of duplicate images failed.\n You will have to remove any images ending with _original, yourself..."
					if nuke.GUI:	
						nuke.message("INFO: Tagging probably suceeded, but the removal of duplicate images failed.\n You will have to remove any images ending with _original, yourself...")
					return
			# If the file doesn't exist, just ignore the error... 
			except OSError as e:
				# Some other kind of error must have occurred. Better let somebody know about it...
				if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
					raise
		else:
			pass
		##print "TAGGED IMAGE -->", self.current_frame_file


	def create_nested_color_and_trim_folders(self):
		''''''
		# Update variables for the current frame...
		self.get_current_frame_info()

		self.trim, self.color = self._get_trim_and_color_for_view(self.TrimsList)
		print 'self.trim --> ', self.trim
		print 'self.color --> ', self.color

		if self.trim is not None and self.color is not None:
			#self.dir_view_name = os.path.dirname(self.current_frame_path).split("/").pop()
			self.new_base_dir = os.path.dirname(self.current_frame_path).replace(self.dir_view_name,"")
			self.dir_to_create = self.new_base_dir + self.trim + "/" + self.color
			# Try to create the trim and color directories and cope with the directory already existing by ignoring that exception...
			if os.path.isdir(self.dir_to_create):
				pass
			else:
				try:
					os.makedirs(self.dir_to_create)
				except OSError, e:
					if e.errno != errno.EEXIST:
						raise
				if os.path.isdir(self.dir_to_create):
					print "Created output directory: %s " % (self.dir_to_create)
					pass
				else:
					print "ERROR: Directory %s cannot be created." % (self.dir_to_create)
					if nuke.GUI:
						nuke.message("Directory cannot be created. Press OK to cancel." % (self.dir_to_create))		
			# Build pieces for new frame file path...
			self.current_frame_file = os.path.basename(self.current_frame_path)
			self.new_frame_path = self.dir_to_create + "/" + self.current_frame_file
			# Move the current rendered file to the new directory path that has the trim and color folders...
			print 'self.current_frame_path --- ', self.current_frame_path
			print 'self.new_frame_path --- ', self.new_frame_path
			# Check to see if it's really there...
			####if os.path.isfile(self.current_frame_path):
			shutil.move(self.current_frame_path, self.new_frame_path)
			print 'MOVED DIR.--> ', self.current_frame_path, ' to ', self.new_frame_path
			# Remove the old empty directory, if it's not empty...
			old_dir_to_remove = os.path.dirname(self.current_frame_path)
			if not os.listdir(old_dir_to_remove):
				os.rmdir(old_dir_to_remove)
				print 'REMOVED OLD DIR.--> ', old_dir_to_remove
		else:
			# There is no trim and color data in the Nuke Project Settings/comment panel, so we probably aren't using Nuke views in this comp. So, just tag the images and don't try to create the trim and color directories...
			pass

