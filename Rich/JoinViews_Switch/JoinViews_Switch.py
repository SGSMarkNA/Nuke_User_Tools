
import sys

try:
	from PySide import QtGui, QtCore
except ImportError:
	from PySide2 import QtCore
	from PySide2 import QtWidgets as QtGui
	
try:
	import nuke
except ImportError:
	nuke = None


class JoinViewsSwitch(QtGui.QWidget):


	def __init__(self):
		''''''
		# Initialize the panel object as a QWidget and set its title and minimum width...	
		QtGui.QWidget.__init__(self)
		#---------------------------------------------
		# Additional panel dressing...
		self.setWindowTitle("Create JoinViews Switch")
		#---------------------------------------------
		# Set main container layout...
		self.main_layout = QtGui.QVBoxLayout()
		# This makes sure that the main_layout only uses as much space as needed. So, it shrinks when the internal layouts and widgets shrink.
		self.main_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)		
		#---------------------------------------------
		# Run the methods that create the various sections of the panel...
		self._create_inputs_section()
		#---------------------------------------------
		# Add the layout sections...
		self.main_layout.addLayout(self.inputs_layout)
		#---------------------------------------------
		# Make startup logic_ops_section layout that will be deleted the first time the user types a number entry...
		self.logic_ops_layout = QtGui.QFormLayout()
		self.main_layout.addLayout(self.logic_ops_layout)
		#---------------------------------------------
		# Set the main_layout
		self.setLayout(self.main_layout)
		#---------------------------------------------
		# Initialize the dictionary of logic ops dropdown widgets...
		self.DropdownsDict = {}
		# Initialize the dictionary of text filter widgets...
		self.TextFiltersDict = {}


	def _create_inputs_section(self):
		''''''
		self.inputs_layout = QtGui.QFormLayout()
		#---------------------------------------------
		# Create a Numeric Input Field
		self.inputs = QtGui.QSpinBox()
		# Set this size to make the main_layout be no narrower than this, since its SetFixedSize makes it wrap to this size...
		self.inputs.setMinimumWidth(200)
		# Add it to the form layout with a label...
		self.inputs_layout.addRow('Number of Inputs:', self.inputs)
		#---------------------------------------------
		# Add a divider line...
		self.inputs_divider = QtGui.QFrame()
		self.inputs_divider.setFrameStyle(QtGui.QFrame.HLine)
		# Add it to the form layout
		self.inputs_layout.addRow(self.inputs_divider)
		#---------------------------------------------
		# Hook up user interaction...
		self.inputs.valueChanged.connect(self._inputs_onEditingFinished)


	def _create_expression_section(self):
		''''''
		self.logic_ops_layout = QtGui.QFormLayout()
		#---------------------------------------------
		# Make a list of logic ops...
		self.logicOpsList = ['CONTAINS', 'DOES NOT CONTAIN', 'STARTS WITH', 'ENDS WITH', 'EQUALS']
		#---------------------------------------------
		# Start the naming increment number at 1...
		incr = 1
		#---------------------------------------------
		# Create the widgets, based on the number of inputs the user specifies...
		if self.inputs:
			for Input in range(int(self.inputs.text())):
				#---------------------------------------------
				# Logic Ops widgets...
				Name = "Logic Op " + str(incr) + ':'
				#print Name
				# Create the combo box...
				self.logicOpsDropdown = QtGui.QComboBox()
				# ...and fill it with the list of logic ops to choose from.
				self.logicOpsDropdown.addItems(self.logicOpsList)
				# Add it to the QFormLayout with a label...
				self.logic_ops_layout.addRow(Name, self.logicOpsDropdown)
				# Append the dictionary of dropdown widgets created, so we can get their values later...
				self.DropdownsDict[Name] = self.logicOpsDropdown
				#---------------------------------------------
				# Text Filter widgets...
				Name = "Filter " + str(incr) + ':'
				#print Name
				# Create a text filter input field...
				self.TextFilterInput = QtGui.QLineEdit()
				# Add it to the QFormLayout with a label...
				self.logic_ops_layout.addRow(Name, self.TextFilterInput)
				#---------------------------------------------
				# Add a divider line...
				self.ops_section_divider = QtGui.QFrame()
				self.ops_section_divider.setFrameStyle(QtGui.QFrame.HLine)
				# Add it to the form layout
				self.logic_ops_layout.addRow(self.ops_section_divider)
				# Append the dictionary of dropdown widgets created, so we can get their values later...
				self.TextFiltersDict[Name] = self.TextFilterInput
				#---------------------------------------------
				# Increment the widget counter number...
				incr += 1
		#---------------------------------------------
		# Add OK | Cancel ButtonBox...
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		self.logic_ops_layout.addWidget(self.buttonBox)
		#---------------------------------------------
		# Hook up OK | Cancel actions...
		self.buttonBox.accepted.connect(self._accept)
		self.buttonBox.rejected.connect(self._reject)


	##-----------------------------------------------------------------------##
	## Widget Connection Functions...
	##-----------------------------------------------------------------------##

	def _inputs_onEditingFinished(self):
		''''''
		#---------------------------------------------
		# Clear out any previous layout and widgets... Clear the lists of widgets, also...
		self._clearLayout(self.logic_ops_layout)
		self.DropdownsDict = {}
		self.TextFiltersDict = {}		
		#---------------------------------------------
		# Set the number of inputs to the value of the SpinBox...
		self.num_inputs = int(self.inputs.text())
		#---------------------------------------------
		# Create a number of expression filter sections, based on user input...
		self._create_expression_section()
		#---------------------------------------------
		# Add the layout section...
		self.main_layout.addLayout(self.logic_ops_layout)
		# Added to help prevent having to click twice to activate the OK | Cancel buttons....
		self.setFocus()


	def _accept(self):
		'''When the user clicks OK, create the JoinViewsSwitchGroup...'''
		print 'OK'
		if nuke:
			# Start the Group node.
			##self.JoinViewsSwitchGroup = nuke.nodes.Group(name='JoinViewsSwitchGroup')
			self.JoinViewsSwitchGroup = nuke.createNode('Group', 'name JoinViewsSwitchGroup')
			self.JoinViewsSwitchGroup.begin()
			# Run the node functions...
			self._create_Input_nodes()
			self._create_JoinViews_node()
			self._make_JoinViews_inputs_dictionary()
			self._connect_inputs_based_on_filters()
			self._check_for_unconnected_Input_Nodes()
			# End the Group node.
			self.JoinViewsSwitchGroup.end()
			# Close the panel.
			self.close()
		else:
			# Close the panel.
			self.close()


	def _reject(self):
		''''''
		print 'Cancelled.'
		self.close()


	##-----------------------------------------------------------------------##
	## Nuke Node Functions...
	##-----------------------------------------------------------------------##

	def _create_Input_nodes(self):
		'''Create Input nodes to use as connection points for all of the JoinViews inputs.'''
		self.InputNodes = []
		for InputNode in range(self.num_inputs):
			Input = nuke.nodes.Input()
			self.InputNodes.append(Input)
		# Find the center of the Inputs...
		self.center = self._nodeList_center(self.InputNodes)	


	def _create_JoinViews_node(self):
		'''Create the JoinViews node, centered underneath the OneViews.'''
		self.JoinViews = nuke.nodes.JoinViews()
		self.JoinViews.setXYpos(self.center[0], self.center[1]+200)	


	def _make_JoinViews_inputs_dictionary(self):
		'''Get all the view name inputs from JoinView node view 'viewassoc' knob and create a dictionary out of input index numbers and view names.'''
		self.InputsDict = {}
		for index, name in enumerate(self.JoinViews.knob("viewassoc").value().split()):
			self.InputsDict[index] = name


	def _connect_inputs_based_on_filters(self):
		'''Check to see which JoinViews input names (viewnames) match the Filter. Connect them if they do.'''
		# Make a list of all of the user's logic op choices...
		self.LogicOpList = []
		for key in sorted(self.DropdownsDict.iterkeys()):
			#print "%s: %s" % (key, self.DropdownsDict[key])
			LogicOp = str(self.DropdownsDict[key].currentText())
			self.LogicOpList.append(LogicOp)
		# Make a list of all of the user's text filters...	
		self.ExpressionList = []
		for key in sorted(self.TextFiltersDict.iterkeys()):
			#print "%s: %s" % (key, self.TextFiltersDict[key])
			LogicOp = str(self.TextFiltersDict[key].text())
			self.ExpressionList.append(LogicOp)
		# Combine the text filter list with the associated Logic Ops list...
		self.Expressions_LogicOps_List = zip(self.ExpressionList, self.LogicOpList)
		# Make a dictionary that has both the Nodes To Connect To (Input Nodes) and the Filters (Text and Logic Ops) that the user has typed for each node...	
		self.ConnectionDict = dict(zip(self.InputNodes, self.Expressions_LogicOps_List))
		# Iterate through the ConnectionDict, checking to see which JoinViews input names (viewnames) match the Filter/Logic Op combo...
		# Connect them to the NoOp if they match...
		for NodeToConnectTo, Filter in self.ConnectionDict.iteritems():
			# Make the connections based on the text Filter and logical operator...
			for index, name in self.InputsDict.iteritems():
				if Filter[1] == 'CONTAINS':
					NodeToConnectTo['name'].setValue('CONTAINS_' + Filter[0])
					if Filter[0] in name:
						self.JoinViews.setInput(index, NodeToConnectTo)
				elif Filter[1] == 'DOES NOT CONTAIN':
					NodeToConnectTo['name'].setValue('NOT_' + Filter[0])
					if Filter[0] not in name:
						self.JoinViews.setInput(index, NodeToConnectTo)
				elif Filter[1] == 'STARTS WITH':
					NodeToConnectTo['name'].setValue('STARTS_WITH_' + Filter[0])
					if name.startswith(Filter[0]):
						self.JoinViews.setInput(index, NodeToConnectTo)
				elif Filter[1] == 'ENDS WITH':
					NodeToConnectTo['name'].setValue('ENDS_WITH_' + Filter[0])
					if name.endswith(Filter[0]):
						self.JoinViews.setInput(index, NodeToConnectTo)
				elif Filter[1] == 'EQUALS':
					NodeToConnectTo['name'].setValue('EQUALS_' + Filter[0])
					if (Filter[0]) == name:
						self.JoinViews.setInput(index, NodeToConnectTo)
		# Add the Output pipe...
		output_pipe = nuke.nodes.Output()
		output_pipe.setXYpos(self.JoinViews.xpos(), self.JoinViews.ypos()+200)
		output_pipe.setInput(0, self.JoinViews)


	def _check_for_unconnected_Input_Nodes(self):
		''''''
		self.UnConnectedInputNodes = []
		for Node, Filter in self.ConnectionDict.iteritems():
			if not Node.dependent():
				self.UnConnectedInputNodes.append(Node)
		if self.UnConnectedInputNodes:
			print 'WARNING: Unconnected nodes: ', self.UnConnectedInputNodes
			nuke.message("WARNING: Some inputs are not connected!\n\n"
			             "The logic filters might be overlapping and cause connections to be stolen from one input to another.\n\n"
			             "You can open the Group node and try to fix the problem yourself or start over with a different set of filters...")


	##-----------------------------------------------------------------------##
	## Utility functions...
	##-----------------------------------------------------------------------##

	def _clearLayout(self, layout):
		if layout is not None:
			while layout.count():
				item = layout.takeAt(0)
				widget = item.widget()
				if widget is not None:
					widget.deleteLater()
				else:
					self._clearLayout(item.layout())


	def _nodeList_center(self, nodeList=None):
		'''Node placement function, borrowed from Drew Loveridge...'''
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

##-----------------------------------------------------------------------##
## Run it.
##-----------------------------------------------------------------------##

if not nuke:
	'''
	If we were not able to import nuke, just make this a standalone panel...
	'''
	app = QtGui.QApplication(sys.argv)
	panel = JoinViewsSwitch()
	panel.show()
	panel.raise_()
	app.exec_()
	sys.exit(app.exec_())
else:
	'''
	Otherwise, we are probably wanting to run the panel inside of Nuke.
	So, use this start() function as a way to fire up the panel...
	'''
	def start():
		start.panel = JoinViewsSwitch()
		start.panel.show()
		start.panel.raise_()
	start()
