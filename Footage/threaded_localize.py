#!/usr/bin/env python
import threading
import nuke
from Nuke_Scripts.NodeGraphFns import node_filters

class Threaded_localiseFiles( threading.Thread ):
	def __init__(self):
		threading.Thread.__init__( self )
		self.expression ='[value base_image_folder]/[value working_sub_folder]/[value config_image_name][value image_sufix]/[value image_prefix]_[value config_image_name][value image_sufix]_%0[value image_frame_padding]d.[value image_ext]'
	def run( self ):
		all_file_knobs = []
		for node in node_filters.filter_node_class_recursivly("Config_Image_Reader"):
			node = nuke.toNode(node.fullName()+".Config_Image_Read_Seq")
			knb = node.knob("file")
			all_file_knobs.append(knb)
			knb.setValue(nuke.filename(node))
		nuke.localiseFiles(all_file_knobs)
		for knb in all_file_knobs:
			knb.setValue(self.expression)
			
			
def Localize_Config_Image_Read_Nodes():
	Threaded_localiseFiles().start()