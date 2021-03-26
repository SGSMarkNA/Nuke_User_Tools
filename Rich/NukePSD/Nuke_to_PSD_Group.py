import nuke
import thread

GroupNode = nuke.thisNode()


def _get_group_input_layers():
	'''Get unique layers list from input.'''
	ConnectedNode = GroupNode.input(0)
	#print 'ConnectedNode --> ', ConnectedNode.name()
	if ConnectedNode:
		Layers = []
		Channels = ConnectedNode.channels()
		#print 'Channels --> ', Channels
		for name in Channels:
			name = name.split('.')[0]
			Layers.append(name)
		Layers = list(set(Layers))
		#print 'Layers --> ', Layers
		return Layers
	else:
		nuke.message("Please connect something to the input!")
		return


def _create_layer_order_knobs(Layers):
	''''''
	# Remove any existing knobs before making new ones...
	try:
		_remove_Int_Knobs()
		_remove_replace_layername_knob()
	except:
		# No IntegerKnobs to remove...
		pass
	# Add new Int_Knobs (which actually return a float - go figure) based on the layer names found
	# in the input to the group node, used for setting the numerical ordering of the layers in the PSD file...
	OrderKnobs = []
	if Layers:
		for layer in Layers:
			Knob_string = 'nuke.' + 'Int_Knob' + '(' + "'" + "_ORDER_" + layer + "'" + ', ' + "'" + layer + "'" + ')'
			Knob = eval(Knob_string)
			GroupNode.addKnob(Knob)
			Knob.setFlag(nuke.STARTLINE)
			# Keep a list of all the created knobs for re-use...
			#OrderKnobs.append(Knob)
		#print 'OrderKnobs --> ', OrderKnobs
		#return OrderKnobs

		# Add the layer name replacement knob, if we are using multiple views...
		if len(nuke.views()) > 1:
			_create_layer_name_replacement_knob(Layers)
		else:
			pass

	else:
		nuke.message("No image channels found!")
		return


def _create_layer_name_replacement_knob(Layers):
	''''''
	# Create pulldown knob with layer names. User can select a single layer name to be replaced by the view name...
	Layers.insert(0, 'none')
	layername_replacement_knob = nuke.Enumeration_Knob('replace_layername', 'Replace Layer Name with View Name:', Layers)
	GroupNode.addKnob(layername_replacement_knob)
	layername_replacement_knob.setFlag(nuke.STARTLINE)


def _remove_replace_layername_knob():
	''''''
	
	GroupNodeKnobs = GroupNode.allKnobs()

	for knob in GroupNodeKnobs:
		if knob.name() == "replace_layername":
			try:
				GroupNode.removeKnob(knob)
			except ValueError:
				print 'ValueError: Knob %s could not be removed...' % knob.name()
			except KeyError:
				print 'KeyError: Knob %s could not be removed...' % knob.name()


def _create_group_layer_nodes(Layers):
	''''''
	if Layers:
		with GroupNode:
			# Remove existing nodes, first...
			_cleanup_nodes()

			nuke.toNode('Input1').setSelected(True)

			Reformat = nuke.createNode('Reformat', inpanel=False)
			Reformat['label'].setValue("THIS FIXES PHOTOSHOP\nONE PIXEL OFFSET PROBLEM")
			Reformat['black_outside'].setValue(True)
			#NodesToDelete.append(Reformat)

			for index, layername in enumerate(Layers):
				# Make sure we don't use the 'none' value that was inserted in _create_layer_name_replacement_knob...
				if layername != 'none':
					ShuffleNode = nuke.createNode('Shuffle', inpanel=False)
					ShuffleNode.knob('in').setValue(str(layername))
					ShuffleNode.setInput(0, Reformat)
					#ShuffleNodes.append(ShuffleNode)
					#NodesToDelete.append(ShuffleNode)

					WriteNode = nuke.createNode('Write', inpanel=False)
					WriteNode['channels'].setValue('rgba')
					OutputDir = ""
					WriteNode['file'].setValue(OutputDir + '/' + 'PNG' + '/' + layername + '/' + layername + '_%04d' + '.png')
					WriteNode['file_type'].setValue('png')
					WriteNode['ICC_knob'].setValue('sRGB.icc')
					WriteNode['render_order'].setValue(index+1)
					WriteNode['views'].setValue(GroupNode['views'].value())
					#WriteNodes.append(WriteNode)
					#NodesToDelete.append(WriteNode)

					afterRender_callback = """import NukePSD.Nuke_to_PSD
NPSD = NukePSD.Nuke_to_PSD.NukePSD()
NPSD._run_write_data_file()
NPSD._run_JS_command()"""
				if layername != Layers[-1]:
					pass
				else:
					WriteNode['afterRender'].setValue(afterRender_callback)
	else:
		return


def _cleanup_nodes():
	'''Delete existing nodes in the Group node before making new ones. Initiated by clicking the Scan button on the UI.'''
	try:
		for Node in GroupNode.nodes():
			if Node.Class() == ('Input'):
				pass
			elif Node.Class() == ('Output'):
				pass
			else:
				nuke.delete(Node)
	except ValueError:
		print "Value Error: Check in Group for nodes that were not deleted..."


def _remove_Int_Knobs():
	''''''
	# Get all the knobs in the Group...
	GroupNodeKnobs = GroupNode.allKnobs()
	#print 'GroupNodeKnobs -->', GroupNodeKnobs
	# Set up some variables for removal of preexisting Int_Knobs knobs when the Scan button is pressed...
	order_knobs_to_remove = []
	# Make a list of any knobs with "_ORDER_" in the name...
	for knob in GroupNodeKnobs:
		if knob.name().startswith("_ORDER_"):
			order_knobs_to_remove.append(knob)
	#print 'order_knobs_to_remove --> ', order_knobs_to_remove

	# Get all the knob objects...
	Knobs = GroupNode.knobs()
	#print 'Knobs -->>> ', Knobs

	# Remove any old layer order listings (Int_Knob) when the Scan button is pressed, before we make new ones...    
	for knob in order_knobs_to_remove:
		try:
			GroupNode.removeKnob(knob)
		except ValueError:
			print 'ValueError: Knob %s could not be removed...' % knob.name()
		except KeyError:
			print 'KeyError: Knob %s could not be removed...' % knob.name()


def _pre_render_sanity_checks():
	'''Sanity checks before firing off a render...'''

	check = True

	dir_text = GroupNode.knob('dir_text').value()
	if not dir_text:
		nuke.message("Please enter an output directory.")
		check = False

	PSD_NAME = GroupNode.knob('PSD_filename').value()
	if not PSD_NAME:
		nuke.message("Please enter a name for the PSD file.")
		check = False

	# Get the num_views, so it can be checked against the afterRenderCount global value...
	selected_views = (GroupNode.knob('views').value()).split()
	num_views = len(selected_views)
	if not num_views:
		nuke.message("Please select at least one view to render.")
		check = False

	# Get knobname and knob object from GroupNode.knobs() dictionary...
	layer_order_dict = {}
	Layers = _get_group_input_layers()
	for knobname, knob in GroupNode.knobs().iteritems():
		knobname = knobname.lstrip('_ORDER_')
		if knobname in Layers:
			layer_order_dict[knobname] = knob.value()	
	# Check to see if all the layers are still set to zero...
	if all(value == 0 for value in layer_order_dict.values()):
		nuke.message("Please set the layer order for the PSD files.")
		check = False

	# Check for missing or switched channels, which can cause the Shuffle nodes to have 'none' as their input...
	for Node in GroupNode.nodes():
		if Node.Class() == ('Shuffle'):
			InValue = Node['in'].value()
			if InValue == 'none':
				print ('The Shuffle node named "%s" has an input of "none".\n\nThe Photoshop build will most likely fail...\n\n(Check for missing or switched rgba channels.)' % Node.name())
				nuke.critical('The Shuffle node named "%s" has an input of "none".\n\nThe Photoshop build will most likely fail...\n\n(Check for missing or switched rgba channels.)' % Node.name())
				check = False
			else:
				pass
		else:
			pass

	return check


def _render_write_nodes():
	''''''
	# Get the start frame, end frame and frame range for the render...
	first = int(nuke.root().knob('first_frame').value())
	last = int(nuke.root().knob('last_frame').value())
	FrameRange = [(first, last, 1)]

	with GroupNode:
		WriteNodes = [node for node in GroupNode.nodes() if node.Class() == 'Write']
		#print 'WriteNodes --> ', WriteNodes

		# If we used the Render Views Selector Panel to select views on the GroupNode, it's not enough to trigger
		# a knobChanged event. So, we have to make a last pass to make sure that the Write nodes are in sync with
		# the GroupNode's view knob before we render...		
		try:
			for WriteNode in WriteNodes:
				WriteNode['views'].setValue(GroupNode.knob('views').value())
		except:
			pass

		# Multiple Write node render...
		try:
			## I changed things to have _render_write_nodes() called via a knobChanged callback on the "Render Local" button.
			## Unfortunately, that caused an "I'm already executing something else..." error.
			## So, I had to use the executeInMainThread workaround, below. Seems to work.
			##nuke.executeMultiple(tuple(WriteNodes), tuple(FrameRange))
			
			WriteNodes = tuple(WriteNodes)
			FrameRange = tuple(FrameRange)
			#print WriteNodes
			#print FrameRange			
			def do_execute_multiple(WriteNodes, FrameRange):
				nuke.executeMultiple(tuple(WriteNodes), tuple(FrameRange))
				
			def do_execute_multiple_in_thread(WriteNodes, FrameRange):
				nuke.executeInMainThread(do_execute_multiple, (WriteNodes, FrameRange))
			
			thread.start_new_thread(do_execute_multiple_in_thread, (WriteNodes, FrameRange))

		except Exception as error:
			status = str(error)
			print status
			#nuke.message(status + '\nCheck for "%V" in Output Dir.')
			nuke.message(status)



######################################################################
##                IMPORTANT!!
##
##  Group Node button code:
##      Paste the (uncommented) code into the PyScript buttons.
##      Note: May need to format as spaces only - tabs may not work.
##
######################################################################

### 'Scan' PyScript button code:
#import NukePSD.Nuke_to_PSD_Group
#reload(NukePSD.Nuke_to_PSD_Group)
#Layers = NukePSD.Nuke_to_PSD_Group._get_group_input_layers()
#NukePSD.Nuke_to_PSD_Group._create_layer_order_knobs(Layers)
#NukePSD.Nuke_to_PSD_Group._create_group_layer_nodes(Layers)




## ---------------------------------------------------------------------------------------------------------------
## ------- NOTE: OBSOLETE!!  -------------------------------------------------------------------------------------
##
## The two below are now incorporated into the knobChanged callbacks via Assign_knobChanged_code_to_GroupNode.py.
## There is no longer any code being run in these PyScript buttons! This is only here for historical reference...
##
## ---------------------------------------------------------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------

## 'Render' PyScript button code:
#if nuke.modified():
	#if nuke.ask('Your script has been modified.\n"Save As" before rendering?'):
		#nuke.scriptSaveAs()
	#else:
		#pass

#try:
	#del nuke.__dict__["_afterRenderCount"]
#except:
	#pass

#import NukePSD.Nuke_to_PSD_Group
#reload(NukePSD.Nuke_to_PSD_Group)

#check = NukePSD.Nuke_to_PSD_Group._pre_render_sanity_checks()
#if check:
	#NukePSD.Nuke_to_PSD_Group._render_write_nodes()
#else:
	#print "Pre-render check failed!"
	#nuke.critical('Pre-render check failed!')


## 'Submit to Deadline' PyScript button code:
#if nuke.modified():
	#if nuke.ask('Your script has been modified.\n"Save As" before rendering?'):
		#nuke.scriptSaveAs()
	#else:
		#pass

#import NukePSD.Nuke_to_PSD_Group
#reload(NukePSD.Nuke_to_PSD_Group)

#check = NukePSD.Nuke_to_PSD_Group._pre_render_sanity_checks()
#if check:
	#import NukePSD.Nuke_to_PSD_Submitter
	#reload(NukePSD.Nuke_to_PSD_Submitter)
	#NukePSD.Nuke_to_PSD_Submitter.Nuke_to_PSD_SubmitPanel().show()
