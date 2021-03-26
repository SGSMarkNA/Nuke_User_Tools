

#############################################################################################
######################## Imports: ###########################################################

try:
	import nuke
except Exception:
	pass

try:
	## Initialize Write node tab and callbacks for adding an ICC profile to rendered inages...
	from Custom_ICC_Write_Node import Custom_ICC_Write_Node
except Exception:
	pass


#############################################################################################
######################## addOnCreate callbacks: #############################################

try:
	## Create the ICC Knobs when a script makes a Write node...
	nuke.addOnCreate(Custom_ICC_Write_Node.createICCKnobs, (), {}, 'Write')
except Exception:
	pass

try:
	## Force the addAfterFrameRender callback to be "sticky", by setting it each time the script is loaded...
	nuke.addOnCreate(Custom_ICC_Write_Node.initialize_ICC_Profile_Knob_Callbacks, (), {}, 'Write')
except Exception:
	pass

try:
	## Force the addAfterFrameRender callback to be "sticky", by setting it each time the script is loaded...
	nuke.addOnCreate(Custom_ICC_Write_Node.initialize_TagImages_Knob_Callbacks, (), {}, 'Write')
except Exception:
	pass


#############################################################################################
######################## addKnobChanged callbacks: ##########################################

try:
	## Add the knobChanged functions, including adding the AfterFrameRender callback...
	nuke.addKnobChanged(Custom_ICC_Write_Node.knobChanged, (), {}, 'Write')
except Exception:
	pass



