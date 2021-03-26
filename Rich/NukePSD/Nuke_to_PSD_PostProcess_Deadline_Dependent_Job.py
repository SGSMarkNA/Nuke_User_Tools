import sys
import os
import subprocess
import errno
import time
try:
	import nuke
except ImportError:
	nuke = None


class NukePSD_PostProcess_Deadline_Dependent_Job(object):

	def __init__(self):

		# Photoshop Executable - OS-specific...
		if os.name == 'nt':
			import _winreg
			# Set the Photoshop application to run...
			self.PS_APP = 'start photoshop.exe'

		elif os.name == 'posix':
			# Set the Photoshop application to run...
			self.PS_APP = 'open -b "com.adobe.Photoshop"'

		# Set the location for the JSX file to run...
		if os.name == 'nt':
			#self.jsx_file = os.environ["NUKE_USER_TOOLS_DIR"] + os.sep + 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx'
			self.jsx_file = os.path.join(os.environ["NUKE_USER_TOOLS_DIR"], 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx')
			self.jsx_file = self.jsx_file.replace('/', '\\')
		elif os.name == 'posix':
			#self.jsx_file = "'" + os.environ["NUKE_USER_TOOLS_DIR"] + os.sep + 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx' + "'"
			self.jsx_file = os.path.join(os.environ["NUKE_USER_TOOLS_DIR"], 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx')
		#print 'self.jsx_file --> ', self.jsx_file		
		#-----------------------------------------------------------------------------------------------


	# def btnstate(self):
	# 	''''''
	# 	if self.b1.isChecked() == True:
	# 		delete_temp_files = True
	# 		self.DELETE_FILES_POST_PROCESS = 'var DELETE_FILES_POST_PROCESS = ' + '"' + str(delete_temp_files) + '"'
	# 	else:
	# 		delete_temp_files = False
	# 		self.DELETE_FILES_POST_PROCESS = 'var DELETE_FILES_POST_PROCESS = ' + '"' + str(delete_temp_files) + '"'
	#
	# 	print "DELETE_FILES_POST_PROCESS ---> %s" % self.DELETE_FILES_POST_PROCESS


	def _update_data_file_paths(self, data_file):
		''''''
		png_string = 'var PNG_FOLDER = '
		psd_filename_string = 'var PSD_FileName = '

		NEW_DATA = []

		#print 'This is self.data_file inside _update_data_file_paths ====> ', self.data_file

		if os.path.isfile(self.data_file):
			try:
				# Get the original PNG_DIR from the NukePSD_Data.txt file...
				with open(self.data_file, 'r') as data_read:
					for line in data_read:
						if png_string in line:
							#print 'line -----> ', repr(line)
							OLD_PNG_DIR = line
							OLD_PNG_DIR = OLD_PNG_DIR.lstrip(png_string)
							OLD_PNG_DIR = OLD_PNG_DIR.rstrip("\n")
							OLD_PNG_DIR = OLD_PNG_DIR.strip("'")
							#print 'OLD_PNG_DIR --->> ', repr(OLD_PNG_DIR)
			except:
				print "Error: Data file cannot be read!"
				if nuke:            
					nuke.critical("Data file cannot be read!")
				data_read.close()
				return None		
			try:			
				# Replace OLD_PNG_DIR with new one, selected by user...
				with open(self.data_file, 'r') as data_read:
					for line in data_read:
						if psd_filename_string in line:
							# Replace old PSD_FileName parent dir. with new parent dir. derived from new PNG_DIR, selected by user...
							OLD_PSD_PARENTDIR = os.path.abspath(os.path.join(OLD_PNG_DIR, os.pardir))
							PNG_DIR_PARENTDIR = os.path.abspath(os.path.join(self.PNG_DIR, os.pardir))
							new_line = line.replace(OLD_PSD_PARENTDIR, PNG_DIR_PARENTDIR)
							new_line = new_line.replace('\\', '/')
							#print '>>>>>>>>>>>> ', repr(line)
							#print '>>>>>>>>>>>> ', repr(new_line)
							#print ''
							NEW_DATA.append(new_line)                    
						elif OLD_PNG_DIR in line:
							# Replace OLD_PNG_DIR with new one, selected by user...
							#print ''
							new_line = line.replace(OLD_PNG_DIR, self.PNG_DIR)
							new_line = new_line.replace('\\', '/')
							#print '++++++++++++ ', repr(line)
							#print '++++++++++++ ', repr(new_line)
							#print ''
							NEW_DATA.append(new_line)
						else:
							NEW_DATA.append(line)
				#print ''
				#print NEW_DATA
				# Write out the edited/updated file...
				with open(self.data_file, 'w') as out_file:
					out_file.write(''.join(NEW_DATA))			
			except:
				print "Error: Data file cannot be updated!"
				if nuke:
					nuke.critical("Data file cannot be updated!")
					return None		
		else:
			print "Error: Data file does not exist!"
			if nuke:        
				nuke.critical("Data file does not exist!")
			return None		


	def _write_data_location_file_PostProcess(self):
		'''Write out a file in a known temp directory that holds the location of the main data_file, so that the JSX file knows where to find it.'''

		# Path for the data file...
		self.data_file = os.path.join(self.PNG_DIR + os.sep + 'NukePSD_Data.txt')
		#print 'self.data_file >>>>>>>>>> ', self.data_file

		# Update the file paths in the data file, in case the PNG folder has been moved from its original location...
		self._update_data_file_paths(self.data_file)

		# Defaulting this to False for now...
		#delete_temp_files = False
		#self.DELETE_FILES_POST_PROCESS = 'var DELETE_FILES_POST_PROCESS = ' + '"' + str(delete_temp_files) + '"'

		# String to write to file, which is a var definition for the JSX file to process...
		if os.name == 'nt':
			DATA_FILE_LOCATION = 'var DATA_FILE_LOCATION = ' + "'" + self.data_file + "'"
			DATA_FILE_LOCATION = DATA_FILE_LOCATION.replace('\\', '/')
		elif os.name == 'posix':
			DATA_FILE_LOCATION = 'var DATA_FILE_LOCATION = ' + "'" + self.data_file + "'"
		#print 'DATA_FILE_LOCATION --> ', DATA_FILE_LOCATION
		#self.Data_Location = [DATA_FILE_LOCATION, self.DELETE_FILES_POST_PROCESS]
		self.Data_Location = [DATA_FILE_LOCATION]
		#print 'self.Data_Location --> ', self.Data_Location

		if os.name == "nt":
			self.data_location_file = os.path.join((os.environ.get('TEMP')), '.nuke\NukePSD\data_file_location.txt')
			#print 'self.data_location_file --> ', self.data_location_file
		else:
			self.data_location_file = os.path.join((os.environ.get('HOME')), '.nuke/NukePSD/data_file_location.txt')

		# Set the directory so we can make it, if it doesn't exist...
		self.data_location_dir = os.path.dirname(self.data_location_file)
		#print 'self.data_location_dir --> ', self.data_location_dir

		# Try to create the directory and cope with the directory already existing by ignoring that exception...
		try:
			os.makedirs(self.data_location_dir)
		except OSError, e:
			if e.errno != errno.EEXIST:
				raise
		#finally:
			#print "Created data location directory: %s " % (self.data_location_dir)

		# Save the file...
		try:
			self.data_location_save = open(self.data_location_file, 'w')
			for item in self.Data_Location:
				#print 'item -->', item
				self.data_location_save.write(item)
				self.data_location_save.write("\n")
			self.data_location_save.close()
			self.Data_Location_Save_Success = True
		except Exception as e:
			self.Data_Location_Save_Success = False
			print e
			nuke.message("Data File cannot be saved to %s!" % (self.data_location_file))	


	def _run_JS_command(self):
		'''Launch Photoshop and run the JSX file via the subprocess module.'''

		# Remove any lingering status file before we start...
		self.jsx_script_status_file = os.path.join((os.environ.get('TEMP')), '.nuke\NukePSD\jsx_script_status.txt')
		try:
			os.remove(self.jsx_script_status_file)
		except OSError as e:
			if e.errno != errno.ENOENT:		# errno.ENOENT = no such file or directory
				raise						# Something else happened. Better raise an error...		


		if self.Data_Location_Save_Success:
			if os.name == 'nt':
				self.target = self.PS_APP + " " + '"' + self.jsx_file + '"'
				self.target = self.target.replace('/', '\\')
				#print 'self.target --> ', self.target
				#process = subprocess.Popen(self.target, shell=True)
				process = subprocess.call(self.target, shell=True)
				# Start checking loop...
				while not os.path.exists(self.jsx_script_status_file):
					print 'Checking...'
					time.sleep(5)
				# The file exists. Let's see if we can read it...
				if os.path.isfile(self.jsx_script_status_file):
					try:
						with open(self.jsx_script_status_file, 'r') as data_read:
							for line in data_read:
								if "Complete." in line:
									print line
									print process
									return 0
					except:
						print "Error: JSX Script Status File cannot be read!"
						data_read.close()
						return 1

			elif os.name == 'posix':
				self.target = self.PS_APP + " " + self.jsx_file
				#print 'self.target --> ', self.target
				#process = subprocess.Popen(self.target, shell=True)
				#process.wait()
				process = subprocess.call(self.target, shell=True)
				# Start checking loop...
				while not os.path.exists(self.jsx_script_status_file):
					print 'Checking...'
					time.sleep(5)
				# The file exists. Let's see if we can read it...
				if os.path.isfile(self.jsx_script_status_file):
					try:
						with open(self.jsx_script_status_file, 'r') as data_read:
							for line in data_read:
								if "Complete." in line:
									print line
									print process
									return 0
					except:
						print "Error: JSX Script Status File cannot be read!"
						data_read.close()
						return 1

			# Remove the status file when we're done...
			try:
				os.remove(self.jsx_script_status_file)
			except OSError as e:
				if e.errno != errno.ENOENT:		# errno.ENOENT = no such file or directory
					raise						# Something else happened. Better raise it...

		else:
			return None


	#-----------------------------------------------------------------------------------------------
	# The function that runs stuff...

	def _run(self):
		''''''
		# Get the PNG_DIR value from the Deadline environment var...
		self.PNG_DIR = os.environ['PNG_DIR']
		#print 'This is self.PNG_DIR from os.environ --> ', self.PNG_DIR

		# Write the location file...
		self._write_data_location_file_PostProcess()
		#print 'GOT HERE - _write_data_location_file_PostProcess'

		# Run the JSX Photoshop PSD assembler script...
		self._run_JS_command()
		#print 'GOT HERE - _run_JS_command'

	#-----------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------
# Start the class and run everything.
#-----------------------------------------------------------------------------------------------
NPDDJ = NukePSD_PostProcess_Deadline_Dependent_Job()
#print 'GOT HERE -- initialized NukePSD_PostProcess_Deadline_Dependent_Job class...'
NPDDJ._run()