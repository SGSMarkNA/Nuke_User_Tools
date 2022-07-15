import nuke

class PathChangeTools(object):

	def __init__(self):

		self.read_nodes = []
		self.readgeo2_nodes = []
		self.write_nodes = []
		self.collected_nodes = []
		ReadNodePaths = []

	def recursiveFindNodes(self, nodeClass, startNode):
		'''Recursive node class find function from Drew Loveridge.
		   EXAMPLE USAGE:
		        for d in recursiveFindNodes("Dot", nuke.root()):
		            print d.name()
		'''
		if startNode.Class() == nodeClass:
			yield startNode
		elif isinstance(startNode, nuke.Group):
			for child in startNode.nodes():
				for foundNode in self.recursiveFindNodes(nodeClass, child):
					yield foundNode

	def collectReadNodes(self):
		# Collect all of the "Read" nodes...
		for n in self.recursiveFindNodes("Read", nuke.root()):
			self.read_nodes.append(n)
		for node in self.read_nodes:
			node.knob('selected').setValue(True)

	def collectReadGeo2Nodes(self):
		# Collect all of the "ReadGeo2" nodes...
		for n in self.recursiveFindNodes("ReadGeo2", nuke.root()):
			self.readgeo2_nodes.append(n)        
		for node in self.readgeo2_nodes:
			node.knob('selected').setValue(True)

	def collectWriteNodes(self):
		# Collect all of the "Write" nodes...        
		for n in self.recursiveFindNodes("Write", nuke.root()):
			self.write_nodes.append(n)      
		for node in self.write_nodes:
			node.knob('selected').setValue(True)

	def print_node_collection(self):
		self.collected_nodes = self.read_nodes + self.readgeo2_nodes + self.write_nodes
		list = [n.name() for  n in self.collected_nodes]
		print(list)	

	def getAllNodes(self, topLevel):
		'''
		Recursively return all nodes starting at topLevel.
		Looks in all groups. Default topLevel to use is nuke.root()
		'''
		allNodes = nuke.allNodes(group=topLevel)
		for n in allNodes:
			allNodes = allNodes + getAllNodes(n)
		return allNodes

	def deselectAllNodes(self):
		allNodes = self.getAllNodes(nuke.root())
		for n in allNodes:
			n.knob('selected').setValue(False)

	def selectAllNodes(self):
		allNodes = self.getAllNodes(nuke.root())
		for n in allNodes:
			n.knob('selected').setValue(True)

	def listReadNodePaths(self):
		for p in self.read_nodes:
			path = p.knob('file').value()
			print(path)

	## 
	def findNodesWithFileKnob(self): 
		selection = nuke.selectedNodes() 
		if not selection: 
			nuke.message('No nodes selected') 
			return 
		if nuke.ask('Print nodes with file knobs?'): 
			for node in selection:
				if 'file' in node.knobs():
					print(node.name())

	def findNodesWithProxyKnob(self): 
		selection = nuke.selectedNodes() 
		if not selection: 
			nuke.message('No nodes selected') 
			return 
		if nuke.ask('Print nodes with proxy knobs?'): 
			for node in selection:
				if 'proxy' in node.knobs():
					print(node.name())    

##-------------------------------------------------------------##
#x = PathChangeTools()
#x.collectReadNodes()
#x.collectReadGeo2Nodes()
#x.collectWriteNodes()
#x.print_node_collection()
#x.getAllNodes(nuke.root())
#x.deselectAllNodes()
#x.selectAllNodes()
#x.listReadNodePaths()
#x.findNodesWithfileKnob()
#x.findNodesWithProxyKnob()


#[n.name() for n in collected_nodes]

#n = nuke.selectedNode()
#n.Class()