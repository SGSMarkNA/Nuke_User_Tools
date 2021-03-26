import nuke
import nukescripts
import re
# Customized auto_backdrop function...
from auto_backdrop.auto_backdrop import auto_backdrop

####################################################
class TrimViewGenerator(nukescripts.PythonPanel):
	'''
	Part of a system that creates a car configurator comp. An EXR CGI rebuild comp is created using Nuke's views mechanism.
	Trim and Color names are entered by the user and a view is created for each combination. This facilitates easy switching between
	trims when color correcting. Also, a Write node is created that is set up to automatically render each trim view within separate directories.
	This Class runs the Trims and Colors Input Panels to get the list of trims and colors from the user. It also makes Nuke views from the trim + color names.
	Finally, it creates a Group node to act as an input for EXR Read nodes. This class is imported by the TrimViewGenerator Class to build the rest of the comp structure.
	'''

	def __init__(self):

		self.auto_backdrop = auto_backdrop

		self.spacing_x = 150
		self.spacing_y = 150
		self.offset = 34

	#### Node placement function borrowed from Drew Loveridge...
	def nodeList_center(self, nodeList=None):
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

	##################################
	#### CLEANUP VIEWS...
	##################################
	def cleanup_old_views(self):
		for view in nuke.views():
			if view != 'main':
				nuke.Root().deleteView(view)
			if 'main' not in nuke.views():
				nuke.Root().addView('main')

	def createModelNameInputPanel(self):

		# Build a model name input panel...
		nukescripts.PythonPanel.__init__(self, "Model Name Data Entry:", "com.armstrong-white.ModelNameInputPanel")
		self.userInput = nuke.String_Knob("modelName", "Add Vehicle Model Name:")
		self.addKnob(self.userInput)

		''' Get the vehicle Model Name from the user and sanitize the input - removing spaces and illegal characters.'''
		self.userInput.setText('')
		self.userInput.setLabel("Add Vehicle Model Name:")
		self.userInput.setTooltip("model_name")

		self.modelYear = "2018"
		self.yearInput = nuke.Enumeration_Knob( 'modelYear', 'Model Year: ', ([self.modelYear, '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015']))
		self.addKnob(self.yearInput)

		self.Build = "Int"
		self.buildInput = nuke.Enumeration_Knob( 'buildType', 'Build Type: ', ([self.Build, 'Int', 'Ext']))
		self.addKnob(self.buildInput)	

		modelNameInputPanel = nukescripts.PythonPanel.showModalDialog(self)
		if modelNameInputPanel:
			# Check for no input from user.
			if self.userInput.value() is '':
				nuke.message('Nothing Entered for Model Name.')
				return False
			else:
				# Strip out illegal characters...
				pattern = re.compile(r'[^\w]')
				self.modelName = self.userInput.value()
				self.modelName = pattern.sub('_', self.modelName)

			self.modelYear = self.yearInput.value()
			self.Build = self.buildInput.value()

			return self.modelName, self.modelYear, self.Build

	def createTrimsInputPanel(self):
		''' Get a list of colors from the user and sanitize the input - removing spaces and illegal characters. Create views from the trim names + colors entered by the user...'''
		self.trims_to_build = []
		# Build a trim name input panel...
		nukescripts.PythonPanel.__init__(self, "Trim Data Entry:", "com.armstrong-white.TrimsInputPanel")
		self.setMinimumSize(400, 300)
		self.userInput = nuke.Multiline_Eval_String_Knob("trim_names", "Add Trim Names - One per line:")
		self.addKnob(self.userInput)		

		self.userInput.setText('')
		self.userInput.setTooltip("trim_names")
		trimsInputPanel = nukescripts.PythonPanel.showModalDialog(self)
		if trimsInputPanel:
			# Check for no input from user.
			if self.userInput.value() is '':
				nuke.message('Nothing Entered for Trim Names.')
				return False
			else:
				# Strip out illegal characters...
				pattern = re.compile(r'[^\w]')
				self.trimsList = self.userInput.value().splitlines()
				for x in self.trimsList:
					clean_x = pattern.sub('_', x)
					self.trims_to_build.append(clean_x)
				return self.trims_to_build

	def createColorsInputPanel(self):
		''' Get a list of colors from the user and sanitize the input - removing spaces and illegal characters. Create views from the trim names + colors entered by the user...'''
		self.colors_to_build = []
		# Build a color name input panel...
		nukescripts.PythonPanel.__init__(self, "Color Data Entry:", "com.armstrong-white.ColorInputPanel")
		self.setMinimumSize(400, 300)
		self.userInput = nuke.Multiline_Eval_String_Knob("color_names", "Add color Names - One per line:")
		self.addKnob(self.userInput)		

		self.userInput.setText('')
		self.userInput.setTooltip("color_names")
		colorsInputPanel = nukescripts.PythonPanel.showModalDialog(self)
		if colorsInputPanel:
			# Check for no input from user.
			if self.userInput.value() is '':
				nuke.message('Nothing Entered for Color Names.')
				return False
			else:
				# Strip out illegal characters...
				pattern = re.compile(r'[^\w]')
				self.colorsList = self.userInput.value().splitlines()
				for x in self.colorsList:
					clean_x = pattern.sub('_', x)
					self.colors_to_build.append(clean_x)
				return self.colors_to_build

	def createTrimColorViews(self):
		# Check for no input from user.
		if not self.trims_to_build or not self.colors_to_build:
			nuke.message("I don't have enough information. Please enter a list of Trims in the first pop-up window and a list of colors in the second window.")
			return
		#Combine the trims names and colors...
		self.views_to_create = []
		for trim in self.trims_to_build:
			for color in self.colors_to_build:
				view_name = trim+'_'+color
				self.views_to_create.append(view_name)
		# Add the views...
		for v in self.views_to_create:
			try:
				nuke.Root().addView(v)
			except ValueError:
				# View might already exist...
				pass
			if len(self.views_to_create) >5:
				nuke.Root().knob('views_button').setValue(False)
			# Remove the default 'main' view...
			try:
				nuke.Root().deleteView('main')
			except Exception:
				pass

	def storeTrimColorViews(self):
		# Add the list of trims_to_build and colors_to_build to the Nuke Project Settings/comment panel...
		self.input_list = []
		self.label_string = None
		self.input_list.append('** DO NOT DELETE OR MODIFY THIS LIST! **\n')
		self.input_list.append('TRIMS:')
		for trim in self.trims_to_build:
			self.input_list.append(trim)
		self.input_list.append('\n')
		self.input_list.append('COLORS:')
		for color in self.colors_to_build:
			self.input_list.append(color)
		self.label_string = '\n'.join(self.input_list)
		# Write the values to the comment knob...
		nuke.Root().knob('label').setValue(self.label_string)

	def createTrimViewSection(self):
		''' Start building the comp schematic with the OneView nodes, first...'''

		#########################################
		#### Start the Group node.
		self.List_of_commonDots = []
		self.TrimViewsGroup = nuke.nodes.Group(name='TrimViewsGroup')
		self.TrimViewsGroup.begin()

		# Check for no input from user.
		if not self.trims_to_build or not self.colors_to_build:
			return

		# Create a OneView node for each view name...
		self.List_of_OneView_Nodes = []
		for index, v in enumerate(nuke.views()):
			if index ==0:
				node = nuke.nodes.OneView(name=v+'_OneView', view=v, label='[value view]', xpos=0, ypos=0)
			else:
				node = nuke.nodes.OneView(name=v+'_OneView', view=v, label='[value view]', xpos=0+self.spacing_x*index, ypos=0)
			self.List_of_OneView_Nodes.append(node)

		# Create a list of the OneView nodes and get their midpoint...
		center = self.nodeList_center(self.List_of_OneView_Nodes)
		#print 'center----->', center

		# Create a JoinView node and hook up the OneView inputs...
		self.joinviewNode = nuke.nodes.JoinViews(xpos=center[0], ypos=300)
		input_num = 0
		for z in self.List_of_OneView_Nodes:
			#print 'z------------->', repr(z)
			self.joinviewNode.setInput( input_num, z )
			input_num += 1

		# Create a list of the OneView nodes with common trim base names and get their midpoint...
		self.Common_OneView_Nodes = []
		num_colors = len(self.colors_to_build)
		num_colors = int(num_colors)
		counter = len(self.trims_to_build)
		start_index = 0
		end_index = num_colors
		trim_index = 0
		for x in self.List_of_OneView_Nodes:
			while counter >0:
				self.Common_OneView_Nodes = self.List_of_OneView_Nodes[start_index:end_index]
				start_index += num_colors
				end_index += num_colors
				counter -= 1
				center = self.nodeList_center(self.Common_OneView_Nodes)
				trim = self.trims_to_build[trim_index]
				# Create a central dot above each OneView trim section and connect all the common OneViews to it...
				commonDot = nuke.nodes.Dot(name=trim+'_dot')#, label='[knob name]')
				commonDot.setXYpos(center[0]+self.offset, center[1]-300)
				node = commonDot
				self.List_of_commonDots.append(node)
				trim_index += 1

				for OV_node in self.Common_OneView_Nodes:
					OV_node.setInput(0, commonDot)

		#########################################
		# Add a Backdrop node behind the whole graph...
		self.joinviewNode["selected"].setValue(True)
		nuke.selectConnectedNodes()
		# Run the auto_backdrop function... And, set it's name, based on the type of build.
		backdrop_node = self.auto_backdrop(bd_label='OneViews_from_Trim_Names')

		#########################################
		# End the Group node.
		self.TrimViewsGroup.end()

		#########################################
		# Set the exposed input names for the Group node and connect them to the dots...
		with self.TrimViewsGroup:
			for dot in self.List_of_commonDots:
				input_pipe = dot.name().replace('_dot', '')
				input_pipe = nuke.nodes.Input(name=input_pipe)
				input_pipe.setXYpos(dot.xpos()-self.offset, dot.ypos()-200)
				dot.setInput(0, input_pipe)
			# Add the Output pipe...
			output_pipe = nuke.nodes.Output()
			output_pipe.setXYpos(self.joinviewNode.xpos(), self.joinviewNode.ypos()+200)
			output_pipe.setInput(0, self.joinviewNode)

		# Create a backdrop behind the TrimViewsGroup...
		[ n['selected'].setValue(False) for n in nuke.allNodes() ]
		self.TrimViewsGroup['selected'].setValue(True)
		backdrop_node = self.auto_backdrop(bd_label='Read_Node_Inputs')

		# Return values for ConfigCompBuilder to use...
		TrimViewsGroup = self.TrimViewsGroup
		colors_to_build = self.colors_to_build

		return (TrimViewsGroup, colors_to_build)

