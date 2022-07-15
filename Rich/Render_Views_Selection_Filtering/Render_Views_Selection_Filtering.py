import nuke, nukescripts, sys, os

class RenderViewsSelectorPanel( nukescripts.PythonPanel ):

	def __init__(self):
		'''
		--------------------------------------------------------------------------------------------------
		A Brief Explanation of Functionality:
		--------------------------------------------------------------------------------------------------
		A Wite node render view name filtering selection panel.

		Automobile global configurator Nuke scripts can be very complex and contain many hundreds of Viewer "views" - each showing an individual car part.
		Selecting groups of views to render can be cumbersome - and downright impossible - under certain circumstances.
		This panel allows the artist to more easily select which views will be rendered by the Write node.

		Created by Rich Bobo - 04/26/2013
		richbobo@mac.com
		http://richbobo.com
		--------------------------------------------------------------------------------------------------
		'''
		nukescripts.PythonPanel.__init__(self, 'Render Views Selector', 'com.richbobo.RenderViewsSelectorPanel')

		#-------------------------------------------------------------------------------------------------
		# Define and create knobs for the panel...
		#-------------------------------------------------------------------------------------------------
		self.selected_write_node_knob = nuke.String_Knob('selected_write_node', 'Write Node :')
		self.addKnob(self.selected_write_node_knob)
		self.selected_write_node_knob.setFlag(nuke.READ_ONLY)

		self.info = nuke.Text_Knob('info', '', 'NOTE: This panel affects ONLY the selected node above.' )
		self.addKnob(self.info)
		self.info.setFlag( nuke.READ_ONLY )	

		self.newline6_knob = nuke.Text_Knob("")
		self.addKnob(self.newline6_knob)

		self.BeginGroup2 = nuke.Text_Knob('BeginGroup2', 'VIEW SELECTION:')
		self.addKnob(self.BeginGroup2)		

		self.selectNone_knob = nuke.PyScript_Knob('select_none', 'SELECT NONE')
		self.addKnob(self.selectNone_knob)

		self.selectAll_knob= nuke.PyScript_Knob('select_all', 'SELECT ALL')
		self.addKnob(self.selectAll_knob)

		self.view_selector_knob = nuke.SceneView_Knob('pick_a_view', 'Selected Views', nuke.views())
		self.addKnob(self.view_selector_knob)

		self.newline1_knob = nuke.Text_Knob("")
		self.addKnob(self.newline1_knob)

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
		self.clear_filters_knob.clearFlag(nuke.STARTLINE)

		self.newline5_knob = nuke.Text_Knob("")
		self.addKnob(self.newline5_knob)

		self.filtered_views_list_knob = nuke.Multiline_Eval_String_Knob('filtered_views_list', '')
		self.addKnob(self.filtered_views_list_knob)
		self.filtered_views_list_knob.setFlag(nuke.READ_ONLY)

		self.select_filtered_views_knob = nuke.PyScript_Knob('select_filtered_views', 'SELECT FILTERED VIEWS')
		self.addKnob(self.select_filtered_views_knob)

		#-------------------------------------------------------------------------------------------------
		# Some initialization variables, based on the selected Write node, for passing knob values back and forth between the view_selector_knob and the view_knob...
		#-------------------------------------------------------------------------------------------------
		
		## Acceptable node classes to check for...
		## Note: If changed, also update lists in Create_Render_Views_Selector_Panel and Return_Render_Views_Selector_Panel functions at the bottom...
		self.Node_Classes = ['Write', 'Config_Image_Writer', 'Group']
		
		try:
			if nuke.selectedNode():
				if nuke.selectedNode().Class() in self.Node_Classes:
					self.write_node = nuke.selectedNode()
					self.selected_write_node_knob.setValue(self.write_node.name())
					self.view_knob = self.write_node.knob("views")
					self.SelectedViews_from_ViewKnob = self.view_knob.value()
					self.view_selector_knob.setSelectedItems(self.SelectedViews_from_ViewKnob.split())
					self._do_part_filtering()
					self._viewname_filter_mashup()
		except ValueError:
			nuke.message("Please select a Write node and try again.")
			return

	#-------------------------------------------------------------------------------------------------
	# Methods for filtering, displaying and selecting views...
	#-------------------------------------------------------------------------------------------------
	def _do_part_filtering(self):
		''''''
		self.FilteredViewsList = []
		self.StartsWith_FilteredViewsList = []
		self.Contains_FilteredViewsList = []
		self.EndsWith_FilteredViewsList = []
		#-----------------------------------------------------------------------------------
		self.StartsWithString = self.partStartsWith_knob.value()
		self.StartsWithString = self.StartsWithString.split()
		print('self.StartsWithString ----> ', self.StartsWithString)

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
						else:
							pass
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

	def _Set_to_All_for_scene_knob(self):
		''''''
		# Special method to avoid needless knobChanged stuff, when executing a select all...
		items = self.view_selector_knob.getAllItems()
		self.view_selector_knob.setSelectedItems(items)
		self.SelectedViews_from_ViewSelectorKnob = ' '.join(self.view_selector_knob.getSelectedItems())
		self.view_knob.setValue(self.SelectedViews_from_ViewSelectorKnob)

	#-------------------------------------------------------------------------------------------------
	# Hook up the buttons on the panel to the methods that they will call...
	#-------------------------------------------------------------------------------------------------
	def knobChanged(self, knob):
		''''''
		# If we select a new view...
		if nuke.thisKnob().name() == 'pick_a_view':
			self.SelectedViews_from_ViewSelectorKnob = ' '.join(self.view_selector_knob.getSelectedItems())
			self.view_knob.setValue(self.SelectedViews_from_ViewSelectorKnob)		
		# Pressing ENTER/RETURN or clicking outside the field will update the current filters...
		if nuke.thisKnob().name() == 'select_none':
			self.view_knob.setValue(" ")
			self._do_part_filtering()
			self._viewname_filter_mashup()
			self._update_selected_views_in_view_selector()
		if nuke.thisKnob().name() == 'select_all':
			self._Set_to_All_for_scene_knob()
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
		if nuke.thisKnob().name() == 'select_filtered_views':
			self.view_knob.setValue(self.FilteredViews)
			self._update_selected_views_in_view_selector()	

#-------------------------------------------------------------------------------------------------
# Function: To pop up the view selector panel... which menu.py uses to add the command to the User Tools menu.
#-------------------------------------------------------------------------------------------------
def Create_Render_Views_Selector_Panel():
	if len(nuke.selectedNodes()) == 0:
		nuke.message("Please select a Write node and try again.")
		return
	elif nuke.selectedNode().Class() not in ['Write', 'Config_Image_Writer', 'Group'] :
		nuke.message("No Write node selected. Please select a Write node and try again.")
		return
	else:
		p = RenderViewsSelectorPanel()
		p.show()

#-------------------------------------------------------------------------------------------------
# Function: To return the panel class of the view selector panel... which menu.py uses to add it to the Pane menu.
#-------------------------------------------------------------------------------------------------
def Return_Render_Views_Selector_Panel():
	if len(nuke.selectedNodes()) == 0:
		nuke.message("Please select a Write node and try again.")
		return
	elif nuke.selectedNode().Class() not in ['Write', 'Config_Image_Writer', 'Group'] :
		nuke.message("No Write node selected. Please select a Write node and try again.")
		return	
	else:	
		p = RenderViewsSelectorPanel()
		return p


#########################################
## Testing in Nuke Script Editor...
#########################################
#Create_Render_Views_Selector_Panel()
