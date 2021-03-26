import nuke
import nukescripts

class ViewerViewsSelectorPanel( nukescripts.PythonPanel ):

	def __init__(self):
		'''
		--------------------------------------------------------------------------------------------------
		A Brief Explanation of Functionality:
		--------------------------------------------------------------------------------------------------
		A Viewer view name filtering selection panel.

		Product configurator Nuke scripts can be very complex and contain many Viewer "views", each showing an individual part,
		version or camera angle. Selecting an individual part to display can be cumbersome and sometimes impossible if there are
		hundreds of views. This panel allows the artist to more easily narrow down the choices of views to display.

		Created by Rich Bobo - 04/23/2018
		richbobo@mac.com
		http://richbobo.com
		--------------------------------------------------------------------------------------------------
		'''
		# Initialize the PythonPanel...
		nukescripts.PythonPanel.__init__(self, 'Viewer View Selector', 'com.richbobo.ViewerViewsSelectorPanel')

		# Define and add knobs to the panel...
		## Note: I decided to prompt the user to hit the "Clear Filters button" to force a refresh.
		## At script load time, Nuke only knows about the hero_view and none of the rest of the views.
		## This message to the user to manually refresh seemed to be the best way to do it...
		
		self.newline6_knob = nuke.Text_Knob("")
		self.addKnob(self.newline6_knob)

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
		self.partStartsWith_knob.setValue('PRESS THE "Clear Filters" BUTTON TO INITIALIZE.')
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
		self.partContains_knob.setValue('PRESS THE "Clear Filters" BUTTON TO INITIALIZE.')
		self.partContains_knob.clearFlag(nuke.STARTLINE)
		#-----------------------------------------------------------------------------------------------------
		self.EndsWith_Boolean_selector_knob = nuke.Enumeration_Knob('endswith_boolean', 'Ends With', ['ANY'])
		self.addKnob(self.EndsWith_Boolean_selector_knob)
		self.EndsWith_Boolean_selector_knob.setFlag(nuke.STARTLINE)		

		self.partEndsWith_knob = nuke.String_Knob('endswith', '')	
		#self.partEndsWith_knob = nuke.String_Knob('endswith', 'Ends With ANY ')		
		self.addKnob(self.partEndsWith_knob)
		self.partEndsWith_knob.setValue('PRESS THE "Clear Filters" BUTTON TO INITIALIZE.')
		self.partEndsWith_knob.clearFlag(nuke.STARTLINE)
		#-----------------------------------------------------------------------------------------------------
		self.newline4_knob = nuke.Text_Knob("")		
		self.addKnob(self.newline4_knob)

		self.clear_filters_knob = nuke.PyScript_Knob('clear_filters', 'Clear Filters')
		self.addKnob(self.clear_filters_knob)

		self.newline2_knob = nuke.Text_Knob("")		
		self.addKnob(self.newline2_knob)

		self.newline3_knob = nuke.Text_Knob("")
		self.addKnob(self.newline3_knob)

		self.view_selector_knob = nuke.Enumeration_Knob('pick_a_view', 'CHOOSE VIEW :', nuke.views() )
		self.addKnob(self.view_selector_knob)

		self.filter_views_list_knob = nuke.Multiline_Eval_String_Knob('filtered_views_list', '')
		self.addKnob(self.filter_views_list_knob)
		self.filter_views_list_knob.setFlag(nuke.READ_ONLY )

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

		# Populate the view selector knob with the filtered values...
		self.view_selector_knob.setValues(self.FilteredViewsList)

		# Set the current view to the first one in the filtered list...
		if len(self.FilteredViewsList) > 0:
			nuke.activeViewer().setView(self.FilteredViewsList[0])
			self.view_selector_knob.setValue(self.FilteredViewsList[0])

		# Build the info list of filtered views and display them in the panel, so we can see the result of all of the filtering...
		self.FilteredViews= '\n'.join(self.FilteredViewsList)
		self.filter_views_list_knob.setValue(self.FilteredViews)

	def _clear_views_filters(self):
		''''''
		# Set the FilteredViewsList to all of the views...
		self.FilteredViewsList = []
		for v in nuke.views():
			self.FilteredViewsList.append(v)
		self.view_selector_knob.setValues(self.FilteredViewsList)
		self.view_selector_knob.setValue(nuke.activeViewer().view())

		# Set the list of views to display in the filter_views_list_knob at the bottom...
		self.FilteredViews = '\n'.join(self.FilteredViewsList)
		self.filter_views_list_knob.setValue(self.FilteredViews)
		
		# Clear...
		self.StartsWithList = []
		self.ContainsList =[]
		self.EndsWithList = []
		self.FilteredViewsList = []
		# Clear...
		self.partStartsWith_knob.setValue('')
		self.partContains_knob.setValue('')
		self.partEndsWith_knob.setValue('')
	
	def knobChanged(self, knob):
		''''''
		# Hook up the buttons on the panel to the methods that they will call...
		# Pressing ENTER/RETURN or clicking outside the field will update the current filters...
		if  nuke.thisKnob().name() == 'startswith':
			self._do_part_filtering()
		if  nuke.thisKnob().name() == 'contains':
			self._do_part_filtering()
		if  nuke.thisKnob().name() == 'contains_boolean':
			self._do_part_filtering()		
		if  nuke.thisKnob().name() == 'endswith':
			self._do_part_filtering()
		if nuke.thisKnob().name() == 'clear_filters':
			self._clear_views_filters()
		if nuke.thisKnob().name() == 'pick_a_view':
			nuke.activeViewer().setView(self.view_selector_knob.value())

	# This extends the python built-in show() method to include some initialization of the search filters in the panel.
	def show(self):
		self._clear_views_filters()
		super(ViewerViewsSelectorPanel, self).show()

# Main function to run the view selector panel...
def Create_Viewer_Views_Selector_Panel():
	p = ViewerViewsSelectorPanel()
	p.show()


#########################################
## Testing in Nuke Script Editor...
#########################################
#Create_Viewer_Views_Selector_Panel()