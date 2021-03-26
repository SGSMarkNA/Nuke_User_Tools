import nuke
import nukescripts
import sys
import os

# Global list of node classes that this class can operate on...
global NodeClasses
NodeClasses = ['RotoPaint', 'Roto']

import PySide.QtGui as QtGui


class RotoViewsSelectorPanel(nukescripts.PythonPanel):

	def __init__(self):
		'''
		--------------------------------------------------------------------------------------------------
		A Brief Explanation of Functionality:
		--------------------------------------------------------------------------------------------------
		A RotoPaint and Roto node view name filtering selection panel.

		Created by Rich Bobo - 03/12/2016
		richbobo@mac.com
		http://richbobo.com
		--------------------------------------------------------------------------------------------------
		'''
		##################################################################################################
		## Make sure that the _SelectedShapesCheck doesn't run when the panel gets created...
		##
		## NOTE:
		##      This gets set to True from menu_constructor.py. Therefore, for testing purposes, you'll
		##      need to set this to True after the panel gets created. Otherwise, it will not work!
		##
		self._SelectedShapesCheck = False
		##
		##################################################################################################

		nukescripts.PythonPanel.__init__(self, 'Roto Views Selector', 'com.richbobo.RotoViewsSelectorPanel')
		#-------------------------------------------------------------------------------------------------
		# Define and create knobs for the views selector filtering panel...
		#-------------------------------------------------------------------------------------------------
		self.selected_roto_knob = nuke.String_Knob('selected_roto_node', 'Roto Node :')
		self.addKnob(self.selected_roto_knob)
		self.selected_roto_knob.setFlag( nuke.READ_ONLY )

		self.info = nuke.Text_Knob('info', '', 'NOTE: This panel affects ONLY the selected node above.\nSelect all of the shapes you wish to modify and then set the views below.' )
		self.addKnob(self.info)
		self.info.setFlag( nuke.READ_ONLY )			

		self.newline6_knob = nuke.Text_Knob("")
		self.addKnob(self.newline6_knob)

		self.BeginGroup2 = nuke.Text_Knob('BeginGroup2', 'VIEW SELECTION:')
		self.addKnob(self.BeginGroup2)		
		#-------------------------------------------------------------------------------------------------
		self.viewsKnob = nuke.MultiView_Knob('views')
		self.addKnob(self.viewsKnob)
		self.viewsKnob.setValue((' ').join(nuke.views()))
		# Set the knob to be Invisible.
		self.viewsKnob.setFlag(0x00040000)
		#-------------------------------------------------------------------------------------------------
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

		self.newline2_knob = nuke.Text_Knob("")
		self.addKnob(self.newline2_knob)		
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
		#-----------------------------------------------------------------------------------------------------

	def _check_for_selected_roto_node(self):
		''''''
		# Get the current qtgui instance...
		nuke_app = QtGui.QApplication.instance()

		# Get all the widgets...
		all_widgets = nuke_app.allWidgets()

		node_graph_widget = None

		# Get the visible DAG Node Graph widget...
		for w in all_widgets:
			name =  w.objectName()
			if 'DAG' in name:
				if w.isVisible():
					#print name
					node_graph_widget = w

		# Current DAG widget name, e.g. "DAG.1" is the Root node graph or "DAG.2" is a Group node graph...
		self.Current_Group_DAG = node_graph_widget.objectName()
		print 'self.Current_Group_DAG', self.Current_Group_DAG

		# Check to see if the current Node Graph is the Root Node Graph, a.k.a. "DAG.1"...
		if self.Current_Group_DAG == 'DAG.1':
			try:
				if nuke.selectedNode():
					if nuke.selectedNode().Class() in NodeClasses:
						roto_node = nuke.selectedNode()
						# Make sure only one roto node is selected...
						for n in nuke.allNodes():
							if n.Class() in NodeClasses and n is not roto_node:
								n.setSelected(False)						
						return roto_node
				else:
					return None
			except:
				return None
		else:
			# The current DAG is a Group Node Graph.
			# Get the current Group node name that's on the pane tab - the Group node we need to get...
			Current_Group_DAG_Name = node_graph_widget.windowTitle()
			print 'Current_Group_DAG_Name', Current_Group_DAG_Name

			# Get only the DAG name string...
			Current_Group_Name = Current_Group_DAG_Name.split()[0]
			print 'Current_Group_Name', Current_Group_Name

			# Get the Group node object...
			for Node in nuke.allNodes('Group'):
				self.GroupNode = nuke.toNode(Current_Group_Name)
			print self.GroupNode.name()		

			with self.GroupNode:
				try:
					if nuke.selectedNode():
						if nuke.selectedNode().Class() in NodeClasses:
							roto_node = nuke.selectedNode()
							# Make sure only one roto node is selected...
							for n in nuke.allNodes():
								if n.Class() in NodeClasses and n is not roto_node:
									n.setSelected(False)							
							return roto_node
					else:
						return None
				except:
					return None
		return None

	def _init_knobs(self, Node):
		''''''
		# Initialize variables and knob values, based on the selected node...
		# Set things up for passing knob values back and forth between the view_selector_knob and the view_knob...

		# If the current DAG is the Root Node Graph...
		if self.Current_Group_DAG == 'DAG.1':
			self.roto_node = Node
			self.selected_roto_knob.setValue(self.roto_node.name())
			# Invisible MultiView_Knob...
			self.view_knob = self.viewsKnob
			self.SelectedViews_from_ViewKnob = self.view_knob.value()
			self._do_part_filtering()
			self._viewname_filter_mashup()
		else:
			# If the current DAG is a Group Node Graph...
			with self.GroupNode:
				self.roto_node = Node
				self.selected_roto_knob.setValue(self.roto_node.name())
				# Invisible MultiView_Knob...
				self.view_knob = self.viewsKnob
				self.SelectedViews_from_ViewKnob = self.view_knob.value()
				self._do_part_filtering()
				self._viewname_filter_mashup()			

	def _changeViews(self, Node, views):
		''''''
		k = Node['curves']
		selected = k.getSelected()
		if self._SelectedShapesCheck:
			if selected:
				for shape in selected:
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
			else:
				print "No shapes selected!"
				nuke.message("No shapes selected!")

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
					#print 'result ---> ', result
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

	def _set_scene_knob_to_All(self):
		''''''
		# Special method to avoid needless knobChanged stuff, when executing a select all...
		items = self.view_selector_knob.getAllItems()
		self.view_selector_knob.setSelectedItems(items)
		self.SelectedViews_from_ViewSelectorKnob = ' '.join(self.view_selector_knob.getSelectedItems())
		self.view_knob.setValue(self.SelectedViews_from_ViewSelectorKnob)
		#-------------------------------------------------------------------------------------------------
		# Copy the view selections from the invisible view_knob to the node's roto shapes...
		self._changeViews(self.roto_node, self.view_knob.value().split())
		#-------------------------------------------------------------------------------------------------

	def knobChanged(self, knob):
		''''''
		# If we select a new view...
		if nuke.thisKnob().name() == 'pick_a_view':
			self.SelectedViews_from_ViewSelectorKnob = ' '.join(self.view_selector_knob.getSelectedItems())
			self.view_knob.setValue(self.SelectedViews_from_ViewSelectorKnob)
			#-------------------------------------------------------------------------------------------------
			# Copy the view selections from the invisible view_knob to the node's roto shapes...
			self._changeViews(self.roto_node, self.view_knob.value().split())
			#-------------------------------------------------------------------------------------------------			
		# Pressing ENTER/RETURN or clicking outside the field will update the current filters...
		if nuke.thisKnob().name() == 'select_none':
			self.view_knob.setValue(" ")
			#-------------------------------------------------------------------------------------------------
			# Copy the view selections from the invisible view_knob to the node's roto shapes...
			self._changeViews(self.roto_node, self.view_knob.value().split())
			#-------------------------------------------------------------------------------------------------			
			self._do_part_filtering()
			self._viewname_filter_mashup()
			self._update_selected_views_in_view_selector()
		if nuke.thisKnob().name() == 'select_all':
			self._set_scene_knob_to_All()
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
			# Copy the view selections from the invisible view_knob to the node's roto shapes...
			self._changeViews(self.roto_node, self.view_knob.value().split())
			#-------------------------------------------------------------------------------------------------			
			self._update_selected_views_in_view_selector()

##-------------------------------------------------------------------------------------------------
## Used by menu_constructor.py to add the panel in Nuke...
##-------------------------------------------------------------------------------------------------
def Return_RotoViewsSelectorPanel():
	''''''
	panel = RotoViewsSelectorPanel()

	roto_node = panel._check_for_selected_roto_node()

	if roto_node is not None:
		#print 'roto_node ---> ', roto_node.name()
		panel._init_knobs(roto_node)
		return panel
	else:
		print "Please select a single RotoPaint or Roto node and try again."
		nuke.message("Please select a single RotoPaint or Roto node and try again.")
		return



#------------------------------------------------##
# *** TESTING *** For use in Nuke Script Editor.
#------------------------------------------------##
#p = Return_RotoViewsSelectorPanel()
#p.show()
#p._SelectedShapesCheck = True