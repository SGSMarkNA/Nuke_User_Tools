# Usage: run printKnobs()

import nuke

def printKnobs():

    try:
        p = nuke.Panel('printKnobs 2.0')
        p.setWidth(800)
        
        knob_data = ''
        knobs_list = []
        knobs_result = ''
        
        for node in nuke.selectedNodes():
            for knob in nuke.selectedNode().allKnobs():
                knob_data = str(type(knob)) + '  |  ' + knob.name() + '  |  ' + 'value=' + str(knob.value()) + '  |  ' + str(type(knob.value()))
                knobs_list.append(knob_data)
        knobs_result = ('\n ').join(knobs_list)
        
        p.addMultilineTextInput(node.name() + ' data', knobs_result )
        p.show()
        
    except UnboundLocalError:
        nuke.message('No node selected?')