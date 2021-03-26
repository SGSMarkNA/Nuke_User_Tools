import nuke
import re
import thread

# A global dictionary of the current collections of nodes, grouped by node class.
# These values are set by the selections in each master node control's NODE FILTERS...
CollectedNodesDict = {}


def MasterControlNodes(knb_event=False):
    '''
    Creates a master control panel node that can set values on knobs of other nodes that are of the same class.
    Changes to the master control node will affect any "Selected" nodes of the same class or "All" nodes of the same class.
    The selected nodes can be selected from the "Entire Script" or the "Current Node Graph Only".

    Here is a sample menu.py entry to add a menu command to Nuke:
    import Nodes_Master_Control_Panel.MasterControlNodes
    nodeMenu=nuke.menu('Nuke')
    m = nodeMenu.addMenu("Test")
    m.addCommand('Test', 'Nodes_Master_Control_Panel.MasterControlNodes.MasterControlNodes()')

    Created by Rich Bobo - 09/24/2014
    richbobo@mac.com
    http://richbobo.com
    '''
    # Initially, set the knb_event flag to False for the first pass through the main wrapper function.
    # That way, values can be set and the master control panel node can be created *before* any knob events are registered.
    # In the hidden knobChanged knob on the master control panel, knb_event is always set to True. That ensures that
    # only the Control_Nodes() function section of the main wrapper function is run when any knob events happen...

    ##-------------------------------------------------
    ## CREATE NODE CLASS SELECTOR PANEL...
    ##-------------------------------------------------
    def SelectPanel():
        '''
        Panel to select the type of node class to be controlled...
        '''
        # Default node class choice...
        NodeClassChoice = 'Write'

        p = nuke.Panel('MASTER CONTROL SELECTOR')
        p.addEnumerationPulldown('Select Node Class to Control: ', ' '.join([NodeClassChoice, 'Write', 'Read', 'Blur', 'Crop', 'Erode', 'Merge2', 'Reformat', 'Transform', 'ColorCorrect', 'Grade', 'Camera2', 'Axis2', 'ScanlineRender', 'ZDefocus2', 'Position']))
        p.addSingleLineInput('OR - Type the Class name: ', '')

        # Set the width of the panel...
        p.setWidth(300)

        # Show the panel...
        if not p.show():
            return False

        # Assign selected value:
        # If the user types in a class name, use that. Otherwise, use the pulldown value...
        if p.value('OR - Type the Class name: ') != '':
            NodeClassChoice = p.value('OR - Type the Class name: ')
            print NodeClassChoice
        else:
            NodeClassChoice = p.value('Select Node Class to Control: ')
            print NodeClassChoice

        return NodeClassChoice

    ##-------------------------------------------------
    ## Node Filtering Methods...
    ##-------------------------------------------------
    def recursiveFindNodes(nodeClass, startNode):
        '''
        Recursive node class find method from Drew Loveridge. I added a nodeClass argument for use with this script...
        EXAMPLE USAGE:
            for d in recursiveFindNodes("Dot", nuke.root()):
                print d.name()
        '''
        if startNode.Class() == nodeClass:
            yield startNode
        elif isinstance(startNode, nuke.Group):
            for child in startNode.nodes():
                for foundNode in  recursiveFindNodes(nodeClass, child):
                    yield foundNode

    def collectClassNodes(Choice):
        '''
        Collect all of the nodes of a certain Class in the entire script, including all Groups...
        '''
        class_nodes = []

        for n in  recursiveFindNodes( Choice, nuke.root()):
            class_nodes.append(n)
        return class_nodes

    def getAllSelectedClassNodes(topLevel, Choice):
        '''
        Recursively return all the Selected Read nodes in the script, starting at topLevel...
        Looks in all groups. Default topLevel to use is nuke.root()
        '''
        # Get all of the nodes in the script...
        allNodes = nuke.allNodes(group=topLevel)
        for n in allNodes:
            allNodes = allNodes +  getAllSelectedClassNodes(n, Choice)
        # Get just the ones that are selected...
        allSelectedNodes = []
        for n in allNodes:
            if n.knob('selected').value() == True and n.Class() ==  Choice:
                allSelectedNodes.append(n)
        return allSelectedNodes

    def getNodeFilterSettings(Choice, nodesChoice, searchScope):
        '''
        Look at the knob selections and set the node filter selections...
        '''
        if  searchScope.value() == "Entire Script":
            if  nodesChoice.value() == "All":
                CollectedNodes =  collectClassNodes(Choice)
            elif  nodesChoice.value() == "Selected":
                CollectedNodes =  getAllSelectedClassNodes(nuke.root(), Choice)
        elif  searchScope.value() == "Current Node Graph Only":
            if  nodesChoice.value() == "All":
                CollectedNodes = [n for n in nuke.allNodes() if n.Class() ==  Choice]
            elif  nodesChoice.value() == "Selected":
                CollectedNodes = [n for n in nuke.allNodes() if n.Class() ==  Choice and n.knob('selected').value() == True]
        # Remove the master control node from the list of nodes to process...
        for n in CollectedNodes:
            if "MASTER_CONTROL_" in n.name():
                CollectedNodes.remove(n)
        return CollectedNodes

    ##-------------------------------------------------
    ## These two functions are necessary to prevent threading complaints from Nuke
    ## when trying to activate all of the collected nodes' reload buttons at the same time...
    def do_reload(node):
        node.knob('reload').execute()

    def do_reload_with_thread(node):
        nuke.executeInMainThread(do_reload, (node,))
        print node.name() + ' reloaded'
    ##-------------------------------------------------

    ##-------------------------------------------------
    ## Main function that is run by the hidden knobChanged knob on the master control node.
    ## Processes knobs and knob values generated by the master control node's knobChanged events.
    ## Sets values for knobs on the selected nodes of the same class as the master control node.
    ##-------------------------------------------------
    def Control_Nodes():
        '''
        This function is run via the master control panel's hidden knobChanged knob.
        When there's a knobChanged event on the master control panel, the knob name and value are assigned to variables - thisNode, thisKnob, etc....
        Any undesired knob events get filtered out by the list of knobs_to_ignore. A selection of same class nodes are filtered into a collection...
        Each node in the collection has its corresponding knob value set to the same value as that of the master control node...
        '''
        # The global dictionary stores lists of selected nodes by each master control node. It gets created once and then only updated after that...
        global CollectedNodesDict

        # Assign variables to the current master control node-knob event...
        this_node = nuke.thisNode()
        this_class = nuke.thisNode().Class()
        knob_name = nuke.thisKnob().name()
        knob_value = nuke.thisKnob().value()

        # After the initial SelectPanel node class selection is made by the user, all subsequent changes to the
        # node class value are set here, based on the class of the node that originated the knob event...
        Choice = this_class

        # The value of the "Scope:" node filter selection - "Entire Script" or "Current Node Graph Only".
        searchScope = nuke.thisNode().knob('scope')

        # The value of the "Nodes:" node filter selection - "All" or "Selected".
        nodesChoice = nuke.thisNode().knob('nodes')

        # Run the getNodeFilterSettings() function that sets the selection of nodes to control, based on all of the node filter knob settings...
        CollectedNodes = getNodeFilterSettings(Choice, nodesChoice, searchScope)

        # Add the collection of class nodes to the CollectedNodesDict. If there's already a list with the same name there, its members will be updated to reflect the current selection...
        CollectedNodesDict[this_class] = CollectedNodes

        # Ignore changes to knobs we want to filter out...
        knobs_to_ignore = ['executing', 'help', 'onCreate', 'onDestroy', 'updateUI', 'autolabel', 'knobChanged', 'panel', 'selected', 'xpos', 'ypos', 'icon', 'indicators', 'showPanel', 'hidePanel', 'nodes', 'scope', 'Main_Tab']

        if this_node:
            if this_class:
                # Get the class-based collection of nodes to be processed...
                ClassNodes = CollectedNodesDict.get(this_class)
                if knob_name not in knobs_to_ignore:
                    if ClassNodes:
                        for node in ClassNodes:
                            if knob_name == "reload":
                                # Push the reload button on all of the selected nodes.
                                # Do it as a thread, though, because Nuke complains saying,
                                # "I'm already executing something..."
                                thread.start_new_thread(do_reload_with_thread, (node,))
                            else:
                                node.knob(knob_name).setValue(knob_value)
                    else:
                        print "No Nodes Selected..."
                        nuke.message("No Nodes Selected...")
                else:
                    pass
    ##-------------------------------------------------
    ## CREATE MASTER CONTROL PANEL WITH TAB FOR NODE FILTERING KNOBS...
    ##-------------------------------------------------
    if not knb_event:
        # knb_event=False. On the first pass through the main wrapper function, knb_event=False, so only set values and create the control panel - Don't process any knob events.

        # Select the master control node class to be built, via a panel.
        # After this, the Choice value (node class) will be determined by the class of node generating the knob event.
        # Doing so allows multiple master control nodes of different classes to co-exist.
        Choice = SelectPanel()
        if Choice == False:
            return

        # Strip out any illegal characters in the node class name...
        pattern = re.compile(r'[^\w]')
        clean_Choice = pattern.sub('_', Choice)

        # Create the master control class node...
        createMasterControl = 'nuke.nodes.%s(name="MASTER_CONTROL_%s", tile_color="4278190080", note_font="Verdana Bold Italic", note_font_size="20.0", note_font_color="4294967040")' % (Choice, clean_Choice)
        Master_Control = eval(createMasterControl)

        # Create the knobs...
        X = nuke.Tab_Knob('', '')	## Note: This knob is a "sacrificial" Tab_Knob, to workaround the problem of the first tab added, always being named "User"...
        Main_Tab = nuke.Tab_Knob('main_tab', 'NODE FILTERS')
        Choice_BeginGroup = nuke.Text_Knob('choice_BeginGroup', 'NODE FILTERING:')
        nodesChoice = nuke.Enumeration_Knob('nodes', 'Nodes: ', ['All', 'Selected'])
        nodesChoice.setTooltip('Choose to perform action on All nodes or only the Selected ones.')
        searchScope = nuke.Enumeration_Knob('scope', 'Scope: ', ['Entire Script', 'Current Node Graph Only'])
        searchScope.setTooltip('Choose whether to perform the action on all the filtered nodes in the entire script or only on the current node graph (either the main node graph or another group that you are viewing).')
        divider1 = nuke.Text_Knob('')
        divider2 = nuke.Text_Knob('')
        info = nuke.Multiline_Eval_String_Knob('info', 'INFO:', 'Select the nodes to be controlled via the filters above. The default selection filter is to control all of the same type of node in the entire script, including any groups.\n\nUse the controls in the other tabs, as usual, to set values for the filtered collection of nodes.\n\nNote that for some knobs, such as checkboxes, you may have to click it more than once to set the value. That is because there is no starting value, since all nodes could have different values to begin with.\n\nYou can create multiple controllers, as long as there aren\'t more than one of each class of node.' )
        # Add knobs to the panel...
        Master_Control.addKnob(X)
        Master_Control.addKnob(Main_Tab)
        Master_Control.addKnob(Choice_BeginGroup)
        Master_Control.addKnob(nodesChoice)
        Master_Control.addKnob(searchScope)
        Master_Control.addKnob(divider1)
        Master_Control.addKnob(divider2)
        Master_Control.addKnob(info)
        Master_Control.removeKnob(X)	## Remove the sacrificial Tab_Knob to please the gods of Nukedom...

        # Because I am using the name string ("MASTER_CONTROL_") of the master control node as a way to identify it (rather than a custom node class), I am locking out any name editing...
        Master_Control.knob('name').setFlag(nuke.READ_ONLY)

        # No editing of the INFO text...
        Master_Control.knob('info').setFlag(nuke.READ_ONLY)

        # Float the panel, so it's more obvious to the user...
        Master_Control.showControlPanel(forceFloat=True)

        # This hack forces the NODE FILTERS knob to be the active tab...
        Master_Control.knob('main_tab').setFlag(0)

        # Show the control panel...
        Master_Control.showControlPanel()

        # Set the hidden "knobChanged" knob to the Control_Nodes() function. (This is where the "magic" happens!)
        # The Control_Nodes() function is set up to return the name and value of any knob that is changed in the master control knob.
        # There is also a "knobs_to_ignore" list that acts as a filter, so that only meaningful knobs are used to set the values on the node collection...
        ## NOTE: This needs to be triple-quoted, with an actual newline and no tabs. I.e., leave it as is!
        Master_Control.knob('knobChanged').setValue('''import Nodes_Master_Control_Panel.MasterControlNodes
Nodes_Master_Control_Panel.MasterControlNodes.MasterControlNodes(knb_event=True)''')	

    else:
        # knb_event=True. The second and subsequent passes of the main function are triggered by the hidden "knobChanged" knob
        # on the master control panel, which sets knb_event to True. As a result, only the Control_Nodes() function is executed...
        try:
            Control_Nodes()
        except ValueError:
            # This catches errors that can occur when exiting Nuke. The knobChanged function fires on the master control nodes
            # as Nuke is closing the panels. Certain referenced PythonObjects have already been destroyed, causing ValueErrors...
            pass



