import nuke
import nukescripts
import sys
import os

import Node_Tools.Node_Tools
NodeTools = Node_Tools.Node_Tools.Node_Tools()

# Global list of node classes that this class can operate on...
global NodeClasses
NodeClasses = ['RotoPaint', 'Roto']


class RotoNodesViewsSelectionPanel(nukescripts.PythonPanel):

	def __init__(self):
		'''
		--------------------------------------------------------------------------------------------------
		A Brief Explanation of Functionality:
		--------------------------------------------------------------------------------------------------
		A RotoPaint and Roto node view name filtering selection panel.

		Created by Rich Bobo - 02/14/2018
		richbobo@mac.com
		http://richbobo.com
		--------------------------------------------------------------------------------------------------
		'''
		nukescripts.PythonPanel.__init__(self, 'Roto Nodes Shapes Views Selector', 'com.richbobo.RotoNodesViewsSelectionPanel')
		#self.setMinimumSize(500, 500)

		# Create the knobs...
		self.BeginGroup = nuke.Text_Knob('BeginGroup', 'NODE FILTERING:')
		self.nodesChoice = nuke.Enumeration_Knob('nodes', 'Nodes: ', ['All', 'Selected'])
		self.nodesChoice.setTooltip('Choose to perform action on All nodes or only the Selected ones.')
		self.searchScope = nuke.Enumeration_Knob('scope', 'Scope: ', ['Entire Script', 'Current Node Graph Only'])
		self.searchScope.setTooltip('Choose whether to perform the action on all the filtered nodes in the entire script or only on the current node graph (either the main node graph or another group that you are viewing).')
		self.info = nuke.Text_Knob('info', '', 'NOTE: This panel affects ALL of the Roto/RotoPaint nodes selected by the filters above.\nThe views are set for every shape of the selected nodes in the VIEW SELECTION section below.' )
		# Add knobs to the panel...
		self.addKnob(self.BeginGroup)
		self.addKnob(self.nodesChoice)
		self.addKnob(self.searchScope)
		self.addKnob(self.info)
		self.info.setFlag( nuke.READ_ONLY )

		#-------------------------------------------------------------------------------------------------
		self.viewsKnob = nuke.MultiView_Knob('views')
		self.addKnob(self.viewsKnob)
		self.viewsKnob.setValue((' ').join(nuke.views()))
		# Set the knob to be Invisible.
		self.viewsKnob.setFlag(0x00040000)
		#-------------------------------------------------------------------------------------------------

		self.newline2_knob = nuke.Text_Knob("")
		self.addKnob(self.newline2_knob)

		self.BeginGroup2 = nuke.Text_Knob('BeginGroup2', 'VIEW SELECTION:')
		self.addKnob(self.BeginGroup2)

		self.selectNone_knob = nuke.PyScript_Knob('select_none', 'SELECT NONE')
		self.addKnob(self.selectNone_knob)

		self.selectAll_knob= nuke.PyScript_Knob('select_all', 'SELECT ALL')
		self.addKnob(self.selectAll_knob)

		self.view_selector_knob = nuke.SceneView_Knob('pick_a_view', 'Selected Views', nuke.views())
		self.addKnob(self.view_selector_knob)

		self.newline3_knob = nuke.Text_Knob("")
		self.addKnob(self.newline3_knob)

		self.FilteringTitle_knob = nuke.Text_Knob('filtering_title', 'VIEW FILTERING:')
		self.addKnob(self.FilteringTitle_knob)

		self.newline7_knob = nuke.Text_Knob("")
		self.addKnob(self.newline7_knob)
		#-----------------------------------------------------------------------------------------------------
		self.StartsWith_Boolean_selector_knob = nuke.Enumeration_Knob('startswith_boolean', 'Starts With', ['ANY'])
		self.addKnob(self.StartsWith_Boolean_selector_knob)
		self.StartsWith_Boolean_selector_knob.setFlag(nuke.STARTLINE)		

		self.partStartsWith_knob = nuke.String_Knob('startswith', '')
		#self.partStartsWith_knob = nuke.String_Knob('startswith', 'Starts With ANY ')
		self.addKnob(self.partStartsWith_knob)		
		self.partStartsWith_knob.setFlag(nuke.KNOB_CHANGED_RECURSIVE)
		self.partStartsWith_knob.clearFlag(nuke.KNOB_CHANGED_RECURSIVE)
		self.partStartsWith_knob.clearFlag(nuke.STARTLINE)			
		#-----------------------------------------------------------------------------------------------------	
		self.Contains_Boolean_selector_knob = nuke.Enumeration_Knob('contains_boolean', 'Contains', ['ALL', 'ANY'])
		self.addKnob(self.Contains_Boolean_selector_knob)
		self.Contains_Boolean_selector_knob.setFlag(nuke.STARTLINE)

		self.partContains_knob = nuke.String_Knob('contains', '')
		self.addKnob(self.partContains_knob)
		self.partContains_knob.clearFlag(nuke.KNOB_CHANGED_RECURSIVE)
		self.partContains_knob.clearFlag(nuke.STARTLINE)
		#-----------------------------------------------------------------------------------------------------
		self.EndsWith_Boolean_selector_knob = nuke.Enumeration_Knob('endswith_boolean', 'Ends With', ['ANY'])
		self.addKnob(self.EndsWith_Boolean_selector_knob)
		self.EndsWith_Boolean_selector_knob.setFlag(nuke.STARTLINE)		

		self.partEndsWith_knob = nuke.String_Knob('endswith', '')	
		#self.partEndsWith_knob = nuke.String_Knob('endswith', 'Ends With ANY ')		
		self.addKnob(self.partEndsWith_knob)
		self.partEndsWith_knob.clearFlag(nuke.STARTLINE)		
		#-----------------------------------------------------------------------------------------------------
		self.newline4_knob = nuke.Text_Knob("")
		self.addKnob(self.newline4_knob)

		self.clear_filters_knob = nuke.PyScript_Knob('clear_filters', 'Clear Filters')
		self.addKnob(self.clear_filters_knob)
		self.clear_filters_knob.clearFlag( nuke.STARTLINE )

		self.newline5_knob = nuke.Text_Knob("")
		self.addKnob(self.newline5_knob)

		self.filtered_views_list_knob = nuke.Multiline_Eval_String_Knob('filtered_views_list', '')
		self.addKnob(self.filtered_views_list_knob)
		self.filtered_views_list_knob.setFlag( nuke.READ_ONLY )

		self.select_filtered_views_knob = nuke.PyScript_Knob('select_filtered_views', 'SELECT FILTERED VIEWS')
		self.addKnob(self.select_filtered_views_knob)

		#-------------------------------------------------------------------------------------------------
		# Initialize UI variables, based on the selected node, for passing knob values back and forth between the view_selector_knob and the view_knob...
		#-------------------------------------------------------------------------------------------------
		self.CollectedNodes = []
		# Invisible MultiView_Knob...
		self.view_knob = self.viewsKnob
		self.SelectedViews_from_ViewKnob = self.view_knob.value()
		self._do_part_filtering()
		self._viewname_filter_mashup()

	##---------------------------------------------------------------------------
	## Nuke Node Filtering Methods...
	##---------------------------------------------------------------------------

	def _collect_all_roto_and_rotopaint_nodes(self):
		'''Select all the Roto and RotoPaint nodes in the script, including all Groups.'''
		allRotoNodes = NodeTools._collect_class_nodes('RotoPaint') + NodeTools._collect_class_nodes('Roto')
		return allRotoNodes

	def _getAllSelectedRotoNodes(self, topLevel):
		'''
		Recursively return all the Selected Roto and RotoPaint nodes in the script, starting at topLevel...
		Looks in all groups. Default topLevel group to use is nuke.root()
		'''
		# Get all of the nodes in the script...
		allNodes = nuke.allNodes(group=topLevel)
		for n in allNodes:
			allNodes = allNodes +  self._collect_all_roto_and_rotopaint_nodes()
		# Get just the ones that are selected...
		allSelectedRotoNodes = []
		for n in allNodes:
			if n.knob('selected').value() == True and n.Class() in NodeClasses:
				allSelectedRotoNodes.append(n)
		return allSelectedRotoNodes	

	def _getNodeFilterSettings(self):
		'''
		Look at the knob selections and set the node filter selections...
		'''
		if  self.searchScope.value() == "Entire Script":
			if  self.nodesChoice.value() == "All":
				self.CollectedNodes =  self._collect_all_roto_and_rotopaint_nodes()
			elif  self.nodesChoice.value() == "Selected":
				self.CollectedNodes =  self._getAllSelectedRotoNodes(nuke.root())
		elif  self.searchScope.value() == "Current Node Graph Only":
			if  self.nodesChoice.value() == "All":
				self.CollectedNodes = [n for n in nuke.allNodes() if n.Class() in NodeClasses]
			elif  self.nodesChoice.value() == "Selected":
				self.CollectedNodes = [n for n in nuke.allNodes() if n.Class() in NodeClasses and n.knob('selected').value() == True]
		return self.CollectedNodes

	##---------------------------------------------------------------------------
	## UI View Filtering Knob Functions...
	## Methods for filtering, displaying and selecting views...
	##---------------------------------------------------------------------------

	def _do_part_filtering(self):
		''''''
		self.FilteredViewsList = []
		self.StartsWith_FilteredViewsList = []
		self.Contains_FilteredViewsList = []
		self.EndsWith_FilteredViewsList = []		
		#-----------------------------------------------------------------------------------
		self.StartsWithString = self.partStartsWith_knob.value()
		self.StartsWithString = self.StartsWithString.split()
		#print 'self.StartsWithString ----> ', self.StartsWithString

		# For clearing filters...
		self.StartsWithList = [self.StartsWithString]

		if self.StartsWithString != []:
			# Find any of the search string chunks...
			if self.StartsWith_Boolean_selector_knob.value() == 'ANY':
				for p in self.StartsWithString:
					for v in nuke.views():
						if v.startswith(p):
							if v not in self.StartsWith_FilteredViewsList:
								self.StartsWith_FilteredViewsList.append(v)
				for viewname in self.StartsWith_FilteredViewsList:
					if viewname not in self.FilteredViewsList:
						self.FilteredViewsList.append(viewname)
		else:
			pass
		#print ''
		#print 'self.StartsWith_FilteredViewsList', self.StartsWith_FilteredViewsList
		#print ''
		#print 'self.FilteredViewsList', self.FilteredViewsList
		#-----------------------------------------------------------------------------------
		self.ContainsString = self.partContains_knob.value()
		self.ContainsString = self.ContainsString.split()
		#print 'self.ContainsString ----> ', self.ContainsString

		# For clearing filters...
		self.ContainsList = [self.ContainsString]

		if self.ContainsString != []:
			if self.Contains_Boolean_selector_knob.value() == 'ANY':
				for p in self.ContainsString:
					for v in nuke.views():
						if p in (v):
							if v not in self.Contains_FilteredViewsList:
								self.Contains_FilteredViewsList.append(v)
				for viewname in self.Contains_FilteredViewsList:
					if viewname not in self.FilteredViewsList:
						self.FilteredViewsList.append(viewname)	

			elif self.Contains_Boolean_selector_knob.value() == 'ALL':
				for v in nuke.views():
					result = all(p in v for p in self.ContainsString)
					#print v + '--> ' + str(result)
					if result:
						self.Contains_FilteredViewsList.append(v)
				for viewname in self.Contains_FilteredViewsList:
					if viewname not in self.FilteredViewsList:
						self.FilteredViewsList.append(viewname)
		else:
			pass
		#print ''
		#print 'self.Contains_FilteredViewsList', self.Contains_FilteredViewsList
		#print ''
		#print 'self.FilteredViewsList', self.FilteredViewsList
		#-----------------------------------------------------------------------------------
		self.EndsWithString = self.partEndsWith_knob.value()
		self.EndsWithString = self.EndsWithString.split()
		#print 'self.EndsWithString ----> ', self.EndsWithString

		# For clearing filters...
		self.EndsWithList = [self.EndsWithString]

		if self.EndsWithString != []:
			# Find any of the search string chunks...
			if self.EndsWith_Boolean_selector_knob.value() == 'ANY':
				for p in self.EndsWithString:
					for v in nuke.views():
						if v.endswith(p):
							if v not in self.EndsWith_FilteredViewsList:
								self.EndsWith_FilteredViewsList.append(v)
				for viewname in self.EndsWith_FilteredViewsList:
					if viewname not in self.FilteredViewsList:
						self.FilteredViewsList.append(viewname)
		else:
			pass
		#print ''
		#print 'self.StartsWith_FilteredViewsList', self.StartsWith_FilteredViewsList
		#print ''
		#print 'self.FilteredViewsList', self.FilteredViewsList
		#-----------------------------------------------------------------------------------

	def _clear_views_filters(self):
		''''''
		# In case the "Active Filters" list doesn't get automatically cleared when the "Starts With" and "Contain" fields are cleared...
		self.StartsWithList = []
		self.ContainsList =[]
		self.EndsWithList = []
		self.FilteredViewsList = []
		self.partStartsWith_knob.setValue('')
		self.partEndsWith_knob.setValue('')
		self.partContains_knob.setValue('')
		# Re-run the list filters to refresh everything...
		self._do_part_filtering()
		self._viewname_filter_mashup()

	def _update_selected_views_in_view_selector(self):
		''''''
		self.SelectedViews_from_ViewKnob = self.view_knob.value()
		self.view_selector_knob.setSelectedItems(self.SelectedViews_from_ViewKnob.split())

	def _viewname_filter_mashup(self):
		''''''
		# Build the info list of filtered views and display them in the panel, so we can see the result of all of the filtering...
		self.FilteredViews= '\n'.join(self.FilteredViewsList)
		self.filtered_views_list_knob.setValue(self.FilteredViews)

	def _set_scene_knob_to_All(self, Node):
		''''''
		# Special method to avoid needless knobChanged stuff, when executing a select all...
		items = self.view_selector_knob.getAllItems()
		self.view_selector_knob.setSelectedItems(items)
		self.SelectedViews_from_ViewSelectorKnob = ' '.join(self.view_selector_knob.getSelectedItems())
		self.view_knob.setValue(self.SelectedViews_from_ViewSelectorKnob)
		#-------------------------------------------------------------------------------------------------
		# Copy the view selections from the invisible view_knob to the node's roto shapes...
		self._changeViews(Node, self.view_knob.value().split())
		#-------------------------------------------------------------------------------------------------

	##---------------------------------------------------------------------------
	## Apply the changes...
	##---------------------------------------------------------------------------

	def _getShapes(self, layer):
		'''
		Usage:
		k = Node['curves']
		shapes = self._getShapes(k.rootLayer)
		'''
		shapes = []
		for element in layer:
			if isinstance(element, nuke.rotopaint.Layer):
				shapes.extend(self._getShapes(element))
			elif isinstance(element, nuke.rotopaint.Shape) or isinstance(element, nuke.rotopaint.Stroke):
				shapes.append(element)
		return shapes	

	def _changeViews(self, Node, views):
		'''Apply the filtered views selections to a node.'''
		k = Node['curves']
		shapes = self._getShapes(k.rootLayer)

		for shape in shapes:
			attrs = shape.getAttributes()
			# Reset the number of views attribute...
			if 'nv' in attrs:
				attrs.remove('nv')
				attrs.add('nv', len(views))
			# Delete any previous view attributes...
			count = 1
			while ('view%s' % count) in attrs:             
				attrs.remove('view%s'% count)
				count +=1
			# Handle no selected views...
			if views == [''] :
				attrs.add('view1', 0.0)
			# Handle any other number of views...
			else:                   
				count = 1
			for view in views:
				index = float(nuke.views().index(view)+1)
				attrs.add('view%s'% count, index)
				count +=1
		k.changed()

	def knobChanged(self, knob):
		''''''
		# If we select a new view...	
		if nuke.thisKnob().name() == 'pick_a_view':
			self.SelectedViews_from_ViewSelectorKnob = ' '.join(self.view_selector_knob.getSelectedItems())
			self.view_knob.setValue(self.SelectedViews_from_ViewSelectorKnob)
			#-------------------------------------------------------------------------------------------------
			self._getNodeFilterSettings()
			# Copy the view selections from the invisible view_knob to the node's roto shapes...
			for node in self.CollectedNodes:
				self._changeViews(node, self.view_knob.value().split())
			#-------------------------------------------------------------------------------------------------			
		# Pressing ENTER/RETURN or clicking outside the field will update the current filters...
		if nuke.thisKnob().name() == 'select_none':
			self.view_knob.setValue(" ")
			#-------------------------------------------------------------------------------------------------
			# Copy the view selections from the invisible view_knob to the node's roto shapes...
			self._getNodeFilterSettings()
			for node in self.CollectedNodes:
				self._changeViews(node, self.view_knob.value().split())
			#-------------------------------------------------------------------------------------------------			
			self._do_part_filtering()
			self._viewname_filter_mashup()
			self._update_selected_views_in_view_selector()
		if nuke.thisKnob().name() == 'select_all':
			for node in self.CollectedNodes:
				self._set_scene_knob_to_All(node)
		# Pressing ENTER/RETURN or clicking outside the field will update the current filters...
		if  nuke.thisKnob().name() == 'startswith':
			self._do_part_filtering()
			self._viewname_filter_mashup()
		if  nuke.thisKnob().name() == 'contains':
			self._do_part_filtering()
			self._viewname_filter_mashup()
		if  nuke.thisKnob().name() == 'contains_boolean':
			self._do_part_filtering()
			self._viewname_filter_mashup()
		if  nuke.thisKnob().name() == 'endswith':
			self._do_part_filtering()
			self._viewname_filter_mashup()
		# Not necessary for the most part, since the filters get cleared automatically... Except when they don't.
		if nuke.thisKnob().name() == 'clear_filters':
			self._clear_views_filters()
			self._viewname_filter_mashup()
		# Use the filtered views to make selections to render...
		if nuke.thisKnob().name() == 'select_filtered_views':
			self.view_knob.setValue(self.FilteredViews)
			#-------------------------------------------------------------------------------------------------
			self._getNodeFilterSettings()
			# Copy the view selections from the invisible view_knob to the node's roto shapes...
			for node in self.CollectedNodes:
				self._changeViews(node, self.view_knob.value().split())
			#-------------------------------------------------------------------------------------------------			
			self._update_selected_views_in_view_selector()


##-------------------------------------------------------------------------------------------------
##  Used by menu_constructor.py to add the panel in Nuke...
##-------------------------------------------------------------------------------------------------
def Return_RotoNodesViewsSelectionPanel():
	p = RotoNodesViewsSelectionPanel()
	return p

##------------------------------------------------##
## *** TESTING *** For use in Nuke Script Editor.
##------------------------------------------------##
#p = Return_RotoNodesViewsSelectionPanel()
#p.show()


'''
REFERENCE:
#-------------------------------------------------------------------------------------------------
# Set views for shapes and layers in RotoPaint and Roto nodes...
# ORIG. Code for RotoPaint Shapes:
# http://satheesrev.wix.com/satheeshvfx
# http://satheeshnuketutorials.blogspot.co.nz/2012/06/change-roto-views-to-left-and-right.html	
#-------------------------------------------------------------------------------------------------
def _getShapes(self, layer):

	"Usage:
	k = Node['curves']
	shapes = self._getShapes(k.rootLayer)"

	shapes = []
	for element in layer:
		if isinstance(element, nuke.rotopaint.Layer):
			shapes.extend(self._getShapes(element))
		elif isinstance(element, nuke.rotopaint.Shape) or isinstance(element, nuke.rotopaint.Stroke):
			shapes.append(element)
	return shapes
'''