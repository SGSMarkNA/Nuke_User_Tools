#############################################################################################
######     Nuke Callbacks for adding a 'Metadata' Tab to each Write Node    #################
##
##  On a local mmachine, add 'import Callbacks_WriteNodeMetadata' to the .nuke/menu.py file...
##
##  For the AW environment, add it to the "app_Initialization.py" file.
##  You may also need to add the path to the system path list, e.g.:
##      os.sys.path.append('//isln-smb/aw_config/Git_Live_Code/Global_Systems/User_Tools/Nuke_User_Tools/Rich')
##      import Callbacks_WriteNodeMetadata
##

#############################################################################################
#####  Imports:

try:
	import nuke
except Exception:
	pass

try:
	# Import the main module for adding a Metadata tab to Write nodes and running code...
	# Callbacks to run the functions are added below..
	from WriteNodeMetadata import WriteNodeMetadata
except Exception as e:
	print "Can't import WriteNodeMetadata because... ", e
#except Exception:
	#pass

#############################################################################################
#####  addOnCreate Callbacks:

try:
	# Create the knobs automatically when the user or a script makes a Write node or loads a Nuke file...
	nuke.addOnCreate(WriteNodeMetadata.createMetadataTabKnobs, nodeClass = 'Write')
	# Add AfterFrameRender callbacks...
	nuke.addAfterFrameRender(WriteNodeMetadata.Run_ICC_Code, nodeClass = 'Write')
	nuke.addAfterFrameRender(WriteNodeMetadata.Run_IPTC_Code, nodeClass = 'Write')
	nuke.addAfterFrameRender(WriteNodeMetadata.Run_Hyundai_Folder_Restructuring, nodeClass = 'Write')
except Exception as e:
	print "Did not add WriteNodeMetadata callbacks because... ", e
#except Exception:
	#pass

try:
	# Convert any existing old style sRGB Write nodes automatically when the user loads a Nuke file...
	nuke.addOnCreate(WriteNodeMetadata.convert_OldStyle_sRGB_Write_Nodes, nodeClass = 'Write')
except Exception:
	pass

#############################################################################################
#####  addKnobChanged Callbacks:

try:
	# Add the knobChanged function for the Metadata Tab...
	nuke.addKnobChanged(WriteNodeMetadata.knobChanged, nodeClass = 'Write')
except Exception:
	pass


"""
##################################################################

# NOTE: Use these to check for callbacks...

print nuke.beforeRenders
print nuke.afterFrameRenders
print nuke.afterRenders

##################################################################
"""