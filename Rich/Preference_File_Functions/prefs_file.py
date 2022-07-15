try:
	import nuke
except ImportError:
	nuke = None
import os
import sys
import pickle
import errno

class PrefsFileUtils(object):
	
	'''
	Utility methods for writing and reading a list of preferences.
	
	write_prefs_file -- Takes three arguments: dir_name - a file path string, file_name - a prefs filename string (.pref will be appended) and prefs_list - a list of the values to save. Optionally, just specify the prefs_list and a default path will be used.
	read_prefs_file -- Takes two arguments: dir_name - a file path string, file_name - a prefs filename string (.pref will be appended). Returns prefs_list - a list of the saved values. Optionally, if no arguments given, will use a default path to try to find the prefs_file.
	
	Created by Rich Bobo - 11/01/2013
		richbobo@mac.com
		http://richbobo.com
	'''
	
	def __init__(self):

		# Get the current file's name - the calling file for these methods - and use it to name the prefs file when no filename is supplied...
		self.this_file = os.path.basename(__file__).split('.')[0]
		
		# Extension for file...
		self.prefs_ext = '.pref'
		
		# Run the method that checks for the OS and checks to see if we have successfully loaded Nuke before setting the location of the PREFS directory...
		self.environ_check()
		
	def environ_check(self):
		if os.name == 'nt':
			home_dir = os.environ.get('TEMP')
			sep = '\\'
		else:
			home_dir = os.environ.get('HOME')
			sep = '/'
		if not nuke:
			prefs_dir = sep + 'PREFS' + sep
		else:
			prefs_dir = sep + '.nuke' + sep + 'PREFS' + sep
		# Assign some constants...
		self.home_dir, self.prefs_dir, self.sep = home_dir, prefs_dir, sep
		# Set the default full path for the prefs file, based on the OS and whether or not we've loaded Nuke. This is used if no dir_name and no file_name are supplied...
		self.default_path = self.home_dir + self.prefs_dir + self.this_file + self.prefs_ext
	
	def write_prefs_file(self, dir_name=None, file_name=None, prefs_list=None):
		
		'''Method for saving a list of preferences. Takes three keyword arguments: dir_name - a file path string, file_name - a prefs filename string (.pref will be appended) and prefs_list - a list of the values to save.
		Otionally, only the prefs_list may be supplied and the preference file will be saved in a default path.'''

		# Assign self.prefs_list to the list supplied by the user. The prefs_list is the minimum info that needs to be supplied...
		self.prefs = prefs_list
		
		# If no directory and no filename provided, the prefs file will be saved in a new directory in the user's home directory path - or the .nuke directory, if Nuke is loaded...
		if dir_name is None and file_name is None :
			# Nothing supplied -- use the default path...
			self.prefs_file = self.default_path
		# If no directory provided -- only file_name, the prefs file will be saved in a default directory in the user's home directory path - or the .nuke directory, if Nuke is loaded...
		elif dir_name is None and file_name is not None:
			# Nothing supplied -- use the default path...
			self.prefs_file = self.home_dir + self.prefs_dir + file_name + self.prefs_ext		
		else:
			# Check for TypeErrors...
			if not isinstance(dir_name, str):
				raise TypeError("The first keyword argument, dir_name, needs to be a directory path string.")
			if not isinstance(file_name, str):
				raise TypeError("The second keyword argument, file_name, needs to be a filename string.")
			if not isinstance(prefs_list, list):
				raise TypeError("The third keyword argument, prefs_list, needs to be a list of values to be saved.")			
				
			# Build the path from the user supplied dir_name and file_name values...
			self.prefs_file = dir_name + self.sep + file_name + self.prefs_ext
				
		# Set the prefs directory so we can create it later, if it doesn't exist...
		self.dir_to_create = os.path.dirname(self.prefs_file)
		
		# Try to create the prefs directory and cope with the directory already existing by ignoring that exception...
		if os.path.isdir(self.dir_to_create):
			print("Directory %s already exists..." % (self.dir_to_create))
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
				if nuke:
					nuke.message("Directory cannot be created. Press OK to cancel." % (self.dir_to_create))
		# Try to save the file...
		try:
			self.prefs_save = open(self.prefs_file, 'w')
			pickle.dump(self.prefs, self.prefs_save)
			self.prefs_save.close()
			print("Prefs File saved to: %s" % (self.prefs_file))
			if nuke:		
				nuke.message("Prefs File saved to: %s" % (self.prefs_file))
		except:
			print("ERROR: Prefs cannot be saved to: %s" % (self.prefs_file))
			if nuke:		
				nuke.message("Prefs cannot be saved to: %s Press OK to cancel." % (self.prefs_file))
			return
				
	def read_prefs_file(self, dir_name=None, file_name=None):
		
		'''Method for retreiving a list of preferences, saved with the write_prefs_file method. Takes two arguments: dir_name - a file path string, file_name - a prefs filename string. Returns prefs_list - a list of the saved values.
		If dir_name and file_name not supplied, will try to use a default path to retrieve the pref settings.'''
		
		if dir_name is None and file_name is None :
			# Nothing supplied -- use the default path...
			self.prefs_file = self.default_path
		# If no directory provided -- only file_name, the prefs file will be saved in a default directory in the user's home directory path - or the .nuke directory, if Nuke is loaded...
		elif dir_name is None and file_name is not None:
			# Nothing supplied -- use the default path...
			self.prefs_file = self.home_dir + self.prefs_dir + file_name + self.prefs_ext	
		else:
			# Check for TypeErrors...
			if not isinstance(dir_name, str):
				raise TypeError("The first keyword argument, dir_name, needs to be a directory path string.")
			if not isinstance(file_name, str):
				raise TypeError("The second keyword argument, file_name, needs to be a filename string.")
			
			# Build the path from the user supplied dir_name and file_name values...
			self.prefs_file = dir_name + self.sep + file_name + self.prefs_ext
			
		# Try to read the prefs file, if it exists...
		if os.path.isfile(self.prefs_file):
			try:
				self.prefs_read = open(self.prefs_file, 'r')
				self.saved_prefs = pickle.load(self.prefs_read)
				self.prefs_read.close()
			except:
				print("Sorry - Prefs file %s cannot be read." % (self.prefs_file))
				if nuke:			
					nuke.message("Prefs file cannot be read:\n %s\n\n Press OK to continue.\n\n You will need to save a new Prefs file.\n On the next panel, check the box for  [x] <----- SAVE PREFS." % (self.prefs_file))
				self.prefs_read.close()
			finally:
				print("Prefs file loaded successfully from %s" % (self.prefs_file))
				print("self.saved_prefs --------->", self.saved_prefs)
				saved_prefs = self.saved_prefs
				return saved_prefs
			
		else:
			print("Sorry - Prefs file %s does not seem to exist." % (self.prefs_file))
			if nuke:		
				nuke.message("Prefs file cannot be read:\n %s\n\n Press OK to continue.\n\n You will need to save a new Prefs file.\n On the next panel, check the box for  [x] <----- SAVE PREFS." % (self.prefs_file))
			return None
			
#----------------------------------------------------------------------------------------------------------------------------
# Supply default arguments for testing... This form may be added to code that gets used in production
# because the class, method or function will typically be called from a Python executable or program
# that will become "__main__". Therefore, "__name__", which is this file, will not be "__main__" and
# this test will not ever be run...

if __name__=='__main__':
	
	# EXAMPLE VALUES:
	nodeSpacingX = '60'
	nodeSpacingY = '100'
	postage_stamps = False
	backdrop_off = False
	rand_color = False
	render_layers = 'Maya'
	Build = 'Int'
	TotalLightBuild = False
	
	PrefsList = [nodeSpacingX, nodeSpacingY, postage_stamps, backdrop_off, rand_color, render_layers, Build, TotalLightBuild]
	
	FileName = 'TEST_ConfigCompBuilder'	

	prefs = PrefsFileUtils()
	prefs.write_prefs_file(file_name=FileName, prefs_list=PrefsList)
	prefs.read_prefs_file(file_name=FileName)
