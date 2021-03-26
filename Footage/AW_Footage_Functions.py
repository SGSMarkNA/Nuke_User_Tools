
# Menu_Item
#  [menu_item]
#   label:Reload All Footage
#   tooltip:Scans For All Read Nodes and Executes The Reload Function
def Reload_All_Footage():
	import Nuke_Scripts.NodeFns.footage
	reload(Nuke_Scripts.NodeFns.footage)
	Nuke_Scripts.NodeFns.footage.reload_all_footage()
	
# Menu_Item
#  [menu_item]
#   label:Auto Crop Selected
#   tooltip:Auto Crops The Selected Nodes\n Warning This Is Time Intensive
def Auto_Crop_Selected():
	import Nuke_Scripts.NodeFns.croping
	reload(Nuke_Scripts.NodeFns.croping)
	Nuke_Scripts.NodeFns.croping.auto_crop()
	

	
# Menu_Item
#  [menu_item]
#   label:Collect ALL Read Nodes
#   tooltip:Makes A New Group And Makes A Copy Of All The Read Nodes In The Nuke Script
def Collect_ALL_Read_Nodes():
	import Nuke_Scripts.NodeFns.footage
	reload(Nuke_Scripts.NodeFns.footage)
	Nuke_Scripts.NodeFns.footage.collect_read_nodes()
	
# Menu_Item	
def Exr_Layer_Extractor():
	import Nuke_Scripts.NodeFns.split_layers
	reload(Nuke_Scripts.NodeFns.split_layers)
	Nuke_Scripts.NodeFns.split_layers.split_layers()
