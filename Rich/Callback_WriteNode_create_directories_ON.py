import nuke


############################################################################################################
## Add knobDefault for automatically creating missing directories...
Major = nuke.NUKE_VERSION_MAJOR
if Major >= 10:
	nuke.knobDefault('Write.create_directories', 'True')


############################################################################################################
#####  Convert Existing Write nodes to make sure the create_directories knob is checked...

def set_create_directories_ON_for_existing_write_nodes():
	'''
	Make sure that all Write nodes' create_directories knob is turned on...
	'''
	Node = nuke.thisNode()
	try:
		Node.knob('create_directories').setValue(True)
	except Exception:
		# Something went wrong, so we should just leave things as they are, to preserve any existing functionality...
		pass


#############################################################################################
#####  addOnCreate Callback:
try:
	# Convert any existing Write nodes to make sure the create_directories knob is checked...
	nuke.addOnCreate(set_create_directories_ON_for_existing_write_nodes, nodeClass = 'Write')
except Exception:
	pass