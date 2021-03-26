import nuke
import re

def MasterControl_SingleNode(ClassName='', SlaveName='', knb_event=False):
	'''
	Creates a Master Control Node that can set values on knobs of a SlaveNode of the same class.
	Initially, it sets the 'knb_event' flag to False for the first pass through the main function.
	The Master Control Node is then created *before* any knob events are registered. In the hidden
	knobChanged knob on the master control panel, knb_event is always set to True. That ensures that
	only certain parts of the main function are run by the Master Control Node's knobChanged knob.

	Created by Rich Bobo - 09/01/2017
	richbobo@mac.com
	http://richbobo.com
	'''

	if knb_event:
		'''
		The knb_event is True.
		This code runs only on the Master Control Node, after it has been created.
		'''
		this_node = nuke.thisNode()
		knob_name = nuke.thisKnob().name()
		knob_value = nuke.thisKnob().value()

	def Control_Node():
		'''
		This function controls the SlaveNode and is run via the Master Control Node's hidden knobChanged knob.
		When there's a knobChanged event on the Master Control Node, the knob name and value are assigned to
		variables - thisNode, thisKnob, etc. Any undesired knob events get filtered out by the list of knobs_to_ignore.
		'''
		# Get the slave node we're controlling...
		SlaveNode = nuke.toNode(SlaveName)
		# Ignore changes to knobs we want to filter out...
		knobs_to_ignore = ['executing', 'help', 'onCreate', 'onDestroy', 'updateUI', 'autolabel', 'knobChanged', 'panel', 'selected', 'xpos', 'ypos', 'icon', 'indicators', 'showPanel', 'hidePanel', 'nodes', 'scope']    
		# Control the SlaveNode's knobs...
		if this_node:
			if knob_name not in knobs_to_ignore:
				SlaveNode.knob(knob_name).setValue(knob_value)
			else:
				pass

	if not knb_event:
		'''
		The knb_event is False.
		On the first pass through the main wrapper function, only create the Master Control Node. Don't process any knob events, yet!
		'''
		# Strip out any illegal characters in the node class name, so we can use it in the node's name...
		pattern = re.compile(r'[^\w]')
		Clean_ClassName = pattern.sub('_', ClassName)

		# Create the master control class node...
		createMasterControl = 'nuke.nodes.%s(name="MASTER_CONTROL_%s")' % (ClassName, Clean_ClassName)
		Master_Control = eval(createMasterControl)

		# Lock the Master Control Node's name...
		Master_Control.knob('name').setFlag(nuke.READ_ONLY)

		# Float the panel...
		Master_Control.showControlPanel(forceFloat=True)

		# Show the control panel...
		Master_Control.showControlPanel()

		# Sets the hidden "knobChanged" knob to execute the Control_Node() function. The function is set up to return the
		# name and value of any knob that is changed on the Master Control Node. There is also a "knobs_to_ignore" list that
		# acts as a filter so that only meaningful knobs are used to set the values on the SlaveNode.
		# NOTE: This needs to be triple-quoted, with an actual newline and no tabs -- i.e., leave it as is!
		code = """import Nodes_Master_Control_Panel.MasterControl_SingleNode
Nodes_Master_Control_Panel.MasterControl_SingleNode.MasterControl_SingleNode(ClassName=%r, SlaveName=%r, knb_event=True)""" % (ClassName, SlaveName)
		# Set the Master Control Node's knobChanged knob with the code...
		Master_Control.knob('knobChanged').setValue(code)
	else:
		'''
		The knb_event is True.
		This code runs only on the Master Control Node, after it has been created.
		'''
		try:
			Control_Node()
		except ValueError:
			# This catches errors that can occur when exiting Nuke. The knobChanged function fires on the Master Control Node
			# as Nuke is closing. Certain referenced PythonObjects have already been destroyed, which causes ValueErrors...			
			pass


############################################
## EXAMPLE:
## Provide node Class name and Slave node's name...

# MasterControl_SingleNode('Write', 'Write1')
