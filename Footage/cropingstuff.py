import nuke
import nukescripts.nodes

# Menu_Item
#  [menu_item]
#   label:CornerPin Setup Alpha
#   tooltip:Does And AutoCrop On The Selected Cornerpin Node And The The Node To Autocrop Using The a channel and applies That info to the selected Cornerpin
#   arg:"a"
#
#   shift_label:CornerPin Setup rgb
#   shift_tooltip:Does And AutoCrop On The Selected Cornerpin Node And The The Node To Autocrop Using The rgb channel and applies That info to the selected Cornerpin
#   shift_arg:"rgb"
#
#   ctrl_label:CornerPin Setup rgba
#   ctrl_tooltip:Does And AutoCrop On The Selected Cornerpin Node And The The Node To Autocrop Using The rgba channel and applies That info to the selected Cornerpin
#   ctrl_arg:"rgba"
def autocrop_to_cornerpin(layer):
	"""Run the CurveTool's AutoCrop function on each selected node over the
	specified frame range and channels. If the range values are None, the
	project first_frame and last_frame are used; if inc is None, 1 is used.
	After execution, the CurveTool AutoCrop results are copied into a Crop
	node attached to each selected node."""

	# Sort out execute range
	root = nuke.root()
	first = int(root.knob("first_frame").value())
	last = int(root.knob("last_frame").value())
	inc = 1
	
	# Remember original set of selected nodes...we'll need this
	original_nodes = nuke.selectedNodes()
	
	# Deselect everything so we can add CurveTool nodes
	all_nodes = nuke.allNodes()
	for i in all_nodes:
		i.knob("selected").setValue(False)
	
	for i in original_nodes:
		# Reselect originally selected nodes and create a CurveTool node,
		# which will automatically connect to the last selected.
		i.knob("selected").setValue(True)
		autocropper = nuke.createNode("CurveTool",
		                              '''operation 0 ROI {0 0 input.width input.height} Layer %s label "Processing Crop..." selected true''' % (str(layer), ), False)
		
		# Execute the CurveTool node thru all the frames
		nuke.executeMultiple([autocropper,], ([first, last, inc],))
		
		# select the curvewriter
		autocropper.knob("selected").setValue(True)
		
		# add crop node
		cropnode = nuke.createNode("Crop", 'label "DML Auto\nCrop"', False)
		
		# put the new data from the autocrop into the new crop
		cropbox = cropnode.knob("box")
		autocropbox = autocropper.knob("autocropdata")
		cropbox.copyAnimations(autocropbox.animations())
		
		# turn on the animated flag
		cropnode.knob("indicators").setValue(1)
		
		# deselect everything
		all_nodes = nuke.allNodes()
		for j in all_nodes:
			j.knob("selected").setValue(False)
		
		# select the curvewriter and delete it
		autocropper.knob("selected").setValue(True)
		
		# delete the autocropper to make it all clean
		nukescripts.nodes.node_delete()
		
		# deselect everything
		all_nodes = nuke.allNodes()
		for j in all_nodes:
			j.knob("selected").setValue(False)
			
		# select the new crop
		cropnode.knob("selected").setValue(True)
		
		# place it in a nice spot
		nuke.autoplace(cropnode)
		
		CornerPin = nuke.createNode("CornerPin2D", 'label "DML Auto\nCornerPin"', False)
		
		#CornerPin.knob("selected").setValue(False)
		cropnode.knob("selected").setValue(True)
		nuke.autoplace(CornerPin)
		
		CornerPin.knob("selected").setValue(False)
		cropnode.knob("selected").setValue(False)
		
		from1 = CornerPin.knob("from1")
		from2 = CornerPin.knob("from2")
		from3 = CornerPin.knob("from3")
		from4 = CornerPin.knob("from4")
		
		to1 = CornerPin.knob("to1")
		to2 = CornerPin.knob("to2")
		to3 = CornerPin.knob("to3")
		to4 = CornerPin.knob("to4")
		
		animx = cropbox.animation(0)
		animy = cropbox.animation(1)
		animr = cropbox.animation(2)
		animt = cropbox.animation(3)
		
		from1.copyAnimation(0,animx)
		from1.copyAnimation(1,animy)

		to1.copyAnimation(0,animx)
		to1.copyAnimation(1,animy)
		
		from2.copyAnimation(0,animr)
		from2.copyAnimation(1,animy)

		to2.copyAnimation(0,animr)
		to2.copyAnimation(1,animy)

		from3.copyAnimation(0,animr)
		from3.copyAnimation(1,animt)
		
		to3.copyAnimation(0,animr)
		to3.copyAnimation(1,animt)
		
		from4.copyAnimation(0,animx)
		from4.copyAnimation(1,animt)
		
		to4.copyAnimation(0,animx)
		to4.copyAnimation(1,animt)