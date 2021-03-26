# ------------------------------------------------------------------
#	Cyclo v0.9
#
#	Creates a panoramic image out of live footage frames
#	or just simple coverage maps.
#	Needs a moving camera as input.
# ------------------------------------------------------------------
#	Author: makis stergiou
# ------------------------------------------------------------------
#	Licence: sVFX v0.1
# ------------------------------------------------------------------

import nuke
import nukescripts

# ------------------------------------------------------------------
# Create the control node
def createControl(first, last, camera, projections):
	control = nuke.nodes.Group()
	control.setName('Cyclo', uncollide=True)
	# Camera section
	tab = nuke.Tab_Knob('Rig Control')
	control.addKnob(tab)
	# Print info
	knob = nuke.Text_Knob('Camera', 'camera:', camera)
	control.addKnob(knob)
	knob = nuke.Text_Knob('Frames', 'frames:', str(first) + '-' + str(last) + ' (' + str(last-first) + ')')
	control.addKnob(knob)
	knob = nuke.Text_Knob('Projections', 'projections:', projections)
	control.addKnob(knob)
	knob = nuke.Text_Knob('divider1', '', '')
	control.addKnob(knob)
	# Set ditribution over time (snapshot spacing)
	knob = nuke.Double_Knob('Spacing', 'spacing')
	control.addKnob(knob)
	knob.setAnimated()
	knob.setValueAt(0, first)
	knob.setValueAt(1, last)
	# Set near parameter
	knob = nuke.Link_Knob('near') 
	knob.setLink('controlCamera.near')
	control.addKnob(knob)
	# Set far parameter
	knob = nuke.Link_Knob('far') 
	knob.setLink('controlCamera.far')
	control.addKnob(knob)
	# Set visibility
	knob = nuke.Boolean_Knob('Visible', 'visible')
	knob.setFlag(nuke.STARTLINE)
	control.addKnob(knob)
	knob.setValue(1)
	# Print version
	knob = nuke.Text_Knob('divider2', '', '')
	control.addKnob(knob)
	knob = nuke.Text_Knob('Version', '', 'Cyclo v1.1')
	control.addKnob(knob)
	return control

# ------------------------------------------------------------------
# Create the hold frames and the projections
def createProjection(source, previous, index, lookup, first, last):
	name = str(index)
	# Create the nodes
	merge = ''
	if previous != source:
		merge = nuke.nodes.MergeMat(name = 'MergeMat_' + name)
	frameHold = nuke.nodes.FrameHold(name = 'Frame_' + name)
	projection = nuke.nodes.Project3D(name = 'Project3D_' + name)
	camera = nuke.nodes.Camera2(name = 'C_' + name)
	camera['selectable'].setValue(0)
	# Do the connections
	if merge:
		merge.setInput(0, previous)
		merge.setInput(1, projection)
		previous = merge
		merge['disable'].setExpression('[expression parent.controlCamera.disable]')
	else:
		previous = projection
	frameHold.setInput(0, source)
	projection.setInput(0, frameHold)
	projection.setInput(1, camera)
	# The expressions
	projection['disable'].setExpression('[expression parent.controlCamera.disable]')
	exp = 'int(' + str(last-first) + '*parent.Spacing(' + str(lookup) + ')+' + str(first) + ')'
	frameHold['first_frame'].setExpression(exp)
	frameHold['disable'].setExpression('[expression parent.controlCamera.disable]')
	camera['display'].setExpression('[expression parent.controlCamera.display]')
	camera['near'].setExpression('[expression parent.controlCamera.near]')
	camera['far'].setExpression('[expression parent.controlCamera.far]')
	exp = '[expression parent.controlCamera.translate([expression ' + frameHold['name'].toScript() + '.knob.first_frame])]'
	camera['translate'].setExpression(exp, -1)
	exp = '[expression parent.controlCamera.rotate([expression ' + frameHold['name'].toScript() + '.knob.first_frame])]'
	camera['rotate'].setExpression(exp, -1)
	camera['focal'].setExpression('[expression parent.controlCamera.focal]')
	camera['haperture'].setExpression('[expression parent.controlCamera.haperture]')
	camera['vaperture'].setExpression('[expression parent.controlCamera.vaperture]')
	camera['disable'].setExpression('[expression parent.controlCamera.disable]')
	return previous

def getKeys(camera):
	keys=[]
	for curve in camera['translate'].animations():
		for key in curve.keys():
			keys.append(curve.keys()[0].x)
	for curve in camera['rotate'].animations():
		for key in curve.keys():
			keys.append(curve.keys()[0].x)

	first = nuke.root().firstFrame()
	if len(keys)>0:
		first = min(key for key in keys)

	keys=[]
	for curve in camera['translate'].animations():
		for key in curve.keys():
			keys.append(curve.keys()[-1].x)
	for curve in camera['rotate'].animations():
		for key in curve.keys():
			keys.append(curve.keys()[-1].x)

	last = nuke.root().lastFrame()
	if len(keys)>0:
		last = max(key for key in keys)

	return int(first), int(last)

# ------------------------------------------------------------------
# Create the rig
def createRig(camera, projections):
	# Get first and last keyframes
	first, last = getKeys(camera)
	if projections < 2:
		projections = 2
	step = (last - first) / float(projections-1)
	# Create the control group
	control = createControl(first, last, camera['name'].value(), str(projections))
	control.begin()
	# Add inputs
	input_shot = nuke.nodes.Input(name = 'Source')
	input_camera = nuke.nodes.Input(name = 'cam')
	control.setInput(1, camera)
	#Create a control camera
	controlCamera = nuke.nodes.Camera2(name = 'controlCamera')
	controlCamera['selectable'].setValue(0)
	controlCamera['display'].setExpression('parent.Visible')
	controlCamera['translate'].setExpression('[topnode parent.input1].translate', -1)
	controlCamera['rotate'].setExpression('[topnode parent.input1].rotate', -1)
	controlCamera['focal'].setExpression('[topnode parent.input1].focal')
	controlCamera['haperture'].setExpression('[topnode parent.input1].haperture')
	controlCamera['vaperture'].setExpression('[topnode parent.input1].vaperture')
	controlCamera['disable'].setExpression('parent.disable')
	# Create the projections
	previous = input_shot
	index = 1
	p = first
	while p <= last + 1:
		previous = createProjection(input_shot, previous, index, float(index-1)/(projections-1) * (last-first) + first, first, last)
		p += step
		index += 1
	# Set the output node
	nuke.nodes.Output().setInput(0, previous)
	control.end()
	control.showControlPanel()
	for n in nuke.selectedNodes():
		n['selected'].setValue(False)
	control['selected'].setValue(True)
	#control['knobChanged'].setValue('if nuke.thisKnob().name() == \'inputChange\': print nuke.thisNode().input(1).name()')

# ------------------------------------------------------------------
# Populate and display the dialog
if nuke.env["gui"]:
	class CycloPanel(nukescripts.PythonPanel):
		def __init__(self):
			nukescripts.PythonPanel.__init__(self, "Cyclo", "com.mstergiou.Cyclo")

			cameras = []
			for n in (nuke.allNodes('Camera') + nuke.allNodes('Camera2')):
				if n.knob('translate').isAnimated() or n.knob('rotate').isAnimated():
					cameras.append(n.knob('name').value())

			self.camera = nuke.Enumeration_Knob('camera', 'Camera:', cameras)
			self.addKnob(self.camera)
			self.projections = nuke.Int_Knob('projections', 'Projections:')
			self.addKnob(self.projections)
			self.projections.setValue(16)
			
		def showModalDialog(self):
			result = nukescripts.PythonPanel.showModalDialog(self)
			if result:
				# If there is an animated camera, do the job
				createRig(nuke.toNode(self.camera.value()), self.projections.value())

	def cyclo():
		return CycloPanel().showModalDialog()