import nuke
#from Write_ICC_Profile import Write_ICC_Profile_with_Args

############################################################################################################
## Knobs

def createICCKnobs(knb_event=False):
	''''''
	Node = nuke.thisNode()

	if 'ICC_Profile_Tab' not in Node.knobs():
		# Create User knobs...
		tabKnob = nuke.Tab_Knob('ICC_Profile_Tab', 'ICC Profile')
		dividerKnob_1 = nuke.Text_Knob('divider_knob_1', '')
		instructKnob = nuke.Text_Knob('instruct_knob', 'Select an ICC Profile: ')
		ICC_Knob = nuke.Enumeration_Knob('icc_knob', '', ['Empty', 'sRGB_profile_from_Photoshop.icc', 'AdobeRGB1998.icc', 'REC709.icc', 'REC2020.icc', 'ACESCG Linear.icc'])
		dividerKnob_2 = nuke.Text_Knob('divider_knob_2', '')
		warningKnob_1 = nuke.Text_Knob('warning_knob_1', 'Use ONLY with PNG, JPG and TIF image types!')
		TagImages_Toggle_Knob = nuke.Boolean_Knob('tagimages_knob', 'Add Photoshop Metadata')
		Hyundai_Toggle_Knob = nuke.Boolean_Knob('hyundai_knob', 'Rearrange Folders for Innocean/Hyundai project.')
		for knob in (tabKnob, dividerKnob_1, instructKnob, ICC_Knob, dividerKnob_2, warningKnob_1, TagImages_Toggle_Knob, Hyundai_Toggle_Knob):
			Node.addKnob(knob)
	else:
		pass

############################################################################################################
## Function Calls for Callbacks...

def add_selected_ICC_profile(ICC_Profile_Name):
	'''
	Function that builds the Python command which writes the ICC Profile metadata...
	'''
	from Write_ICC_Profile import Write_ICC_Profile_with_Args
	Write_ICC_Profile_with_Args.Write_ICC_Profile_with_Args().copy_ICC_profile_to_image(ICC_Profile_Name)

def create_TagImages_args_file():
	'''
	Function that builds the Python command which creates the metadata file to use for tagging...
	'''
	from TagImages import TagImages
	TagImages.TagImages().create_args_file()
	print('Executing create_TagImages_args_file') 

def do_TagImages_tagging():
	'''
	Function that builds the Python command to add Photoshop metadata tags to the rendered images...
	'''
	from TagImages import TagImages
	TagImages.TagImages().tag_images()
	print('Executing do_TagImages_tagging')

def do_TagImages_Hyundai_folder_rearrangment():
	'''
	Function that builds the Python command that rearranges the folder structure for Innocean/Hyundai projects...
	'''
	from TagImages import TagImages
	TagImages.TagImages().create_nested_color_and_trim_folders()
	print('Executing do_TagImages_Hyundai_folder_rearrangment')

############################################################################################################
## Remove Callbacks...

def remove_existing_ICC_callbacks():
	'''
	Find and remove all of the existing callbacks of the type "Custom_ICC_Write_Node.add_selected_ICC_profile".
	Each time a user selects a different item on the ICC Profile name selector knob, a new call back is added.
	This makes sure to keep only the most recent callback.
	'''
	argitems_ICC_afterFrameRenders = []
	if nuke.afterFrameRenders and 'Write' in nuke.afterFrameRenders:
		for callback in nuke.afterFrameRenders['Write']:
			if callback[0] == add_selected_ICC_profile:
				argitems_ICC_afterFrameRenders.append(callback[1])
				print('argitems_ICC -->', argitems_ICC_afterFrameRenders)
		for arg_ICC in argitems_ICC_afterFrameRenders:
			nuke.removeAfterFrameRender(add_selected_ICC_profile, arg_ICC, {}, 'Write')
			print('Removed ', callback[0], arg_ICC)

def remove_existing_TagImages_callbacks():
	'''
	Find and remove all of the existing callbacks if the user unchecks the TagImages checkbox knob...
	'''
	argitems_TagImages_beforeRenders = []
	if nuke.beforeRenders and 'Write' in nuke.beforeRenders:
		for callback in nuke.beforeRenders['Write']:
			if callback[0] == create_TagImages_args_file:
				argitems_TagImages_beforeRenders.append(callback[1])
				print('argitems_TagImages -->', argitems_TagImages_beforeRenders)
		for arg_TagImages in argitems_TagImages_beforeRenders:
			nuke.removeBeforeRender(create_TagImages_args_file, arg_TagImages, {}, 'Write')
			print('Removed ', callback[0], arg_TagImages)

def remove_existing_Tagging_callbacks():
	''''''
	argitems_TagImages_afterFrameRenders = []
	if nuke.afterFrameRenders and 'Write' in nuke.afterFrameRenders:
		for callback in nuke.afterFrameRenders['Write']:
			if callback[0] == do_TagImages_tagging:
				argitems_TagImages_afterFrameRenders.append(callback[1])
				print('argitems_Tagging -->', argitems_TagImages_afterFrameRenders)			
		for arg_tagging in argitems_TagImages_afterFrameRenders:
			nuke.removeAfterFrameRender(do_TagImages_tagging, arg_tagging, {}, 'Write')
			print('Removed ', callback[0], arg_tagging)
			print('DOING IT NOW!')

def remove_existing_Hyundai_callbacks():
	'''
	Find and remove all of the existing callbacks if the user unchecks the Hyundai checkbox knob...
	'''	
	argitems_TagImages_Hyundai_afterFrameRenders = []
	if nuke.afterFrameRenders and 'Write' in nuke.afterFrameRenders:
		for callback in nuke.afterFrameRenders['Write']:
			if callback[0] == do_TagImages_Hyundai_folder_rearrangment:
				argitems_TagImages_Hyundai_afterFrameRenders.append(callback[1])
				print('argitems_TagImages_Hyundai -->', argitems_TagImages_Hyundai_afterFrameRenders)			
		for arg_Hyundai in argitems_TagImages_Hyundai_afterFrameRenders:
			nuke.removeAfterFrameRender(do_TagImages_Hyundai_folder_rearrangment, arg_Hyundai, {}, 'Write')
			print('Removed ', callback[0], arg_Hyundai)


############################################################################################################
## Initialize Callbacks

def initialize_ICC_Profile_Knob_Callbacks():
	'''
	Function to use when script is loaded, so that the initial ICC Profile name selection gets added as an AfterFrameRender callback.
	Otherwise, the callback is not sticky and needs to be manually re-selected each time the script is opened...
	'''
	Node = nuke.thisNode()
	ICC_Knob = Node.knob('icc_knob')
	ICC_Profile_Name = ICC_Knob.value()
	# Set some color transforms...
	r,g,b = 1.0, 1.0, 1.0
	WhiteTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
	r,g,b = .66, 0.0, 0.0
	RedTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
	r,g,b = 0.0, 0.0, 0.0
	BlackTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)

	if ICC_Knob:
		if ICC_Profile_Name != 'Empty':
			## Add the code for AfterFrameRender...
			nuke.addAfterFrameRender(add_selected_ICC_profile, ICC_Profile_Name, {}, 'Write')
			# Change the look of the node to indicate to the user that this node is special...
			Node['note_font_color'].setValue(RedTextColor)
			Node['note_font'].setValue('Verdana Bold')
			Node['note_font_size'].setValue(14.0)
			Node['label'].setValue('ICC Profile: ' + ICC_Profile_Name)
		else:
			## Remove any existing code...
			nuke.removeAfterFrameRender(add_selected_ICC_profile, ICC_Profile_Name, {}, 'Write')
			# Change the look of the node back to the default to indicate to the user that this node is normal...
			Node['note_font_color'].setValue(BlackTextColor)
			Node['note_font'].setValue('Verdana')
			Node['note_font_size'].setValue(11.0)
			Node['label'].setValue('')

def initialize_TagImages_Knob_Callbacks():
	'''
	Function to use when script is loaded, so that the initial TagImages selection gets set as an AfterFrameRender callback.
	Otherwise, the callback is not sticky and needs to be manually re-selected each time the script is opened...
	'''
	Node = nuke.thisNode()
	TagImages_Knob = Node.knob('tagimages_knob')
	Hyundai_Knob = Node.knob('hyundai_knob')

	if TagImages_Knob:
		if TagImages_Knob.value() == True:
			# Add the code for for the callbacks...
			nuke.addBeforeRender(create_TagImages_args_file, (), {}, 'Write')
			nuke.addAfterFrameRender(do_TagImages_tagging, (), {}, 'Write')
			print('INIT: Added TagImages callbacks')
		elif TagImages_Knob.value() == False:
			# Remove any existing callbacks...
			remove_existing_TagImages_callbacks()
			print('INIT: Removed existing TagImages callbacks')

	if Hyundai_Knob:
		if Hyundai_Knob.value() == True:
			# Add the code for for the callbacks...
			nuke.addAfterFrameRender(do_TagImages_Hyundai_folder_rearrangment, (), {}, 'Write')
			print('INIT: Added Hyundai callbacks')
		elif Hyundai_Knob.value() == False:
			# Remove any existing callbacks...
			remove_existing_Hyundai_callbacks()
			print('INIT: Removed existing Hyundai callbacks')

############################################################################################################
## knobChanged

def knobChanged():
	''''''
	# Set some color transforms...
	r,g,b = 1.0, 1.0, 1.0
	WhiteTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
	r,g,b = .66, 0.0, 0.0
	RedTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
	r,g,b = 0.0, 0.0, 0.0
	BlackTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)

	Node = nuke.thisNode()
	Knob = nuke.thisKnob()

	ICC_KNOB = Node.knob('icc_knob')
	TAGIMAGES_KNOB = Node.knob('tagimages_knob')
	HYUNDAI_KNOB = Node.knob('hyundai_knob')
	KNOBS = (ICC_KNOB, TAGIMAGES_KNOB, HYUNDAI_KNOB)

	if Knob in KNOBS:
		print(Knob.name())
		print(Knob.value())
		## FIRST, REMOVE ALL EXISTING CALLBACKS...
		remove_existing_ICC_callbacks()
		remove_existing_TagImages_callbacks()
		remove_existing_Tagging_callbacks()
		remove_existing_Hyundai_callbacks()

		for Knob in KNOBS:
			## THEN, ADD THEM IN THIS ORDER, IF TRUE...
			if Knob == ICC_KNOB:
				# Get the selected ICC profile name from the dropdown knob... 
				ICC_Profile_Name = Knob.value()
				print(ICC_Profile_Name) 
				if ICC_Profile_Name != 'Empty':
					# Add the code for for the new AfterFrameRender callback...
					nuke.addAfterFrameRender(add_selected_ICC_profile, ICC_Profile_Name, {}, 'Write')
					# Change the look of the node to indicate to the user that this node is special...
					Node['note_font_color'].setValue(RedTextColor)
					Node['note_font'].setValue('Verdana Bold')
					Node['note_font_size'].setValue(14.0)
					Node['label'].setValue('ICC Profile: ' + ICC_Profile_Name)
					print('Added ICC callbacks')
				else:
					# Remove any existing callbacks of the type "Custom_ICC_Write_Node.add_selected_ICC_profile...
					remove_existing_ICC_callbacks()
					# Change the look of the node back to the default to indicate to the user that this node is normal...
					Node['note_font_color'].setValue(BlackTextColor)
					Node['note_font'].setValue('Verdana')
					Node['note_font_size'].setValue(11.0)
					Node['label'].setValue('')

			#elif Knob == HYUNDAI_KNOB:
				#if Knob.value() == True and Node.knob('tagimages_knob').value() == True:				
					## Add the code for for the callbacks...
					#nuke.addAfterFrameRender(do_TagImages_Hyundai_folder_rearrangment, (), {}, 'Write')
					#print 'Added Hyundai callbacks'
				##else:
					##pass
					## If there's not tagging going on, then we don't need to rearrange any folders...
					####Knob.setValue(False)
					####remove_existing_Hyundai_callbacks()

			elif Knob == TAGIMAGES_KNOB:
				if Knob.value() == True:					
					# Add the code for for the callbacks...
					nuke.addBeforeRender(create_TagImages_args_file, (), {}, 'Write')
					nuke.addAfterFrameRender(do_TagImages_tagging, (), {}, 'Write')
					Node.knob('hyundai_knob').setEnabled(True)
					print('Added TagImages callbacks')
				else:
					Node.knob('hyundai_knob').setEnabled(False)

			if Knob == HYUNDAI_KNOB:
				if Knob.value() == True and Node.knob('tagimages_knob').value() == True:				
					# Add the code for for the callbacks...
					nuke.addAfterFrameRender(do_TagImages_Hyundai_folder_rearrangment, (), {}, 'Write')
					print('Added Hyundai callbacks')
				else:
					# If there's not tagging going on, then we don't need to rearrange any folders...
					Knob.setValue(False)
					remove_existing_Hyundai_callbacks()



"""
###############################################

Note: Use to check for callbacks on a node...

Node = nuke.selectedNode()

print nuke.beforeRenders
print nuke.afterFrameRenders
print nuke.afterRenders

###############################################
"""
