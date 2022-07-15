import nuke

############################################################################################################
#####  Build Write Node Tab Knobs...

def createMetadataTabKnobs():
	''''''
	Node = nuke.thisNode()

	if 'Metadata_Tab' not in Node.knobs():

		# Create the knobs...
		tabKnob = nuke.Tab_Knob('Metadata_Tab', 'Metadata')	

		## ICC Profile...
		ICCSectionTitle = nuke.Text_Knob('ICC_Section_Title', '', "<FONT COLOR=\"#7777EE\">ICC Profile (JPG, PNG & TIF images):<\FONT>")
		ICCKnob = nuke.Enumeration_Knob('ICC_knob', '', ['Empty', 'sRGB.icc', 'AdobeRGB1998.icc', 'REC709.icc', 'REC2020.icc', 'ACESCG Linear.icc'])
		ICCKnob.clearFlag(nuke.ENDLINE)

		divider2 = nuke.Text_Knob('divider2', '')
		divider2.setFlag(nuke.STARTLINE)
		divider2B = nuke.Text_Knob('divider2B', '')
		divider2B.setFlag(nuke.STARTLINE)

		## XMP/IPTC Data...
		IPTCSectionTitle = nuke.Text_Knob('IPTC_Section_Title', '', "<FONT COLOR=\"#7777EE\">IPTC Data (TIF images only - Required for Innocean/Hyundai projects):<\FONT>")
		IPTCCheckbox = nuke.Boolean_Knob('IPTC_knob', 'Armstrong White Contact/Author Data')
		IPTCCheckbox.setFlag(nuke.STARTLINE)

		divider3 = nuke.Text_Knob('divider3', '')
		divider3.setFlag(nuke.STARTLINE)
		divider3B = nuke.Text_Knob('divider3B', '')
		divider3B.setFlag(nuke.STARTLINE)		

		## ConfigCompBuilder, views-based comps - folders rearrangement for Innocean/Hyundai projects...
		HyundaiFoldersTitle = nuke.Text_Knob('Hyundai_Folders_Title', '', "<FONT COLOR=\"#7777EE\">Views-Based Comp:<\FONT>")
		HyundaiFoldersCheckbox = nuke.Boolean_Knob('Hyundai_knob', 'Rearrange Folders per Innocean/Hyundai requirements.')
		HyundaiFoldersCheckbox.setFlag(nuke.STARTLINE)

		# Add the knobs...
		for knob in (tabKnob, ICCSectionTitle, ICCKnob, divider2, divider2B, IPTCSectionTitle, IPTCCheckbox, divider3, divider3B, HyundaiFoldersTitle, HyundaiFoldersCheckbox):
			Node.addKnob(knob)
	else:
		pass

############################################################################################################
#### Code that is run via onCreate callbacks, loaded from Callbacks_WriteNodeMetadata.py ...

def Run_ICC_Code():
	'''
	Adds an ICC Profile to the image...
	'''	
	Node = nuke.thisNode()
	ICC_Profile_Name = Node.knob('ICC_knob').value()
	if ICC_Profile_Name != 'Empty':
		# Tag the file with ICC Color Profile data...
		from Write_ICC_Profile import Write_ICC_Profile_with_Args
		Write_ICC_Profile_with_Args.Write_ICC_Profile_with_Args().copy_ICC_profile_to_image(ICC_Profile_Name)
		#print 'Executing add_selected_ICC_profile'
	else:
		pass

def Run_IPTC_Code():
	'''
	Creates a metadata text file to be used for IPTC metadata tagging...
	'''	
	Node = nuke.thisNode()
	IPTC_Knob = Node.knob('IPTC_knob')
	if IPTC_Knob.value() == True:
		# Create the data file...
		from TagImages import AW_TagImages
		AW_TagImages.AW_TagImages().create_args_file()
		#print 'Executing create_IPTC_data_file'
		# Tag the file with the metadata...
		from TagImages import AW_TagImages
		AW_TagImages.AW_TagImages().tag_images()
		#print 'Executing add_IPTC_metadata'		
	else:
		pass

def Run_Hyundai_Folder_Restructuring():
	'''
	Rearranges the folder structure for Innocean/Hyundai projects that are created
	via ConfigCompBuilder, that utilize view names, formatted with the trimname + the color name ...
	'''
	Node = nuke.thisNode()
	Hyundai_Knob = Node.knob('Hyundai_knob')
	if Hyundai_Knob.value() == True:	
		from TagImages import AW_TagImages
		AW_TagImages.AW_TagImages().create_nested_color_and_trim_folders()
		#print 'Executing ConfigCompBuilder_Hyundai_Folder_Restructuring'
	else:
		pass

############################################################################################################
#####  Knob Callbacks...

def knobChanged():
	''''''
	Node = nuke.thisNode()
	Knob = nuke.thisKnob()

	try:
		if 'ICC_knob' in Node.knobs():
			# NOTE: I added this sanity check because deleting a Write node via nuke.delete() can trigger the knobChanged callback after the node is already gone,
			# resulting in a ValueError when the knob variable names are assigned...

			# Set some color transforms for Write node appearance changes when an ICC profile selection is made...
			r,g,b = 1.0, 1.0, 1.0
			WhiteTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
			r,g,b = .66, 0.0, 0.0
			RedTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
			r,g,b = 0.0, 0.0, 0.0
			BlackTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
			r,g,b = 0.4, 0.3, 0.96
			PurpleTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)

			# The list of knobs to be checked...
			ICC_KNOB = Node.knob('ICC_knob')
			IPTC_KNOB = Node.knob('IPTC_knob')
			FILE_TYPE = Node.knob('file_type')
			# Limit the number of knobs to be searched to only these...
			KNOBS = (ICC_KNOB, IPTC_KNOB, FILE_TYPE)

			if Knob in KNOBS:
				for Knob in KNOBS:
					if Knob == ICC_KNOB:
						ICC_Profile_Name = Knob.value()
						if ICC_Profile_Name != 'Empty':
							# Check to make sure the file_type knob is not set to exr, since ICC profiles are not supported...
							if Node.knob('file_type').value() != 'exr':
								Node['note_font_color'].setValue(PurpleTextColor)
								Node['note_font'].setValue('Verdana Bold')
								Node['note_font_size'].setValue(12.0)
								Node['label'].setValue('ICC Profile: ' + ICC_Profile_Name)
							elif Node.knob('file_type').value() == 'exr':
								Node.knob('ICC_knob').setValue('Empty')
								print('ERROR:\nTurning Off ICC Profile tagging!\n\nEXR file format not supported.\nRenders will fail on the render farm.')
								if nuke.GUI:
									nuke.critical('\nTurning Off ICC Profile tagging!\n\nEXR file format not supported.\nRenders will fail on the render farm.')
						else:
							Node['note_font_color'].setValue(BlackTextColor)
							Node['note_font'].setValue('Verdana')
							Node['note_font_size'].setValue(11.0)
							Node['label'].setValue('')
					elif Knob == IPTC_KNOB:
						if Knob.value() == True:
							# Then we can enable the Hyundai folder rearrangement checkbox...
							Node.knob('Hyundai_knob').setEnabled(True)
						else:
							# Disable this knob, since it's only an option if we're using ConfigCompbuilder and it's a Hyundai project...
							Node.knob('Hyundai_knob').setValue(False)
							Node.knob('Hyundai_knob').setEnabled(False)
					elif Knob == FILE_TYPE:
						if Node.knob('file_type').value() == 'exr' and ICC_Profile_Name != 'Empty':
							Node.knob('ICC_knob').setValue('Empty')
							print('ERROR:\nTurning Off ICC Profile tagging!\n\nEXR file format not supported.\nRenders will fail on the render farm.')
							if nuke.GUI:
								nuke.critical('\nTurning Off ICC Profile tagging!\n\nEXR file format not supported.\nRenders will fail on the render farm.')
	except ValueError:
		pass

############################################################################################################
#####  Convert Existing old style sRGB Write nodes to the new Metadata tab style...

def convert_OldStyle_sRGB_Write_Nodes():
	'''
	If the name of the Write node matches "Write_sRGB_ICC_Profile" and the value in the Python "afterFrameRender" knob match,
	clear the afterFrameRender knob and set the value of the ICC_knob to be "sRGB_profile_from_Photoshop.icc" to match its original setting...
	'''
	Node = nuke.thisNode()
	try:
		ICCKnob = Node.knob('ICC_knob')
		NodeNameToCompare = 'Write_sRGB_ICC_Profile'
		PyKnob = Node.knob('afterFrameRender')
		ValueToCompare = '''from Write_ICC_Profile import Write_ICC_profile
Write_ICC_profile.Write_ICC_Profile().copy_ICC_profile_to_image()'''
		# Check to see if the node name matches and the python knob value matches...
		if NodeNameToCompare in Node.name() and PyKnob.value() == ValueToCompare:
			PyKnob.setValue('')
			ICCKnob.setValue('sRGB_profile_from_Photoshop.icc')
			print("Converted old style sRGB Write node.")
	except Exception:
		# Something went wrong, so we should just leave things as they are, to preserve any existing functionality...
		pass



"""
##################################################################

# NOTE: Use these to check for callbacks...

print nuke.beforeRenders
print nuke.afterFrameRenders
print nuke.afterRenders

##################################################################
"""