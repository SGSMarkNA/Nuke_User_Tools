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
