# This is for debugging in vanilla Python - with no Nuke...
try:
	import nuke
except ImportError:
	nuke = None
import sys
import os
import errno
import shutil
import socket
import tag_data_file
# Rename the imported utils class from the tag_data_file...
TagsFileUtils = tag_data_file.TagsFileUtils
# Make a global variable for self.args_file_path in the main module.
# This is necessary because we create an instance of the class twice: once for the beforeRender callback - the create_args_file method - but it gets destroyed afterward, along with any self.xxxxx variables we created.
# Then, we create another instance of the class for the afterFrameRender callback - the tag_images method. When we run the second instance, it doesn't know about the "self.args_file_path" variable we already created.
# So, by storing it in the module at the end of the first method, we can retrieve it before running the second method...
_Global_args_file_path = None


class TagImages(object):
	''' The TagImages class uses the exiftool metadata utility to add XMP style metadata to images. These data tags may be viewed in Photoshop.
	Two methods are used as callbacks in a Nuke Write node's Python tab: The first method, create_args_file(), operates as a beforeRender
	callback and generates a text file containing tag arguments for exiftool to use. On a Nuke Write node, add "TagImages.TagImages().create_args_file()"
	in the Write node's Python tab in the "before render" field. The second method, tag_images(), operates as an afterFrameRender callback.
	On the same Nuke Write node, add "TagImages.TagImages().tag_images()" in the Write node's Python tab in the "after each frame" field.
	For further info on exiftool, go to --> http://www.sno.phy.queensu.ca/~phil/exiftool/

	WARNING: Metadata tagging for Photoshop does *not* work with PNG Files! It is recommended to use TIF files. Other formats may work, but have not been tested...

	Created by Rich Bobo - 04/04/2014
	richbobo@mac.com
	http://richbobo.com
	'''	
	def __init__(self):

		# Build exiftool executable path for Windows...
		if os.name == 'nt':
			try:
				def get_exiftool_executable():
					BIN = os.environ.get("AW_COMMAND_LINE_APPS")
					EXE = "exiftool.exe"
					PATH = os.path.join(BIN, EXE)
					EXECUTABLE = '"%s"' % PATH
					return EXECUTABLE
				self.EXECUTABLE = get_exiftool_executable()
			except:
				print("ERROR: Cannot find path to exiftool executable! Exiting now.")
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return	
		# Test for MacOS location of exiftool executable...
		elif os.name == 'posix':
			home_dir = os.environ.get('HOME')
			# If I'm at home testing, this is the binary location... Also would be for a local Mac OS X system - just wouldn't need the home_dir test, of course...
			if home_dir == "/Users/richbobo":			
				if os.path.exists('/usr/local/bin/exiftool'):
					#print 'Found exiftool at /usr/local/bin/exiftool'
					pass
			elif home_dir == "/Users/rbobo":			
				if os.path.exists('/usr/local/bin/exiftool'):
					#print 'Found exiftool at /usr/local/bin/exiftool'
					pass
			else:
				print("ERROR: Cannot find path to exiftool executable! Exiting now.")
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

	def create_args_file(self):
		''' Function that writes the temp file containing metadata tag arguments for the exiftool command.'''
		global _Global_args_file_path
		# Get the returned file path from the saved file...
		self.args_file_path = self.write_args_file(file_name=self.args_filename, args_list=self.args)
		# Sanity check to see if we got anything back from the tags file...
		if self.args_file_path:
			#print "Args file saved to: ", self.args_file_path
			pass
		else:
			print("ERROR: Tags file not saved!")
			if nuke.GUI:	
				nuke.critical("Tags file not saved!\n Something went wrong with the image metadata tagging!")
			return	
		# Store the value in a global variable, so we can retrieve it when tag_images runs.
		_Global_args_file_path = self.args_file_path

	def _get_lists_of_stored_trims_and_colors(self):
		# Initialize the list for holding all of the trim and color data...
		TrimsColorsList = []
		self.TrimsList = []
		self.ColorsList = []
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
				# Initialize the TrimsList and ColorList...
				TrimsList = []
				ColorsList = []
				# Iterate through the TrimsColorsList and separate into a trims list and a colors list...
				for x in TrimsColorsList:
					if x != "COLORS:":
						TrimsList.append(x)
					else:
						break
				ColorsList = list(set(TrimsColorsList) - set(TrimsList))
				TrimsList.pop(0)
				ColorsList.pop(0)
				self.TrimsList = TrimsList
				self.ColorsList = ColorsList

	def _get_trim_and_color_for_view(self):
		color = ''
		trim = ''
		# view to the currently active view...
		view = nuke.thisView()
		# Get the current view's trim and color parts by comparing to the current view name...
		if self.TrimsList:
			for t in self.TrimsList:
				if t in view:
					trim = t
					break
			for c in self.ColorsList:
				if c in view:
					color = c
					break
			return trim, color
		else:
			trim, color = None, None
			return trim, color		

	def tag_images(self):
		'''
		Function that executes the exiftool command, using the temp file containing metadata tag arguments created by create_args_file.
		TIF images are tagged with Armstrong White identifier info. Also, if it's an Innocean/Hyundai project, a special folder hierarchy
		is created.
		'''	
		# Make the args file path available as a global variable.
		global _Global_args_file_path
		# Retrieve the stored value that was created when create_args_file ran...
		self.args_file_path =_Global_args_file_path
		# Get the path for the current frame we're rendering...
		self.current_frame_path = nuke.filename(nuke.thisNode(),nuke.REPLACE)
		# Get the stored lists of trim and colors...
		self._get_lists_of_stored_trims_and_colors()
		# Get the trim and color values for the current view...
		trim, color = self._get_trim_and_color_for_view()	
		# Check for the current OS and choose which executable flavor of exiftool to use...
		if os.name == 'nt':
			home_dir = os.environ.get('HOMEPATH')
			# Operates on a single frame. This works well on the farm.
			exec_string = self.EXECUTABLE + ' -@ ' + self.args_file_path + " " + self.current_frame_path
			#print 'exec_string ---------->', exec_string
		elif os.name == 'posix':
			home_dir = os.environ.get('HOME')
			# If I'm at home testing, this is the binary location... Also would be for a local Mac OS X system - just wouldn't need the home_dir test, of course...
			if home_dir == "/Users/richbobo":
				exec_string = "/usr/local/bin/exiftool -@ " + self.args_file_path + " " + self.current_frame_path
				#print 'exec_string ---------->', exec_string
			else:
				# Operates on a single frame. This works well on the farm.
				exec_string = 'exiftool -@ ' + self.args_file_path + " " + self.current_frame_path
				#print 'exec_string ---------->', exec_string
		# Run the exiftool command on the rendered files, with arguments supplied by self.args_file_path...
		try:
			os.system(exec_string)
		except:
			print("ERROR: Metadata Tagging Failed!\n Something went wrong with the image metadata tagging!")
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
					print("INFO: Tagging probably suceeded, but the removal of duplicate images failed.\n You will have to remove any images ending with _original, yourself...")
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
		# Check to see if we have trim and color data to work with. If so, use it to compare to the current view name and create directories for the corresponding trim and color...
		if trim is not None and color is not None:
			# Set the args directory so we can create it later, if it doesn't exist...
			self.dir_view_name = os.path.dirname(self.current_frame_path).split("/").pop()
			self.new_base_dir = os.path.dirname(self.current_frame_path).replace(self.dir_view_name,"")
			self.dir_to_create = self.new_base_dir + trim + "/" + color
			# Try to create the trim and color directories and cope with the directory already existing by ignoring that exception...
			if os.path.isdir(self.dir_to_create):
				pass
			else:
				try:
					os.makedirs(self.dir_to_create)
				except OSError as e:
					if e.errno != errno.EEXIST:
						raise
				if os.path.isdir(self.dir_to_create):
					print("Created output directory: %s " % (self.dir_to_create))
				else:
					print("ERROR: Directory %s cannot be created." % (self.dir_to_create))
					if nuke.GUI:
						nuke.message("Directory cannot be created. Press OK to cancel." % (self.dir_to_create))		
			# Build pieces for new frame file path...
			self.current_frame_file = os.path.basename(self.current_frame_path)
			self.new_frame_path = self.dir_to_create + "/" + self.current_frame_file
			# Move the current rendered file to the new directory path that has the trim and color folders...
			shutil.move(self.current_frame_path, self.new_frame_path)
			# Remove the old empty directory, if it's not empty...
			old_dir_to_remove = os.path.dirname(self.current_frame_path)
			if not os.listdir(old_dir_to_remove):
				os.rmdir(old_dir_to_remove)
		else:
			# There is no trim and color data in the Nuke Project Settings/comment panel, so we probably aren't using Nuke views in this comp. So, just tag the images and don't try to create the trim and color directories...
			pass
