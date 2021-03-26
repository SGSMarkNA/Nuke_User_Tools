##----------------------------------------------------------------------------------------------------------------------
##
##          'Manual' TAB of the Group Node's 'Invert Selected' PyScript Button:
##
##   The code in the section below gets loaded into the 'Invert Selected' button (PyScript_Knob) of the Group node
##   by the Manual_Scan.py code.
##
##----------------------------------------------------------------------------------------------------------------------

def invertSelection_checkbox_knobs():
    import nuke
    import re
    GroupNode = nuke.thisNode()
    # Make a list of all the checkbox knobs (Boolean_Knob)...
    checkboxKnobs = []
    # Also, make sure to ignore the exr_consolidate knob on the Automatic tab...
    knobs_to_ignore = ['exr_consolidate', 'exr_consolidate2', 'selected', 'hide_input', 'cached', 'dope_sheet', 'bookmark', 'postage_stamp', 'useLifetime', 'lock_connections']
    # Make a list of any checkbox (Boolean_Knob) knobs...
    regex = re.compile(r"\WBoolean_Knob\W")   # \W is anything but a word character...
    # Start with a list of all the Group's knobs...
    AllKnobs = GroupNode.knobs()
    for name, knob in AllKnobs.iteritems():
        if bool(regex.search(str(type(knob)))):
            if knob.name() not in knobs_to_ignore:
                name = knob.name()
                checkboxKnobs.append(knob)
            else:
                pass
    for knob in checkboxKnobs:
        if knob.value():
            knob.setValue(False)
        else:
            knob.setValue(True)
invertSelection_checkbox_knobs()





