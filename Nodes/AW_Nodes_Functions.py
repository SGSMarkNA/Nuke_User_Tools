import nuke
import importlib

# Menu_Item
#  [menu_item]
#   label:Align Horizontal
#   tooltip:Align The Selected Nodes Horizontally
#   shortcut:shift+h
#   arg:"h"
#  [menu_item]
#   label:Align Vertical
#   shortcut:shift+v
#   tooltip:Align The Selected Nodes Vertically
#   arg:"v"
def Aline_Nodes(direction):
	import Nuke_Scripts.NodeGraphFns.transforms
	importlib.reload(Nuke_Scripts.NodeGraphFns.transforms)
	undo = nuke.Undo()
	undo.begin()
	Nuke_Scripts.NodeGraphFns.transforms.aline_Avarage(direction=direction)
	undo.end()

# Menu_Item
#  [menu_item]
#   label:Scale From Center
#   tooltip:Scale The Selected Nodes From Collective Center
def aw_nodes_scale_From_Center():
	import Nuke_Scripts.NodeGraphFns.transforms
	importlib.reload(Nuke_Scripts.NodeGraphFns.transforms)
	Nuke_Scripts.NodeGraphFns.transforms.scale_from_center()

# Menu_Item
#  [menu_item]
#   label:Multi Node Declone
#   tooltip:Declone Selected Nodes
def Multi_Node_Declone():
	import Nuke_Scripts.NodeFns.declone
	importlib.reload(Nuke_Scripts.NodeFns.declone)
	Nuke_Scripts.NodeFns.declone.multi_declone()

# Menu_Item
#  [menu_item]
#   label:Multi Input Connect
def Multi_Input_connect():
	import Nuke_Scripts.NodeFns.connections
	importlib.reload(Nuke_Scripts.NodeFns.connections)
	Nuke_Scripts.NodeFns.connections.multi_input_connect()

# Menu_Item
#  [menu_item]
#   label:Multi Output Connect
def Multi_Output_connect():
	import Nuke_Scripts.NodeFns.connections
	importlib.reload(Nuke_Scripts.NodeFns.connections)
	Nuke_Scripts.NodeFns.connections.multi_output_connect()

	