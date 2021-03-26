import sys
import os
import subprocess
import errno

try:
	from PySide import QtGui, QtCore
except ImportError:
	from PySide2 import QtCore
	from PySide2 import QtWidgets as QtGui

try:
	import nuke
except ImportError:
	nuke = None

class NukePSD_PostProcess(QtGui.QWidget):

	def __init__(self):

		#---------------------------------------------
		# Initialize the panel object as a QWidget and set its title and minimum width...
		QtGui.QWidget.__init__(self)
		self.setMinimumWidth(700)
		self.setWindowTitle('Nuke_to_PSD: Post Process Layered Photoshop Files')		
		#---------------------------------------------
		# Initialize the QWidget and QFormLayout objects...
		folderWidget = QtGui.QWidget(self)
		folderLayout = QtGui.QFormLayout()
		#---------------------------------------------
		# Create QPushButton to start the QFileDialog browser...
		self.btnBrowse = QtGui.QPushButton('Choose Parent "PNG" Folder', self)
		self.btnBrowse.clicked.connect(self.selectDirectory)
		#---------------------------------------------
		# QLineEdit for selected dir. path display...
		self.etBrowser = QtGui.QLineEdit('', self)
		self.etBrowser.returnPressed.connect(self._updateFromLine)
		#---------------------------------------------
		#self.b1 = QtGui.QCheckBox("Delete All Temp Files")
		#self.b1.setChecked(False)
		#self.b1.stateChanged.connect(self.btnstate)		
		#---------------------------------------------
		# Add a divider line...
		self.ops_section_divider = QtGui.QFrame()
		self.ops_section_divider.setFrameStyle(QtGui.QFrame.HLine)
		#---------------------------------------------
		# Add OK | Cancel QDialogButtonBox...
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		# Hook up OK | Cancel actions to _accept and _reject methods...
		self.buttonBox.accepted.connect(self._accept)
		self.buttonBox.rejected.connect(self._reject)
		#---------------------------------------------
		# Add elements to layout...
		folderLayout.addWidget(self.btnBrowse)
		folderLayout.addWidget(self.etBrowser)
		#folderLayout.addWidget(self.b1)

		folderLayout.addRow(self.ops_section_divider)		
		folderLayout.addRow(self.buttonBox)
		#---------------------------------------------
		# Set the layout...
		folderWidget.setLayout(folderLayout)
		self.setLayout(folderLayout)

		#---------------------------------------------
		# Get the Write node this class is called from. Since it's inside the group node, we can get the fullName, which gives us the group node's name...
		if nuke:
			self.CallbackWriteNode = nuke.thisNode()
			#print 'CallbackWriteNode --> ', self.CallbackWriteNode.name()
			#print 'fullName --> ', self.CallbackWriteNode.fullName()

			# Get the group node onject...
			self.GroupNode = nuke.toNode(self.CallbackWriteNode.fullName().split('.')[0])
			#print 'self.GroupNode --> ', self.GroupNode.name()

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
		#---------------------------------------------

	def selectDirectory(self, title="Select PNG folder"):
		''''''
		options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
		if nuke:
			directory = QtGui.QFileDialog.getExistingDirectory(self, title, nuke.script_directory(), options)
		else:
			directory = QtGui.QFileDialog.getExistingDirectory(self, title, QtCore.QDir.homePath(), options)
			#directory = QtGui.QFileDialog.getExistingDirectory(self, title, os.getcwd(), options)
		self.etBrowser.setText(directory)
		return directory

	def _updateFromLine(self):
		''''''
		self.PNG_DIR = self.etBrowser.text()

	def _accept(self):
		''''''
		#print 'OK'
		self.PNG_DIR = self.etBrowser.text()
		#print "self.selected_directory: %s" % self.PNG_DIR
		# Get the state of the "Delete All Temp Files:" checkbox...
		#self.btnstate()
		# Write the location file with the DELETE_FILES_POST_PROCESS value...
		self._write_data_location_file_PostProcess()
		# Run the JSX Photoshop PSD assembler script...
		self._run_JS_command()
		# Close the panel...
		self.close()

	def _reject(self):
		''''''
		#print 'Cancelled.'
		self.PNG_DIR = None
		# Close the panel...
		self.close()	

	def Get_and_Set_PNG_DIR(self):
		'''Get the main PNG_DIR path from the UI, indicating where the files are located that need to be processed into PSD files.'''
		if not nuke:
			app = QtGui.QApplication(sys.argv)

	#def btnstate(self):
		#''''''
		#if self.b1.isChecked() == True:
			#delete_temp_files = True
			#self.DELETE_FILES_POST_PROCESS = 'var DELETE_FILES_POST_PROCESS = ' + '"' + str(delete_temp_files) + '"'				
		#else:
			#delete_temp_files = False
			#self.DELETE_FILES_POST_PROCESS = 'var DELETE_FILES_POST_PROCESS = ' + '"' + str(delete_temp_files) + '"'

		#print "DELETE_FILES_POST_PROCESS ---> %s" % self.DELETE_FILES_POST_PROCESS

	##--------------------------------------------------------------------------------------

	def _update_data_file_paths(self, data_file):
		''''''
		png_string = 'var PNG_FOLDER = '
		psd_filename_string = 'var PSD_FileName = '

		NEW_DATA = []

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

		# Update the file paths in the data file, in case the PNG folder has been moved from its original location...
		self._update_data_file_paths(self.data_file)

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
		else:
			self.data_location_file = os.path.join((os.environ.get('HOME')), '.nuke/NukePSD/data_file_location.txt')

		# Set the directory so we can make it, if it doesn't exist...
		self.data_location_dir = os.path.dirname(self.data_location_file)

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
		if self.Data_Location_Save_Success:
			if os.name == 'nt':
				self.target = self.PS_APP + " " + '"' + self.jsx_file + '"'
				self.target = self.target.replace('/', '\\')
				#print 'self.target --> ', self.target
				process = subprocess.Popen(self.target, shell=True)		
			elif os.name == 'posix':
				self.target = self.PS_APP + " " + self.jsx_file
				#print 'self.target --> ', self.target
				process = subprocess.Popen(self.target, shell=True)
				process.wait()
		else:
			return None

##-----------------------------------------------------------------------##
## Run it.
##-----------------------------------------------------------------------##

if not nuke:
	'''
	If we were not able to import nuke, just make this a standalone panel...
	'''
	app = QtGui.QApplication(sys.argv)
	panel = NukePSD_PostProcess()
	panel.show()
	panel.raise_()
	if not app.exec_():
		selected_directory = panel.etBrowser.text()
		#print "Selected Folder: %s" % selected_directory
else:
	'''
	Otherwise, we are probably wanting to run the panel inside of Nuke.
	So, use this start() function as a way to fire up the panel...
	'''
	def start():
		start.panel = NukePSD_PostProcess()
		start.panel.show()
		start.panel.raise_()
	start()