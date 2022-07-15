import os
if "AW_GLOBAL_SYSTEMS" in os.environ:
	if not os.environ["AW_GLOBAL_SYSTEMS"] in os.sys.path:
		os.sys.path.append(os.environ["AW_GLOBAL_SYSTEMS"])
from Environment_Access import System_Settings
import nuke
import errno


class Write_ICC_Profile_with_Args(object):
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
		# exiftool executable path...
		if os.name == 'nt':
			try:	
				self.EXECUTABLE = System_Settings.EXIF_TOOL
			except:
				print("ERROR: Cannot find path to exiftool executable! Exiting now.")
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return
		# Build exiftool executable path for MacOS...
		elif os.name == 'posix':
			try:
				self.EXECUTABLE = '/usr/local/bin/exiftool'
			except:
				print("ERROR: Cannot find path to exiftool executable! Exiting now.")
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return

		# ICC profiles location...
		self.ICC_Folder = System_Settings.ICC_FILES
		##print 'self.ICC_Folder ---->>>> ', self.ICC_Folder


	def copy_ICC_profile_to_image(self, ICC_Profile_Name):
		''''''
		self.ICC_Profile_Name = ICC_Profile_Name
		self.ICC_FilePath = os.path.join(self.ICC_Folder, self.ICC_Profile_Name)

		if not os.path.exists(self.ICC_FilePath):
			raise IOError("The ICC Profile %s cannot be found!" % self.ICC_FilePath)

		# Get the path for the current frame we're rendering...
		self.current_frame_path = nuke.filename(nuke.thisNode(),nuke.REPLACE)
		# Operates on a single frame. This works well on the farm.
		exec_string = '%s "-icc_profile<=%s" "%s"' %  (self.EXECUTABLE, self.ICC_FilePath, self.current_frame_path)
		try:
			os.system(exec_string)
		except:
			print("ERROR: ICC Profile Tagging Failed!\n Something went wrong with the image metadata tagging!")
			if nuke.GUI:	
				nuke.critical("ICC Profile Tagging Failed!\n Something went wrong with the image metadata tagging!")
			return

		# Remove the duplicate xxxxxx.xxx_original" file that exiftool creates as a backup...
		dup_frame = self.current_frame_path + "_original"
		if os.path.exists(dup_frame):
			try:
				os.remove(dup_frame)
				# Check to see if we removed the file...And, if not....
				if os.path.exists(dup_frame):
					print("INFO: Tagging probably suceeded, but the removal of duplicate images failed.\n You will have to remove any images ending with _original, yourself...")
			# If the file doesn't exist, just ignore the error... 
			except OSError as e:
				# Some other kind of error must have occurred. Better let somebody know about it...
				if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
					raise
		else:
			pass
