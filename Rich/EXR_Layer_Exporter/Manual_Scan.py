##----------------------------------------------------------------------------------------------------------------------
##
##          'Manual' TAB of the Group Node's 'Scan' PyScript Button:
##
##   The code in the section below gets copied and pasted into the 'Scan' button (PyScript_Knob) of the Group node.
##
##----------------------------------------------------------------------------------------------------------------------
import os
import nuke
import re

# The Group node itself...
GroupNode = nuke.thisNode()

def _input_check():
    # Check if there's an EXR Read node connected to the Group's input...
    try:    
        ConnectedNode = GroupNode.input(0)
        if (ConnectedNode.Class() == 'Read') and (os.path.splitext(nuke.filename(ConnectedNode))[-1] == ".exr"):  
            return ConnectedNode
        else:
            nuke.message("Please connect an EXR file to the input!")
            return False
    except AttributeError:
        nuke.message("Please connect an EXR file to the input!")
        return False

def run_it():   
    # Get all the knobs in the Group...
    GroupNodeKnobs = GroupNode.allKnobs()

    ConnectedNode = _input_check()
    print ConnectedNode
    #----------------------------------------------------------------------
    #                 LAYER DETECTION
    #----------------------------------------------------------------------
    # Get all the layers contained in an EXR image file and put them into a layers list...
    if ConnectedNode:
        try:
            channels = ConnectedNode.channels()
            layers = list(set([c.split('.')[0] for c in channels]))
            layers.sort()
        except NameError:
            nuke.message("No image channels found.")
            return
    else:
        return

    #----------------------------------------------------------------------
    #                KNOB REMOVALS
    #----------------------------------------------------------------------
    # Set up some variables for removal of preexisting checkbox knobs when the Scan button is pressed...
    checkboxes_to_remove = []
    # Also, make sure to ignore the exr_consolidate knob on the Automatic tab which should stay there...
    knobs_to_ignore = ['exr_consolidate', 'exr_consolidate2', 'selected', 'hide_input', 'cached', 'dope_sheet', 'bookmark', 'postage_stamp', 'useLifetime', 'lock_connections']
    # Make a list of any checkbox (Boolean_Knob) knobs...
    regex = re.compile(r"\WBoolean_Knob\W")   # \W is anything but a word character...
    for knob in GroupNodeKnobs:
        if bool(regex.search(str(type(knob)))):
            if knob.name() not in knobs_to_ignore:
                name = knob.name()
                checkboxes_to_remove.append(name)
            else:
                pass
    # Get all the knob objects...
    Knobs = GroupNode.knobs()
    # Remove any old checkboxes (Boolean_Knob) when the Scan button is pressed, before we make new ones...    
    for knobname in checkboxes_to_remove:
        try:
            GroupNode.removeKnob(Knobs[knobname])
        except ValueError:
            print 'Knob %s could not be removed...' % knobname
        except KeyError:
            print 'Knob %s could not be removed...' % knobname    

    # Also delete these additional knobs, so they don't multiply like rabbits... Removed in inverse creation order!
    more_knobs_to_remove = ['do_it2', 'press_the_button', 'newline5', 'icc_profile2', 'exr_consolidate2', 'filetype2', 'dest_dir2', 'step_three', 'newline2', 'invert_selection', 'select_all']
    for knobname in more_knobs_to_remove:
        try:
            GroupNode.removeKnob(Knobs[knobname])
        except ValueError:
            print 'Knob %s could not be removed...' % knobname
        except KeyError:
            print 'Knob %s could not be removed...' % knobname

    #----------------------------------------------------------------------
    #            ADD KNOBS
    #----------------------------------------------------------------------
    # Add knobs for 'Select All' and 'Invert Selection' checkboxes...
    select_all_button = nuke.PyScript_Knob('select_all', 'Select All', '''
def select_all_checkbox_knobs():
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
        knob.setValue(True)
select_all_checkbox_knobs()
''')
    GroupNode.addKnob(select_all_button)
    select_all_button.setFlag(nuke.STARTLINE)

    invert_selection_button = nuke.PyScript_Knob('invert_selection', 'Invert Selection', '''
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
''')
    GroupNode.addKnob(invert_selection_button)

    # Add new checkbox knobs, based on the layer names found in the input EXR Read node...
    checkboxKnobs = []
    try:
        if layers:
            for layer in layers:
                Knob_string = 'nuke.' + 'Boolean_Knob' + '(' + "'" + layer + "'" + ', ' + "'" + layer + "'" + ')'
                Knob = eval(Knob_string)
                GroupNode.addKnob(Knob)
                Knob.setFlag(nuke.STARTLINE)
                # Keep a list of all the created knobs for re-use...
                checkboxKnobs.append(Knob)
                print 'checkboxKnobs -->', checkboxKnobs
    except NameError:
        nuke.message("No image channels found.")

    newlineKnob2 = nuke.Text_Knob('newline2', '')
    GroupNode.addKnob(newlineKnob2)

    Step3Knob = nuke.Text_Knob('step_three', '3) Set the Image Parameters:')
    GroupNode.addKnob(Step3Knob)

    destDir2 = nuke.File_Knob('dest_dir2', 'Output Directory:')
    GroupNode.addKnob(destDir2)

    fileType2 = nuke.Enumeration_Knob('filetype2', 'Image Type:', ['png', 'tif', 'jpg', 'exr', 'tga'])
    GroupNode.addKnob(fileType2)

    exrConsolidate2 = nuke.Boolean_Knob('exr_consolidate2', 'Consolidate Layers (Single EXR File)' )
    GroupNode.addKnob(exrConsolidate2)
    GroupNode.knob('exr_consolidate2').setEnabled(False)
    exrConsolidate2.setFlag(nuke.STARTLINE)

    iccProfile2 = nuke.Enumeration_Knob('icc_profile2', 'ICC Profile:', ['Empty', 'sRGB.icc', 'AdobeRGB1998.icc', 'REC709.icc', 'Rec2020.icc', 'ACESCG Linear.icc'])
    GroupNode.addKnob(iccProfile2)
    GroupNode.knob('icc_profile2').setValue('sRGB.icc')

    newline5 = nuke.Text_Knob('newline5', '')
    GroupNode.addKnob(newline5)

    PressTheButton = nuke.Text_Knob('press_the_button', '4) Press the "Do it." Button! :')
    GroupNode.addKnob(PressTheButton)

    DoIt2 = nuke.PyScript_Knob('do_it2', 'Do it.', '''
import nuke
import re
import CollectSourceFiles.SourceNodeInfo

# Initialize the NodeInfo class to get parameters from the Read node...
Source = CollectSourceFiles.SourceNodeInfo.NodeInfo()

#------------------------------------------------------------------------

# The Group node itself...
GroupNode = nuke.thisNode()

def _input_check():
    # Check if there's an EXR Read node connected to the Group's input...
    try:    
        ConnectedNode = GroupNode.input(0)
        if (ConnectedNode.Class() == 'Read') and (os.path.splitext(nuke.filename(ConnectedNode))[-1] == ".exr"):  
            return ConnectedNode
        else:
            nuke.message("Please connect an EXR file to the input!")
            return False
    except AttributeError:
        nuke.message("Please connect an EXR file to the input!")
        return False

def _get_layers(ConnectedNode):
    # Get the layers from the EXR...
    channels = ConnectedNode.channels()
    #print 'channels', channels
    layers = list(set([c.split('.')[0] for c in channels]))
    layers.sort()
    return layers

def _get_checkbox_knobs():
    # Make a list of all the checkbox knobs (Boolean_Knob)...
    checkboxKnobsDict = {}
    checkboxKnobs = []
    # Also, make sure to ignore the exr_consolidate knob on the Automatic tab...
    knobs_to_ignore = ['exr_consolidate', 'exr_consolidate2', 'selected', 'hide_input', 'cached', 'dope_sheet', 'bookmark', 'postage_stamp', 'useLifetime', 'lock_connections']
    # Make a list of any checkbox (Boolean_Knob) knobs...
    regex = re.compile(r"\WBoolean_Knob\W")   # \W is anything but a word character...
    # Start with a list of all the Group's knobs...
    AllKnobs = GroupNode.knobs()
    for name, knob in AllKnobs.iteritems():
        #print name, knob
        if bool(regex.search(str(type(knob)))):
            if knob.name() not in knobs_to_ignore:
                name = knob.name()
                #print name
                checkboxKnobsDict[name] = knob
            else:
                pass
    #print 'checkboxKnobsDict', checkboxKnobsDict
    return checkboxKnobsDict

def _directory_path_check():
    destDir = GroupNode.knob('dest_dir2').value()
    if destDir:
        # Check to make sure a file path is not passed through.
        # If splitext [1] result is empty, we're good...
        if os.path.splitext(destDir)[1] == '':
            # Make sure target path ends with a slash (for consistency)
            if not destDir.endswith('/'):
                destDir += '/'
            # Put the reformatted directory path back in the knob...
            GroupNode.knob('dest_dir2').setValue(destDir)
        else:
            temp_dir = os.path.splitext(destDir)
            destDir = os.path.dirname(temp_dir[0])          
            # Make sure target path ends with a slash (for consistency)
            if not destDir.endswith('/'):
                destDir += '/'
            # Put the reformatted directory path back in the knob...
            GroupNode.knob('dest_dir2').setValue(destDir)
            if nuke.ask('Filename not allowed. Path has been changed to a directory format. Please re-check for correctness. Continue?'):
                pass
            else:
                destDir = False
    # Return the chosen directory path...
    return destDir

def _cleanup_nodes():
    try:
        for Node in GroupNode.nodes():
            if Node.Class() == ('Input'):
                pass
            elif Node.Class() == ('Output'):
                pass
            else:
                nuke.delete(Node)      
    except ValueError:
        print "Value Error: Check in Group for nodes that were not deleted..."

def _write_layers_to_separate_files(ConnectedNode, destDir, FileType=''):

    # ICC Profile to add to image...
    ICC_Profile_Name = GroupNode.knob('icc_profile').value()

    # Start working inside the Group's context...
    GroupNode.begin()

    # Remove any leftover group nodes...
    _cleanup_nodes()

    # The Input node inside the Group, which is connected to the Read node on the Group's input...
    InputNode = nuke.toNode('Input1')

    WriteNodes = []
    ShuffleNodes = []

    # Build a dict of the checkbox names and their respective knob objects...
    checkboxKnobsDict = _get_checkbox_knobs()

    # Get a list of all the layers...
    layers = _get_layers(ConnectedNode)

    # Initialize the user-selected layers...
    layers_to_export = []
    layers_to_remove = []

    # Create a dict that will contain all the checkbox names and their knob objects (and eventually their boolean value)...
    checkboxesDict = {}
    for checkbox, knob in checkboxKnobsDict.iteritems():
        knob_value = knob.value()
        checkboxesDict[checkbox] = knob_value
    for knobname, value in checkboxesDict.iteritems():
        if value == True:
            # Build a list of layers_to_export by getting the corresponding layer object from layers...by using the checkbox knobnames...
            layers_to_export.append(knobname)
    if not layers_to_export:
        nuke.message('Please select some layers for export!')
        return
    else:
        for layer in layers:
            if layer not in layers_to_export:
                layers_to_remove.append(layer)

    # Get the selected image file type to render...
    FileType = GroupNode.knob('filetype2').value()

    for layer in layers_to_export:
        ShuffleNode = nuke.createNode('Shuffle', inpanel=False)
        ShuffleNode.knob('in').setValue(str(layer))
        # Make sure the Shuffle node's input is connected to the Group's Input node...
        ShuffleNode.setInput(0, InputNode)
        ShuffleNodes.append(ShuffleNode)

        # Get original Read node's basename...
        Filename = Source.get_info(ConnectedNode)['FilenameForRelink']
        # Get first and last frame numbers from Read node...
        first = Source.get_info(ConnectedNode)['firstFrame']
        last = Source.get_info(ConnectedNode)['lastFrame']
        # Set the frame range to be rendered...
        FrameRange = [(int(first), int(last), 1)]        

        WriteNode = nuke.createNode('Write', inpanel=False)
        WriteNode.knob('file').setValue(str(destDir) + str(layer) + '_%04d' + '.' + FileType)
        WriteNode.knob('use_limit').setValue(True)
        WriteNode.knob('first').setValue(first)
        WriteNode.knob('last').setValue(last)
        # Make sure the Write node's input is connected to the Shuffle...
        WriteNode.setInput(0, ShuffleNode)
        # Add selected ICC Profile...
        WriteNode.knob('ICC_knob').setValue(ICC_Profile_Name)
        if layer is not 'rgba':
            WriteNode.knob('channels').setValue('rgb')
        else:
            WriteNode.knob('channels').setValue('rgba')
        WriteNodes.append(WriteNode)

    if WriteNodes:
        if len(WriteNodes) == 1:
            # Single Write node...
            # nuke.execute() takes a string for the node name...
            # EX: nuke.execute(nodes, ranges, views, continueOnError=False) -- views is optional.            
            try:
                nuke.execute(WriteNodes[0], first, last, 1)
            except RuntimeError as error:
                status = str(error)
                # Catch the user's Cancel button press...
                if "Cancelled" in status:
                    _cleanup_nodes()
                    nuke.critical('Cancelled. Check for any .tmp files that may remain in the output folder...')
                    return
        else:
            # Multiple Write nodes:
            # executeMultiple() takes a tuple of node objects...
            try:
                nuke.executeMultiple(tuple(WriteNodes), tuple(FrameRange))
            except RuntimeError as error:
                status = str(error)
                # Catch the user's Cancel button press...
                if "Cancelled" in status:
                    _cleanup_nodes()
                    nuke.critical('Cancelled.Check for any .tmp files that may remain in the output folder...')
                    return
                else:
                    _cleanup_nodes()
                    nuke.critical('nuke.executeMultiple failed. Exported images are probably OK, though. Check for last .tmp file that may not have been deleted...')
                    return
    else:
        nuke.critical('Only one rgba layer in EXR file!')
        return None 

    # Cleanup remaining nodes...
    _cleanup_nodes()

    # Finish Group operations...
    GroupNode.end()

def _write_consolidated_EXR_layers_to_single_file(ConnectedNode, destDir):

    # Start working inside the Group's context...
    GroupNode.begin()

    # Remove any leftover group nodes...
    _cleanup_nodes()    

    # The Input node inside the Group, which is connected to the Read node on the Group's input...
    InputNode = nuke.toNode('Input1')

    # Build a dict of the checkbox names and their respective knob objects...
    checkboxKnobsDict = _get_checkbox_knobs()

    # Get a list of all the layers...
    layers = _get_layers(ConnectedNode)

    # Initialize the user-selected layers...
    layers_to_export = []
    layers_to_remove = []

    # Create a dict that will contain all the checkbox names and their knob objects (and eventually their boolean value)...
    checkboxesDict = {}
    for checkbox, knob in checkboxKnobsDict.iteritems():
        knob_value = knob.value()
        checkboxesDict[checkbox] = knob_value
    for knobname, value in checkboxesDict.iteritems():
        if value == True:
            # Build a list of layers_to_export by getting the corresponding layer object from layers...by using the checkbox knobnames...
            layers_to_export.append(knobname)
    if not layers_to_export:
        nuke.message('Please select some layers for export!')
        return
    else:
        for layer in layers:
            if layer not in layers_to_export:
                layers_to_remove.append(layer)

    #----------------------------------------------------------------------
    # Calculate how many Remove nodes we need -- only 4 layers can be removed per node...
    # divmod returns a tuple with (quotient, remainder)...
    num_of_nodes = divmod(len(layers_to_remove), 4)
    if num_of_nodes[1] is 0:
        num_of_nodes = num_of_nodes[0]
    else:
        # We need one additional node for the remainder...
        num_of_nodes = num_of_nodes[0] + 1

    # We've only got a maximum of four channel removal knobs available on a Remove node...
    removal_knobs = ['channels', 'channels2', 'channels3', 'channels4']

    # Select the Input node, so the new nodes get attached after that...
    InputNode = nuke.toNode('Input1')
    InputNode.knob("selected").setValue(True)

    # Create the Remove nodes, based on the number of layers to be removed...
    for node in range(num_of_nodes):
        RemoveNode = nuke.createNode("Remove", inpanel = False)
        for knobname in removal_knobs:
            if layers_to_remove:
                layer = layers_to_remove.pop()
                RemoveNode[knobname].setValue(layer)

    #----------------------------------------------------------------------
    # Add a Crop node to make sure that Photoshop won't lose a pixel,
    # based on a misinterpretation of the bounding box...
    cropnode = nuke.createNode('Crop', inpanel = False)
    cropnode.knob('label').setValue('PHOTOSHOP FIX.')
    cropnode.knob('reformat').setValue(True)
    cropnode.knob('crop').setValue(True)

    # Get original Read node's basename...
    Filename = Source.get_info(ConnectedNode)['FilenameForRelink']
    # Get first and last frame numbers from Read node...
    first = Source.get_info(ConnectedNode)['firstFrame']
    last = Source.get_info(ConnectedNode)['lastFrame']
    # Set the frame range to be rendered...
    FrameRange = [(int(first), int(last), 1)]    

    WriteNode = nuke.createNode('Write', inpanel=False)
    # Get original Read node's basename...
    Filename = Source.get_info(ConnectedNode)['FilenameForRelink']
    WriteNode.knob('file').setValue(destDir + Filename)
    WriteNode.knob('use_limit').setValue(True)
    WriteNode.knob('first').setValue(first)
    WriteNode.knob('last').setValue(last)
    WriteNode.knob('channels').setValue('all')
    # Make sure the Write node's input is connected to the Shuffle...
    WriteNode.setInput(0, cropnode)

    # Execute() takes a string for the node name, executeMultiple() takes a tuple of node objects...
    # Single Write node...
    try:
        nuke.execute(WriteNode.name(), first, last, 1)
    except RuntimeError as error:
        status = str(error)
        if "Cancelled" in status:
            _cleanup_nodes()
            nuke.critical('Cancelled. Check for any .tmp files that may remain in the output folder...')
            return

    #----------------------------------------------------------------------
    # Remove existing internal group nodes...
    _cleanup_nodes()

    GroupNode.end()

#------------------------------------------------------------------------
# RUN IT...
try:
    ConnectedNode = _input_check()
    if ConnectedNode:
        destDir = _directory_path_check()
        if destDir:
            if GroupNode.knob('exr_consolidate2').value() == True:
                _write_consolidated_EXR_layers_to_single_file(ConnectedNode, destDir)
            else:
                # Get the selected image file type to render...
                FileType = GroupNode.knob('filetype2').value()        
                _write_layers_to_separate_files(ConnectedNode, destDir, FileType)
        else:
            nuke.message('Please provide a destination directory.')
except:
    nuke.message("Please connect an EXR file to the input!")
    ''')

    # Add the 'Do it.' button...
    GroupNode.addKnob(DoIt2)


