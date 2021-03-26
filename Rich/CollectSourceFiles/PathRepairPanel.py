import nuke
import nukescripts
import os
import itertools
from pprint import pprint
from SourceNodeInfo import NodeInfo
# Need to be able to find the Node_Tools folder, which is relative to this file...
NodeToolsDir = os.path.realpath(os.path.dirname(__file__) + '/..') + '/Node_Tools'
os.sys.path.append(NodeToolsDir)
from Node_Tools.Node_Tools import Node_Tools


#------------------------------------------------------------------------
class PathReplacePanel(nukescripts.PythonPanel):
	''''''
	def __init__(self):
		''''''

		self._result = None

		self.STOP = None

		# Initialize the panel...
		nukescripts.PythonPanel.__init__(self, 'Path Replacement', 'com.richbobo.PathReplacePanel')
		self.setMinimumSize(800,850)

		##---------------------------------------------------------
		self.Progress = nuke.ProgressTask("Repair Broken File Paths:")
		##---------------------------------------------------------

		##---------------------------------------------------------
		self.Progress.setMessage("Getting Nodes...")
		##---------------------------------------------------------
		# Collect all of the source nodes in the script...
		self.AllNodes = nuke.allNodes(recurseGroups=True, group=nuke.root())

		##---------------------------------------------------------
		self.Progress.setMessage("Finding Source Nodes...")
		##---------------------------------------------------------
		# Collect all the source nodes in the script...
		self.sourceNodes = Node_Tools()._find_all_source_nodes(self.AllNodes)

		##---------------------------------------------------------
		self.Progress.setMessage("Finding Errors...")
		##---------------------------------------------------------
		# Gather the source nodes that have broken paths...
		self.SourceNodesWithErrors = Node_Tools()._find_nodes_with_errors(self.sourceNodes)

		#############################################################################################################
		## Sets a default for the minimum number of path segments to build when reassembling paths in the panel...
		## NOTE --->>> If the STOP value is too low, then not all of the broken nodes will have their paths replaced.
		##             It's important to find the sweet spot number for the current OS and network path structure!
		##             At AW, the best value might need to be 4 or 5 or some other value, depending on the original source
		##             directory structure.
		## EXAMPLES:
		##           X:/Whirpool/WHIR-17-001_Jenn-Air_Oberon_Refrigerators ---> 4
		##           N:/Jobs/SGS/SGSC-16-015_Chobani_Mexico_Cups ---> 5
		##           L:/Jobs/Innocean/Archive/Archive_2012/INNO-12-024_2013_Sonata_8-Frame_Int-360/ ---> 7
		##           //ARCHIVE/Archive/Jobs/Innocean/Archive/Archive_2013/INNO-13-039_2014_Azera_8-Interior_Angles/ ---> 9
		##           //blue/Arc/Jobs/Team_Mazda/TEMA-15-014_2016_Mazda-3_MUSA_MYCO_5D_Assets/ --> 7
		##
		## Current Default Values for Armstrong White:
		if os.name == 'nt':
			self.STOP = 4
		elif os.name == 'posix':
			self.STOP = 5
		#############################################################################################################

		# Make a dict that holds all of the nodes, their associated filepath and the filepath broken into a list of its segments...		
		self.NodePathlistDict = self._create_node_filepath_dict(self.SourceNodesWithErrors)
		#print ''
		#print 'self.NodePathlistDict -----'
		#for node, filepath in self.NodePathlistDict.iteritems():
			#print node.name()
			#print filepath	

		# Use the NodePathlistDict dictionary of nodes and paths to create a new dict of the longest common paths...		
		self.ShortestCommonPathDict = self._create_shortest_common_path_dict(self.STOP)
		#print ''
		#print 'self.ShortestCommonPathDict -----'
		#pprint(self.ShortestCommonPathDict)
		#print ''		

		# Make a dictionary of all the shortest common paths and the list of nodes associated with each path...	
		self.shortest_path_dict = self._create_shortest_path_dict()
		#print ''
		#print 'self.shortest_path_dict -----'		
		#for path, nodeslist in self.shortest_path_dict.iteritems():
			#print path
			#print nodeslist	

		# Create the panel knobs...
		self._assemble_panel_knobs(self.STOP)

		##---------------------------------------------------------
		del(self.Progress)
		##---------------------------------------------------------			


	#-----------------------------------------------------------------------------------------

	def _assemble_panel_knobs(self, STOP):
		'''Populate the panel with knobs...'''

		# Make a list of all the knobs to be deleted when the 'Rescan' button is pressed...
		self.knobs_to_delete = []		
		#---------------------------------
		self.PathSegmentsKnob = nuke.Int_Knob('segs_knob', '', 0)
		self.addKnob(self.PathSegmentsKnob)
		self.PathSegmentsKnob.setValue(STOP)
		self.knobs_to_delete.append(self.PathSegmentsKnob)
		#---------------------------------
		DirSegmentsTitle = nuke.Text_Knob('divider1', 'Directory Path Segments', '')
		self.addKnob(DirSegmentsTitle)
		DirSegmentsTitle.clearFlag(nuke.STARTLINE)
		self.knobs_to_delete.append(DirSegmentsTitle)
		#---------------------------------
		RescanButton = nuke.PyScript_Knob('rescan', 'Rescan', '')
		self.addKnob(RescanButton)
		RescanButton.clearFlag(nuke.STARTLINE)
		self.knobs_to_delete.append(RescanButton)
		#---------------------------------
		NodesStats = nuke.Text_Knob('nodes_stats', '', '')
		self.addKnob(NodesStats)
		# Display the total number of nodes with errors and how many we've accounted for with the common paths for replacement...
		#nodes_accounted_for = 0
		#for path, nodeslist in self.shortest_path_dict.iteritems():
			#nodes_accounted_for += len(nodeslist)  
		#NodesStats.setValue(str(nodes_accounted_for) + ' nodes accounted for - out of ' + str(len(self.SourceNodesWithErrors)) + ' Total Nodes')
		NodesStats.setValue(str(len(self.SourceNodesWithErrors)) + ' Total Source Nodes with Errors')
		self.knobs_to_delete.append(NodesStats)
		#---------------------------------
		Divider1 = nuke.Text_Knob('divider1', '', '')
		self.addKnob(Divider1)
		Divider1.setFlag(nuke.STARTLINE)
		self.knobs_to_delete.append(Divider1)
		#---------------------------------
		Divider2 = nuke.Text_Knob('divider2', '', '')
		self.addKnob(Divider2)
		Divider2.setFlag(nuke.STARTLINE)
		self.knobs_to_delete.append(Divider2)		
		#---------------------------------
		# Create a dictionary to hold all the pathknobs and their associated fileknobs...
		self.PathFileKnobs = {}
		# Knob index number for naming...
		num = 1
		for path, nodeslist in self.shortest_path_dict.iteritems():
			try:
				#---------------------------------
				name1 = 'pathknob_' + str(num)
				Knob_string = 'nuke.' + 'Text_Knob' + '(' + "'" + name1 + "'" + ', ' + "'" + "'" + ')'
				Knob = eval(Knob_string)
				self.addKnob(Knob)
				Knob.setFlag(nuke.STARTLINE)
				Knob.setValue(path)
				self.PathFileKnobs[name1] = [Knob, nodeslist[0]]
				self.PathFileKnobs[name1].append(STOP)
				self.knobs_to_delete.append(Knob)
				#---------------------------------
				name2 = 'minusknob_' + str(num)
				Knob_string_minus = 'nuke.' + 'PyScript_Knob' + '(' + "'" + name2 + "'" + ', ' + "'" + "-" + "'" + ')'
				Knob_minus = eval(Knob_string_minus)
				self.addKnob(Knob_minus)
				Knob_minus.clearFlag(nuke.STARTLINE)
				self.knobs_to_delete.append(Knob_minus)
				#---------------------------------				
				name3 = 'plusknob_' + str(num)
				Knob_string_plus = 'nuke.' + 'PyScript_Knob' + '(' + "'" + name3 + "'" + ', ' + "'" + "+" + "'" + ')'
				Knob_plus = eval(Knob_string_plus)
				self.addKnob(Knob_plus)
				Knob_plus.clearFlag(nuke.STARTLINE)
				self.knobs_to_delete.append(Knob_plus)
				#---------------------------------
				name1A = 'nodestotalknob_' + str(num)
				Knob_string = 'nuke.' + 'Text_Knob' + '(' + "'" + name1A + "'" + ', ' + "'" + "'" + ')'
				Knob_NodesTotal = eval(Knob_string)
				self.addKnob(Knob_NodesTotal)
				Knob_NodesTotal.clearFlag(nuke.STARTLINE)				
				Knob_NodesTotal.setValue('          ' + 'NODES: ' + str(len(nodeslist)))
				self.knobs_to_delete.append(Knob_NodesTotal)
				#---------------------------------
				####################################################
				#name4 = 'dirknob_' + str(num)
				#Knob_string2 = 'nuke.' + 'File_Knob' + '(' + "'" + name4 + "'" + ', ' + "'" + "'" + ')'
				#Knob2 = eval(Knob_string2)
				#self.addKnob(Knob2)
				#Knob2.setFlag(nuke.STARTLINE)
				## ...File_Knob value is read-only...
				#self.PathFileKnobs[name4] = Knob2
				#self.knobs_to_delete.append(Knob2)
				#---------------------------------

				name4 = 'dirknob_' + str(num)
				Knob_string2 = 'nuke.' + 'String_Knob' + '(' + "'" + name4 + "'" + ', ' + "'" + "'" + ')'
				Knob2 = eval(Knob_string2)
				self.addKnob(Knob2)
				Knob2.setFlag(nuke.STARTLINE)
				self.PathFileKnobs[name4] = Knob2
				self.knobs_to_delete.append(Knob2)


				name4B = 'dirselectknob_' + str(num)
				Knob_string_dirselect = 'nuke.' + 'PyScript_Knob' + '(' + "'" + name4B + "'" + ', ' + "'" + "Pick Directory" + "'" + ')'
				Knob_dir_select = eval(Knob_string_dirselect)
				self.addKnob(Knob_dir_select)
				Knob_dir_select.clearFlag(nuke.STARTLINE)
				self.PathFileKnobs[name4B] = Knob_dir_select
				self.knobs_to_delete.append(Knob_dir_select)

				####################################################
				#---------------------------------
				name5 = 'dividerknobA_' + str(num)
				Knob_string_dividerA = 'nuke.' + 'Text_Knob' + '(' + "'" + name5 + "'" + ', ' + "'" + "'" + ')'
				Knob_dividerA = eval(Knob_string_dividerA)
				self.addKnob(Knob_dividerA)
				Knob_dividerA.setFlag(nuke.STARTLINE)
				self.knobs_to_delete.append(Knob_dividerA)
				#---------------------------------
				name6 = 'dividerknobB_' + str(num)
				Knob_string_dividerB = 'nuke.' + 'Text_Knob' + '(' + "'" + name6 + "'" + ', ' + "'" + "'" + ')'
				Knob_dividerB = eval(Knob_string_dividerB)
				self.addKnob(Knob_dividerB)
				Knob_dividerB.setFlag(nuke.STARTLINE)
				self.knobs_to_delete.append(Knob_dividerB)
				#---------------------------------				
				num += 1
			except Exception as e:
				print e
		OK_button = nuke.PyScript_Knob('ok', 'OK', '')
		self.addKnob(OK_button)
		self.knobs_to_delete.append(OK_button)

		Cancel_button = nuke.PyScript_Knob('cancel', 'Cancel', '')
		self.addKnob(Cancel_button)
		Cancel_button.clearFlag(nuke.STARTLINE)
		self.knobs_to_delete.append(Cancel_button)
		#print ''
		#print 'self.PathFileKnobs -----'
		#for name, knob in self.PathFileKnobs.iteritems():
			#print name, knob

	def _prompt_for_search_path(self, path_string, startPath=None):
		Path = nuke.getFilename('ORIGINAL PATH ---> %s' % path_string, default=startPath, type = 'open')
		if Path != None:
			Path = os.path.join(Path)
		return Path

	def _delete_panel_knobs(self):
		# Get all the knob objects...		
		for knob in self.knobs_to_delete:		
			try:
				self.removeKnob(knob)
			except:
				print 'Knob %s could not be removed...' % knob.name()

	def _create_node_filepath_dict(self, Nodes):
		'''Make a dictionary of all the nodes in the script and their filepaths...'''
		NodePathlistDict = {}		
		for node in Nodes:
			##---------------------------------------------------------
			self.Progress.setMessage("NodePathlistDict:" + node.name())
			##---------------------------------------------------------

			# Make sure to keep the raw, padded filepath, so we don't evaluate to a single frame...
			path = NodeInfo().get_info(node)['rawKnob']

			if path:
				NodePathlistDict[node] = dict(path=path, parts=self._get_components(path))
			else:
				NodePathlistDict[node] = dict(path='', parts=self._get_components(path))
		return NodePathlistDict

	def _create_shortest_common_path_dict(self, STOP):
		'''Find the shortest matching parent directory for each of the Read nodes' paths...'''
		ShortestCommonPathDict = {}	
		for node, pathcomponents in self.NodePathlistDict.iteritems():
			##---------------------------------------------------------
			try:
				self.Progress.setMessage("ShortestCommonPathDict:" + node.name())
			except:
				self.RescanProgress.setMessage("ShortestCommonPathDict:" + node.name())
			##---------------------------------------------------------			
			path = pathcomponents['path']
			node, COMMON_PATHS_LIST = self._find_common_paths(node, path, STOP)
			try:
				shortest_common_path = min(COMMON_PATHS_LIST, key=len)
				shortest_common_path = shortest_common_path.replace('\\', '/')
			except:
				shortest_common_path = None
			#print ''
			#print 'SHORTEST COMMON PARENT DIRECTORY:'
			#if shortest_common_path :
				#print node.name() + ' --> ' + shortest_common_path
				#print ''
			#else:
				#print node.name() + ' --> '
				#print ''
			#print '================================================================================'
			if shortest_common_path is not None:
				ShortestCommonPathDict[node] = shortest_common_path
			else:
				ShortestCommonPathDict[node] = 'None'
		return ShortestCommonPathDict

	def _find_common_paths(self, node, path, STOP):
		''''''
		node_to_check = node.name()
		COMMON_PATHS_LIST = []
		CurrentString = path
		#print '================================================================================'
		#print node.name() + ':'
		#print CurrentString		
		for NODE, PATHSTRING in self.NodePathlistDict.iteritems():
			PATH = PATHSTRING['path']
			common = self._common_prefix_path(CurrentString, PATH, STOP)
			common = common.replace('\\', '/')
			if common != '':
				if NODE.name() != node_to_check:
					COMMON_PATHS_LIST.append(common)
					#print NODE.name() + ' --> ' + common
			else:
				pass		
				#print NODE.name() + ' --> '
		#print 'COMMON_PATHS_LIST ----> ', COMMON_PATHS_LIST

		return node, COMMON_PATHS_LIST

	def _common_prefix_path(self, path0, path1, STOP):
		''''''
		# Two paths to compare length...
		result = self._get_longest_prefix(self._get_components(path0), self._get_components(path1), STOP)
		if len(result):
			return os.path.join(*result)
		else:
			return ''

	def _get_longest_prefix(self, iter0, iter1, STOP):
		'''Returns the longest common prefix of the two iterables.'''
		longest_prefix = []
		"""
		NOTE: I added STOP, which sets the minimum number of path segments to build. This is hooked into the GUI, so the user can
		tune it to their liking. You can add or subtract the number of segments to one path at a time in the UI. So, for instance, if the
		best STOP value is 5 for all the paths except for one, because it is one directory segment too short, then the user can hit
		buttons [ - ] [ + ] to add or subtract path segments. The STOP values for each path are stored in the NodePathlistDict.
		"""
		COUNTER = 0
		for (elmt0, elmt1) in itertools.izip(iter0, iter1):
			#print 'Compare----> : ', elmt0, elmt1
			if elmt0 != elmt1 and COUNTER >= STOP:
				#print 'BREAK       : ', elmt0, elmt1
				#print 'COUNTER =====>>>', COUNTER
				break
			longest_prefix.append(elmt0)
			COUNTER += 1
		return longest_prefix	

	def _get_components(self, path):
		'''
		Returns the individual components of the given file path string (for the local operating system).
		The returned components, when joined with os.path.join(), point to the same location as the original path.
		REF. for components, longest_prefix and common_prefix_path functions:
		https://stackoverflow.com/questions/21498939/how-to-circumvent-the-fallacy-of-pythons-os-path-commonprefix/36187656#36187656
		'''
		components = []
		# The loop guarantees that the returned components can be os.path.joined with the path separator and point to the same location. ..   
		while True:
			(new_path, tail) = os.path.split(path)  # Works on any platform...
			#print new_path, tail
			if tail:
				components.append(tail)        
			if new_path == path:  # Root (including drive, on Windows) has been reached...
				break
			path = new_path
		components.append(new_path)
		#print 'components *******>>> ', components
		# First component first...
		components.reverse()
		return components

	def _create_shortest_path_dict(self):
		'''Make a dictionary of all the shortest paths and a list of the common nodes.'''
		self.shortest_path_dict = {}
		for node, path in self.ShortestCommonPathDict.iteritems():
			##---------------------------------------------------------
			try:
				self.Progress.setMessage("shortest_path_dict:" + node.name())
			except:
				self.RescanProgress.setMessage("shortest_path_dict:" + node.name())
			##---------------------------------------------------------				
			if path not in self.shortest_path_dict.iterkeys():
				self.shortest_path_dict[path] = []
			if node not in self.shortest_path_dict[path]:
				self.shortest_path_dict[path].append(node)
		return self.shortest_path_dict	

	def _get_parts_for_node_path(self, node):
		'''For the path_to_resize in the shortest_path_dict, get the first node in the list and return all of its path segments.'''
		self.allParts = self.NodePathlistDict[node]['parts']
		return self.allParts

	def _assemble_path_segments(self, newSTOP):
		'''Assemble new path from its constituent parts.'''
		self.path_reassembled = []
		new_parts = self.allParts[0:newSTOP]
		self.path_reassembled = (os.path.join(*new_parts)).replace('\\', '/')
		#print self.path_reassembled
		return self.path_reassembled

	def _modify_path(self, node, operator, NODE_STOP, path_knob_to_get):
		'''Called when the plus or minus buttons are pressed. Assembles the path from components, based on the NODE_STOP value.'''
		# Retrieve all of the path conmponents for reassembly...
		self.all_parts = self._get_parts_for_node_path(node)

		# The newSTOP value is calculated when the '+' or '-' buttons are pressed...
		if operator == 'plus':
			if NODE_STOP+1 <= len(self.NodePathlistDict[node]['parts']):
				newSTOP = NODE_STOP+1
			else:
				newSTOP = len(self.NodePathlistDict[node]['parts'])
		elif operator == 'minus':
			if NODE_STOP-1 >= 1:
				newSTOP = NODE_STOP-1
			else:
				newSTOP = 1

		NODE_STOP = newSTOP

		#print 'THIS IS THE VALUE OF path_knob_to_get >>>>>>>>', path_knob_to_get
		self.PathFileKnobs[path_knob_to_get][2] = NODE_STOP
		#print 'Updated NODE_STOP for ' + node.name() + ' is ' + str(NODE_STOP)

		# Assemble the path components with the newSTOP value...
		self._assemble_path_segments(newSTOP)

	def _get_path_replacements(self):
		# Build dict of the numbered pathknobs, their corresponding numbered dirknobs and the list of nodes to have their paths replaced..
		self.DirReplacements = {}
		for knob_name, knob in self.PathFileKnobs.iteritems():
			if 'pathknob_' in knob_name:
				self.path_knob = knob_name
				#print 'self.path_knob - - - - >> ', self.path_knob
				self.path_knob_path = self.PathFileKnobs[self.path_knob][0].value()
				self.knob_num = knob_name.split('_')[1]
				self.dir_knob = 'dirknob' + '_' + self.knob_num
				#print 'self.dir_knob - - - - >> ', self.dir_knob
				self.dir_knob_path = self.PathFileKnobs[self.dir_knob].value().rstrip('/')
				#print 'self.dir_knob_path ----->', self.dir_knob_path
				self.ref_node = self.PathFileKnobs.get(self.path_knob)[1]
				for path, nodes in self.shortest_path_dict.iteritems():
					if self.ref_node in nodes:
						self.nodes = nodes
						#print 'self.nodes ----', self.nodes
				self.DirReplacements[self.path_knob] = {self.path_knob: self.path_knob_path}
				if self.dir_knob_path:
					self.DirReplacements[self.path_knob][self.dir_knob] = self.dir_knob_path
				else:
					self.DirReplacements[self.path_knob][self.dir_knob] = ''
				self.DirReplacements[self.path_knob]['nodes'] = self.nodes
			else:
				pass
		#print ''
		#print '--- self.DirReplacements ---'
		#for pathknob, data in self.DirReplacements.iteritems():
			#print pathknob
			#print data

	def _replace_paths(self):
		''''''
		for knob_key in self.DirReplacements.iterkeys():
			#print ''
			#if 'pathknob_' in knob_key:
				#print 'STOP value -->>>>> ', self.PathFileKnobs[knob_key][2]
			#print 'knob_key - - - - >> ', knob_key
			knob_key_path = self.DirReplacements[knob_key][knob_key]
			#print 'knob_key_path ----->', knob_key_path
			knob_num = knob_key.split('_')[1]
			dir_knob = 'dirknob' + '_' + knob_num
			#print 'dir_knob - - - - >> ', dir_knob
			dir_knob_path = self.DirReplacements[knob_key][dir_knob]			
			#print 'dir_knob_path ----->', dir_knob_path		
			nodes = self.DirReplacements[knob_key]['nodes']
			#print 'nodes ++++++>>> ', nodes

			for node in nodes:
				#print 'node =====>>> ', node.name()
				Filepath = self.NodePathlistDict[node]['path']
				#print 'Filepath --->>>> ', Filepath
				if dir_knob_path != '':
					NEW_Filepath = Filepath.replace(knob_key_path, dir_knob_path)
					#print 'NEW_Filepath --->>>> ', NEW_Filepath
				else:
					NEW_Filepath = None

				if NEW_Filepath is not None:
					if NEW_Filepath == Filepath:
						print node.name() + ' FAIL'
					else:
						try:
							node['file'].setValue(NEW_Filepath)
							#print node.name() + ' SUCCESS'
						except:
							node['vfield_file'].setValue(NEW_Filepath)
							#print node.name() + ' SUCCESS'
				else:
					print node.name() + ' PASS - No dir. replacement selected.'
					pass

		# Recheck to see if there are still nodes with errors...
		self.ErrorNodes = Node_Tools()._find_nodes_with_errors(self.sourceNodes)
		if self.ErrorNodes:
			error_nodes = [node.name() for node in self.ErrorNodes]
			errors = str(error_nodes)
			message = 'There are still nodes with broken file path links:\n\n' + errors + '\n\n\nCheck for non-existant paths or other errors.\n\nYou can run repair nodes again, if necessary.'
			nuke.message(message)
			print message
			# Return False for when this is used with CollectSourceFiles...
			return False
		else:
			message = 'All broken paths repaired.'
			nuke.message(message)
			print message
			# Return True for when this is used with CollectSourceFiles...
			return True

	##-----------------------------------------------------------------------------------------
	## UI Buttons...
	##-----------------------------------------------------------------------------------------
	def knobChanged(self, knob):
		''''''
		if 'dirselectknob_' in knob.name():
			path_knob_to_get = 'pathknob' + '_' + knob.name().split('_')[1]
			path_knob = self.PathFileKnobs.get(path_knob_to_get)[0]
			pathknob_path = path_knob.value()
			#print ''
			#print 'pathknob_path --> ', pathknob_path	
			dir_knob_to_get = 'dirknob' + '_' + knob.name().split('_')[1]
			#print ''
			#print 'dir_knob_to_get --> ', dir_knob_to_get
			dir_knob = self.PathFileKnobs.get(dir_knob_to_get)
			#print ''
			#print 'dir_knob --> ', dir_knob
			#print ''
			SelectedPath = self._prompt_for_search_path(pathknob_path, startPath=dir_knob.value())
			#print ''
			#print 'SelectedPath --> ', SelectedPath
			if SelectedPath is not None:
				dir_knob.setValue(SelectedPath)

		if 'rescan' in knob.name():
			##---------------------------------------------------------
			self.RescanProgress = nuke.ProgressTask("Rescan For Common Paths:")
			##---------------------------------------------------------			
			# Update the global STOP value...
			STOP = self.PathSegmentsKnob.value()
			for knobname, valueslist in self.PathFileKnobs.iteritems():
				if 'pathknob_' in knobname:
					self.PathFileKnobs[knobname][2] = STOP
			# Use the NodePathlistDict dictionary of nodes and paths to create a new dict of the longest common paths...
			self.ShortestCommonPathDict = self._create_shortest_common_path_dict(STOP)
			# Make a dictionary of all the shortest common paths and the list of nodes associated with each path...
			self.shortest_path_dict = self._create_shortest_path_dict()			
			#print ''
			#print 'self.shortest_path_dict -----'		
			#for path, nodeslist in self.shortest_path_dict.iteritems():
				#print path
				#print nodeslist			
			self._delete_panel_knobs()
			self._assemble_panel_knobs(STOP)
			##---------------------------------------------------------
			del(self.RescanProgress)
			##---------------------------------------------------------				

		if 'plusknob' in knob.name():
			NODE_STOP = self.PathSegmentsKnob.value()
			path_knob_to_get = 'pathknob' + '_' + knob.name().split('_')[1] 
			path_knob = self.PathFileKnobs.get(path_knob_to_get)[0]
			node = self.PathFileKnobs.get(path_knob_to_get)[1]
			NODE_STOP = self.PathFileKnobs.get(path_knob_to_get)[2]
			self._modify_path(node, 'plus', NODE_STOP, path_knob_to_get)
			path_knob.setValue(self.path_reassembled)

		if 'minusknob' in knob.name():
			NODE_STOP = self.PathSegmentsKnob.value()
			path_knob_to_get = 'pathknob' + '_' + knob.name().split('_')[1]
			path_knob = self.PathFileKnobs.get(path_knob_to_get)[0]
			node = self.PathFileKnobs.get(path_knob_to_get)[1]
			NODE_STOP = self.PathFileKnobs.get(path_knob_to_get)[2]
			self._modify_path(node, 'minus', NODE_STOP, path_knob_to_get)
			path_knob.setValue(self.path_reassembled)

		if 'ok' in knob.name():
			self._result = True
			return self.finishModalDialog(True)

		if 'cancel' in knob.name():
			self._result = False
			return self.finishModalDialog(False)		

############################################
## Run it.
############################################
def start_panel():
	''''''
	# Collect all of the source nodes in the script...
	task = nuke.ProgressTask("Initial Error Check:")
	task.setMessage("Getting Nodes...")
	AllNodes = nuke.allNodes(recurseGroups=True, group=nuke.root())

	# Collect all the source nodes in the script...
	task.setMessage("Finding Source Nodes...")
	sourceNodes = Node_Tools()._find_all_source_nodes(AllNodes)

	# Gather the source nodes that have broken paths...
	task.setMessage("Finding Nodes with Errors...")
	SourceNodesWithErrors = Node_Tools()._find_nodes_with_errors(sourceNodes)

	del(task)

	# Ask the user if they want to repair the broken links...
	if SourceNodesWithErrors:
		if nuke.ask("Do you want to repair nodes with broken file links?"):
			panel = PathReplacePanel()
			result = panel.showModal()
			if panel._result == True:
				panel._get_path_replacements()
				if panel._replace_paths():
					return True
				else:
					return False
	else:
		nuke.message('No broken links found.')
		return True
