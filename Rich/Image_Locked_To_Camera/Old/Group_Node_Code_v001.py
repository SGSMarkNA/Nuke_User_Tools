import nuke
import re

GroupNode = nuke.thisNode()

################################################################
RootNode = nuke.Root()
# Make sure we're operating inside the Root group...
RootNode.begin()
# Get a list of all the cameras...
cameras = []
for node in (nuke.allNodes('Camera') + nuke.allNodes('Camera2')):
    cameras.append(node.name())
RootNode.end()
print cameras
################################################################

## Get all the knobs in the Group...
GroupNodeKnobs = GroupNode.allKnobs()
#print 'GroupNodeKnobs', GroupNodeKnobs

# Make sure we're operating inside the GroupNode...
GroupNode.begin()

# Set up some variables for removal of preexisting knobs when the 'Pick Camera' button is pressed...
knobs_to_remove = []
knobs_to_ignore = ['selected', 'hide_input', 'cached', 'dope_sheet', 'bookmark', 'postage_stamp', 'useLifetime', 'lock_connections']
## Make a list of any pulldown (Enumeration_Knob) knobs...
regex = re.compile(r"\Enumeration_Knob\W")   # \W is anything but a word character...
for knob in GroupNodeKnobs:
    if bool(regex.search(str(type(knob)))):
        if knob.name() not in knobs_to_ignore:
            name = knob.name()
            knobs_to_remove.append(name)
        else:
            pass
print 'knobs_to_ignore', knobs_to_ignore
print 'knobs_to_remove', knobs_to_remove

## Remove existing pulldown knob when the 'Pick Camera' PyScript button is pressed, before we make a new one...
Knobs = GroupNode.knobs()
try:
    for knobname in knobs_to_remove:
        GroupNode.removeKnob(Knobs[knobname])
except KeyError:
    print 'Key Error: Some nonexistant knobs could not be removed.'
except ValueError:
    print 'Value Error: Some nonexistant knobs could not be removed.'

# Build selector to pick the camera to link to...
cameraChoiceKnob = nuke.Enumeration_Knob('cameras', 'Select Camera: ', cameras)
print cameraChoiceKnob, cameraChoiceKnob.value(), cameraChoiceKnob.name()
GroupNode.addKnob(cameraChoiceKnob)
cameraChoiceKnob.setFlag(nuke.STARTLINE)

GroupNode.end()
