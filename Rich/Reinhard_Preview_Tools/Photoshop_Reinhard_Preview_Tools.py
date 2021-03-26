import os
if os.environ.has_key("AW_GLOBAL_SYSTEMS"):
	if not os.environ["AW_GLOBAL_SYSTEMS"] in os.sys.path:
		os.sys.path.append(os.environ["AW_GLOBAL_SYSTEMS"])
from Environment_Access import System_Settings
import colorsys
import nuke
# Customized auto_backdrop function...
from auto_backdrop.auto_backdrop import auto_backdrop


class Add_Reinhard_Preview_Tools(object):
	''''''

	def __init__(self):
		''''''	
		# Get active Viewer node...
		self.CurrentViewer = nuke.activeViewer()
		self.CurrentViewerNode = self.CurrentViewer.node()
		# Get input_process_node knob, so we can set the Reinhard_Vray_VIEWER_PROCESS to be active...
		self.InputProcessNode = self.CurrentViewerNode.knob('input_process_node')
		# Set some color transforms for the Backdrop node...
		r,g,b = .6, .118, .118
		self.RedBackdropColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
		r,g,b = .5, .5, .5
		self.GrayBackdropColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)        
		r,g,b = 1.0, 1.0, 1.0
		self.WhiteTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
		r,g,b = .66, 0.0, 0.0
		self.RedTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)        


	def _import_Reinhard_Vray_VIEWER_PROCESS_node(self):
		''''''
		# Deselect all nodes...
		for Node in nuke.allNodes():
			Node.setSelected(False)
		# Import the Reinhard_Vray_VIEWER_PROCESS group node for the Viewer Input Process...
		self.RVP_Path = os.environ["NUKE_USER_TOOLS_DIR"] + os.sep + 'Rich/Reinhard_Preview_Tools/Reinhard_Vray_VIEWER_PROCESS.nk'
		nuke.nodePaste(self.RVP_Path)
		# Set the label note...
		self.RVP_Node = nuke.selectedNode()
		self.RVP_Node['label'].setValue("Modified Reinhard V-Ray gamma curve.")
		# Hide the input...
		self.RVP_Node['hide_input'].setValue(True)
		# Add a backdrop for the Reinhard Viewer Process node...
		self.ReinhardBackdrop = auto_backdrop(bd_label = 'Reinhard_V-Ray_VIEWER_PROCESS\n\n\n\n\n\n\n           (Do not connect.)')
		# Set some values for the Backdrop node...
		self.ReinhardBackdrop['tile_color'].setValue(self.RedBackdropColor)
		self.ReinhardBackdrop['note_font_size'].setValue(15)
		self.ReinhardBackdrop['note_font_color'].setValue(self.WhiteTextColor)
		# Activate the node for the Reinhard_Vray_VIEWER as an Input Process...
		self.InputProcessNode.setValue('Reinhard_Vray_VIEWER_PROCESS')
		
	
	def _import_Reinhard_Curve_Gizmo(self):
		''''''
		# Deselect all nodes...
		for Node in nuke.allNodes():
			Node.setSelected(False)
		# Import the Reinhard_Curve_Gizmo node...
		self.RG_Path = os.environ["NUKE_GIZMOS"] + os.sep + 'Image/Reinhard_Curve.gizmo'
		nuke.nodePaste(self.RG_Path)
		self.RG_Node = nuke.selectedNode()
		# Set the name...
		self.RG_Node.knob('name').setValue('Reinhard Curve')
		self.RG_Node.setXYpos(self.ReinhardBackdrop.xpos() + 425, self.ReinhardBackdrop.ypos() + 75)


##############################################################
## RUN IT...

def start():
	''''''
	x = Add_Reinhard_Preview_Tools()
	x._import_Reinhard_Vray_VIEWER_PROCESS_node()
	x._import_Reinhard_Curve_Gizmo()



'''

##----------------------------------------------##
## Test Run it in the Nuke Script Editor...
##----------------------------------------------##

import os
# This line adds the Mac-HOME search path...
# /Users/richbobo/Dropbox/CODE/aw_projects/Reinhard_Preview_Tools/Photoshop_Reinhard_Preview_Tools.py
os.sys.path.append("/Users/richbobo/Dropbox/CODE")

# This line adds the Mac-WORK search path...
# /Users/rbobo/Dropbox/CODE/aw_projects/Reinhard_Preview_Tools/Photoshop_Reinhard_Preview_Tools.py
os.sys.path.append("/Users/rbobo/Dropbox/CODE")

# This line adds the Windows search path...
# D:\rbobo\Dropbox\CODE\aw_projects\Reinhard_Preview_Tools\Photoshop_Reinhard_Preview_Tools.py
os.sys.path.append(r"D:\rbobo\Dropbox\CODE")


# Loads the python file into the environment...
import aw_projects.Reinhard_Preview_Tools.Photoshop_Reinhard_Preview_Tools
# After editing and saving the file in the text editor, this reloads it into the environment...
reload(aw_projects.Reinhard_Preview_Tools.Photoshop_Reinhard_Preview_Tools)

x = aw_projects.Reinhard_Preview_Tools.Photoshop_Reinhard_Preview_Tools.Add_Reinhard_Preview_Tools()
x._import_Reinhard_Vray_VIEWER_PROCESS_node()

'''
