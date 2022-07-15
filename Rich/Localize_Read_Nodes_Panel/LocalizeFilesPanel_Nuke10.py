import nuke
import nukescripts
import os
import shutil
import re
import errno

import _thread

from Node_Tools.Node_Tools import Node_Tools


class LocalizeFilesPanel_Nuke10(nukescripts.PythonPanel):

	def __init__(self):
		'''
		Note: To load the LocalizeFilesPanel_Nuke10 into the Nuke "Pane" menu and make it save with layouts properly,
		drop something like this into your menu.py:
		######################################################
		import Localize_Read_Nodes_Panel.LocalizeFilesPanel_Nuke10
		def addLFPanel():
		    myPanel = Localize_Read_Nodes_Panel.LocalizeFilesPanel.LocalizeFilesPanel_Nuke10()
		    return myPanel.addToPane()
		#### THIS LINE WILL ADD THE NEW ENTRY TO THE PANE MENU...
		nuke.menu('Pane').addCommand('LocalizeFiles', addLFPanel)
		#### THIS LINE WILL REGISTER THE PANEL SO IT CAN BE RESTORED WITH LAYOUTS...
		nukescripts.registerPanel('com.richbobo.LocalizeFiles', addLFPanel)		
		######################################################
		Created by Rich Bobo - 06/27/2017
		richbobo@mac.com
		http://richbobo.com	
		'''
		##---------------------------------------------------------------------------------
		## Initialize the panel...

		nukescripts.PythonPanel.__init__(self, 'Localize Read Nodes', 'com.richbobo.LocalizeFiles')

		# Initialize some variables...
		# Get the string value from the preferences panel knob "localCachePath"...
		self.curLocalCachePath = nuke.toNode('preferences').knob('localCachePath').value()	
		# Get the current localCachePath computed path value...
		self.curCachePathValue = nuke.value('preferences.localCachePath')
		# Initialize the list that will hold all of the Read nodes we want to process...
		self.ReadNodes = []

		##---------------------------------------------------------------------------------
		## Create the panel knobs...

		self.divider13 = nuke.Text_Knob('divider13', '')
		self.divider14 = nuke.Text_Knob('divider14', '')

		self.title0 = nuke.Text_Knob('title0', '')

		self.pauseLocalization = nuke.PyScript_Knob('pauseLocalization', 'PAUSE')
		self.pauseLocalization.setFlag(nuke.STARTLINE)

		self.resumeLocalization = nuke.PyScript_Knob('resumeLocalization', 'RESUME')

		self.status = nuke.Text_Knob('status', '')
		self.status.setFlag(nuke.STARTLINE)

		self.curCachePath = nuke.Text_Knob('curCachePath', '')

		self.divider1 = nuke.Text_Knob('divider1', '')
		self.divider2 = nuke.Text_Knob('divider2', '')		

		self.title1 = nuke.Text_Knob('title1', '')

		self.nodesChoice = nuke.Enumeration_Knob('nodes', 'Nodes: ', ['All Reads', 'Selected Reads'])
		self.nodesChoice.setTooltip('Choose to perform action on all Read nodes or only the selected ones.')

		self.searchScope = nuke.Enumeration_Knob('scope', 'Scope: ', ['Entire Script', 'Current Node Graph Only'])
		self.searchScope.setTooltip('Choose whether to search for Read nodes in the entire script or only in the current node graph (either the main node graph or another group that you are viewing).')

		self.title2 = nuke.Text_Knob('title2', '')

		self.setCacheValueOn = nuke.PyScript_Knob('setCacheValueOn', 'on')
		self.setCacheValueOn.clearFlag(nuke.STARTLINE)

		self.setCacheValueOff = nuke.PyScript_Knob('setCacheValueOff', 'off')

		self.divider3 = nuke.Text_Knob('divider3', '')
		self.divider4 = nuke.Text_Knob('divider4', '')

		self.title3 = nuke.Text_Knob('title3', '')

		self.forceUpdateAll = nuke.PyScript_Knob('forceUpdateAll', 'Force Update ALL Localized')

		self.forceUpdateSelected = nuke.PyScript_Knob('forceUpdateSelected', 'Force Update SELECTED Localized')
		self.forceUpdateSelected.setFlag(nuke.STARTLINE)

		self.divider7 = nuke.Text_Knob('divider7', '')
		self.divider8 = nuke.Text_Knob('divider8', '')

		self.title6 = nuke.Text_Knob('title6', '')

		self.reloadAllFootage = nuke.PyScript_Knob('reloadAllFootage', 'RELOAD ALL FOOTAGE')
		self.reloadAllFootage.setTooltip('Reload all of the Read nodes in this Nuke script')

		##---------------------------------------------------------------------------------
		## Tab Group with disclosure triangle...
		self.begin_tab = nuke.Tab_Knob('', None)
		self.begin_group = nuke.Tab_Knob('groupstart', 'MORE...', nuke.TABBEGINCLOSEDGROUP)

		self.divider9 = nuke.Text_Knob('divider9', '')
		self.divider10 = nuke.Text_Knob('divider10', '')

		self.title7 = nuke.Text_Knob('title7', '')

		self.alwaysUseSourceFilesOn = nuke.PyScript_Knob('alwaysUseSourceFilesOn', 'On')
		self.alwaysUseSourceFilesOn.setFlag(nuke.STARTLINE)

		self.alwaysUseSourceFilesOff = nuke.PyScript_Knob('alwaysUseSourceFilesOff', 'Off')		

		self.sources = nuke.Text_Knob('sources', '')
		self.sources.setFlag(nuke.STARTLINE)

		self.divider5 = nuke.Text_Knob('divider5', '')
		self.divider6 = nuke.Text_Knob('divider6', '')		

		self.title5 = nuke.Text_Knob('title5', '')

		self.deleteUnusedFiles = nuke.PyScript_Knob('deleteUnusedFiles', 'Delete Unused Localized Files')
		self.deleteUnusedFiles.setTooltip('Delete all of the unused localized cache files for Nuke.')

		self.divider11 = nuke.Text_Knob('divider11', '')
		self.divider12 = nuke.Text_Knob('divider12', '')

		self.title8 = nuke.Text_Knob('title8', '')
		self.title9 = nuke.Text_Knob('title9', '')

		self.setCacheValueToAuto = nuke.PyScript_Knob('setCacheValueToAuto', 'from auto-localize path')
		self.setCacheValueToAuto.setFlag(nuke.STARTLINE)

		self.autoLocalizeFromCachePath = nuke.Text_Knob('autoLocalizeFromCachePath', '')

		self.title10 = nuke.Text_Knob('title10', '')
		self.title10.setFlag(nuke.STARTLINE)

		##---------------------------------------------------------------------------------
		## End Tab Group...
		self.end_group = nuke.Tab_Knob('', None, nuke.TABENDGROUP)

		##---------------------------------------------------------------------------------
		## Add knobs to the panel...

		for k in (self.divider13,
		          self.title0,
		          self.pauseLocalization,
		          self.resumeLocalization,
		          self.status,
		          self.curCachePath,
		          self.divider2,
		          self.title1,
		          self.nodesChoice,
		          self.searchScope,
		          self.title2,
		          self.setCacheValueOn,
		          self.setCacheValueOff,
		          self.divider4,		          
		          self.forceUpdateAll,
		          self.forceUpdateSelected,
		          self.divider8,
		          self.reloadAllFootage,
		          self.begin_tab,
		          self.begin_group,
		          self.divider10,
		          self.title7,
		          self.alwaysUseSourceFilesOn,
		          self.alwaysUseSourceFilesOff,
		          self.sources,
		          self.divider6,
		          self.title5,
		          self.deleteUnusedFiles,
		          self.divider12,
		          self.title8,
		          self.setCacheValueToAuto,
		          self.autoLocalizeFromCachePath,
		          self.title9,
		          self.title10,
		          self.end_group
		          ):
			self.addKnob(k)

		##---------------------------------------------------------------------------------
		## Set some Text_Knob values. These are initially set to nothing, so that there is no line printed...

		self.title0.setValue('<FONT COLOR=\"#E55416\">LOCALIZE ENGINE MASTER SWITCH:<\FONT>')

		self.title1.setValue('<FONT COLOR=\"#E55416\">FILTERS:<\FONT>')

		self.title2.setValue('<FONT COLOR=\"#E55416\">NODE SWITCH:<\FONT>')

		self.title7.setValue('ALWAYS USE SOURCES:')

		self.title5.setValue('DELETE UNUSED FILES:')

		self.title8.setValue('READS USE "auto-localize from" PATH:')

		self.title10.setValue('<FONT COLOR=\"#686868\">NOTE: Button uses Read node FILTERS above.<\FONT>')

		self.title9.setValue('<FONT COLOR=\"#686868\">Path set in Preferences.<\FONT>')

	##---------------------------------------------------------------------------------
	## Initialize various status indicators...

		# Initialize the localization engine status indicator, so it shows the current state of localization - paused or running...
		if self.status:
			STATUS = nuke.localization.isLocalizationPaused()
			if STATUS == True:
				self.status.setValue('<FONT COLOR=\"#CB2222\">                      ENGINE IS STOPPED.<\FONT>')
			else:
				self.status.setValue('<FONT COLOR=\"#009D47\">                      ENGINE IS RUNNING...<\FONT>')

		# Initialize the alwaysUseSourceFiles indicator, so it shows the current state ...
		if self.sources:
			SOURCES = nuke.localization.alwaysUseSourceFiles()
			if SOURCES == True:
				self.sources.setValue('<FONT COLOR=\"#E3D108\">                      Always Use Sources is ON<\FONT>')
			else:
				self.sources.setValue('<FONT COLOR=\"#716805\">                      Always Use Sources is OFF<\FONT>')

		# Get the localized cache path and display it...
		if self.curCachePath:
			curCachePathValue = nuke.value('preferences.localCachePath')
			self.curCachePath.setValue('<FONT COLOR=\"#686868\">Localized Cache Path is ' + curCachePathValue + '<\FONT>')

		# Get the "auto-localize from" cache path and display it...
		if self.autoLocalizeFromCachePath:
			localizeFromCachePathValue = nuke.value('preferences.autoLocalCachePath')
			if localizeFromCachePathValue == '':
				localizeFromCachePathValue = 'NOT SET.'
			self.autoLocalizeFromCachePath.setValue('<FONT COLOR=\"#686868\">auto-localize Cache Path is ' + localizeFromCachePathValue + '<\FONT>')

	##---------------------------------------------------------------------------------
	## Node utility functions...

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


	#---------------------------------------------------------------------------------
	# These functions are necessary to prevent threading complaints from Nuke when
	# trying to activate all of the collected nodes' reload buttons at the same time...
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
	#---------------------------------------------------------------------------------


	##---------------------------------------------------------------------------------
	## knobChanged actions...

	def knobChanged(self, knob):
		'''What happens when the buttons are pressed...'''
		# Pause Localization engine...
		if knob is self.pauseLocalization:
			nuke.localization.pauseLocalization()
			if nuke.localization.isLocalizationPaused() == True:
				self.status.setValue('<FONT COLOR=\"#CB2222\">                      ENGINE IS STOPPED.<\FONT>')
		# Resume Localization engine...
		if knob is self.resumeLocalization:
			nuke.localization.resumeLocalization()
			if nuke.localization.isLocalizationPaused() == False:
				self.status.setValue('<FONT COLOR=\"#009D47\">                      ENGINE IS RUNNING...<\FONT>')		
		# Set localizationPolicy knobs of the Read nodes in the self.ReadNodes list to "on"...
		if knob is self.setCacheValueOn:
			self.getReadNodeFilterSettings()            
			if self.ReadNodes:
				for node in self.ReadNodes:
					node.knob("localizationPolicy").setValue("on")
			else:
				print("No Read Nodes Selected...")
				nuke.message("No Read Nodes Selected...")
		# Set localizationPolicy knobs of the Read nodes in the self.ReadNodes list to "off"...
		if knob is self.setCacheValueOff:
			self.getReadNodeFilterSettings()            
			if self.ReadNodes:
				for node in self.ReadNodes:
					node.knob("localizationPolicy").setValue("off")
			else:
				print("No Read Nodes Selected...")
				nuke.message("No Read Nodes Selected...")
		# Set localizationPolicy knobs of the Read nodes in the self.ReadNodes list to "auto" -- the default...
		if knob is self.setCacheValueToAuto:
			if nuke.ask("Set filtered Reads to use auto-localize path?"):
				self.getReadNodeFilterSettings()            
				if self.ReadNodes:
					for node in self.ReadNodes:
						node.knob("localizationPolicy").setValue("auto")
				else:
					print("No Read Nodes Selected...")
					nuke.message("No Read Nodes Selected...")
			else:
				pass
		# Set alwaysUseSourceFiles to On...	
		if knob is self.alwaysUseSourceFilesOn:
			nuke.localization.setAlwaysUseSourceFiles(True)
			if nuke.localization.alwaysUseSourceFiles() == True:
				self.sources.setValue('<FONT COLOR=\"#E3D108\">                      Always Use Sources is ON<\FONT>')
		# Set alwaysUseSourceFiles to Off...	
		if knob is self.alwaysUseSourceFilesOff:
			nuke.localization.setAlwaysUseSourceFiles(False)
			if nuke.localization.alwaysUseSourceFiles() == False:
				self.sources.setValue('<FONT COLOR=\"#716805\">                      Always Use Sources is OFF<\FONT>')
		# Force an update of All localized nodes...
		if knob is self.forceUpdateAll:
			nuke.localization.forceUpdateAll()
		# Force an update of the Selected localized nodes...
		if knob is self.forceUpdateSelected:
			nuke.localization.forceUpdateSelectedNodes()
		# Delete any previously localized files for all Reads whose localization policy has been set to Off...
		if knob is self.deleteUnusedFiles:
			if nuke.ask("Really delete *ALL* of the unused localized file cache?"):
				nuke.localization.clearUnusedFiles()
			else:
				pass
		# Pushes the "Reload" button on all Read nodes in the script...
		if knob is self.reloadAllFootage:
			self._reload_all_footage()
		# Refresh the auto-localize Chache Path status display...
		if knob is self.begin_group:
			localizeFromCachePathValue = nuke.value('preferences.autoLocalCachePath')
			if localizeFromCachePathValue == '':
				self.autoLocalizeFromCachePath.setValue('<FONT COLOR=\"#716805\">auto-localize Cache Path is NOT SET.<\FONT>')
			else:
				self.autoLocalizeFromCachePath.setValue('<FONT COLOR=\"#E3D108\">auto-localize Cache Path is ' + localizeFromCachePathValue + '<\FONT>')


##---------------------------------------------------------------------------------
## Startup the panel Class...

def Create_LocalizeFilesPanel_Nuke10():
	'''Main function to create the LocalizeFiles panel.'''
	p = LocalizeFilesPanel_Nuke10()
	p.show()
