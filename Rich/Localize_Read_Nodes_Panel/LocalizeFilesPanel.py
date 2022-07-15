import nuke
import nukescripts
import os
import shutil
import re
import errno

import _thread

from Node_Tools.Node_Tools import Node_Tools


class LocalizeFilesPanel(nukescripts.PythonPanel):
	def __init__(self):
		'''
		Note: To load the LocalizeFilesPanel into the Nuke "Pane" menu and make it save with layouts properly,
		drop something like this into your menu.py:
		######################################################
		import Localize_Read_Nodes_Panel.LocalizeFilesPanel
		def addLFPanel():
		    myPanel = Localize_Read_Nodes_Panel.LocalizeFilesPanel.LocalizeFilesPanel()
		    return myPanel.addToPane()
		#### THIS LINE WILL ADD THE NEW ENTRY TO THE PANE MENU...
		nuke.menu('Pane').addCommand('LocalizeFiles', addLFPanel)
		#### THIS LINE WILL REGISTER THE PANEL SO IT CAN BE RESTORED WITH LAYOUTS...
		nukescripts.registerPanel('com.richbobo.LocalizeFiles', addLFPanel)		
		######################################################
		This panel is designed to work best with the LocaliseThreaded.py script, written by Frank Rueter.
		His script replaces and is a re-working of the nuke.localiseFiles() method, built into Nuke.
		Frank's code improves on the localise files function by making it multi-threaded - allowing the user
		to continue working while it copies the files to the local disk. Plus, it speeds up copying by virtue of multi-threading.
		The LocaliseThreaded script is freely available for download on nukepedia.com.
		######################################################
		Created by Rich Bobo - 09/24/2014
		richbobo@mac.com
		http://richbobo.com	
		'''
		# Initialize the panel.
		nukescripts.PythonPanel.__init__(self, 'Localize Read Nodes', 'com.richbobo.LocalizeFiles')

		# Initialize some variables...
		# The current NUKE_TEMP_DIR directory value...
		self.NUKE_TEMP_DIR = os.environ['NUKE_TEMP_DIR']
		# This is the Nuke default path string that is in the Preferences "localise to" field for all OSes... Note the British spelling of "localise", with an "s".
		self.localCachePath = '[getenv NUKE_TEMP_DIR]/localise'
		# Get the string value from the preferences panel knob "localCachePath"...
		self.curLocalCachePath = nuke.toNode('preferences').knob('localCachePath').value()	
		# Get the current localCachePath computed path value...
		self.curCachePathValue = nuke.value('preferences.localCachePath')
		# Initialize the list that will hold all of the Read nodes we want to process...
		self.ReadNodes = []


		# Create panel knobs...
		self.title1 = nuke.Text_Knob('title1', 'FILTER READ NODES:')

		self.nodesChoice = nuke.Enumeration_Knob('nodes', 'Nodes: ', ['All Reads', 'Selected Reads'])
		self.nodesChoice.setTooltip('Choose to perform action on all Read nodes or only the selected ones.')

		self.searchScope = nuke.Enumeration_Knob('scope', 'Scope: ', ['Entire Script', 'Current Node Graph Only'])
		self.searchScope.setTooltip('Choose whether to search for Read nodes in the entire script or only in the current node graph (either the main node graph or another group that you are viewing).')

		self.title2 = nuke.Text_Knob('title2', 'LOCALIZE NODES:')

		self.doLocalize = nuke.PyScript_Knob('localize_files', 'START')
		self.doLocalize.setTooltip('Start copying files to the local machine. Select the number of CPU threads to use. Since processing is independent, you can continue working while files are copied. You can move the process status window out of the way - just don\'t close it. Automatically sets the Read nodes\' cache value to "always".')
		self.doLocalize.setFlag(nuke.STARTLINE)

		self.divider1 = nuke.Text_Knob('divider1', '')
		self.divider2 = nuke.Text_Knob('divider2', '')

		self.title3 = nuke.Text_Knob('title3', 'SET NODE CACHE VALUE:')

		self.setCacheValueToAuto = nuke.PyScript_Knob('setCacheValueToAuto', 'auto')
		self.setCacheValueToAuto.clearFlag(nuke.STARTLINE)

		self.setCacheValueToAlways = nuke.PyScript_Knob('setCacheValueToAlways', 'always')
		self.setCacheValueToAlways.clearFlag(nuke.STARTLINE)

		self.setCacheValueToNever = nuke.PyScript_Knob('setCacheValueToNever', 'never')

		self.title4 = nuke.Text_Knob('title4', '(uses Read node filters above)')

		self.divider3 = nuke.Text_Knob('divider3', '')
		self.divider4 = nuke.Text_Knob('divider4', '')

		self.title5 = nuke.Text_Knob('title5', 'DELETE *ALL* LOCALIZED FILE CACHE:')

		self.deleteLocalizedFiles = nuke.PyScript_Knob('deleteLocalizedFiles', 'DELETE')
		self.deleteLocalizedFiles.setTooltip('Delete ALL of the localized cache files for Nuke. That means for every script that has been localized. Just sayin\'...')

		self.divider5 = nuke.Text_Knob('divider5', '')
		self.divider6 = nuke.Text_Knob('divider6', '')		

		self.title6 = nuke.Text_Knob('title6', 'RELOAD ALL FOOTAGE:')

		self.reloadAllFootage = nuke.PyScript_Knob('reloadAllFootage', 'RELOAD ALL FOOTAGE')
		self.reloadAllFootage.setTooltip('Reload all of the Read nodes in this Nuke script')		

		# Add knobs to the panel...
		for k in (self.title1, self.nodesChoice, self.searchScope, self.title2, self.doLocalize, self.divider1, self.divider2, self.title6, self.reloadAllFootage, self.divider5, self.divider6, self.title3, self.setCacheValueToAuto, self.setCacheValueToAlways, self.setCacheValueToNever, self.title4, self.divider3, self.divider4, self.title5, self.deleteLocalizedFiles,):
			self.addKnob(k)


	def recursiveFindNodes(self, nodeClass, startNode):
		'''Recursive node class find method from Drew Loveridge.
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
		'''Collect all of the "Read" nodes in the entire script, including all Groups.'''
		read_nodes = []
		for n in self.recursiveFindNodes("Read", nuke.root()):
			read_nodes.append(n)
		return read_nodes


	def getAllSelectedReadNodes(self, topLevel):
		'''
		Recursively return all the Selected Read nodes in the script, starting at topLevel.
		Looks in all groups. Default topLevel to use is nuke.root()
		'''
		# Get all of the nodes in the script...
		allNodes = nuke.allNodes(group=topLevel)
		for n in allNodes:
			allNodes = allNodes + self.getAllSelectedReadNodes(n)
		# Get just the ones that are selected...
		allSelectedNodes = []
		for n in allNodes:
			if n.knob('selected').value() == True and n.Class() == "Read":
				allSelectedNodes.append(n)
		return allSelectedNodes                  


	def getReadNodeFilterSettings(self):
		'''Look at the knob selections and set the Read node selection...'''
		if self.searchScope.value() == "Entire Script":
			if self.nodesChoice.value() == "All Reads":
				self.ReadNodes = self.collectReadNodes()
			elif self.nodesChoice.value() == "Selected Reads":
				self.ReadNodes = self.getAllSelectedReadNodes(nuke.root()) 
		elif self.searchScope.value() == "Current Node Graph Only":
			if self.nodesChoice.value() == "All Reads":
				self.ReadNodes = [n for n in nuke.allNodes() if n.Class() == "Read"]
			elif self.nodesChoice.value() == "Selected Reads":
				self.ReadNodes = [n for n in nuke.allNodes() if n.Class() == "Read" and n.knob('selected').value() == True]		


	def getTargetDir(self, filePath):
		'''
		NOTE: This method is borrowed from Frank Rueter's LocaliseThreaded.py code.
		I'm using it to compute the localized path, so I can check its length for Windows (256 char. limit)... RKB.
		#
		Get the target directory for filePath based on Nuke's cache preferences and localisation rules.
		'''
		parts = filePath.split('/') # NUKE ALREADY CONVERTS BACK SLASHES TO FORWARD SLASHES ON WINDOWS
		if not filePath.startswith('/'):
			# DRIVE LETTER
			driveLetter = parts[0]
			parts = parts [1:] # REMOVE DRIVE LETTER FROM PARTS BECAUSE WE ARE STORING IT IN PREFIX
			prefix =  driveLetter.replace(':', '_')
		else:
			# REPLACE EACH LEADING SLASH WITH UNDERSCORE
			# GET LEADING SLASHES
			slashCountRE = re.match('/+', filePath)
			slashCount = slashCountRE.span()[1]
			#slashCount = len([i for i in parts if not i])
			root = [p for p in parts if p][0]
			parts = parts[slashCount + 1:] # REMOVE SLASHES AND ROOT FROM PARTS BECAUSE WE ARE STORING THOSE IN PREFIX
			prefix = '_' * slashCount + root
		# RE-ASSEMBLE TO LOCALISED PATH
		parts.insert(0, prefix)
		parts = self.curCachePathValue.split('/') + parts
		return '/'.join(parts[:-1]) # RETURN LOCAL DIRECTORY USING FORWARD SLASHES TO BE CONSISTENT WITH NUKE


	def check_localCachePath(self):
		'''Check if the localCachePath value is default setting and, if not, set it to the to the default value...'''
		if self.curLocalCachePath == self.localCachePath:
			pass
		elif self.curLocalCachePath != self.localCachePath:
			if nuke.ask("The localCachePath is not set to the default:\n %s \nWould you like to change it back to the default value?" % self.localCachePath):
				nuke.toNode('preferences').knob('localCachePath').setValue(self.localCachePath)
				## Save an updated version of the preferences file, so the new localize files path is persistent across Nuke sessions...
				##if nuke.ask("About to save over the current Nuke Preferences file with an updated Localize Files cache path...\n\nThis should not be a problem - unless you have temporarily changed some preference settings that you do not wish to save at this time.\n\n...OK to save the Preferences File?"):
					##self.save_NukePrefsFile()
				##else:
					##nuke.message("Preferences File Not Saved.\nNot Localizing Files.\n\nExiting...")
					##return				
			else:
				nuke.message("OK. localCachePath value not changed.")


	def save_NukePrefsFile(self):
		'''Save a new version of the Nuke preferences file.'''
		prefs = nuke.toNode('preferences')
		prefs_file_ver = str(nuke.NUKE_VERSION_MAJOR) + "." + str(nuke.NUKE_VERSION_MINOR)
		preference_file = os.path.expandvars('$HOME/.nuke/preferences' + prefs_file_ver + '.nk')        
		# Generate the prefs file contents and append some standard stuff about the node that needs to be there...
		# NOTE: Leave the formatting in triple-double quotes below, as is. If the lines are tabified, it adds extra characters to the output file...
		# I know, I know...it looks ugly!
		preferences_code = """Preferences {
inputs 0
name Preferences %s
} """ % prefs.writeKnobs( nuke.WRITE_USER_KNOB_DEFS | nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_SCRIPT | nuke.TO_VALUE )
		# Write the prefs file...
		f = open( preference_file , 'w' )
		f.write( preferences_code )
		f.close()


	def check_destPathLongerThan256Chars(self):
		'''Check for and eliminate any selected nodes with local destination pathnames longer than 256 characters...
		Only necessary for Windows OS.'''
		if self.ReadNodes:
			for node in self.ReadNodes:
				filePath = node.knob("file").value()
				destPath = self.getTargetDir(filePath)
				localFile = os.path.join(destPath, os.path.basename(filePath))
				if len(localFile) > 256:
					# Add the node to the list of "bad" nodes to report to the user///
					self.skipped_nodes.append(node)
					self.skipped_node_names.append(node.name())
					print(node.name(), " has a destination path longer than 256 characters. Skipping...")
				else:
					print(node.name(), " is OK.")

			# Remove any of the skipped nodes we found...
			for node in self.skipped_nodes:
				if node in self.ReadNodes:
					try:
						self.ReadNodes.remove(node)
					except ValueError:
						pass


	def do_Localize(self):
		'''Run some checks and execute nuke.localiseFiles...'''
		self.skipped_nodes = []
		self.skipped_node_names = []

		# Run the localCachePath checker that looks for the default localCachePath value...
		#### This turned out to be annoying when using a local SSD drive as a cache location...
		####self.check_localCachePath()

		# Get the current Read node filter knob settings to set the list of self.ReadNodes to process...
		self.getReadNodeFilterSettings()

		if self.ReadNodes:
			# If Windows OS, check for local destination pathname longer than 256 characters. Remove those Reads from list...
			if os.name == 'nt':
				self.check_destPathLongerThan256Chars()

			# Collect the file paths for each Read node we'll process...
			file_knobs_list = []
			for node in self.ReadNodes:
				file_knob = node.knob("file")
				file_knobs_list.append(file_knob)
				file_knob.setValue(nuke.filename(node))

			# Do the actual localizing of Read nodes, using the Nuke method... Although, I am replacing it with Frank Rueter's LocaliseThreaded version.
			nuke.localiseFiles(file_knobs_list)

			# Set cacheLocal knobs of the Read nodes in the self.ReadNodes list to "always"...
			for node in self.ReadNodes:
				node.knob("cacheLocal").setValue("always")
		else:
			print("No Read Nodes Selected...")
			nuke.message("No Read Nodes Selected...")

		# Report any nodes that were skipped, due to paths longer than 256 characters... Windows only.
		if self.skipped_nodes:
			print("Skipping these nodes, since the local stored file path would be longer than 256 characters:\n ", self.skipped_node_names)
			nuke.message("Some Read nodes will be skipped, since the local stored file path would be longer than 256 characters.\n %s " % self.skipped_node_names)


	def remove_localCacheFiles(self):
		'''Method to delete all the localy cached files to free up some disk space...'''
		# Get the current localCachePath value...
		dir_to_remove = self.curCachePathValue
		# Build the directory paths to delete...
		for filename in os.listdir(dir_to_remove):
			filepath = os.path.join(dir_to_remove, filename)
			filepath = filepath.replace('\\', '/')
			if os.path.exists(filepath):
				try:
					shutil.rmtree(filepath)
					print("Cache Removed.")					
				except:
					print("ERROR: Could not remove cache files.")
					nuke.message("ERROR: Could not remove cache files.\n\nWait 5 or 10 seconds and try again.")


	def _clearFlagBeforeRemove(self):
		'''Try to make sure the local file cache is not being accessed before attempting to remove it.'''
		# Collect all of the Read nodes in the script and turn off local caching, since we'll be deleting it.
		self.ReadNodes = self.collectReadNodes()
		if self.ReadNodes:
			for node in self.ReadNodes:
				node.knob("cacheLocal").setValue("never")
			else:
				pass


	##-------------------------------------------------
	## These two functions are necessary to prevent threading complaints from Nuke
	## when trying to activate all of the collected nodes' reload buttons at the same time...
	def _do_reload(self, node):
		node.knob('reload').execute()

	def _do_reload_with_thread(self, node):
		nuke.executeInMainThread(self._do_reload, (node,))
		print(node.name() + ' reloaded')

	def _reload_all_footage(self):
		'''Runs the threaded function, _do_reload_with_thread, on a list of nodes (gathered inside this method)...'''
		self.AllNodes = Node_Tools()._get_all_nodes()
		self.sourceNodes = Node_Tools()._find_all_source_nodes(self.AllNodes)	
		for node in self.sourceNodes:
			# Push the reload button on all of the selected nodes.
			# Do it as a thread, though, because Nuke complains saying,
			# "I'm already executing something..."
			_thread.start_new_thread(self._do_reload_with_thread, (node,))
	##-------------------------------------------------


	def knobChanged(self, knob):
		'''Press the buttons.'''
		if knob is self.doLocalize:
			self.do_Localize()
		if knob is self.reloadAllFootage:
			self._reload_all_footage()
		if knob is self.setCacheValueToAuto:
			self.getReadNodeFilterSettings()            
			# Set cacheLocal knobs of the Read nodes in the self.ReadNodes list to "auto" -- the default...
			if self.ReadNodes:
				for node in self.ReadNodes:
					node.knob("cacheLocal").setValue("auto")
			else:
				print("No Read Nodes Selected...")
				nuke.message("No Read Nodes Selected...")  
		if knob is self.setCacheValueToAlways:
			self.getReadNodeFilterSettings()            
			# Set cacheLocal knobs of the Read nodes in the self.ReadNodes list to "always"...
			if self.ReadNodes:
				for node in self.ReadNodes:
					node.knob("cacheLocal").setValue("always")
			else:
				print("No Read Nodes Selected...")
				nuke.message("No Read Nodes Selected...")
		if knob is self.setCacheValueToNever:
			self.getReadNodeFilterSettings()            
			# Set cacheLocal knobs of the Read nodes in the self.ReadNodes list to "auto" -- the default...
			if self.ReadNodes:
				for node in self.ReadNodes:
					node.knob("cacheLocal").setValue("never")
			else:
				print("No Read Nodes Selected...")
				nuke.message("No Read Nodes Selected...")
		if knob is self.deleteLocalizedFiles:
			if nuke.ask("Remove all of the localized file cache?"):
				self._clearFlagBeforeRemove()
				nuke.executeInMainThread(self.remove_localCacheFiles, ())
			else:
				#nuke.message("Aborted. Not removing any files.")
				return			


def Create_LocalizeFilesPanel():
	'''Main function to create the LocalizeFiles panel.'''
	p = LocalizeFilesPanel()
	p.show()

