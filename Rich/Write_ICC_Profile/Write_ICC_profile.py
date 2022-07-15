import os
try:
	import nuke
except ImportError:
	nuke = None


class Write_ICC_Profile(object):
	'''
	For further info on exiftool, go to --> http://www.sno.phy.queensu.ca/~phil/exiftool/

	NOTE:
	To Extract ICC profile from an image that already has one...
	exiftool -icc_profile -b Image_with_sRGB_ICC_Profile.png > sRGB_profile_from_Photoshop.icc

	Then, to copy it to a new image...
	exiftool "-icc_profile<=sRGB_profile_from_Photoshop.icc" new_image_to_be_tagged.png
	'''

	def __init__(self):	
		''''''
		# TEMPORARY PATH FOR TESTING... 
		#self.ICC_FilePath = "/Users/richbobo/Dropbox/richbobo/NUKE/Photoshop_and_Nuke/__sRGB_exiftool_ICC_Profile_TESTING__/sRGB_profile_from_Photoshop.icc"

		#################################################################
		# Build path to ICC profile file for Windows...
		if os.name == 'nt':
			try:
				def get_ICC_profile_path():
					SERVER_PATH = os.environ.get("AW_SOFTWARE_SYSTEMS")
					#print 'SERVER_PATH ---------->', SERVER_PATH
					ICC_FILE = "Nuke\ICC_Profiles\sRGB_profile_from_Photoshop.icc"
					#print 'ICC_FILE ---------->', ICC_FILE
					ICC_FILE_PATH = os.path.join(SERVER_PATH, ICC_FILE)
					return ICC_FILE_PATH
				self.ICC_FilePath = get_ICC_profile_path()
				#print 'self.ICC_FilePath ---------->', self.ICC_FilePath
			except:
				print("ERROR: Cannot find path to ICC Profile! Exiting now.")
				nuke.message('ERROR: Cannot find path to ICC Profile!\nExiting now.')
				return
		elif os.name == 'posix':
			home_dir = os.environ.get('HOME')
			if home_dir == "/Users/richbobo":			
				if os.path.exists('/Users/richbobo/Dropbox/CODE/aw_LIVE_CODE/Git_Live_Code/Nuke/ICC_Profiles/sRGB_profile_from_Photoshop.icc'):
					self.ICC_FilePath = '/Users/richbobo/Dropbox/CODE/aw_LIVE_CODE/Git_Live_Code/Nuke/ICC_Profiles/sRGB_profile_from_Photoshop.icc'
					print(self.ICC_FilePath)
			elif home_dir == "/Users/rbobo":
				if os.path.exists('/Volumes/app_config/Git_Live_Code/Nuke/ICC_Profiles/sRGB_profile_from_Photoshop.icc'):
					self.ICC_FilePath = '/Volumes/app_config/Git_Live_Code/Nuke/ICC_Profiles/sRGB_profile_from_Photoshop.icc'				
				#if os.path.exists('/Users/rbobo/Dropbox/CODE/aw_LIVE_CODE/Git_Live_Code/Nuke/ICC_Profiles/sRGB_profile_from_Photoshop.icc'):
					#self.ICC_FilePath = '/Users/rbobo/Dropbox/CODE/aw_LIVE_CODE/Git_Live_Code/Nuke/ICC_Profiles/sRGB_profile_from_Photoshop.icc'
					print(self.ICC_FilePath)
			else:
				print("ERROR: Cannot find path to sRGB_profile_from_Photoshop.icc! Exiting now.")
				nuke.message('ERROR: Cannot find path to sRGB_profile_from_Photoshop.icc!\nExiting now.')
				return			

		#################################################################
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
					print('Found exiftool at /usr/local/bin/exiftool')
			elif home_dir == "/Users/rbobo":			
				if os.path.exists('/usr/local/bin/exiftool'):
					print('Found exiftool at /usr/local/bin/exiftool')
			else:
				print("ERROR: Cannot find path to exiftool executable! Exiting now.")
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return


	def copy_ICC_profile_to_image(self):
		''''''
		# Get the path for the current frame we're rendering...
		self.current_frame_path = nuke.filename(nuke.thisNode(),nuke.REPLACE)
		if os.name == 'nt':
			home_dir = os.environ.get('HOMEPATH')
			# Operates on a single frame. This works well on the farm.
			ARGS = '"' + '-icc_profile<=' + self.ICC_FilePath + '"'
			#print 'ARGS ---------->', ARGS
			exec_string = self.EXECUTABLE.strip('"') + ' ' + ARGS + ' ' + self.current_frame_path
			print('exec_string ---------->', exec_string)
		elif os.name == 'posix':
			home_dir = os.environ.get('HOME')
			# If I'm at home testing, this is the binary location... Also would be for a local Mac OS X system - just wouldn't need the home_dir test, of course...
			if home_dir == "/Users/richbobo":
				exec_string = '/usr/local/bin/exiftool ' + '"-icc_profile<=' + self.ICC_FilePath + '"' + ' ' + self.current_frame_path
				print('exec_string ---------->', exec_string)
			elif home_dir == "/Users/rbobo":
				# Operates on a single frame. This works well on the farm.
				exec_string = '/usr/local/bin/exiftool ' + '"-icc_profile<=' + self.ICC_FilePath + '"' + ' ' + self.current_frame_path
				print('This is the AW iMac exec_string -->', exec_string)
		# Run the exiftool command on the rendered files, with arguments supplied by self.args_file_path...
		try:
			os.system(exec_string)
		except:
			print("ERROR: ICC Profile Tagging Failed!\n Something went wrong with the image metadata tagging!")
			if nuke.GUI:	
				nuke.critical("ICC Profile Tagging Failed!\n Something went wrong with the image metadata tagging!")
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


