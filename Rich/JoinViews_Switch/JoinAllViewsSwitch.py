import sys
try:
	import nuke
except ImportError:
	nuke = None


class JoinAllViewsSwitch(object):


	def __init__(self):
		''''''
	##-----------------------------------------------------------------------##
	## Nuke Node Functions...
	##-----------------------------------------------------------------------##
	def _create_Input_nodes(self):	
		self.InputNodes = []
		self.ViewNamesList = []
		for Index, View in enumerate(nuke.views()):
			self.ViewNamesList.append(View)
			Input = nuke.nodes.Input(name=View)
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

	def _connect_all_inputs_to_all_views(self):
		'''Check to see which JoinViews input names (viewnames) match... Connect them if they do.'''
		# Make a dictionary that has both the Nodes To Connect To (Input Nodes) and the Filters (Text and Logic Ops) that the user has typed for each node...	
		self.ConnectionDict = dict(list(zip(self.InputNodes, self.ViewNamesList)))
		# Iterate through the ConnectionDict, checking to see which JoinViews input names (viewnames) match the Filter/Logic Op combo...
		# Connect them to the NoOp if they match...
		for NodeToConnectTo, ViewName in self.ConnectionDict.items():
			for index, name in self.InputsDict.items():
				if ViewName == name:
					self.JoinViews.setInput(index, NodeToConnectTo)
		# Add the Output pipe...
		output_pipe = nuke.nodes.Output()
		output_pipe.setXYpos(self.JoinViews.xpos(), self.JoinViews.ypos()+200)
		output_pipe.setInput(0, self.JoinViews)
	##-----------------------------------------------------------------------##
	## Utility functions...
	##-----------------------------------------------------------------------##
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
## TESTING...
##-----------------------------------------------------------------------##
def start():
	# Initialize the Class...
	x = JoinAllViewsSwitch()
	# Start the Group node.
	##x.JoinAllViewsSwitchGroup = nuke.nodes.Group(name='JoinAllViewsSwitchGroup')
	x.JoinAllViewsSwitchGroup = nuke.createNode('Group', 'name JoinAllViewsSwitchGroup')
	x.JoinAllViewsSwitchGroup.begin()
	# Run the node functions...
	x._create_Input_nodes()
	x._create_JoinViews_node()
	x._make_JoinViews_inputs_dictionary()
	x._connect_all_inputs_to_all_views()
	# End the Group node.
	x.JoinAllViewsSwitchGroup.end()
####start()