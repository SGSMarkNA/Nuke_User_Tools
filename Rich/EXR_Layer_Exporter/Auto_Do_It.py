##----------------------------------------------------------------------------------------------------------------------
##
##          'Automatic' TAB of the Group Node's 'Do it.' PyScript Button:
##
##   The code in the section below gets copied and pasted into the 'Do it.' button (PyScript_Knob) of the Group node.
##
##----------------------------------------------------------------------------------------------------------------------

import os
import nuke
import EXR_Layer_Exporter.EXR_ValidLayers_Checker as LayersChecker
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

def _directory_path_check():
    '''
    Make sure the destination directory path is of the correct form...
    '''
    destDir = GroupNode.knob('dest_dir').value()
    if destDir:
        # Check to make sure a file path is not passed through.
        # If splitext [1] result is empty, we're good...
        if os.path.splitext(destDir)[1] == '':
            # Make sure target path ends with a slash (for consistency)
            if not destDir.endswith('/'):
                destDir += '/'
            # Put the reformatted directory path back in the knob...
            GroupNode.knob('dest_dir').setValue(destDir)
        else:
            temp_dir = os.path.splitext(destDir)
            destDir = os.path.dirname(temp_dir[0])          
            # Make sure target path ends with a slash (for consistency)
            if not destDir.endswith('/'):
                destDir += '/'
            # Put the reformatted directory path back in the knob...
            GroupNode.knob('dest_dir').setValue(destDir)
            if nuke.ask('Filename not allowed.\nPath has been changed to a directory format.\nPlease re-check for correctness.\n\nContinue?'):
                pass
            else:
                destDir = False
    # Return the chosen directory path...
    return destDir    

def _cleanup_nodes():
    '''Remove any leftover group nodes...'''
    try:
        for Node in GroupNode.nodes():
            if Node.Class() == ('Input'):
                pass
            elif Node.Class() == ('Output'):
                pass
            else:
                nuke.delete(Node)      
    except ValueError:
        print 'Value Error: Check in Group for nodes that were not deleted...'        

def _write_layers_to_separate_files(ConnectedNode, destDir, FileType=''):
    ''''''

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

    # Get only the non-empty layers...
    layers = LayersChecker.EXR_ValidLayers_Checker(InputNode)[0]

    # Get the selected image file type to render...
    FileType = GroupNode.knob('filetype').value()

    for layer in layers:
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
                    nuke.critical('Cancelled.\nCheck for any .tmp files that may remain in the output folder...')
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
                    nuke.critical('Cancelled.\nCheck for any .tmp files that may remain in the output folder...')
                    return
                else:
                    _cleanup_nodes()
                    nuke.critical('nuke.executeMultiple failed. Exported images are probably OK, though.\nCheck for last .tmp file that may not have been deleted...')
                    return
    else:
        nuke.critical('Only one rgba layer in EXR file!')
        return None 

    # Cleanup remaining nodes...
    _cleanup_nodes()

    GroupNode.end()

def _write_consolidated_EXR_layers_to_single_file(ConnectedNode, destDir):
    ''''''
    # ICC Profile to add to image...
    ICC_Profile_Name = GroupNode.knob('icc_profile').value()

    # Start working inside the Group's context...
    GroupNode.begin()

    # Remove any leftover group nodes...
    _cleanup_nodes()    

    # The Input node inside the Group, which is connected to the Read node on the Group's input...
    InputNode = nuke.toNode('Input1')

    # Get the valid and the empty layers...
    layers_check = LayersChecker.EXR_ValidLayers_Checker(InputNode)
    layers_to_export = layers_check[0]
    layers_to_remove = layers_check[1]

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
            nuke.critical('Cancelled.\nCheck for any .tmp files that may remain in the output folder...')
            return

    # Remove existing internal group nodes...
    _cleanup_nodes()

    GroupNode.end()

#------------------------------------------------------------------------
# RUN IT...
def run_it():
    ConnectedNode = _input_check()
    if ConnectedNode:
        destDir = _directory_path_check()
        if destDir:
            if GroupNode.knob('exr_consolidate').value() == True:
                _write_consolidated_EXR_layers_to_single_file(ConnectedNode, destDir)
            else:
                # Get the selected image file type to render...
                FileType = GroupNode.knob('filetype').value()        
                _write_layers_to_separate_files(ConnectedNode, destDir, FileType)
        else:
            nuke.message('Please provide a destination directory.')