###############################################################################################
####----------------------------------------------------------------------------------------
#### ---- This goes in the 'Find Cameras' Python Button on the Group node...

import nuke
import re
# Assign the Group node to a variable we can get later...
GroupNode = nuke.thisNode()
################################################################
# Get a list of all the available cameras in the Root node...
RootNode = nuke.Root()
# Make sure we're operating inside the Root group...
RootNode.begin()
cameras = []
for node in (nuke.allNodes('Camera') + nuke.allNodes('Camera2')):
    cameras.append(node.name())
RootNode.end()
################################################################
# Get all the knobs in the Group...
GroupNodeKnobs = GroupNode.allKnobs()
#print 'GroupNodeKnobs', GroupNodeKnobs
# Make sure we're operating inside the GroupNode...
GroupNode.begin()
# Set up some variables for removal of preexisting knobs when the 'Pick Camera' button is pressed...
knobs_to_remove = []
knobs_to_ignore = ['selected', 'hide_input', 'cached', 'dope_sheet', 'bookmark', 'postage_stamp', 'useLifetime', 'lock_connections']
# Make a list of any pulldown (Enumeration_Knob) knobs...
regex = re.compile(r"\Enumeration_Knob\W")   # \W is anything except a word character...
for knob in GroupNodeKnobs:
    if bool(regex.search(str(type(knob)))):
        if knob.name() not in knobs_to_ignore:
            name = knob.name()
            knobs_to_remove.append(name)
        else:
            pass
# Remove existing pulldown knob when the 'Pick Camera' PyScript button is pressed, before we make a new one...
Knobs = GroupNode.knobs()
try:
    for knobname in knobs_to_remove:
        GroupNode.removeKnob(Knobs[knobname])
except KeyError:
    print 'Key Error: Some nonexistant knobs could not be removed.'
except ValueError:
    print 'Value Error: Some nonexistant knobs could not be removed.'
# Build pulldown selector to pick the camera to link to...
cameraChoiceKnob = nuke.Enumeration_Knob('cameras', 'Select Camera: ', cameras)
GroupNode.addKnob(cameraChoiceKnob)
cameraChoiceKnob.setFlag(nuke.STARTLINE)
# Finish operating inside Group node...
GroupNode.end()



###############################################################################################
####----------------------------------------------------------------------------------------
#### ---- These expressions go in knobs of the 'BKGND_IMAGE_CARD' node "Card" tab, inside the Group node...


## lens-in focal ---------------------------------
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('focal')

ret = CameraKnob.value()
## -----------------------------------------------


## lens-in haperture -----------------------------
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('haperture')

ret = CameraKnob.value()
## -----------------------------------------------


## -----------------------------------------------
## translate x 
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('translate')

ret = CameraKnob.value()[0]
## translate y 
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('translate')

ret = CameraKnob.value()[1]
## translate z 
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('translate')

ret = CameraKnob.value()[2]
## -----------------------------------------------


## -----------------------------------------------
## rotate x 
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('rotate')

ret = CameraKnob.value()[0]
## rotate y
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('rotate')

ret = CameraKnob.value()[1]
## rotate z
Node = nuke.toNode('Image_Locked_to_Camera')
Knob = Node.knob('cameras')

selected_camera = Knob.value()

CameraNode = nuke.toNode(selected_camera)
CameraKnob = CameraNode.knob('rotate')

ret = CameraKnob.value()[2]
## -----------------------------------------------
