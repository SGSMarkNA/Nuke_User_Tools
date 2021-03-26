import nuke
import os
# Customized auto_backdrop function...
from auto_backdrop.auto_backdrop import auto_backdrop
# Writes and reads preference files...
from Preference_File_Functions.prefs_file import PrefsFileUtils as PrefsFileUtils
# Creates multiple input connector for Trim renders / Read nodes...
import TrimViewGenerator
# NOTE: Changes to the imported module are not automatically reloaded...

class ConfigCompBuilder(object):
	'''
	Create an exr rebuild comp using Nuke's views machanism. Trim names are entered by the user and a view is created for each one. This facilitates easy switching between
	trims when color correcting. Also, a Write node is created that is set up to automatically render each trim view within separate directories.

	Here are the basic VRay render passes we need from the CG rendered EXR file. These may be named completely differently - below are just the default names.
	An accurate representation of the rgba "beauty pass" can be created by layering these passes in the proper way.
	By rebuilding the 'beauty' pass from these layers, we are able to color shift and fine tune the look and, from only one render, we can create many different looks...

		ShuffleLayers  -->	['VRayReflection', 'VRaySpecular', 'VRaySelfIllumination', 'VRayRefraction']			#### Additive layers, which can be plussed together. SuperAmbient is multiplied...
		DiffuseLayers  -->	['VRayGlobalIllumination', 'VRayDiffuseFilter', 'VRayLighting']							#### Layers needed for a comp that splits up the TotalLighting pass into its components for more color control...
		BodyLayers -->		['VRayMtlSelect_Car_Paint', 'VRayMtlSelect_Clearcoat', 'VRayMtlSelect_Metalic']			#### Layers needed to isolate the car body for finer control over the color...
		CarBodyAlpha -->	['Paint_Windows_Rimz']																	#### Car Body alpha channel...
		AmbientLayer -->	['VRayExtraTex_SuperAmbient']															#### Ambient layer that gets multiplied over all...
	'''

	def __init__(self):

		# Make sure that the script executes in the root node...
		nuke.root().begin()

		# Function for creating backdrop that frames all the connected nodes...
		self.auto_backdrop = auto_backdrop

		# Initialize instance of the class PrefsFileUtils...
		PrefsUtils = PrefsFileUtils()
		self.write_prefs_file = PrefsUtils.write_prefs_file
		self.read_prefs_file = PrefsUtils.read_prefs_file

		self.config_filename = 'ConfigCompBuilder'

		self.save_prefs = False
		self.prefs_file = []
		self.prefs_dir = []
		self.prefs = []
		self.saved_prefs =[]
		self.prefs_save = []
		self.prefs_read = []

		self.postage_stamps = False
		self.backdrop_off = False
		self.rand_color = False

		self.startPos = (0, 0)
		self.nodeSpacingX = None		# These two spacing variables are set via the prefsPanel...
		self.nodeSpacingY = None
		self.NoOpSpacingX = 30
		self.offset = 34				# Fudge factor to account for placement of rounded nodes, such as Dots or JoinViews...

		self.TotalLightBuild = False

		self.ShuffleLayers = []
		self.DiffuseLayers = []
		self.BodyLayers = []
		self.CarBodyAlpha = []
		self.AmbientLayer = []
		self.TotalLightLayer = []

		self.main_dir = "HyundaiUSA.com"

		#========================================================================================================
		# Check for Read nodes before running...
		#========================================================================================================		
		if self.Read_Node_Detector():
			#========================================================================================================
			# Run the main method that builds the comp.
			#========================================================================================================		
			self.exr_shuffle()

	def Read_Node_Detector(self):
		read_nodes = nuke.allNodes('Read')
		if not len(read_nodes):
			if nuke.ask("It is recommended that you have at least one of your EXR Reads loaded before building the comp. That way, the Shuffle nodes will be able to grab the available layers, instead of displaying None...\n\nDo you wish to continue?"):
				return True
			else:
				return False
		else:
			return True

	def prefPanel(self):
		'''
		Gets a list of spacing and decorator parameters from the user. Otherwise, sets them exisiting preferences, loaded from a prefs file.
		'''
		self.saved_prefs = self.read_prefs_file(file_name=self.config_filename)

		if not self.saved_prefs:
			# Default values if no pref file found...
			self.nodeSpacingX = '60'
			self.nodeSpacingY = '100'
			self.postage_stamps = False
			self.backdrop_off = False
			self.rand_color = False
			self.render_layers = 'Maya'
			# Get Build type from TrimViewGenerator Class...
			if self.TrimViewGen.Build:
				self.Build = self.TrimViewGen.Build
			else:
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
			# Get Build type from TrimViewGenerator Class...
			if self.TrimViewGen.Build:
				self.Build = self.TrimViewGen.Build
			else:			
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
			self.write_prefs_file(file_name=self.config_filename, prefs_list=self.prefs)
		return True

	def nodeList_center(self, nodeList=None):
		'''Node placement function borrowed from Drew Loveridge...'''
		if nodeList == None:
			nodeList=nuke.selectedNodes()
		nNodes = len(nodeList)
		x=0
		y=0
		for n in nodeList:
			x += n.xpos()
		for n in nodeList:
			y += n.ypos()
		try:
			return [x/nNodes,y/nNodes]
		except ZeroDivisionError:
			return [0,0]

	def exr_shuffle(self):
		'''
		Create an exr rebuild comp using Nuke's views mechanism. Trim names and colors are entered by the user
		and a new view is created for each combination. This facilitates easy switching between trims when color correcting.
		'''
		# Instantiate the imported TrimViewGenerator Panel Class...
		self.TrimViewGen = TrimViewGenerator.TrimViewGenerator()

		# NOTE: cleanup_old_views can probably be disabled when done debugging. This is here to avoid stacking up lots of views when re-running...
		# Make sure cleanup_old_views does not run if the user cancels the initial dialogue window...
		# Otherwise, any extra views they have in their current script get waxed!
		if nuke.ask("If you continue, any existing Views will be removed! Do you still wish to continue...?"):
			pass
		else:
			return False
		self.TrimViewGen.cleanup_old_views()
		# This panel prompts for the Model Name, Model Year and whether the Build is an Exterior or Interior...
		if self.TrimViewGen.createModelNameInputPanel():
			self.modelName = self.TrimViewGen.modelName
			self.modelYear = self.TrimViewGen.modelYear
			self.Build = self.TrimViewGen.Build
			if self.Build == "Int":
				self.Exterior_Interior = "Interior"
				self.ex_in = "in"
			elif self.Build == "Ext":
				self.Exterior_Interior = "Exterior"
				self.ex_in = "ex"
			# This panel prompts for a list of trim names...
			if self.TrimViewGen.createTrimsInputPanel():
				# This panel prompts for a list of color names...
				if self.TrimViewGen.createColorsInputPanel():
					# This function creates Nuke views from the list of trim + color names...
					self.TrimViewGen.createTrimColorViews()
					#This method stores the list of trims and colors into the Nuke Project Settings/comment panel. The data is used to intelligently separate the view name parts later, for making separate output folder names...
					self.TrimViewGen.storeTrimColorViews()
		else:
			return False	

		if self.TrimViewGen.colors_to_build:
			self.ColorPipesSpacingX = (len(self.TrimViewGen.colors_to_build)*90)	#  90 for each color pipe, times the number of color pipes...
		else:
			return False

		#========================================================================================================
		# Run the prefPanel function to get the build parameters from the user...
		#========================================================================================================
		if self.prefPanel():
			#========================================================================================================
			# Run the comp_constructor function to generate the exr rebuild schematic...
			#========================================================================================================			
			self.comp_constructor()

	def comp_constructor(self):
		# Depending on the type of build chosen: Int or Ext and the Render Layers naming scheme: Maya or Max -- set the layer names...

		if self.Build == 'Int':
			if self.render_layers == 'Max':
				self.ShuffleLayers = ['VRayReflection', 'VRaySpecular', 'VRaySelfIllumination', 'VRayRefraction']
				self.DiffuseLayers = ['VRayGlobalIllumination', 'VRayDiffuseFilter', 'VRayLighting']
				self.AmbientLayer = ['SuperAmbient']
				self.TotalLightLayer = ['VRayTotalLighting']

			elif self.render_layers == 'Maya':
				self.ShuffleLayers = ['reflect', 'specular', 'selfIllum', 'refract']
				self.DiffuseLayers = ['GI', 'diffuse', 'lighting']
				self.AmbientLayer = ['SuperAmbient_SuperAmbient']
				self.TotalLightLayer = ['totalLight']

		elif self.Build == 'Ext':
			if self.render_layers == 'Max':
				self.ShuffleLayers = ['VRayReflection', 'VRaySpecular', 'VRaySelfIllumination', 'VRayRefraction']
				self.DiffuseLayers = ['VRayGlobalIllumination', 'VRayDiffuseFilter', 'VRayLighting']
				self.BodyLayers = ['VRayMtlSelect_Car_Paint', 'VRayMtlSelect_Clearcoat', 'VRayMtlSelect_Metalic']
				self.CarBodyAlpha = ['Paint_Window_Rimz.red']
				self.AmbientLayer = ['VRayExtraTex_amb']
				self.TotalLightLayer = ['VRayTotalLighting']

			elif self.render_layers == 'Maya':
				self.ShuffleLayers = ['reflect', 'specular', 'selfIllum', 'refract']
				self.DiffuseLayers = ['GI', 'diffuse', 'lighting']
				self.BodyLayers = ['ms__aw_ext_Base', 'ms__aw_ext_Clearcoat', 'ms__aw_ext_Metallic']
				self.CarBodyAlpha = ['Paint_Windows_Rimz.red']
				self.AmbientLayer = ['extraTex_AMB']
				self.TotalLightLayer = ['totalLight']

		#--------------------------------------------------------------------------------------------------------

		# Convert the spacing variables from strings to integers...
		self.nodeSpacingX = int(self.nodeSpacingX)
		self.nodeSpacingY = int(self.nodeSpacingY)

		# Print out the current values in the Nuke shell window...
		print "-------------------------------------"
		print "ConfigCompBuilder VARIABLES:"
		print "-------------------------------------"
		print "Build: ", self.Build							# Type of build - 'Int' = Interior Build, 'Ext' = Exterior Build with Car Body...
		print "TotalLightBuild: ", self.TotalLightBuild		# Flag to turn on a different comp layout. The TotalLight pass replaces the entire Diffuse section.
		print "Start Position: ", self.startPos				# Screen coordinates for comp build starting point...
		print "nodeSpacingX: ", self.nodeSpacingX			# Pixel tiling values to change the spacing of nodes...
		print "nodeSpacingY: ", self.nodeSpacingY			# Pixel tiling values to change the spacing of nodes...
		print "render_layers: ", self.render_layers			# Which set of VRay render layer names to use - currently 'Max and 'Maya'...
		print "ShuffleLayers: ", self.ShuffleLayers			# List of layers to use when creating the additive Shuffle nodes...
		print "DiffuseLayers: ", self.DiffuseLayers			# Flag to turn on creation of the Diffuse comp section that builds a TotalLighting pass...
		print "CarBodyAlpha: ", self.CarBodyAlpha			# List of the channel that holds the CarBody Paint alpha...
		print "AmbientLayer:", self.AmbientLayer			# Ambient layer that gets multiplied over all the other layers...
		print "TotalLightLayer:", self.TotalLightLayer		# TotalLight layer - Diffuse multiplied by GI and Lighting. Used primarily for Exterior Builds - replaces Diffuse build section of comp...
		print "BodyLayers: ", self.BodyLayers				# List of the layers used to build the CarBody nodes, if found...
		print "postage_stamps: ", self.postage_stamps		# Flag to turn on/off the Postage Stamp icons for Shuffle nodes...
		print "backdrop_off: ", self.backdrop_off			# Flag to turn on/off the automatic backdrop creation...
		print "rand_color: ", self.rand_color				# Flag to turn on/off the random color setting for backdrops created with the "auto_backdrop" method...
		print "--------------------------------"

		#========================================================================================================
		# Run the imported class TrimViewGen.createTrimViewsSection() and get the nodes we made...
		#========================================================================================================

		# This runs the Trims and Colors Input Panels to get the initial list of trims and colors from the user. It also makes Nuke views from the trim + color names.
		# Finally, it creates a Group node to act as an input for EXR Read nodes. The createTrimViewSection method is imported and its data is used to build the rest of the comp structure.
		self.TrimViewGen.createTrimViewSection()
		##print self.TrimViewGen.__dict__.keys()

		# Initialize inputB variable for B pipe connections...
		inputB = None

		# Create a central start_dot below EXR Read node for common attachment point...
		dot_start = nuke.nodes.Dot(name='dot_start')#, label='[knob name]')
		dot_start.setXYpos(self.TrimViewGen.TrimViewsGroup.xpos()+self.offset, self.TrimViewGen.TrimViewsGroup.ypos()+200)
		dot_start.setInput(0, self.TrimViewGen.TrimViewsGroup)

		#========================================================================================================
		#  Diffuse Comp Section...
		#========================================================================================================

		# Initialize a new variable to collect the TrimColorsGroup node we create...
		TrimColorsGroupList = []

		if self.TotalLightBuild == False:

			#--------------------------------------------------------------------------------------------------------
			# Create the Diffuse section Shuffle nodes...	
			for index, p in enumerate(self.DiffuseLayers):
				# Create dot for each Shuffle node to hang from...
				shuffle_dot = nuke.nodes.Dot(name='dot_'+p)#, label='[knob name]')

				if (index == 0):
					shuffle_dot.setXYpos(dot_start.xpos(), dot_start.ypos() + 125)
					shuffle_dot.setInput(0, dot_start)
					inputB = shuffle_dot
				else:
					shuffle_dot.setXYpos(dot_start.xpos()+(index*self.nodeSpacingX*4)+(index*(self.ColorPipesSpacingX)), dot_start.ypos() + 125)
					shuffle_dot.setInput(0, inputB)
					inputB = shuffle_dot

				# Add the three Diffuse Comp Shuffle nodes...
				ShuffleNode = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				ShuffleNode.setXYpos(shuffle_dot.xpos()-self.offset, shuffle_dot.ypos() + 25)
				ShuffleNode.knob('in').setValue(p)
				ShuffleNode.setInput(0, shuffle_dot)

				if index == 0:
					VRayGlobalIllumination = ShuffleNode
				if index == 1:
					VRayDiffuseFilter = ShuffleNode
				if index == 2:
					VRayLighting = ShuffleNode

			#--------------------------------------------------------------------------------------------------------
			# Build and connect the rest of the Diffuse comp top section...
			dotDiffuse = nuke.nodes.Dot(name='dotDiffuse')
			if self.postage_stamps:
				dotDiffuse.setXYpos(VRayDiffuseFilter.xpos()+self.offset, VRayDiffuseFilter.ypos()+90)
			else:
				dotDiffuse.setXYpos(VRayDiffuseFilter.xpos()+self.offset, VRayDiffuseFilter.ypos()+40)
			dotDiffuse.setInput(0, VRayDiffuseFilter)

			#=========================================================
			# BEGIN -- individual color pipes for DiffuseFilter section...
			#=========================================================

			connecting_node = dotDiffuse

			#--------------------------------------------------------------------------------------------------------
			# Make a connecting dot...
			Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos(), ypos=dotDiffuse.ypos()+30)
			Pipe_Start.setInput(0, connecting_node)
			input_pipe = None
			input_pipe2 = None

			#--------------------------------------------------------------------------------------------------------
			# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
			List_of_NoOp_Nodes =[]

			for index, c in enumerate(self.TrimViewGen.colors_to_build):
				n = nuke.nodes.NoOp(name=c)
				n2 =  nuke.nodes.NoOp(name=c)
				List_of_NoOp_Nodes.append(n2)
				top_dot = nuke.nodes.Dot(name=c+'_dot')

				if (index == 0):
					n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, Pipe_Start)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)				

					n2.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(8*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

				else:
					n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, input_pipe)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)				

					n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(8*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

			#=========================================================
			# END -- individual color pipes for DiffuseFilter section...
			#=========================================================

			#=========================================================
			# Begin the TrimColorsGroup node for DiffuseFilter section...
			#=========================================================
			TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label='Diffuse')
			TrimColorsGroup.begin()

			#--------------------------------------------------------------------------------------------------------
			# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
			joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset, ypos=n2.ypos()-(self.nodeSpacingY))

			input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
			inputs = []

			for index, x in enumerate(List_of_NoOp_Nodes):
				exposed_input = nuke.nodes.Input(name=x.name())
				exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
				inputs.append(exposed_input)
				# Function to get centroid of nodes...
				inputs_center = self.nodeList_center(inputs)

				common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
				common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
				common_dot.setInput(0, exposed_input)

				for index, i in enumerate(input_names_list):
					if i.endswith(x.name()):
						joinviewPipes.setInput(index, common_dot)

			joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

			output_pipe = nuke.nodes.Output()
			output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
			output_pipe.setInput(0, joinviewPipes)

			TrimColorsGroup.end()	
			#=========================================================                   
			# End the TrimColorsGroup node for DiffuseFilter section...
			#=========================================================			

			# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
			for index, NoOp in enumerate(List_of_NoOp_Nodes):
				TrimColorsGroup.setInput(index, NoOp)

			TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), n2.ypos()+(self.nodeSpacingY))

			# Make a list of the TrimColorsGroup node we've made...
			TrimColorsGroupList.append(TrimColorsGroup)	

			dotDiffuse2 = nuke.nodes.Dot(name='dotDiffuse2')
			dotDiffuse2.setXYpos(dotDiffuse.xpos(), dotDiffuse.ypos()+(self.nodeSpacingY*10))
			dotDiffuse2.setInput(0, TrimColorsGroup)

			mergeDiffuseGI = nuke.nodes.Merge2( operation='divide', inputs=[ dotDiffuse, VRayGlobalIllumination ], label='RawGI', output='rgb' )
			mergeDiffuseGI.setXYpos(VRayGlobalIllumination.xpos(), (dotDiffuse.ypos()-9))

			#=========================================================
			# BEGIN -- individual color pipes for GI section...
			#=========================================================

			connecting_node = mergeDiffuseGI

			#--------------------------------------------------------------------------------------------------------
			# Make a connecting dot...
			Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos()+self.offset, ypos=mergeDiffuseGI.ypos()+40)
			Pipe_Start.setInput(0, connecting_node)
			input_pipe = None
			input_pipe2 = None

			#--------------------------------------------------------------------------------------------------------
			# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
			List_of_NoOp_Nodes =[]

			for index, c in enumerate(self.TrimViewGen.colors_to_build):
				n = nuke.nodes.NoOp(name=c)
				n2 =  nuke.nodes.NoOp(name=c)
				List_of_NoOp_Nodes.append(n2)
				top_dot = nuke.nodes.Dot(name=c+'_dot')

				if (index == 0):
					n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, Pipe_Start)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)				

					n2.setXYpos(Pipe_Start.xpos()-self.offset, mergeDiffuseGI.ypos()+(8*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

				else:
					n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, input_pipe)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)				

					n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, mergeDiffuseGI.ypos()+(8*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

			#=========================================================
			# END -- individual color pipes for GI section...
			#=========================================================

			#=========================================================
			# Begin the TrimColorsGroup node for GI section...
			#=========================================================
			TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label='GI')
			TrimColorsGroup.begin()

			#--------------------------------------------------------------------------------------------------------
			# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
			joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset, ypos=n2.ypos()-(self.nodeSpacingY))

			input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
			inputs = []

			for index, x in enumerate(List_of_NoOp_Nodes):
				exposed_input = nuke.nodes.Input(name=x.name())
				exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
				inputs.append(exposed_input)
				# Function to get centroid of nodes...
				inputs_center = self.nodeList_center(inputs)

				common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
				common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
				common_dot.setInput(0, exposed_input)

				for index, i in enumerate(input_names_list):
					if i.endswith(x.name()):
						joinviewPipes.setInput(index, common_dot)

			joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

			output_pipe = nuke.nodes.Output()
			output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
			output_pipe.setInput(0, joinviewPipes)

			TrimColorsGroup.end()	
			#=========================================================                   
			# End the TrimColorsGroup node for GI section...
			#=========================================================			

			# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
			for index, NoOp in enumerate(List_of_NoOp_Nodes):
				TrimColorsGroup.setInput(index, NoOp)

			TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), n2.ypos()+(self.nodeSpacingY))

			# Make a list of the TrimColorsGroup node we've made...
			TrimColorsGroupList.append(TrimColorsGroup)

			mergeDiffuseLight = nuke.nodes.Merge2( operation='divide', inputs=[ dotDiffuse, VRayLighting ], label='RawLight', output='rgb' )
			mergeDiffuseLight.setXYpos(VRayLighting.xpos(), (dotDiffuse.ypos()-9))

			mergeDiffuseRawGI = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, TrimColorsGroup ], label='DiffuseGI', output='rgb' )
			mergeDiffuseRawGI.setXYpos(VRayGlobalIllumination.xpos(), (dotDiffuse2.ypos()-9))

			#=========================================================
			# BEGIN -- individual color pipes for Lighting section...
			#=========================================================

			connecting_node = mergeDiffuseLight

			#--------------------------------------------------------------------------------------------------------
			# Make a connecting dot...
			Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos()+self.offset, ypos=mergeDiffuseGI.ypos()+40)
			Pipe_Start.setInput(0, connecting_node)
			input_pipe = None
			input_pipe2 = None

			#--------------------------------------------------------------------------------------------------------
			# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
			List_of_NoOp_Nodes =[]

			for index, c in enumerate(self.TrimViewGen.colors_to_build):
				n = nuke.nodes.NoOp(name=c)
				n2 =  nuke.nodes.NoOp(name=c)
				List_of_NoOp_Nodes.append(n2)
				top_dot = nuke.nodes.Dot(name=c+'_dot')

				if (index == 0):
					n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, Pipe_Start)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)				

					n2.setXYpos(Pipe_Start.xpos()-self.offset, mergeDiffuseGI.ypos()+(8*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

				else:
					n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, input_pipe)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)				

					n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, mergeDiffuseGI.ypos()+(8*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

			#=========================================================
			# END -- individual color pipes for Lighting section...
			#=========================================================

			#=========================================================
			# Begin the TrimColorsGroup node for Lighting section...
			#=========================================================
			TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label='Lighting')
			TrimColorsGroup.begin()

			#--------------------------------------------------------------------------------------------------------
			# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
			joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset, ypos=n2.ypos()-(self.nodeSpacingY))

			input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
			inputs = []

			for index, x in enumerate(List_of_NoOp_Nodes):
				exposed_input = nuke.nodes.Input(name=x.name())
				exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
				inputs.append(exposed_input)
				# Function to get centroid of nodes...
				inputs_center = self.nodeList_center(inputs)

				common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
				common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
				common_dot.setInput(0, exposed_input)

				for index, i in enumerate(input_names_list):
					if i.endswith(x.name()):
						joinviewPipes.setInput(index, common_dot)

			joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

			output_pipe = nuke.nodes.Output()
			output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
			output_pipe.setInput(0, joinviewPipes)

			TrimColorsGroup.end()	
			#=========================================================                   
			# End the TrimColorsGroup node for for Lighting section...
			#=========================================================			

			# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
			for index, NoOp in enumerate(List_of_NoOp_Nodes):
				TrimColorsGroup.setInput(index, NoOp)

			TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), n2.ypos()+(self.nodeSpacingY))

			# Make a list of the TrimColorsGroup node we've made...
			TrimColorsGroupList.append(TrimColorsGroup)		

			mergeDiffuseRawLight = nuke.nodes.Merge2( name='mergeDiffuseRawLight', operation='multiply', inputs=[ dotDiffuse2, TrimColorsGroup ], label='DiffuseLight', output='rgb' )
			mergeDiffuseRawLight.setXYpos(VRayLighting.xpos(), (dotDiffuse2.ypos()-9))

			mergeTotalLight = nuke.nodes.Merge2( operation='plus', inputs=[ mergeDiffuseRawGI, mergeDiffuseRawLight ], label='TotalLight', output='rgb' )
			mergeTotalLight.setXYpos(VRayDiffuseFilter.xpos(), dotDiffuse2.ypos()+(self.nodeSpacingY*2))

		else:

			#========================================================================================================
			# The TotalLight section...
			#========================================================================================================

			# Initialize a new variable to collect the TrimColorsGroup node we create...
			TrimColorsGroupList = []

			#--------------------------------------------------------------------------------------------------------
			# Create the TotalLight Dot and Shuffle nodes...		
			TotalLightDot = nuke.nodes.Dot(name='TotalLightDot')
			TotalLightDot.setXYpos(dot_start.xpos(), dot_start.ypos()+125)
			TotalLightDot.setInput(0, dot_start)		

			TotalLight = nuke.nodes.Shuffle(name='Shuffle_'+self.TotalLightLayer[0], label='[value in]', postage_stamp=self.postage_stamps)
			TotalLight.setXYpos(TotalLightDot.xpos()-self.offset, TotalLightDot.ypos()+25)
			TotalLight.knob('in').setValue(self.TotalLightLayer[0])
			TotalLight.setInput(0, TotalLightDot)

			#=========================================================
			# BEGIN -- individual color pipes for TotalLight section...
			#=========================================================

			connecting_node = TotalLight

			#--------------------------------------------------------------------------------------------------------
			# Make a connecting dot below the shuffle node...
			# NOTE: This is called "dotDiffuse" for now because a bunch of other parts base their position on this name...
			dotDiffuse = nuke.nodes.Dot(name='dotDiffuse')
			if self.postage_stamps:
				dotDiffuse.setXYpos(TotalLight.xpos()+self.offset, TotalLight.ypos()+90)
			else:
				dotDiffuse.setXYpos(TotalLight.xpos()+self.offset, TotalLight.ypos()+40)
			dotDiffuse.setInput(0, TotalLight)			

			Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos()+self.offset, ypos=dotDiffuse.ypos())
			Pipe_Start.setInput(0, connecting_node)
			input_pipe = None
			input_pipe2 = None

			#--------------------------------------------------------------------------------------------------------
			# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
			List_of_NoOp_Nodes =[]

			for index, c in enumerate(self.TrimViewGen.colors_to_build):
				n = nuke.nodes.NoOp(name=c)
				n2 =  nuke.nodes.NoOp(name=c)
				List_of_NoOp_Nodes.append(n2)
				top_dot = nuke.nodes.Dot(name=c+'_dot')

				if (index == 0):
					n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, Pipe_Start)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)

					n2.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(8*self.nodeSpacingY))


					n2.setInput(0, top_dot)
					input_pipe2 = n

				else:
					n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, input_pipe)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)				

					n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(8*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

			#=========================================================
			# END -- individual color pipes for TotalLight section...
			#=========================================================

			#=========================================================
			# Begin the TrimColorsGroup node for TotalLight section...
			#=========================================================
			TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label='TotalLight')
			TrimColorsGroup.begin()

			#--------------------------------------------------------------------------------------------------------
			# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
			joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset, ypos=dotDiffuse.ypos()-(self.nodeSpacingY))

			input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
			inputs = []

			for index, x in enumerate(List_of_NoOp_Nodes):
				exposed_input = nuke.nodes.Input(name=x.name())
				exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
				inputs.append(exposed_input)
				# Function to get centroid of nodes...
				inputs_center = self.nodeList_center(inputs)

				common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
				common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
				common_dot.setInput(0, exposed_input)

				for index, i in enumerate(input_names_list):
					if i.endswith(x.name()):
						joinviewPipes.setInput(index, common_dot)

			joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

			output_pipe = nuke.nodes.Output()
			output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
			output_pipe.setInput(0, joinviewPipes)

			TrimColorsGroup.end()	
			#=========================================================                   
			# End the TrimColorsGroup node for TotalLight section...
			#=========================================================			

			# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
			for index, NoOp in enumerate(List_of_NoOp_Nodes):
				TrimColorsGroup.setInput(index, NoOp)

			TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), List_of_NoOp_Nodes[0].ypos()+(self.nodeSpacingY))

			# Make a list of the TrimColorsGroup node we've made...
			TrimColorsGroupList.append(TrimColorsGroup)

			# Make the bottom left corner of the comp...
			TotalLight_BottomDot = nuke.nodes.Dot(name='TotalLight_BottomDot')
			TotalLight_BottomDot.setXYpos(TrimColorsGroup.xpos()+self.offset, TrimColorsGroup.ypos()+(self.nodeSpacingY*3))
			TotalLight_BottomDot.setInput(0, TrimColorsGroup)

		#========================================================================================================
		# The alpha Copy node section...
		#========================================================================================================

		# Initialize a new variable to collect the TrimColorsGroup node we create...
		TrimColorsGroupList = []

		#--------------------------------------------------------------------------------------------------------
		# Create the Alpha Shuffle node and Copy nodes...		
		ShuffleAlphaDot = nuke.nodes.Dot(name='ShuffleAlphaDot')
		# If this is a TotalLight Build, everything is relative to the TotalLight shuffle node, not the "ShuffleNode..."
		if self.TotalLightBuild:
			ShuffleAlphaDot.setXYpos((TotalLight.xpos()+self.offset+(self.nodeSpacingX*4))+self.ColorPipesSpacingX, TotalLightDot.ypos())
			ShuffleAlphaDot.setInput(0, TotalLightDot)
		else:
			ShuffleAlphaDot.setXYpos((ShuffleNode.xpos()+self.offset+(self.nodeSpacingX*4))+self.ColorPipesSpacingX, shuffle_dot.ypos())
			ShuffleAlphaDot.setInput(0, shuffle_dot)

		if self.TotalLightBuild:
			ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
			ShuffleAlpha.setXYpos(ShuffleAlphaDot.xpos()-self.offset, TotalLight.ypos())
			ShuffleAlpha.knob('in').setValue('alpha')
			ShuffleAlpha.setInput(0, ShuffleAlphaDot)			
		else:
			ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
			ShuffleAlpha.setXYpos(ShuffleAlphaDot.xpos()-self.offset, VRayLighting.ypos())
			ShuffleAlpha.knob('in').setValue('alpha')
			ShuffleAlpha.setInput(0, ShuffleAlphaDot)

		#=========================================================
		# BEGIN -- individual color pipes for alpha Copy section...
		#=========================================================

		connecting_node = ShuffleAlpha

		#--------------------------------------------------------------------------------------------------------
		# Make a connecting dot below the shuffle nodes...
		Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos()+self.offset, ypos=dotDiffuse.ypos())
		Pipe_Start.setInput(0, connecting_node)
		input_pipe = None
		input_pipe2 = None

		#--------------------------------------------------------------------------------------------------------
		# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
		List_of_NoOp_Nodes =[]

		for index, c in enumerate(self.TrimViewGen.colors_to_build):
			n = nuke.nodes.NoOp(name=c)
			n2 =  nuke.nodes.NoOp(name=c)
			List_of_NoOp_Nodes.append(n2)
			top_dot = nuke.nodes.Dot(name=c+'_dot')

			if (index == 0):
				n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
				n.setInput(0, Pipe_Start)
				input_pipe = n

				top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
				top_dot.setInput(0, n)

				if self.TotalLightBuild:
					n2.setXYpos(Pipe_Start.xpos()-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
				else:
					n2.setXYpos(Pipe_Start.xpos()-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
				n2.setInput(0, top_dot)
				input_pipe2 = n

			else:
				n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
				n.setInput(0, input_pipe)
				input_pipe = n

				top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
				top_dot.setInput(0, n)				

				if self.TotalLightBuild:
					n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
				else:
					n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
				n2.setInput(0, top_dot)
				input_pipe2 = n

		#=========================================================
		# END -- individual color pipes for alpha Copy section...
		#=========================================================

		#=========================================================
		# Begin the TrimColorsGroup node for alpha Copy section...
		#=========================================================
		TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label='alpha')
		TrimColorsGroup.begin()

		#--------------------------------------------------------------------------------------------------------
		# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
		joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset, ypos=Pipe_Start.ypos())

		input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
		inputs = []

		for index, x in enumerate(List_of_NoOp_Nodes):
			exposed_input = nuke.nodes.Input(name=x.name())
			exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
			inputs.append(exposed_input)
			# Function to get centroid of nodes...
			inputs_center = self.nodeList_center(inputs)

			common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
			common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
			common_dot.setInput(0, exposed_input)

			for index, i in enumerate(input_names_list):
				if i.endswith(x.name()):
					joinviewPipes.setInput(index, common_dot)

		joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

		output_pipe = nuke.nodes.Output()
		output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
		output_pipe.setInput(0, joinviewPipes)

		TrimColorsGroup.end()	
		#=========================================================                   
		# End the TrimColorsGroup node for alpha Copy section...
		#=========================================================			

		# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
		for index, NoOp in enumerate(List_of_NoOp_Nodes):
			TrimColorsGroup.setInput(index, NoOp)

		if self.TotalLightBuild:
			TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), List_of_NoOp_Nodes[0].ypos()+(self.nodeSpacingY))
		else:
			TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), mergeDiffuseRawLight.ypos()-(self.nodeSpacingY))

		# Make a list of the TrimColorsGroup node we've made...
		TrimColorsGroupList.append(TrimColorsGroup)


		# Copy the Alpha back into the B stream...
		copyAlpha = nuke.nodes.Copy( from0='rgba.alpha', to0='rgba.alpha' )

		if self.TotalLightBuild:
			copyAlpha.setXYpos(TrimColorsGroup.xpos(), TotalLight_BottomDot.ypos()-9)
			copyAlpha.setInput(0, TotalLight_BottomDot)
			copyAlpha.setInput(1, TrimColorsGroupList[0])			
		else:
			copyAlpha.setXYpos(mergeDiffuseRawLight.xpos()+(self.nodeSpacingX*4)+self.ColorPipesSpacingX, dotDiffuse2.ypos()+(self.nodeSpacingY*2))
			copyAlpha.setInput(0, mergeTotalLight)
			copyAlpha.setInput(1, TrimColorsGroupList[0])			
		#========================================================================================================
		# The Plus Comp Layers section...
		#========================================================================================================

		plusCompPasses = []

		# Initialize a new variable to collect the TrimColorsGroup node we create...
		TrimColorsGroupList = []

		if (self.Build == 'Int'):

			# If it's an Interior build, we can add the Ambient layer to ShuffleLayers and make it the last one, since it needs to be multiplied by all other layers...
			# If it's an Exterior build, we'll add the Ambient layer after the Car Body passes, since it needs to be multiplied by all other layers...
			self.ShuffleLayers = self.ShuffleLayers + self.AmbientLayer
			##self.ShuffleLayers = ['VRayReflection']		# One layer - for testing...

		#--------------------------------------------------------------------------------------------------------
		# Create the additive/plus Shuffle nodes...		
		for index, p in enumerate(self.ShuffleLayers):

			#Create start_dot for each Shuffle node to hang from...
			shuffle_dot2 = nuke.nodes.Dot()
			shuffle_dot2.setXYpos((ShuffleAlpha.xpos()+self.offset+(self.nodeSpacingX*4))+(index*(self.nodeSpacingX*4))+(index*(self.ColorPipesSpacingX))+self.ColorPipesSpacingX, ShuffleAlphaDot.ypos())
			if (index == 0):	
				shuffle_dot2.setInput(0, ShuffleAlphaDot)
				inputC = shuffle_dot2
			else:
				shuffle_dot2.setInput(0, inputC)
				inputC = shuffle_dot2

			# Create the Shuffle nodes...
			ShuffleNode2 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
			ShuffleNode2.setXYpos(shuffle_dot2.xpos()-self.offset, ShuffleAlpha.ypos())
			ShuffleNode2.knob('in').setValue(p)
			ShuffleNode2.setInput(0, shuffle_dot2)

			# Make an indexed list of the nodes we created...
			plusCompPasses.append((p, ShuffleNode2))

			#=========================================================
			# BEGIN -- individual color pipes for Comp Layers section...
			#=========================================================

			connecting_node = ShuffleNode2

			#--------------------------------------------------------------------------------------------------------
			# Make a connecting dot below the shuffle nodes...
			Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos()+self.offset, ypos=dotDiffuse.ypos())
			Pipe_Start.setInput(0, connecting_node)
			input_pipe = None
			input_pipe2 = None

			#--------------------------------------------------------------------------------------------------------
			# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
			List_of_NoOp_Nodes =[]

			for index, c in enumerate(self.TrimViewGen.colors_to_build):
				n = nuke.nodes.NoOp(name=c)
				n2 =  nuke.nodes.NoOp(name=c)
				List_of_NoOp_Nodes.append(n2)
				top_dot = nuke.nodes.Dot(name=c+'_dot')

				if (index == 0):
					n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, Pipe_Start)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)					

					if self.TotalLightBuild:
						n2.setXYpos(Pipe_Start.xpos()-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
					else:
						n2.setXYpos(Pipe_Start.xpos()-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

				else:
					n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
					n.setInput(0, input_pipe)
					input_pipe = n

					top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
					top_dot.setInput(0, n)					

					if self.TotalLightBuild:
						n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
					else:
						n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
					n2.setInput(0, top_dot)
					input_pipe2 = n

			#=========================================================
			# END -- individual color pipes for Comp Layers section...
			#=========================================================

			#=========================================================
			# Begin the TrimColorsGroup node for Comp Layers section...
			#=========================================================
			TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label=p)
			TrimColorsGroup.begin()

			#--------------------------------------------------------------------------------------------------------
			# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
			joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset, ypos=Pipe_Start.ypos())

			input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
			inputs = []

			for index, x in enumerate(List_of_NoOp_Nodes):
				exposed_input = nuke.nodes.Input(name=x.name())
				exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
				inputs.append(exposed_input)
				# Function to get centroid of nodes...
				inputs_center = self.nodeList_center(inputs)

				common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
				common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
				common_dot.setInput(0, exposed_input)

				for index, i in enumerate(input_names_list):
					if i.endswith(x.name()):
						joinviewPipes.setInput(index, common_dot)

			joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

			output_pipe = nuke.nodes.Output()
			output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
			output_pipe.setInput(0, joinviewPipes)

			TrimColorsGroup.end()	
			#=========================================================                   
			# End the TrimColorsGroup node for Comp Layers section...
			#=========================================================			

			# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
			for index, NoOp in enumerate(List_of_NoOp_Nodes):
				TrimColorsGroup.setInput(index, NoOp)

			if self.TotalLightBuild:
				TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), List_of_NoOp_Nodes[0].ypos()+(self.nodeSpacingY))
			else:
				TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), mergeDiffuseRawLight.ypos()-(self.nodeSpacingY))

			# Make a list of the TrimColorsGroup node we've made...
			TrimColorsGroupList.append(TrimColorsGroup)

			#=========================================================
			# END -- individual color pipes for Comp Layers section...
			#=========================================================

		# If it's an Interior build, then the SuperAmbient Shuffle pass is last and needs to have its input set to the green channel of the SuperAmbient layer...
		if (self.Build == 'Int') and (p == self.ShuffleLayers[-1]):
			ShuffleNode2.knob('red').setValue('green')
			ShuffleNode2.knob('green').setValue('green')
			ShuffleNode2.knob('blue').setValue('green')
			ShuffleNode2.knob('alpha').setValue('green')

		#--------------------------------------------------------------------------------------------------------
		# Create and connect the Merge nodes to the TrimColorsGroup nodes we just made...

		for index, p in enumerate(TrimColorsGroupList):

			if index == 0:

				node = nuke.nodes.Merge2( operation='plus', label=(plusCompPasses[index])[0], output='rgb' )
				if self.TotalLightBuild:
					node.setXYpos(TrimColorsGroupList[index].xpos(), TotalLight_BottomDot.ypos()-9)
				else:
					node.setXYpos((ShuffleAlpha.xpos()+(self.nodeSpacingX*4))+(index*(self.nodeSpacingX*4))+(index*(self.ColorPipesSpacingX))+self.ColorPipesSpacingX, dotDiffuse2.ypos()+(self.nodeSpacingY*2))
				node.setInput(0, copyAlpha)
				node.setInput(1, TrimColorsGroupList[index])

				inputB = node
			else:
				myMerge = nuke.nodes.Merge2(operation='plus', label=(plusCompPasses[index])[0], output='rgb')
				if self.TotalLightBuild:
					myMerge.setXYpos(TrimColorsGroupList[index].xpos(), TotalLight_BottomDot.ypos()-9)
				else:
					myMerge.setXYpos((ShuffleAlpha.xpos()+(self.nodeSpacingX*4))+(index*(self.nodeSpacingX*4))+(index*(self.ColorPipesSpacingX))+self.ColorPipesSpacingX, dotDiffuse2.ypos()+(self.nodeSpacingY*2))
				myMerge.setInput(0, inputB)
				myMerge.setInput( 1, TrimColorsGroupList[index] )

				inputB = myMerge

				lastMerge = myMerge

			# If it's the last layer...
			if (p == TrimColorsGroupList[-1]):

				# If this is an Interior Build, we don't need to have all the CarBody passes, so we're done with the build...
				if (self.Build == 'Int'):

					# The SuperAmbient Merge is the last one and needs to have its Merge operation set to 'multiply'... and needs to have its input set to the green channel of the SuperAmbient layer...
					lastMerge.knob('operation').setValue('multiply')

					#--------------------------------------------------------------------------------------------------------
					# Add a Backdrop node behind the whole graph...

					# Selected all the nodes...
					lastMerge['selected'].setValue(True)
					nuke.selectConnectedNodes()

					# Deselect the top nodes...
					self.TrimViewGen.TrimViewsGroup['selected'].setValue(False)
					dot_start['selected'].setValue(False)

					# Create the backdrop, unless backdrop_off is set to True...
					if self.backdrop_off == False:
						backdrop_node = self.auto_backdrop(rand_color=self.rand_color, bd_label='Interior'+'_'+self.render_layers+'_Rebuild')

					#--------------------------------------------------------
					# Check to see if this is an Innocean/Hyundai project, in which case we need to add callbacks for creating image metadata tags for Photoshop, change the image type to TIFF and set the output path to the preferred format... 
					## NOTE: Make sure the Write node's 'channels' value is set to "rgb" for the Interior Build!
					hyundai = False
					if nuke.ask('Is this an Innocean/Hyundai project?'):
						hyundai = True

					# Add ModifyMetaData node to set pathname metadata values...
					metadata_node = nuke.nodes.ModifyMetaData(name='metadata_node')
					metadata_node.setInput(0, lastMerge)
					metadata_node.setXYpos(lastMerge.xpos(), lastMerge.ypos()+250)
					metadata_node.knob('label').setValue('SET VERSION NUMBER HERE...')

					# Set the ModifyMetaData node's metadata knob with script-defined and user-supplied values...	
					version_data = "{set version v001}"
					Exterior_Interior_data = "{set Exterior_Interior " + self.Exterior_Interior + "}"
					ex_in_data = "{set ex_in " + self.ex_in + "}"
					model_data = "{set model " + self.modelName + "}"
					year_data = "{set year " + self.modelYear + "}"
					main_dir_data = "{set main_dir " + self.main_dir + "}"
					comp_dir_data = "{set comp_dir img/comp}"
					# Set the metadata knob with the new values...
					if hyundai:
						metadata_node["metadata"].fromScript(version_data + "\n" + model_data + "\n" + year_data + "\n" + Exterior_Interior_data + "\n" + ex_in_data + "\n" + comp_dir_data + "\n" + main_dir_data)
					else:
						metadata_node["metadata"].fromScript(version_data + "\n" + model_data + "\n" + year_data + "\n" + Exterior_Interior_data + "\n" + comp_dir_data)
					# Add ViewMetaData node...
					viewmetadata_node = nuke.nodes.ViewMetaData(name='view_metadata_node')
					viewmetadata_node.setInput(0, metadata_node)
					viewmetadata_node.setXYpos(metadata_node.xpos(), metadata_node.ypos()+50)						

					# Check for a project path in Project Settings project_directory knob...
					if nuke.Root().knob('project_directory').value():
						pass
					else:
						nuke.message("1)  Save your script.\n\n2)  Add a project directory path in the Project Settings panel. (Save again.)\n\nNOTE: The Write Node output path depends on having the project directory set. Use a trailing slash at the end of the project directory name.\n\nExample: N:/Jobs/Innocean/INNO-13-025_2014_Tucson_8-Interior_Angles/CGI/Work/s01_Int_8-Frame/\n\nIf you View the Text Node, you can see what the full output path will be...")
					# Add Write node...
					if hyundai:
						Write_Views = nuke.nodes.Write(name='Write_Views', file='[value project_directory][metadata comp_dir]/[metadata version]/[metadata main_dir]/[metadata Exterior_Interior]/[metadata year]/[metadata model]/[python nuke.thisView()]/[metadata year]_[metadata model]_[python nuke.thisView()]_[metadata ex_in]_####.tif')
						##print Write_Views.knobs()
						if 'Metadata_Tab' in Write_Views.knobs():
							Write_Views.knob('ICC_knob').setValue('sRGB_profile_from_Photoshop.icc')
							Write_Views.knob('IPTC_knob').setValue(True)
							Write_Views.knob('Hyundai_knob').setValue(True)
						elif 'Metadata_Tab' not in Write_Views.knobs():
							print "Metadata Tab is missing. Reverting to old TagImages code!"							
							Write_Views.knob('beforeRender').setValue('''from TagImages import TagImages
TagImages.TagImages().create_args_file()''')
							Write_Views.knob('afterFrameRender').setValue('''from TagImages import TagImages
TagImages.TagImages().tag_images()''')						
					else:
						Write_Views = nuke.nodes.Write(name='Write_Views', file='[value project_directory][metadata comp_dir]/[metadata version]/[metadata Exterior_Interior]/[metadata year]/[metadata model]/[python nuke.thisView()]/[metadata year]_[metadata model]_[python nuke.thisView()]_####.png')
					if 'Metadata_Tab' in Write_Views.knobs():
						Write_Views.knob('ICC_knob').setValue('sRGB_profile_from_Photoshop.icc')					
					Write_Views.knob('channels').setValue("rgb")					
					Write_Views.setInput(0, viewmetadata_node)
					Write_Views.setXYpos(viewmetadata_node.xpos(), viewmetadata_node.ypos()+100)	
					# Add Text node to view file knob output path values...
					text_node = nuke.nodes.Text(name='text_node', message='[value [value input.name].file]')
					text_node.setInput(0, Write_Views)
					text_node.setXYpos(Write_Views.xpos()-150, Write_Views.ypos())
					if os.name == "nt":
						text_node.knob('font').setValue('C:/Windows/Fonts/arial.ttf')
					elif os.name == "posix":
						text_node.knob('font').setValue('/Library/Fonts/Arial.ttf')
					text_node.knob('size').setValue(25)
					text_node.knob('translate').setValue((0, 50))
					text_node.knob('label').setValue('View Output Path here...')

					# All nodes unselected...
					[ n['selected'].setValue(False) for n in nuke.allNodes() ]
					# Select the Write node section...
					metadata_node['selected'].setValue(True)
					viewmetadata_node['selected'].setValue(True)
					Write_Views['selected'].setValue(True)
					text_node['selected'].setValue(True)

					# Create the backdrop, unless backdrop_off is set to True...
					if self.backdrop_off == False:
						backdrop_node = self.auto_backdrop(rand_color=self.rand_color, bd_label='Write Trim Views')

				else:
					#========================================================================================================
					#  This is an Exterior Build. We have all of the CarBody passes, so add the extra CarBody comp section to the BasicDiffuse configuration...
					#========================================================================================================

					#========================================================================================================
					# The Car Body section...
					#========================================================================================================					

					bodyPasses = []

					# Initialize a new variable to collect the TrimColorsGroup node we create...
					TrimColorsGroupList = []

					for index, p2 in enumerate(self.BodyLayers):
						# Create start_dot for each Shuffle node to hang from...
						shuffle_dot3 = nuke.nodes.Dot()

						if (index == 0):
							shuffle_dot3.setXYpos((shuffle_dot2.xpos()+(self.nodeSpacingX*4))+(index*(self.nodeSpacingX*4))+(index*(self.nodeSpacingX*4))+(index*(self.ColorPipesSpacingX))+self.ColorPipesSpacingX, ShuffleAlphaDot.ypos())
							shuffle_dot3.setInput(0, shuffle_dot2)
							inputC = shuffle_dot3
						else:
							shuffle_dot3.setXYpos((shuffle_dot2.xpos()+(self.nodeSpacingX*4))+(index*(self.nodeSpacingX*4))+(index*(self.ColorPipesSpacingX))+self.ColorPipesSpacingX, ShuffleAlphaDot.ypos())
							shuffle_dot3.setInput(0, inputC)
							inputC = shuffle_dot3

						# Create the CarBody Shuffle nodes...
						ShuffleNode3 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p2, label='[value in]', postage_stamp = self.postage_stamps)
						# Offset them from the last Shuffle we created...
						ShuffleNode3.setXYpos(shuffle_dot2.xpos()-self.offset+(self.nodeSpacingX*4)+(index*(self.nodeSpacingX*4))+(index*(self.ColorPipesSpacingX))+self.ColorPipesSpacingX, ShuffleNode2.ypos())
						# Set which channel to shuffle...
						ShuffleNode3.knob('in').setValue(p2)
						# Connect to the start_dot node...
						ShuffleNode3.setInput(0, shuffle_dot3)

						# Make an indexed list of the nodes we created...
						bodyPasses.append((p2, ShuffleNode3))

						#=========================================================
						# BEGIN -- individual color pipes for Car Body section...
						#=========================================================

						connecting_node = ShuffleNode3

						#--------------------------------------------------------------------------------------------------------
						# Make a connecting dot below the shuffle nodes...
						Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos()+self.offset, ypos=dotDiffuse.ypos())
						Pipe_Start.setInput(0, connecting_node)
						input_pipe = None
						input_pipe2 = None

						#--------------------------------------------------------------------------------------------------------
						# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
						List_of_NoOp_Nodes =[]

						for index, c in enumerate(self.TrimViewGen.colors_to_build):
							n = nuke.nodes.NoOp(name=c)
							n2 =  nuke.nodes.NoOp(name=c)
							List_of_NoOp_Nodes.append(n2)
							top_dot = nuke.nodes.Dot(name=c+'_dot')

							if (index == 0):
								n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
								n.setInput(0, Pipe_Start)
								input_pipe = n

								top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
								top_dot.setInput(0, n)					

								if self.TotalLightBuild:
									n2.setXYpos(Pipe_Start.xpos()-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
								else:
									n2.setXYpos(Pipe_Start.xpos()-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
								n2.setInput(0, top_dot)
								input_pipe2 = n

							else:
								n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
								n.setInput(0, input_pipe)
								input_pipe = n

								top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
								top_dot.setInput(0, n)					

								if self.TotalLightBuild:
									n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
								else:
									n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
								n2.setInput(0, top_dot)
								input_pipe2 = n

						#=========================================================
						# END -- individual color pipes for Car Body section...
						#=========================================================

						#=========================================================
						# Begin the TrimColorsGroup node for Car Body section...
						#=========================================================
						TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label=p2)
						TrimColorsGroup.begin()

						#--------------------------------------------------------------------------------------------------------
						# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
						joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset, ypos=Pipe_Start.ypos())

						input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
						inputs = []

						for index, x in enumerate(List_of_NoOp_Nodes):
							exposed_input = nuke.nodes.Input(name=x.name())
							exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
							inputs.append(exposed_input)
							# Function to get centroid of nodes...
							inputs_center = self.nodeList_center(inputs)

							common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
							common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
							common_dot.setInput(0, exposed_input)

							for index, i in enumerate(input_names_list):
								if i.endswith(x.name()):
									joinviewPipes.setInput(index, common_dot)

						joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

						output_pipe = nuke.nodes.Output()
						output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
						output_pipe.setInput(0, joinviewPipes)

						TrimColorsGroup.end()	
						#=========================================================                   
						# End the TrimColorsGroup node for Car Body section...
						#=========================================================			

						# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
						for index, NoOp in enumerate(List_of_NoOp_Nodes):
							TrimColorsGroup.setInput(index, NoOp)

						if self.TotalLightBuild:
							TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), List_of_NoOp_Nodes[0].ypos()+(self.nodeSpacingY))
						else:
							TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), mergeDiffuseRawLight.ypos()-(self.nodeSpacingY))

						# Make a list of the TrimColorsGroup node we've made...
						TrimColorsGroupList.append(TrimColorsGroup)

						#=========================================================
						# END -- individual color pipes for Car Body section...
						#=========================================================

					#--------------------------------------------------------------------------------------------------------
					# Create and connect the Merge nodes to the TrimColorsGroup nodes we just made...

					for index, p3 in enumerate(TrimColorsGroupList):
						if (index == 0):
							start_dot3 = nuke.nodes.Dot(name=((bodyPasses[index])[0])+'_Dot')
							if self.TotalLightBuild:
								start_dot3.setXYpos(TrimColorsGroupList[index].xpos()+self.offset, TotalLight_BottomDot.ypos()-(2*self.nodeSpacingY))
							else:
								start_dot3.setXYpos(TrimColorsGroupList[index].xpos()+self.offset, (dotDiffuse2.ypos()))
							start_dot3.setInput(0, TrimColorsGroupList[index] )

							inputB2 = start_dot3
						else:
							myMerge2 = nuke.nodes.Merge2(operation='plus', label=(bodyPasses[index])[0], output='rgb')
							if self.TotalLightBuild:
								myMerge2.setXYpos(TrimColorsGroupList[index].xpos(), (TotalLight_BottomDot.ypos()-9)-(2*self.nodeSpacingY))
							else:
								myMerge2.setXYpos(TrimColorsGroupList[index].xpos(), (dotDiffuse2.ypos()-9))

							myMerge2.setInput(0, inputB2)
							myMerge2.setInput(1, TrimColorsGroupList[index] )
							inputB2 = myMerge2

					#========================================================================================================
					# The CarBody alpha Copy node section...
					#========================================================================================================

					#--------------------------------------------------------------------------------------------------------
					# Create the Alpha Shuffle node and Copy node...
					start_dotBodyAlpha = nuke.nodes.Dot()
					start_dotBodyAlpha.setXYpos((myMerge2.xpos()+self.offset+(self.nodeSpacingX*4))+self.ColorPipesSpacingX, shuffle_dot3.ypos())
					start_dotBodyAlpha.setInput(0, shuffle_dot3)

					# Copy the CarBody alpha into the stream...
					BodyAlpha = nuke.nodes.Copy( from0=self.CarBodyAlpha[0], to0='rgba.alpha', inputs=[ myMerge2, start_dotBodyAlpha ] )
					BodyAlpha.setXYpos(start_dotBodyAlpha.xpos()-self.offset, myMerge2.ypos())

					# Create the last Merge node...
					mergeCarBodyPaint = nuke.nodes.Merge2( operation='over', inputs=[ lastMerge, BodyAlpha ], label='CarBodyPaint', output='rgb')
					mergeCarBodyPaint.setXYpos(BodyAlpha.xpos(), lastMerge.ypos())			


					#========================================================================================================
					# The Ambient Layer section...
					#========================================================================================================					

					# Initialize a new variable to collect the TrimColorsGroup node we create...
					TrimColorsGroupList = []					

					#--------------------------------------------------------------------------------------------------------
					# Add the Ambient layer last...
					shuffle_dot4 = nuke.nodes.Dot()
					shuffle_dot4.setXYpos((start_dotBodyAlpha.xpos()+(self.nodeSpacingX*4)), ShuffleAlphaDot.ypos())
					shuffle_dot4.setInput(0, start_dotBodyAlpha)

					ShuffleNodeAmb = nuke.nodes.Shuffle(name = 'Shuffle_'+ self.AmbientLayer[0], label='[value in]', postage_stamp = self.postage_stamps)
					ShuffleNodeAmb.setXYpos(start_dotBodyAlpha.xpos()-self.offset+(self.nodeSpacingX*4), ShuffleNode3.ypos())
					ShuffleNodeAmb.setInput(0, shuffle_dot4)
					ShuffleNodeAmb.knob('in').setValue(self.AmbientLayer[0])
					ShuffleNodeAmb.knob('red').setValue('green')
					ShuffleNodeAmb.knob('green').setValue('green')
					ShuffleNodeAmb.knob('blue').setValue('green')
					ShuffleNodeAmb.knob('alpha').setValue('green')

					#=========================================================
					# BEGIN -- individual color pipes for Ambient Layer section...
					#=========================================================

					connecting_node = ShuffleNodeAmb

					#--------------------------------------------------------------------------------------------------------
					# Make a connecting dot below the shuffle nodes...
					Pipe_Start = nuke.nodes.Dot(xpos=connecting_node.xpos()+self.offset, ypos=dotDiffuse.ypos())
					Pipe_Start.setInput(0, connecting_node)
					input_pipe = None
					input_pipe2 = None

					#--------------------------------------------------------------------------------------------------------
					# Create the NoOp nodes at the top and bottom of each color pipe and connect them...
					List_of_NoOp_Nodes =[]

					for index, c in enumerate(self.TrimViewGen.colors_to_build):
						n = nuke.nodes.NoOp(name=c)
						n2 =  nuke.nodes.NoOp(name=c)
						List_of_NoOp_Nodes.append(n2)
						top_dot = nuke.nodes.Dot(name=c+'_dot')

						if (index == 0):
							n.setXYpos(Pipe_Start.xpos()-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
							n.setInput(0, Pipe_Start)
							input_pipe = n

							top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
							top_dot.setInput(0, n)

							if self.TotalLightBuild:
								n2.setXYpos(Pipe_Start.xpos()-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
							else:
								n2.setXYpos(Pipe_Start.xpos()-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
							n2.setInput(0, top_dot)
							input_pipe2 = n

						else:
							n.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, dotDiffuse.ypos()+(self.nodeSpacingY))
							n.setInput(0, input_pipe)
							input_pipe = n

							top_dot.setXYpos(n.xpos()+self.offset, n.ypos()+50)
							top_dot.setInput(0, n)

							if self.TotalLightBuild:
								n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, TrimColorsGroup.ypos()-(self.nodeSpacingY))
							else:
								n2.setXYpos(Pipe_Start.xpos()+(index*self.NoOpSpacingX*4)-self.offset, mergeDiffuseRawLight.ypos()-(2*self.nodeSpacingY))
							n2.setInput(0, top_dot)
							input_pipe2 = n

					#=========================================================
					# END -- individual color pipes for Ambient Layer section...
					#=========================================================

					#=========================================================
					# Begin the TrimColorsGroup node for Ambient Layer section...
					#=========================================================
					TrimColorsGroup = nuke.nodes.Group(name='TrimColorsGroup', label='ambient')
					TrimColorsGroup.begin()

					#--------------------------------------------------------------------------------------------------------
					# Create a JoinView node and hook up all the same-color inputs to the corresponding NoOp color pipe...
					joinviewPipes = nuke.nodes.JoinViews(xpos=Pipe_Start.xpos()-self.offset,  ypos=Pipe_Start.ypos())

					input_names_list = joinviewPipes.knob('viewassoc').value().splitlines()
					inputs = []

					for index, x in enumerate(List_of_NoOp_Nodes):
						exposed_input = nuke.nodes.Input(name=x.name())
						exposed_input.setXYpos(joinviewPipes.xpos()+(index*(self.offset*4)), joinviewPipes.ypos()-200)
						inputs.append(exposed_input)
						# Function to get centroid of nodes...
						inputs_center = self.nodeList_center(inputs)

						common_dot = nuke.nodes.Dot(name=x.name()+'_dot')
						common_dot.setXYpos(exposed_input.xpos()+self.offset, exposed_input.ypos()+100 )
						common_dot.setInput(0, exposed_input)

						for index, i in enumerate(input_names_list):
							if i.endswith(x.name()):
								joinviewPipes.setInput(index, common_dot)

					joinviewPipes.setXYpos(inputs_center[0], inputs_center[1]+200)

					output_pipe = nuke.nodes.Output()
					output_pipe.setXYpos(joinviewPipes.xpos(), joinviewPipes.ypos()+100)
					output_pipe.setInput(0, joinviewPipes)

					TrimColorsGroup.end()	
					#=========================================================                   
					# End the TrimColorsGroup node for Ambient Layer section...
					#=========================================================			

					# Connect the TrimColorsGroup node's inputs to the List_of_NoOp_Nodes...
					for index, NoOp in enumerate(List_of_NoOp_Nodes):
						TrimColorsGroup.setInput(index, NoOp)

					if self.TotalLightBuild:
						TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), List_of_NoOp_Nodes[0].ypos()+(self.nodeSpacingY))
					else:
						TrimColorsGroup.setXYpos(List_of_NoOp_Nodes[0].xpos(), mergeDiffuseRawLight.ypos()-(self.nodeSpacingY))

					# Make a list of the TrimColorsGroup node we've made...
					TrimColorsGroupList.append(TrimColorsGroup)

					AmbMerge = nuke.nodes.Merge2(operation='multiply', label=self.AmbientLayer[0], output='rgb')
					AmbMerge.setXYpos(TrimColorsGroup.xpos(), mergeCarBodyPaint.ypos())
					AmbMerge.setInput(0, mergeCarBodyPaint)
					AmbMerge.setInput(1, TrimColorsGroup)

					#--------------------------------------------------------
					# Add a Backdrop node behind the whole graph...
					lastMerge = mergeCarBodyPaint
					lastMerge['selected'].setValue(True)
					nuke.selectConnectedNodes()

					# Deselect the top nodes...
					self.TrimViewGen.TrimViewsGroup['selected'].setValue(False)
					dot_start['selected'].setValue(False)

					# Create the backdrop, unless backdrop_off is set to True...
					if self.backdrop_off == False:
						backdrop_node = self.auto_backdrop(rand_color=self.rand_color, bd_label='Exterior'+'_'+self.render_layers+'_Rebuild')

					#--------------------------------------------------------
					# Check to see if this is an Innocean/Hyundai project, in which case we need to add callbacks for creating image metadata tags for Photoshop, change the image type to TIFF and set the output path to the preferred format... 
					## NOTE: Make sure the Write node's 'channels' value is set to "rgba" for the Exterior Build!
					hyundai = False
					if nuke.ask('Is this an Innocean/Hyundai project?'):
						hyundai = True

					# Add ModifyMetaData node to set pathname metadata values...
					metadata_node = nuke.nodes.ModifyMetaData(name='metadata_node')
					metadata_node.setInput(0, lastMerge)
					metadata_node.setXYpos(lastMerge.xpos(), lastMerge.ypos()+250)
					metadata_node.knob('label').setValue('SET VERSION NUMBER HERE...')

					# Set the ModifyMetaData node's metadata knob with script-defined and user-supplied values...	
					version_data = "{set version v001}"
					Exterior_Interior_data = "{set Exterior_Interior " + self.Exterior_Interior + "}"
					ex_in_data = "{set ex_in " + self.ex_in + "}"
					model_data = "{set model " + self.modelName + "}"
					year_data = "{set year " + self.modelYear + "}"
					main_dir_data = "{set main_dir " + self.main_dir + "}"
					comp_dir_data = "{set comp_dir img/comp}"
					# Set the metadata knob with the new values...
					if hyundai:
						metadata_node["metadata"].fromScript(version_data + "\n" + model_data + "\n" + year_data + "\n" + Exterior_Interior_data + "\n" + ex_in_data + "\n" + comp_dir_data + "\n" + main_dir_data)
					else:
						metadata_node["metadata"].fromScript(version_data + "\n" + model_data + "\n" + year_data + "\n" + Exterior_Interior_data + "\n" + comp_dir_data)
					# Add ViewMetaData node...
					viewmetadata_node = nuke.nodes.ViewMetaData(name='view_metadata_node')
					viewmetadata_node.setInput(0, metadata_node)
					viewmetadata_node.setXYpos(metadata_node.xpos(), metadata_node.ypos()+50)						

					# Check for a project path in Project Settings project_directory knob...
					if nuke.Root().knob('project_directory').value():
						pass
					else:
						nuke.message("1)  Save your script.\n\n2)  Add a project directory path in the Project Settings panel. (Save again.)\n\nNOTE: The Write Node output path depends on having the project directory set. Use a trailing slash at the end of the project directory name.\n\nExample: N:/Jobs/Innocean/INNO-13-025_2014_Tucson_8-Interior_Angles/CGI/Work/s01_Int_8-Frame/\n\nIf you View the Text Node, you can see what the full output path will be...")
					# Add Write node...
					if hyundai:
						Write_Views = nuke.nodes.Write(name='Write_Views', file='[value project_directory][metadata comp_dir]/[metadata version]/[metadata main_dir]/[metadata Exterior_Interior]/[metadata year]/[metadata model]/[python nuke.thisView()]/[metadata year]_[metadata model]_[python nuke.thisView()]_[metadata ex_in]_####.tif')
						##print Write_Views.knobs()
						if 'Metadata_Tab' in Write_Views.knobs():
							Write_Views.knob('ICC_knob').setValue('sRGB_profile_from_Photoshop.icc')
							Write_Views.knob('IPTC_knob').setValue(True)
							Write_Views.knob('Hyundai_knob').setValue(True)
						elif 'Metadata_Tab' not in Write_Views.knobs():
							print "Metadata Tab is missing. Reverting to old TagImages code!"	
							Write_Views.knob('beforeRender').setValue('''from TagImages import TagImages
TagImages.TagImages().create_args_file()''')
							Write_Views.knob('afterFrameRender').setValue('''from TagImages import TagImages
TagImages.TagImages().tag_images()''')						
					else:
						Write_Views = nuke.nodes.Write(name='Write_Views', file='[value project_directory][metadata comp_dir]/[metadata version]/[metadata Exterior_Interior]/[metadata year]/[metadata model]/[python nuke.thisView()]/[metadata year]_[metadata model]_[python nuke.thisView()]_####.png')
					if 'Metadata_Tab' in Write_Views.knobs():
						Write_Views.knob('ICC_knob').setValue('sRGB_profile_from_Photoshop.icc')					
					Write_Views.knob('channels').setValue("rgba")
					Write_Views.setInput(0, viewmetadata_node)
					Write_Views.setXYpos(viewmetadata_node.xpos(), viewmetadata_node.ypos()+100)
					# Add Text node to view file knob output path values...
					text_node = nuke.nodes.Text(name='text_node', message='[value [value input.name].file]')
					text_node.setInput(0, Write_Views)
					text_node.setXYpos(Write_Views.xpos()-150, Write_Views.ypos())
					if os.name == "nt":
						text_node.knob('font').setValue('C:/Windows/Fonts/arial.ttf')
					elif os.name == "posix":
						text_node.knob('font').setValue('/Library/Fonts/Arial.ttf')
					text_node.knob('size').setValue(25)
					text_node.knob('translate').setValue((0, 50))
					text_node.knob('label').setValue('View Output Path here...')

					# All nodes unselected...
					[ n['selected'].setValue(False) for n in nuke.allNodes() ]
					# Select the Write node section...
					metadata_node['selected'].setValue(True)
					viewmetadata_node['selected'].setValue(True)
					Write_Views['selected'].setValue(True)
					text_node['selected'].setValue(True)

					# Create the backdrop, unless backdrop_off is set to True...
					if self.backdrop_off == False:
						backdrop_node = self.auto_backdrop(rand_color=self.rand_color, bd_label='Write Trim Views')
