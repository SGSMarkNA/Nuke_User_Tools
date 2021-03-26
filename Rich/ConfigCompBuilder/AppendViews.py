import nuke
import nukescripts
import re


class AppendViews(nukescripts.PythonPanel):
	'''Simple panel class to quickly add views - without removing any existing views...'''

	def __init__(self):

		pass

	def _create_ViewsList_InputPanel(self):
		''' Get a list of views from the user and sanitize the input - removing spaces and illegal characters...'''
		self.views_to_build = []
		# Build a trim name input panel...
		nukescripts.PythonPanel.__init__(self, "Views Entry:", "com.armstrong-white.ViewsInputPanel")
		self.setMinimumSize(400, 300)
		self.userInput = nuke.Multiline_Eval_String_Knob("view_names", "Add View Names - One per line:")
		self.addKnob(self.userInput)		

		self.userInput.setText('')
		self.userInput.setTooltip("view_names")
		ViewsInputPanel = nukescripts.PythonPanel.showModalDialog(self)
		if ViewsInputPanel:
			# Check for no input from user.
			if self.userInput.value() is '':
				nuke.message('Nothing Entered for View Names.')
				return False
			else:
				# Strip out illegal characters...
				pattern = re.compile(r'[^\w]')
				self.ViewsList = self.userInput.value().splitlines()
				for x in self.ViewsList:
					clean_x = pattern.sub('_', x)
					self.views_to_build.append(clean_x)
				return self.views_to_build

	def _createViews(self):
		# Check for no input from user.
		if not self.views_to_build:
			nuke.message("I don't have enough information. Please enter a list of Views in the pop-up window.")
			return False
		# Add the views...
		for v in self.views_to_build:
			try:
				nuke.Root().addView(v)
			except ValueError:
				# View might already exist...
				pass			
			if len(self.views_to_build) >5:
				nuke.Root().knob('views_button').setValue(False)
			# Remove the default 'main' view...
			try:
				nuke.Root().deleteView('main')
			except Exception:
				pass


##############################################################
## RUN IT...

def start():
	''''''
	x = AppendViews()
	if nuke.ask("Do you wish to add some views...?"):
		pass
	else:
		return False	
	x._create_ViewsList_InputPanel()
	x._createViews()
