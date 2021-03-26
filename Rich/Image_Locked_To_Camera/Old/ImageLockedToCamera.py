import nuke
import nukescripts

class ImageLockedToCameraPanel(nukescripts.PythonPanel):
	''''''
	def __init__(self):

		# Initialize the panel.
		nukescripts.PythonPanel.__init__(self, 'Lock an Image to a Camera', 'com.richbobo.ImageLockedToCamera')
		self.setMinimumSize(525, 125)

		# Get a list of all the cameras...
		self.cameras = []
		for node in (nuke.allNodes('Camera') + nuke.allNodes('Camera2')):
			self.cameras.append(node.name())	

	def _build_Control_Panel(self):
		'''
		Build panel to select and control the camera...
		'''
		self.cameraChoiceKnob = nuke.Enumeration_Knob('cameras', 'Select Camera: ', self.cameras)
		self.addKnob(self.cameraChoiceKnob)
		# Add knobs to the panel...
		#for k in (self.cameraChoice):
			#self.addKnob(k)

	def knobChanged(self, knob):
		if self.cameraChoiceKnob:
			self.SelectedCamera = self.cameraChoiceKnob.value()
			print self.SelectedCamera

##########################################
## TESTING IN Nuke...
##########################################

## Initialize the Class...
CamPanel = ImageLockedToCameraPanel()
## Run it...
CamPanel._build_Control_Panel()
CamPanel.show()