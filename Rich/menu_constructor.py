import os
import nukescripts
import nuke
import TagImages.TagImages
import Nodes_Master_Control_Panel.MasterControlNodes

Major = nuke.NUKE_VERSION_MAJOR 
#Release = nuke.NUKE_VERSION_RELEASE
if Major == 9:
	pass
elif Major == 10:		
	import nuke.localization

'''
Basic Menu Item Options
-----------------------------------------------------------
KEY                   DESCRIPTION
-----------------------------------------------------------
label:                The name the menu item will display
icon:                 The icon that will be displayed to the left of the label (full path to image file)
tooltip:              A tool tip that will be displayed if the curser is hovering over the menu item
arg:                  A value that will be sent to the command upon activation
auto_reload:          Reload before calling the function True by default
shortcut:             Shortcut key for the menu item
parent_menus:         Override the default placment and add menu item to specifed name
user_tool_sub_menu:   Specify a submenu name for this command
panelID:              Used to register panel using nukescripts.registerPanel
-----------------------------------------------------------
'''

#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/3D
##   label:3d Scene Nodes
##   shortcut:alt+shift+d:
##   tooltip:Creates a collection of nodes used as the basis for starting a 3d scene --> Scene, Camera, Light, ScanlineRender, Constant
def Camera_3d_Scene_Start():
	import Camera3dSceneStart.Camera3dSceneStart
	Camera3dSceneStart.Camera3dSceneStart.Camera_3d_Scene_Start()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/3D
##   label:Lock Image to Camera
##   tooltip:Attach output to Scene node, Connect Image Read node to input, Press 'Find Cameras' button, Select a camera and set the 'Image Distance From Camera'.
def LockImageToCamera():
	path = os.environ["AW_USER_TOOLS"] + "/Nuke_User_Tools/Rich/Image_Locked_To_Camera/Image_Locked_to_Camera_GROUP.nk"
	nuke.nodePaste(path)


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/RCHIVING
##   label:Collect Source Files
##   tooltip:Copies all Nuke script source files to a folder, creates a copy of the script with links to the copies.\nAlso, offers to repair any broken source file path links.
def collect_source_files_and_repair_links():
	import CollectSourceFiles.CollectSourceFiles
	CollectSourceFiles.CollectSourceFiles.CollectSourceFiles().collect_source_files()


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/ARCHIVING
##   label:Repair File Paths
##   tooltip:Repairs broken source file path links.
def repair_file_paths():
	import CollectSourceFiles.PathRepairPanel
	CollectSourceFiles.PathRepairPanel.start_panel()


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/CAMERAS
##   label:Camera from EXR
##   tooltip:Creates a new camera that uses the metadata of the animated VRay render camera for the selected EXR Read node.
def create_VRay_Camera_from_Exr():
	import createExrCamVray.createExrCamVray
	createExrCamVray.createExrCamVray.createExrCamVray()


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   label:Field Of View Calculator Panel
##   parent_menus:Pane
##   tooltip:Panel for calculating a camera's fov, focal length and aperature.\nCan be used to create a new camera or to control an existing camera. 
##   panelID:com.ohufx.FovCalculator
def addFovCalc():
	import FovCalculator.FovCalculator
	try:
		myPanel = FovCalculator.FovCalculator.FovCalculator()
		return myPanel.addToPane()
	except:
		pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/CAMERAS
##   label:Field Of View Calculator Panel
##   tooltip:Panel for calculating a camera's fov, focal length and aperature.\nCan be used to create a new camera or to control an existing camera. 
def FovCalc():
	import FovCalculator.FovCalculator
	FovCalculator.FovCalculator.FovCalculator().show()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CAMERAS
##   label:Projection Cameras from Animated Camera
##   tooltip:Panel for automatically creating multiple projection cameras from an animated camera. 
def cyclo():
	import Cyclo.Cyclo
	Cyclo.Cyclo.cyclo()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CAMERAS
##   label:Target Camera
##   tooltip:Creates a new camera that has its aim pointing at a target axis.\nThe axis can be animated to control the camera's viewing direction.
def Target_Camera():
	import TargetCamera.TargetCamera
	TargetCamera.TargetCamera.TargetCamera()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CAMERAS
##   label:OpticalZDefocus
##   tooltip:Physically accurate ZDefocus, which controls circle of confusion (CoC) size, based on lens geometry, using the depth of field equation.\nSet your lens and film-back characteristics, your focus distance and adjust the size of your bokeh with the aperture size, just like a real lens.\nFeatures Unpremultiply your depth channel...
def OpticalZDefocus():
	path = os.environ["AW_USER_TOOLS"] + "/Nuke_User_Tools/Rich/OpticalZDefocus/OpticalZDefocus.nk"
	nuke.nodePaste(path)


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   label:Hex Color to Float
##   parent_menus:Pane
##   tooltip:Simple panel to convert Hex Color Values to 32 bit Float.
##   panelID:com.diogogirondi.hex2nuke
def addHexToFloatPanel():
	import Hex_to_Float_Color.hex2nuke
	try:
		myPanel = Hex_to_Float_Color.hex2nuke.hex2nukePanel()
		return myPanel.addToPane()
	except AttributeError:
		pass

# Menu_Item
## [menu_item]
##   parent_menus:Nuke/COLOR
##   label:Convert from Hex to Float Color
##   tooltip:Hex color value can be obtained via Photoshop Colorpicker.
def HexToFloatColorConvert():
	import Hex_to_Float_Color.hex2nuke
	Hex_to_Float_Color.hex2nuke.hex2nukePanel().show()
	

# Menu_Item
## [menu_item]
##   parent_menus:Nuke/COLOR
##   label:Create Expression_NaN_Filter_and_Clone_Offset
def Create_Expression_NaN_Filter_and_Clone_Offset():
	""""""
	nod = nuke.createNode("Expression",'label "Filters out NaN pixel values\nUser tab has x,y offset values\nto clone adjacent pixels to fill in." expr0 isnan(r)?r(x+xo,y+yo):r expr1 isnan(g)?g(x+xo,y+yo):g expr2 isnan(b)?b(x+xo,y+yo):b expr3 isnan(a)?a(x+xo,y+yo):a name Expression_NaN_Filter_and_Clone')
	int_knb = nuke.Int_Knob("ox")
	int_knb.setLabel("x clone offset")
	int_knb.setValue(-1)
	nod.addKnob(int_knb)
	
	int_knb = nuke.Int_Knob("yo")
	int_knb.setLabel("y clone offset")
	int_knb.setValue(0)
	nod.addKnob(int_knb)	

# Menu_Item
## [menu_item]
##   parent_menus:Nuke/COLOR
##   label:Create Gamma_2point2_for_sRGB_alpha
def Create_Gamma_2point2_for_sRGB_alpha():
	nuke.createNode("Gamma",'label "2.2 Gamma to show what Photoshop sRGB\nlayer blending will look like...\n\nvalue = 2.2\nmask = rgb.alpha\nfringe = \[checked]" name Gamma1 maskChannelInput rgba.alpha fringe true value 2.2 tile_color 0xff0000ff')

#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Build Comp from EXR Layers
##   shortcut:alt+0:
##   tooltip:Automatically builds a vehicle comp from the selected EXR Read node.\nProvides the ability to associate existing VRay layer names and creates a comp for an exterior or interior image sequence.
def exr_CompBuilder():
	import CompBuilder.CompBuilder
	CompBuilder.CompBuilder.exr_CompBuilder()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Build Configurator using Views
##   shortcut:alt+-:
##   tooltip:Builds a Views-based vehicle configurator comp.\nYou provide a vehicle Model Name, Model Year, Build Type (Int or Ext), a list of Trim Names and a list of Color Names.\nTrim Names and Color Names are combined to create View Names for every combination.\nAdvantages --> A single Write node can render any or all combinations at once. Comp navigation and editing is greatly simplified.
def Config_CompBuilder():
	import ConfigCompBuilder.ConfigCompBuilder
	ConfigCompBuilder.ConfigCompBuilder.ConfigCompBuilder()


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   label:Render Views Selector Panel
##   parent_menus:Pane
##   tooltip:Panel for filtering and selecting views to render in a Write node. Needed for comps with a large number of views.
##   panelID:com.richbobo.RenderViewsSelectorPanel
def addRenderViewsSelector():
	import Render_Views_Selection_Filtering.Render_Views_Selection_Filtering
	try:
		myPanel = Render_Views_Selection_Filtering.Render_Views_Selection_Filtering.Return_Render_Views_Selector_Panel()
		return myPanel.addToPane()
	except:
		pass

## Menu_Item
###  [menu_item]
###   parent_menus:Nuke/CONFIGURATORS
###   label:Render Views Selector Panel
###   shortcut:ctrl+alt+shift+w:
###   tooltip:Panel for filtering and selecting views to render in a Write node. Needed for comps with a large number of views.
#def RenderViewsSelectorPanel():
	#import Render_Views_Selection_Filtering.Render_Views_Selection_Filtering
	#try:
		#Render_Views_Selection_Filtering.Render_Views_Selection_Filtering.Return_Render_Views_Selector_Panel().show()
	#except:
		#pass


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   label:Viewer Views Selector Panel
##   parent_menus:Pane
##   tooltip:Panel for filtering and selecting a Viewer view. Needed for comps that use a large number of views.
##   panelID:com.richbobo.ViewerViewsSelectorPanel
def addViewerViewsSelector():
	import Viewer_Views_Selection_Filtering.Viewer_Views_Selection_Filtering
	try:
		myPanel = Viewer_Views_Selection_Filtering.Viewer_Views_Selection_Filtering.ViewerViewsSelectorPanel()
		return myPanel.addToPane()
	except:
		pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Viewer Views Selector Panel
##   tooltip:Panel for filtering and selecting a Viewer view. Needed for comps that use a large number of views.
def ViewerViewsSelectorPanel():
	import Viewer_Views_Selection_Filtering.Viewer_Views_Selection_Filtering
	try:
		Viewer_Views_Selection_Filtering.Viewer_Views_Selection_Filtering.ViewerViewsSelectorPanel().show()
	except:
		pass


##-------------------------------------------------------------------
## Menu_Item
###  [menu_item]
###   label:Roto Views Selector Panel
###   parent_menus:Pane
###   tooltip:Panel for filtering and selecting views in a single RotoPaint or Roto node. Useful for comps with a large number of views.
###   panelID:com.richbobo.RotoViewsSelectorPanel
#def addRotoViewsSelector():
	#import Roto_Views_Selection_Filtering_Panel.Roto_Views_Selection_Filtering_Panel
	#try:
		#myPanel = Roto_Views_Selection_Filtering_Panel.Roto_Views_Selection_Filtering_Panel.Return_RotoViewsSelectorPanel()
		## After the panel gets created, make sure that the _SelectedShapesCheck is run when the _changeViews method executes...
		#myPanel._SelectedShapesCheck = True		
		#return myPanel.addToPane()
	#except:
		#pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Roto Views Selector Panel
##   tooltip:Panel for filtering and selecting views in a single RotoPaint or Roto node. Useful for comps with a large number of views.
def RotoViewsSelectorPanel():
	import Roto_Views_Selection_Filtering_Panel.Roto_Views_Selection_Filtering_Panel
	try:
		p = Roto_Views_Selection_Filtering_Panel.Roto_Views_Selection_Filtering_Panel.Return_RotoViewsSelectorPanel()
		p.show()
		# After the panel gets created and returned, make sure that the _SelectedShapesCheck is run when the _changeViews method executes...
		p._SelectedShapesCheck = True
	except:
		pass


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   label:Roto Nodes Views Selection Panel
##   parent_menus:Pane
##   tooltip:Panel for selecting views for shapes in a collection of RotoPaint or Roto nodes. Useful for comps with a large number of views.
##   panelID:com.richbobo.RotoNodesViewsSelectionPanel
def addRotoNodesViewsSelectionPanel():
	import Roto_Views_Selection_Filtering_Panel.Roto_Nodes_Views_Selection_Panel
	try:
		myPanel = Roto_Views_Selection_Filtering_Panel.Roto_Nodes_Views_Selection_Panel.Return_RotoNodesViewsSelectionPanel()		
		return myPanel.addToPane()
	except:
		pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Roto Nodes Views Selection Panel
##   shortcut:ctrl+alt+shift+r:
##   tooltip:Panel for selecting views for shapes in a collection of RotoPaint or Roto nodes. Useful for comps with a large number of views.
def RotoNodesViewsSelectionPanel():
	import Roto_Views_Selection_Filtering_Panel.Roto_Nodes_Views_Selection_Panel
	try:
		p = Roto_Views_Selection_Filtering_Panel.Roto_Nodes_Views_Selection_Panel.Return_RotoNodesViewsSelectionPanel()
		p.show()
	except:
		pass


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Views-Based JoinViews Switch
##   tooltip:Creates a Views-based JoinViews Switch.\nYou provide the number of inputs, text filters and logical operators via input panel. JoinViews inputs are connected to NoOp nodes, according to the filters and logical operators.
def JoinViews_Switch_Builder_Panel():
	import JoinViews_Switch.JoinViews_Switch
	JoinViews_Switch.JoinViews_Switch.start()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Views-Based JoinAllViews Switch
##   tooltip:Automatically creates a Views-based JoinViews Switch, using all available Views.
def JoinAllViews_Switch_Builder():
	import JoinViews_Switch.JoinAllViewsSwitch
	JoinViews_Switch.JoinAllViewsSwitch.start()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Create Trim Views
##   tooltip:Creates Trim Views using Trim Names and Color Names.
def Create_TrimViews_Group_Node():
	import ConfigCompBuilder.CreateTrimViews
	ConfigCompBuilder.CreateTrimViews.start()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Create a Simple List of Views
##   tooltip:Quickly Creates Multiple Views.
def Simple_Create_Views_From_a_List():
	import ConfigCompBuilder.Simple_CreateViews
	ConfigCompBuilder.Simple_CreateViews.start()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/CONFIGURATORS
##   label:Append Views
##   tooltip:Quickly Add Views without removing any existing views.
def Append_Views_From_a_List():
	import ConfigCompBuilder.AppendViews
	ConfigCompBuilder.AppendViews.start()


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   label:Multi-Submit Nuke Scripts
##   parent_menus:Pane
##   tooltip:Panel for searching and replacing file path values in source nodes.\nWorks with any nodes that have a "file" path knob.\nExamples --> Reads, Writes and ReadGeo nodes.\nCan work on the entire script or just the current Group.
##   panelID:com.richbobo.MultiSubmitPanel
def addMultiSubmitPanel():
	import DeadlineScriptSubmit.MultiSubmitter
	try:
		myPanel = DeadlineScriptSubmit.MultiSubmitter.MultiSubmitPanel()
		return myPanel.addToPane()
	except AttributeError:
		pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/DEADLINE
##   label:Multi-Submit Nuke Scripts
##   tooltip:Panel for searching and replacing file path values in source nodes.\nWorks with any nodes that have a "file" path knob.\nExamples --> Reads, Writes and ReadGeo nodes.\nCan work on the entire script or just the current Group.
def MultiSubmitterPanel():
	import DeadlineScriptSubmit.MultiSubmitter
	try:
		panel = DeadlineScriptSubmit.MultiSubmitter.MultiSubmitPanel().show()
		panel.setMinimumSize(2000,2000)
	except:
		pass


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/EXRs
##   label:Export EXR Layers (Automatic and Manual)
##   tooltip:Create a new EXR image using only the selected layers.
def ExportSelectedEXRLayersGroup():
	path = os.environ["AW_USER_TOOLS"] + "/Nuke_User_Tools/Rich/EXR_Layer_Exporter/Layer_Exporter_GROUP.nk"
	print path
	nuke.nodePaste(path)


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/EXRs
##   label:EXR Compression Checker
##   tooltip:Checks the compression type for the selected EXR Read node and reports it in a pop-up window.
def EXR_Compression_Test():
	import EXRCompressionTest.EXRCompressionTest
	EXRCompressionTest.EXRCompressionTest.EXR_Compression_Test()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/EXRs
##   label:Resave EXR with Zip 1 Compression
##   tooltip:Resaves the currently selected EXR Read node with Zip1 compression.\nNote --> In Nuke versions previous to Nuke 9, EXRs with Zip1 compression load significantly faster.
def Resave_EXR_as_Zip_1():
	import Resave_EXR_as_Zip1.Resave_EXR_as_Zip1
	Resave_EXR_as_Zip1.Resave_EXR_as_Zip1.Resave_EXR_as_Zip1()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/FORMATS
##   label:Create Scaled Image Format
##   tooltip:Methods for scaling and creating a new image format - typically used for client approval or test renders.
def CreateScaledImageFormatPanel():
	import CreateScaledImageFormat.CreateScaledImageFormat
	CreateScaledImageFormat.CreateScaledImageFormat.CreateScaledImageFormat().showModal()

#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/FORMATS
##   label:Create Padded Image Format
##   tooltip:Create a new padded image format using percentage sliders - typically used for consumer packaged goods projects.
def PastePaddedImageFormatGroup():	
	path = os.environ["AW_USER_TOOLS"] + "/Nuke_User_Tools/Rich/CreatePaddedImageFormat/CreatePaddedImageFormat.nk"
	nuke.nodePaste(path)


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/KEYFRAMES
##   label:Axis with Random Noise Generator
##   tooltip:Creates a panel for generating random noise curves.\nSet frequency, amplitude and octaves values and press "Generate Noise".
def Create_Axis_With_Random_Noise_Controls():
	import AxisWithRandomNoiseControls.AxisWithRandomNoiseControls
	AxisWithRandomNoiseControls.AxisWithRandomNoiseControls.Create_Axis_With_Random_Noise_Controls()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/KEYFRAMES
##   label:Bake Expressions to Keyframes
##   tooltip:Bakes expression curves to keyframes.\nExample use --> to bake keyframes for the Axis Random Noise Generator.
def Bake_Expressions():
	import bakeExpressions.bakeExpressions
	bakeExpressions.bakeExpressions.Bake_Expressions()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/MISC
##   label:Restaurant Randomizer
##   shortcut:alt+shift+l:
##   tooltip:When you just can't decide what to eat.
def Lunch_Picker():
	import Restaurant_Randomizer.Restaurant_Randomizer
	Restaurant_Randomizer.Restaurant_Randomizer.RestaurantRandomizer()


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   label:Search and Replace Panel
##   parent_menus:Pane
##   tooltip:Panel for searching and replacing file path values in source nodes.\nWorks with any nodes that have a "file" path knob.\nExamples --> Reads, Writes and ReadGeo nodes.\nCan work on the entire script or just the current Group.
##   panelID:com.richbobo.SearchReplace
def addSRPanel():
	import Search_and_Replace_Panel.SearchReplacePanel
	try:
		myPanel = Search_and_Replace_Panel.SearchReplacePanel.SearchReplacePanel()
		return myPanel.addToPane()
	except AttributeError:
		pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/NODES
##   label:Search and Replace Panel
##   tooltip:Panel for searching and replacing file path values in source nodes.\nWorks with any nodes that have a "file" path knob.\nExamples --> Reads, Writes and ReadGeo nodes.\nCan work on the entire script or just the current Group.
def SearchAndReplacePanel():
	import Search_and_Replace_Panel.SearchReplacePanel
	try:
		Search_and_Replace_Panel.SearchReplacePanel.SearchReplacePanel().show()
	except:
		pass


#-------------------------------------------------------------------
'''Creates a master control panel node that can set values on knobs of other nodes of the same Class.'''
# Menu_Item
##  [menu_item]
##   label:Master Control Nodes
##   parent_menus:Pane
##   tooltip:Create a Master Control Node for a given Class of nodes.\nAny changes to the Master Control Node affects all nodes of the same Class.\nCan work on the entire script or just the current Group.
##   panelID:com.richbobo.MasterControlNodes
def addMCPanel():
	import Nodes_Master_Control_Panel.MasterControlNodes
	try:
		myPanel = Nodes_Master_Control_Panel.MasterControlNodes.MasterControlNodes()
		return myPanel.addToPane()
	except AttributeError:
		pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/NODES
##   label:Master Control Nodes
##   tooltip:Create a Master Control Node for a given Class of nodes.\nAny changes to the Master Control Node affects all nodes of the same Class.\nCan work on the entire script or just the current Group.
def NodesMasterControl():
	import Nodes_Master_Control_Panel.MasterControlNodes
	Nodes_Master_Control_Panel.MasterControlNodes.MasterControlNodes()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/NODES
##   label:Print Knobs
##   tooltip:Prints knob names and values for the selected node.
def Print_Knobs():
	import printKnobs.printKnobs
	printKnobs.printKnobs.printKnobs()


#-------------------------------------------------------------------
# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/PERFORMANCE
##   label:startPerformanceTimers
def start_performance_timing():
	nuke.startPerformanceTimers()

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/PERFORMANCE
##   label:resetPerformanceTimers
def reset_performance_timing():
	nuke.resetPerformanceTimers()

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/PERFORMANCE
##   label:stopPerformanceTimers
def stop_performance_timing():
	nuke.stopPerformanceTimers()


##-------------------------------------------------------------------
## Menu_Item
### [menu_item]
###   parent_menus:Nuke/PHOTOSHOP
###   label:Create Layered PSD Files
###   tooltip:Creates layered PSD files either at the end of a render or later, as a post process.
#def Nuke_to_PSD_Group():
	#path = os.environ["AW_USER_TOOLS"] + "/Nuke_User_Tools/Rich/NukePSD/Nuke_to_PSD_Group.nk"
	#print path
	#nuke.nodePaste(path)


## Menu_Item
### [menu_item]
###   parent_menus:Nuke/PHOTOSHOP
###   label:Post-Process - Create Layered PSD Files
###   tooltip:Creates layered PSD files from pre-rendered files, as a post process.
#def Nuke_to_PSD_Pst_Process_Panel():
	#import NukePSD.Nuke_to_PSD_PostProcess
	#NukePSD.Nuke_to_PSD_PostProcess.start()
	
	
#-------------------------------------------------------------------
'''PROJECTORS module -- Created by Julik Tarkhanov <me@julik.nl> in Amsterdam, 2011.'''
# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/PROJECTORS
##   label:Create a projector from this camera
##   icon://isln-smb/aw_config/Git_Live_Code/Global_Systems/User_Tools/Nuke_User_Tools/Rich/projectionist/icons/at.png
def projectionist_create_projector_panel():
	import projectionist.projectionist
	projectionist.projectionist.create_projector_panel()

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/PROJECTORS
##   label:Create projection alley from this camera
##   icon://isln-smb/aw_config/Git_Live_Code/Global_Systems/User_Tools/Nuke_User_Tools/Rich/projectionist/icons/alley.png
def projectionist_create_projection_alley_panel():
	import projectionist.projectionist
	projectionist.projectionist.create_projection_alley_panel()

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/PROJECTORS
##   label:Convert this camera to nodal with dolly axis
##   icon://isln-smb/aw_config/Git_Live_Code/Global_Systems/User_Tools/Nuke_User_Tools/Rich/projectionist/icons/nodal.png
def projectionist_convert_to_dolly():
	import projectionist.projectionist
	projectionist.projectionist.convert_to_dolly()

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/PROJECTORS
##   label:Make this camera nodal at 0
##   icon://isln-smb/aw_config/Git_Live_Code/Global_Systems/User_Tools/Nuke_User_Tools/Rich/projectionist/icons/onlyNodal.png
def projectionist_make_selected_cam_nodal():
	import projectionist.projectionist
	projectionist.projectionist.make_selected_cam_nodal()


#-------------------------------------------------------------------
'''This panel is designed to work best with the LocaliseThreaded.py script, written by Frank Rueter.
His script replaces and is a re-working of the nuke.localiseFiles() method, built into Nuke.
Frank's code improves on the localise files function by making it multi-threaded - allowing the user
to continue working while it copies the files to the local disk. Plus, it speeds up copying by virtue of multi-threading.
The LocaliseThreaded script is freely available for download on nukepedia.com.
 '''
# Menu_Item
##  [menu_item]
##   label:Localize Files Panel
##   parent_menus:Pane
##   tooltip:Uses multi-threading to localize files.\nSpeeds up the process and allows you to continue working while it runs.
##   panelID:com.richbobo.LocalizeFiles
def addLFPanel():
	# Check for Nuke release...
	Major = nuke.NUKE_VERSION_MAJOR 
	#Release = nuke.NUKE_VERSION_RELEASE 
	if Major == 9:
		import Localize_Read_Nodes_Panel.LocalizeFilesPanel
		try:
			myPanel = Localize_Read_Nodes_Panel.LocalizeFilesPanel.LocalizeFilesPanel()
			return myPanel.addToPane()
		except:
			pass
	elif Major == 10:		
		import Localize_Read_Nodes_Panel.LocalizeFilesPanel_Nuke10
		try:
			myPanel = Localize_Read_Nodes_Panel.LocalizeFilesPanel_Nuke10.LocalizeFilesPanel_Nuke10()
			return myPanel.addToPane()
		except:
			print "NOPE, couldn't find it...."
			pass

# Menu_Item
##  [menu_item]
##   parent_menus:Nuke/READS
##   label:Localize Files Panel
##   tooltip:Uses multi-threading to localize files.\nSpeeds up the process and allows you to continue working while it runs.
def LocalizeFilesPanel():
	# Check for Nuke release...
	Major = nuke.NUKE_VERSION_MAJOR 
	#Release = nuke.NUKE_VERSION_RELEASE 
	if Major == 9:	
		import Localize_Read_Nodes_Panel.LocalizeFilesPanel
		try:
			Localize_Read_Nodes_Panel.LocalizeFilesPanel.LocalizeFilesPanel().show()
		except:
			pass
	elif Major == 10:
		import Localize_Read_Nodes_Panel.LocalizeFilesPanel_Nuke10
		try:
			Localize_Read_Nodes_Panel.LocalizeFilesPanel_Nuke10.LocalizeFilesPanel_Nuke10().show()
		except:
			pass


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/READS
##   label:Show Embedded Image Color Profile
##   tooltip:Prints embedded Color Profile for image file
def Print_Color_Profile():
	import exiftool_Utilities.exiftoolInfo
	exiftool_Utilities.exiftoolInfo.exiftoolInfo().get_ProfileDescription()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/READS
##   label:Show All Image Metadata Tags
##   tooltip:Prints all image metadata tags readable by exiftool
def Print_All_Metadata_Tags():
	import exiftool_Utilities.exiftoolInfo
	exiftool_Utilities.exiftoolInfo.exiftoolInfo().get_ALL_IMAGE_TAGS()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/VERSIONS
##   label:Version Up (Minor Version --> _x###)
##   shortcut:alt+shift+x:
##   tooltip:Version up that works with an "_x###" in the name.\nThis can be used in conjunction with the existing "_v###" version up feature to create a major-minor versioning system.\nExample Script Name --> "scriptname_v001_x005.nk"\nUse ALT-SHIFT-x for incrementing minor versions and ALT-SHIFT-s for incrementing major versions.
def script_version_up_minor():
	import Script_Version_Up_minor.script_version_up_minor
	Script_Version_Up_minor.script_version_up_minor.script_version_up_minor()


#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/VIEWER
##   label:Save Viewer Image
##   shortcut:alt+v:
##   tooltip:Saves a "screen grab" of the current image in the Viewer window.\nRenders to an image type that you choose by specifying an image extension.\nSupported types --> png, dpx, tiff, tga, jpg, exr
def Save_Viewer_Image():
	import SaveViewerImage.SaveViewerImage
	SaveViewerImage.SaveViewerImage.Save_Viewer_Image()


##-------------------------------------------------------------------
## Menu_Item
### [menu_item]
###   parent_menus:Nuke/WRITES
###   label:Write Node with sRGB ICC Color Profile
###   tooltip:Add Write node that will embed an sRGB ICC Color Profile.\nEnsures that images look correct in color-managed applications.
#def ICC_Color_Profile_Write_Node():
	#import Write_ICC_Profile.ICC_Profile_Write_Node
	#Write_ICC_Profile.ICC_Profile_Write_Node.ICC_Profile_Write_Node()


##-------------------------------------------------------------------
## Menu_Item
### [menu_item]
###   parent_menus:Nuke/WRITES
###   label:Hyundai Write Node with TagImages Metadata
###   shortcut:alt+h:
###   tooltip:Add Write node for Innocean/Hyundai projects.\nRenders will be automatically tagged with AW metadata.
#def Hyundai_Write_Node():
	#import TagImages.Hyundai_Metadata_Tag_WriteNode
	#TagImages.Hyundai_Metadata_Tag_WriteNode.Hyundai_Write_Node()


##-------------------------------------------------------------------
## Menu_Item
### [menu_item]
###   parent_menus:Nuke/WRITES
###   label:Write Dirs. for all Write Nodes
###   tooltip:Immediately create any missing directories for all Write node file paths.
#def Create_Write_Dirs_For_All_Write_Nodes():
	#import CreateWriteDirs.CreateWriteDirs
	#CreateWriteDirs.CreateWriteDirs.Create_Write_Dirs_For_All_Write_Nodes()

#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   parent_menus:Nuke/WRITES
##   label:Create Text_File_Path_Viewer
def Create_Text_File_Path_Viewer():
	nod = nuke.createNode("Text",'label "View Output Path here..." message "\[value \[value input.name].file]" name File_Path_text_node font C:/Windows/Fonts/arial.ttf translate {0 50} size 20')
	box_knb = nod.knob("box")
	box_knb.setValue((0.0, 0.0, 0.0, 0.0))
	center_knb = nod.knob("center")
	center_knb.setValue((0.0,0.0))
	yjustify_knb = nod.knob("yjustify")
	yjustify_knb.setValue("baseline")

##-------------------------------------------------------------------
## Menu_Item
### [menu_item]
###   parent_menus:Nuke/sRGB WORKFLOW
###   label:Add Photoshop/sRGB Preview Tools and Write Node.
###   tooltip:Adds Common Tools for sRGB Workflow.
#def Add_sRGB_Preview_Tools_Group():
	#import sRGB_Preview_Tools.Photoshop_sRGB_Preview_Tools
	#sRGB_Preview_Tools.Photoshop_sRGB_Preview_Tools.start()
