#### These disconnect all upstream or downstream connected nodes.

def Disconnect_All_Dependencies(node):
	'''Disconnect all upstream dependency connections.'''
	while len(node.dependencies()):
		for i in range(node.inputs()):
			node.setInput(i, None)

def Disconnect_All_Dependent(node):
	'''Disconnect all downstream connections.'''
	for n in node.dependent():
		for i in range(n.inputs()):
			if n.input(i) == node:
				n.setInput(i, None)