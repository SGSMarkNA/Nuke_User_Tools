import _thread
import threading



########################################################################
## ICC Code on PyScript knob runs via threading...

def _execute_ICC_Code(Knob):
	# Main function...
	Knob.execute()
	print(Knob.name() + ' executing...')

def _thread_ICC_Code():
	# Thread callable version...
	Node = nuke.thisNode()
	Knob = Node.knob('icc_code_knob')
	nuke.executeInMainThread(_execute_ICC_Code, args=(Knob))

def Run_ICC_Code():
	# Thread function runner...
	threading.Thread(target=_thread_ICC_Code).start()

## knobChanged example...
#if knob_name == "icc_code_knob":
	#threading.Thread(target=_thread_ICC_Code).start()

########################################################################



##---------------------------------------------------------------------------------
## These functions are necessary to prevent threading complaints from Nuke when
## trying to activate all of the collected nodes' reload buttons at the same time...

def _do_reload(self, node):
	node.knob('reload').execute()

def _do_reload_with_thread(self, node):
	nuke.executeInMainThread(self._do_reload, (node,))
	print(node.name() + ' reloaded')

def _reload_all_footage(self):
	'''Runs the threaded function, _do_reload_with_thread, on a list of nodes (gathered inside this method)...'''
	self.AllNodes = Node_Tools()._get_all_nodes()
	self.sourceNodes = Node_Tools()._find_all_source_nodes(self.AllNodes)	
	for node in self.sourceNodes:
		# Push the reload button on all of the selected nodes.
		# Do it as a thread, though, because Nuke complains saying,
		# "I'm already executing something..."
		_thread.start_new_thread(self._do_reload_with_thread, (node,))
##---------------------------------------------------------------------------------