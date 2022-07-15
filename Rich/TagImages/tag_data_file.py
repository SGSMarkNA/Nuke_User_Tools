# This is for debugging in vanilla Python - with no Nuke...
try:
	import nuke
except ImportError:
	nuke = None
import os
import sys
import errno
import datetime

class TagsFileUtils(object):

	'''
	Utility methods for writing and reading a text file list of command arguments to exiftool.
	
	write_args_file -- Takes three arguments: dir_name - a file path string, file_name - an args filename string (.args will be appended) and args_list - a list of the values to save. Optionally, just specify the args_list and a default path will be used.
	read_args_file -- Takes two arguments: dir_name - a file path string, file_name - a args filename string (.args will be appended). Returns args_list - a list of the saved values. Optionally, if no arguments given, will use a default path to try to find the args_file.
	
	****WARNING****: Metadata tagging for Photoshop does *not* work with PNG Files! It is recommended to use TIF files. TGA and EXR image types are not supported by exiftool, as of this date.
	
	Created by Rich Bobo - 04/04/2014
	richbobo@mac.com
	http://richbobo.com
	'''
	
	def __init__(self):
		
		# Get the current file's name - the calling file for these methods - and use it to name the args file when no filename is supplied...
		self.this_file = os.path.basename(__file__).split('.')[0]
		
		# Extension for file...
		self.args_ext = '.args'
		
		# Run the method that checks for the OS and checks to see if we have successfully loaded Nuke before setting the location of the args directory...
		self.environ_check()
		
		# List of the XMP tag name args for exiftool to read as command line arguments - written to the TagImages.args file ...
		# http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/XMP.html   <-- Ref. for XMP tags...
		# ...Here are some additional Photoshop XMP Image Info tag fields I've discovered - in case we ever need them:
		#-xmp-Photoshop:AuthorsPosition=Artist
		#-xmp-Photoshop:Credit=Armstrong White
		#-xmp-Photoshop:State=Michigan
		
		# Get the system date. Used to get the current date in the format that exiftool likes...
		self.today = datetime.date.today ()
		
		# Current list of tags needed in Photoshop for client Innocean - for Hyundai deliverable images...
		self.date_created = "%s:%s:%s" % (str(self.today.year),str(self.today.month).zfill(2),str(self.today.day).zfill(2))		
		self.DateCreated =          '-xmp-Photoshop:DateCreated=%s' % self.date_created
		self.Creator =              '-xmp-dc:Creator=Armstrong White'
		self.CreatorAddress =       '-xmp-iptcCore:CreatorAddress=2125 E. Lincoln'
		self.CreatorCity =          '-xmp-iptcCore:CreatorCity=Birmingham'
		self.CreatorRegion =        '-xmp-iptcCore:CreatorRegion=Michigan'
		self.CreatorPostalCode =    '-xmp-iptcCore:CreatorPostalCode=48009'
		self.CreatorCountry =       '-xmp-iptcCore:CreatorCountry=USA'
		self.CreatorWorkTelephone = '-xmp-iptcCore:CreatorWorkTelephone=(248) 594-1818'
		self.CreatorWorkEmail =     '-xmp-iptcCore:CreatorWorkEmail=lindsay.blackwood@armstrong-white.com, lydia.kuivenhoven@armstrong-white.com'
		self.CreatorWorkURL =       '-xmp-iptcCore:CreatorWorkURL=http://armstrong-white.com'		
		# Put 'em all in a list...
		self.args_list = [self.DateCreated, self.Creator, self.CreatorAddress, self.CreatorCity, self.CreatorRegion, self.CreatorPostalCode, self.CreatorCountry, self.CreatorWorkTelephone, self.CreatorWorkEmail, self.CreatorWorkURL]
		
	def environ_check(self):
		
		'''Check to see what OS we're running, set the type of slash separator to use and construct the pathname for the args file.'''
		
		if os.name == 'nt':
			home_dir = os.environ.get('TEMP')
			sep = '\\'
		else:
			home_dir = os.environ.get('HOME')
			sep = '/'
		if not nuke:
			args_dir = sep + 'TAGS' + sep
		else:
			args_dir = sep + '.nuke' + sep + 'TAGS' + sep
		# Assign some constants...
		self.home_dir, self.args_dir, self.sep = home_dir, args_dir, sep
		# Set the default full path for the args file, based on the OS and whether or not we've loaded Nuke. This is used if no dir_name and no file_name are supplied...
		# The default path will be either (a) the user's home directory/TAGS/ - if Nuke is not running or (b) the user's home directory/.nuke/TAGS/ if Nuke is running.
		self.default_path = self.home_dir + self.args_dir + self.this_file + self.args_ext
	
	def write_args_file(self, dir_name=None, file_name=None, args_list=None):
		
		'''Method for saving a list of args for exiftool. Takes three keyword arguments: dir_name - a file path string, file_name - a args filename string (.args will be appended) and args_list - a list of the values to save.
		The args_list is the only required argument. By default it is supplied by self.args_list, but may be replaced. If no dir_name or file_name are supplied the preference file will be saved in a default location - self.default_path.'''

		# Assign self.args_list to the list supplied by the user. The args_list is the minimum info that needs to be supplied...
		args_list = self.args_list
		
		# If no directory and no filename provided, the args file will be saved in a new directory in the user's home directory path - or the .nuke directory, if Nuke is loaded...
		if dir_name is None and file_name is None :
			# Nothing supplied -- use the default path...
			self.args_file = self.default_path
		# If no directory provided -- only file_name, the args file will be saved in a default directory in the user's home directory path - or the .nuke directory, if Nuke is loaded...
		elif dir_name is None and file_name is not None:
			# Nothing supplied -- use the default path...
			self.args_file = self.home_dir + self.args_dir + file_name + self.args_ext		
		else:
			# Check for TypeErrors...
			if not isinstance(dir_name, str):
				raise TypeError("The first keyword argument, dir_name, needs to be a directory path string.")
			if not isinstance(file_name, str):
				raise TypeError("The second keyword argument, file_name, needs to be a filename string.")
			if not isinstance(args_list, list):
				raise TypeError("The third keyword argument, args_list, needs to be a list of values to be saved.")			
				
			# Build the path from the user supplied dir_name and file_name values...
			self.args_file = dir_name + self.sep + file_name + self.args_ext
				
		# Set the args directory so we can create it later, if it doesn't exist...
		self.dir_to_create = os.path.dirname(self.args_file)
		
		# Try to create the args directory and cope with the directory already existing by ignoring that exception...
		if os.path.isdir(self.dir_to_create):
			#print "Directory %s already exists..." % (self.dir_to_create)
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
		
		# Try to save the file...
		try:
			self.args_save = open(self.args_file, 'w')
			for tag_data in args_list:
				self.args_save.write("%s\n" % tag_data)			
			self.args_save.close()
			if self.args_file:
				#print "args File saved to: %s" % (self.args_file)
				#if nuke.GUI:		
				#	nuke.message("args File saved to: %s" % (self.args_file))
				# Return the path where the args_file got saved...
				args_file = self.args_file
				return args_file
		except:
			print("ERROR: args cannot be saved to: %s" % (self.args_file))
			if nuke.GUI:		
				nuke.message("args cannot be saved to: %s Press OK to cancel." % (self.args_file))
			return None

	def read_args_file(self, dir_name=None, file_name=None):
		
		'''Method for retrieving a saved list of args for exiftool, saved by the write_args_file method. Takes two arguments: dir_name - a file path string, file_name - an args filename string. Returns args_list - a list of the saved values.
		If dir_name and file_name not supplied, will try to use a default path to retrieve the args list.'''
		
		if dir_name is None and file_name is None :
			# Nothing supplied -- use the default path...
			self.args_file = self.default_path
		# If no directory provided -- only file_name, the args file will be saved in a default directory in the user's home directory path - or the .nuke directory, if Nuke is loaded...
		elif dir_name is None and file_name is not None:
			# Nothing supplied -- use the default path...
			self.args_file = self.home_dir + self.args_dir + file_name + self.args_ext	
		else:
			# Check for TypeErrors...
			if not isinstance(dir_name, str):
				raise TypeError("The first keyword argument, dir_name, needs to be a directory path string.")
			if not isinstance(file_name, str):
				raise TypeError("The second keyword argument, file_name, needs to be a filename string.")
			
			# Build the path from the user supplied dir_name and file_name values...
			self.args_file = dir_name + self.sep + file_name + self.args_ext
			
		# Try to read the args file, if it exists...
		if os.path.isfile(self.args_file):
			try:
				self.args_read = open(self.args_file, 'r')
				self.saved_args = self.args_read.read()
				self.args_read.close()
			except:
				print("Sorry - args file %s cannot be read." % (self.args_file))
				if nuke.GUI:			
					nuke.message("args file cannot be read:\n %s\n\n Press OK to delete corrupt file and continue.\n\n You will need to save a new args file." % (self.args_file))
				self.args_read.close()
			finally:
				print("args file loaded successfully from %s" % (self.args_file))
				print("self.saved_args --------->\n", self.saved_args)
				saved_args = self.saved_args
				return saved_args		
			
		else:
			print("Sorry - args file %s does not seem to exist." % (self.args_file))
			if nuke.GUI:		
				nuke.message("args file does not seem to exist:\n %s\n\n Press OK to delete corrupt file and continue.\n\n You will need to save a new args file." % (self.args_file))
			return None

#----------------------------------------------------------------------------------------------------------------------------
# Supply some default arguments for testing... This form may be added to code that gets used in production
# because the class, method or function will typically be called from a Python executable or program
# that will become "__main__". Therefore, "__name__", which is this file, will not be "__main__" and
# this test will not ever be run...

if __name__=='__main__':

	#FileName = 'TagImages'
	
	# Make new instance of the class...
	args = TagsFileUtils()
	
	# Test the methods to see if we get something back...
	args.write_args_file()
	args.read_args_file()	
	