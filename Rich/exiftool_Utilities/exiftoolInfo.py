import os
import subprocess
import nukescripts
try:
	import nuke
except ImportError:
	nuke = None

# Need this to find the CollectSourceFiles folder, which is relative to this file...
CollectSourceFilesDir = os.path.realpath(os.path.dirname(__file__) + '/..') + '/CollectSourceFiles'
os.sys.path.append(CollectSourceFilesDir)
from SourceNodeInfo import NodeInfo

# Need this to find the Node_Tools folder, which is relative to this file...
NodeToolsDir = os.path.realpath(os.path.dirname(__file__) + '/..') + '/Node_Tools'
os.sys.path.append(NodeToolsDir)
from Node_Tools.Node_Tools import Node_Tools


class exiftoolInfo(object):
	'''
	For further info on exiftool, go to --> http://www.sno.phy.queensu.ca/~phil/exiftool/

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
				print "ERROR: Cannot find path to exiftool executable! Exiting now."
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return	
		# Test for MacOS location of exiftool executable...
		elif os.name == 'posix':
			home_dir = os.environ.get('HOME')
			# If I'm at home testing, this is the binary location... Also would be for a local Mac OS X system - just wouldn't need the home_dir test, of course...
			if home_dir == "/Users/richbobo":			
				if os.path.exists('/usr/local/bin/exiftool'):
					print 'Found exiftool at /usr/local/bin/exiftool'
			elif home_dir == "/Users/rbobo":			
				if os.path.exists('/usr/local/bin/exiftool'):
					print 'Found exiftool at /usr/local/bin/exiftool'
			else:
				print "ERROR: Cannot find path to exiftool executable! Exiting now."
				nuke.message('ERROR: Cannot find path to exiftool executable!\nExiting now.')
				return

		## Possible error message strings from exiftool...
		self.error_msg_1 = '0 image files read'


	def get_ProfileDescription(self, TagName='ProfileDescription'):
		''''''
		# Check for a selected Read node.
		try:
			Node = nuke.selectedNode()
		except ValueError:
			nuke.message('Please select a Read node.')
			return
		if Node.Class() == 'Read':
			FilePath = NodeInfo().get_info(Node)['filePath']
		else:
			nuke.message('Please select a Read node.')
			return
		# Check for the current OS to decide which flavor of exiftool to use...
		if os.name == 'nt':
			home_dir = os.environ.get('HOMEPATH')
			exec_string = self.EXECUTABLE + ' -TAG ' + '-' + TagName + ' ' + FilePath		
		elif os.name == 'posix':
			home_dir = os.environ.get('HOME')
			# If I'm at home testing, this is the binary location... Also would be for a local Mac OS X system - just wouldn't need the home_dir test, of course...
			if home_dir == '/Users/richbobo':
				exec_string = '/usr/local/bin/exiftool -TAG ' + '-' + TagName + ' ' + FilePath
			else:
				exec_string = 'exiftool -TAG ' + '-' + TagName + ' ' + FilePath
		# Run the exiftool command on the files...
		print 'exec_string ---------->', exec_string
		# Run exec_string in command shell as a subprocess...
		try:
			p = subprocess.Popen(exec_string, stdout=subprocess.PIPE, shell=True)
			result = p.communicate()[0]
			print result
			# Check for exiftool error...
			if self.error_msg_1 in result:
				print "ERROR: Reading metadata Failed!"
				nuke.critical('exiftool could not read the file metadata!\n\n')
				return			
			else:
				TagValue = result.strip().split(': ')[-1]
				if TagValue == '':
					TagValue = 'None'
				print TagName + ': \n' + TagValue
				nuke.message(TagName + ': \n\n' + TagValue)
		except:
			print "ERROR: Reading metadata Failed!"
			return
		# Ask if the user wants to add a colorspace_node after the Read node, to properly manage the image's color...
		if nuke.ask('Add Colorspace transform node?'):
			colorspace_node = nuke.nodes.Colorspace()
			colorspace_node.setInput(0, Node)
			colorspace_node.knob('primary_in').setValue(TagValue)
			if TagValue is not 'None':
				## There's probably a better way to do this...
				## Check to see if the Colorspace primary_in knob got changed or not...
				## If the TagValue is still set to 'sRGB', then that's what the image profile actually is...
				if TagValue.startswith('sRGB'):
					pass
				## If the TagValue in not 'sRGB', check to see if it's *still* sRGB after setting the value.
				## If it is, that probably means that the embedded profile name is not available in Nuke's primary_in knob
				## and it kept the default value of 'sRGB', so we'd better let the user know...
				else:
					if colorspace_node.knob('primary_in').value() == 'sRGB':
						nuke.critical('Embedded colorspace ' + '"' + TagValue + '"' + ' not available!\n\nDefaulting to sRGB colorspace.')
			else:
				colorspace_node.knob('primary_in').setValue('sRGB')
				nuke.critical('Embedded colorspace ' + '"' + TagValue + '"' + ' not available!\n\nDefaulting to sRGB colorspace.')


	def get_ALL_IMAGE_TAGS(self):
		''''''
		# Need to have the metadata variable available to the infoPanel Class...
		global metadata

		# Check for a selected Read node.
		try:
			Node = nuke.selectedNode()
		except ValueError:
			nuke.message('Please select a Read node.')
			return
		if Node.Class() == 'Read':
			FilePath = NodeInfo().get_info(Node)['filePath']
		else:
			nuke.message('Please select a Read node.')
			return
		# Check for the current OS to decide which flavor of exiftool to use...
		if os.name == 'nt':
			home_dir = os.environ.get('HOMEPATH')
			exec_string = self.EXECUTABLE + ' ' + FilePath		
		elif os.name == 'posix':
			home_dir = os.environ.get('HOME')
			# If I'm at home testing, this is the binary location... Also would be for a local Mac OS X system - just wouldn't need the home_dir test, of course...
			if home_dir == '/Users/richbobo':
				exec_string = '/usr/local/bin/exiftool ' + FilePath
			else:
				exec_string = 'exiftool ' + FilePath
		print 'exec_string ---------->', exec_string
		# Run the exiftool command on the files...
		try:
			p = subprocess.Popen(exec_string, stdout=subprocess.PIPE, shell=True)
			metadata = p.communicate()[0]
			print metadata
		except:
			print "ERROR: Reading metadata Failed!"
			return
		# If there are no exiftool errors, show the panel with metadata tags...
		if self.error_msg_1 not in metadata:
			p = self.infoPanel()
			p.show()
		else:
			print "ERROR: Reading metadata Failed!"
			nuke.critical('exiftool could not read the file metadata!\n\n')
			return


	# Use a scrollable PythonPanel info window for long metadata tag listings...
	class infoPanel(nukescripts.PythonPanel):
		''''''
		def __init__(self):
			nukescripts.PythonPanel.__init__(self, 'Metadata Tags', 'com.richbobo.infoPanel')
			self.info = nuke.Multiline_Eval_String_Knob('info', '')
			#self.info.setEnabled(False)
			self.addKnob(self.info)
			self.info.setValue(metadata)


'''
##########################################
## TESTING IN Nuke...
##########################################

import wingdbstub
wingdbstub.Ensure()

#######################################

import exiftool_Utilities.exiftoolInfo
reload(exiftool_Utilities.exiftoolInfo)

EXIF = exiftool_Utilities.exiftoolInfo.exiftoolInfo()

EXIF.get_ProfileDescription()

EXIF.get_ALL_IMAGE_TAGS()

#######################################

'''