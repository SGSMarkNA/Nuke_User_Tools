
def prefPanel(self):
	'''
	Gets a list preference parameters from the user. Otherwise, sets them to exisiting preferences, loaded from a prefs file.
	Note that all of the names and values are remnants of one particular project and will need to be changed to suit...
	'''
	
	if not self.read_prefs_file():
		# Default values if no pref file found...
		self.nodeSpacingX = '60'
		self.nodeSpacingY = '100'
		self.postage_stamps = False
		self.backdrop_off = False
		self.rand_color = False
		self.render_layers = 'Maya'
		self.Build = 'Int'
		self.TotalLightBuild = False
		self.prefs = [self.nodeSpacingX, self.nodeSpacingY, self.postage_stamps, self.backdrop_off, self.rand_color, self.render_layers, self.Build, self.TotalLightBuild]

	else:
		# If there's an existing prefs file, set the current prefs to those values...
		self.nodeSpacingX = self.saved_prefs[0]
		self.nodeSpacingY = self.saved_prefs[1]
		self.postage_stamps = self.saved_prefs[2]
		self.backdrop_off = self.saved_prefs[3]
		self.rand_color = self.saved_prefs[4]
		self.render_layers = self.saved_prefs[5]
		self.Build = self.saved_prefs[6]
		# I added this parameter, so older prefs files do not include it. This catches an index-out-of-range error...
		try:
			self.TotalLightBuild = self.saved_prefs[7]
		except:
			self.TotalLightBuild = False

	# Ask the user what node spacing they prefer and whether or not they want postage stamps for the
	# Shuffle nodes... Also, if they want a backdrop and if it is a random color, rather than grey.
	# And, if they want to override the automatic layer filtering and pick their own layer associations...

	p = nuke.Panel( 'Preferences:' )
	p.addEnumerationPulldown( 'Spacing X: ', ' '.join([self.nodeSpacingX, '50', '30', '60', '80', '100', '120', '150', '200']))
	p.addEnumerationPulldown( 'Spacing Y: ', ' '.join([self.nodeSpacingY, '50', '30', '60', '80', '100', '120', '150', '200']))
	p.addBooleanCheckBox('Shuffle Postage Stamps ON', self.postage_stamps)
	p.addBooleanCheckBox('Backdrop OFF', self.backdrop_off)
	p.addBooleanCheckBox('Random Backdrop Color', self.rand_color)
	p.addEnumerationPulldown( 'Render Layers Naming: ', ' '.join([self.render_layers, 'Maya', 'Max']))
	p.addEnumerationPulldown( 'Comp Build Type: ', ' '.join([self.Build, 'Int', 'Ext']))
	p.addBooleanCheckBox('TotalLight Build', self.TotalLightBuild)
	p.addBooleanCheckBox('<----- SAVE PREFS ', False)
	if not p.show():
		return False
	# Assign the new values...
	self.nodeSpacingX = p.value( 'Spacing X: ' )
	self.nodeSpacingY = p.value( 'Spacing Y: ' )
	self.postage_stamps = p.value('Shuffle Postage Stamps ON')
	self.backdrop_off = p.value('Backdrop OFF')
	self.rand_color = p.value('Random Backdrop Color')
	self.render_layers = p.value('Render Layers Naming: ')
	self.Build = p.value('Comp Build Type: ')
	self.TotalLightBuild = p.value('TotalLight Build')
	self.save_prefs = p.value('<----- SAVE PREFS ')
	self.prefs = [self.nodeSpacingX, self.nodeSpacingY, self.postage_stamps, self.backdrop_off, self.rand_color, self.render_layers , self.Build, self.TotalLightBuild]
	# Write the result to a prefs file...
	if self.save_prefs:
		self.write_prefs_file(self.prefs)
	return True