########################################################################################################################
########################################################################################################################
########################################################################################################################
#
#          The Group's Hidden knobChanged Knob:
#
#   The code in the section below gets assigned to the Group node's hidden knobChanged knob.
#
#   -- Copy and paste the code below into Nuke's Script Editor.
#   -- Select the Group node and evaluate all of it.
#
########################################################################################################################
########################################################################################################################
########################################################################################################################


code = '''
import operator
GroupNode = nuke.thisNode()
Knob = nuke.thisKnob()

# The list of Write nodes in the group...
try:
    Writes = [node for node in GroupNode.nodes() if node.Class() == 'Write']
    # Use the render_order of the Writes to identify which one has the afterRender callback in its Python tab...
    # Dictionary of Writes, ordered by render_order, to find last Write that holds the afterRender callback code...
    WritesOrderDict = {}
    for node in Writes:
        order = node['render_order'].value()
        WritesOrderDict[node] = order
    #print "WritesOrderDict --> ", WritesOrderDict
    # Sort by render_order value...
    sorted_WritesOrderDict = sorted(WritesOrderDict.items(), key=operator.itemgetter(1))
    #print "sorted_WritesOrderDict --> ", sorted_WritesOrderDict
    CallBackWriteNode = sorted_WritesOrderDict[-1][0]
    #print "CallBackWriteNode --> ", CallBackWriteNode.name()
except:
    pass

# The list of knobs to be checked...
ICC_KNOB = GroupNode.knob('ICC_knob')
PSD_KNOB = GroupNode.knob('create_PSD_files')
#DEL_KNOB = GroupNode.knob('delete_temp_files')
OUTPUT_KNOB = GroupNode.knob('dir_text')
PSD_FILE_KNOB = GroupNode.knob('PSD_filename')
VIEWS_KNOB = GroupNode.knob('views')
SCAN_KNOB = GroupNode.knob('scan_button')
RENDER_KNOB = GroupNode.knob('render_button')
SUBMIT_KNOB = GroupNode.knob('submit_to_deadline')
REPLACE_LAYERNAME_KNOB = GroupNode.knob('replace_layername')

# afterRender callbacks...
Callback_with_PSD = """import NukePSD.Nuke_to_PSD
NPSD = NukePSD.Nuke_to_PSD.NukePSD()
NPSD._run_write_data_file()
NPSD._run_JS_command()"""

Callback_no_PSD = """import NukePSD.Nuke_to_PSD
NPSD = NukePSD.Nuke_to_PSD.NukePSD()
NPSD._run_write_data_file()"""

if len(nuke.views()) > 1:
    PSD_FILE_KNOB.setValue("Not used for multiple views. View name is used, instead.")
    PSD_FILE_KNOB.setEnabled(False)
elif len(nuke.views()) == 1:
    PSD_FILE_KNOB.setEnabled(True)

#-------------------------------------------------------------------------
if Knob == ICC_KNOB:
    for WriteNode in Writes:
        WriteNode['ICC_knob'].setValue(Knob.value())

#-------------------------------------------------------------------------
if Knob == RENDER_KNOB:
    if PSD_KNOB.value() == 'now, on render completion':
        try:
            CallBackWriteNode['afterRender'].setValue(Callback_with_PSD)
        except:
            pass
    elif PSD_KNOB.value() == 'later, with post process function':
        try:
            CallBackWriteNode['afterRender'].setValue(Callback_no_PSD)
        except:
            pass

    try:
        for WriteNode in Writes:
            WriteNode['views'].setValue(VIEWS_KNOB.value())
    except:
        pass

    if nuke.modified():
        if nuke.ask("Your script has been modified. 'Save As' before rendering?"):
            nuke.scriptSaveAs()
        else:
            pass

    try:
        del nuke.__dict__["_afterRenderCount"]
    except:
        pass

    import NukePSD.Nuke_to_PSD_Group
    reload(NukePSD.Nuke_to_PSD_Group)

    check = NukePSD.Nuke_to_PSD_Group._pre_render_sanity_checks()
    if check:
        NukePSD.Nuke_to_PSD_Group._render_write_nodes()
    else:
        print "Pre-render check failed!"
        nuke.critical('Pre-render check failed!')

#-------------------------------------------------------------------------
if Knob == SUBMIT_KNOB:
    if PSD_KNOB.value() == 'now, on render completion':
        try:
            CallBackWriteNode['afterRender'].setValue(Callback_no_PSD)
        except:
            pass
    elif PSD_KNOB.value() == 'later, with post process function':
        try:
            CallBackWriteNode['afterRender'].setValue(Callback_no_PSD)
        except:
            pass

    try:
        for WriteNode in Writes:
            WriteNode['views'].setValue(VIEWS_KNOB.value())
    except:
        pass    

    if nuke.modified():
        if nuke.ask("Your script has been modified. 'Save As' before rendering?"):
            nuke.scriptSaveAs()
        else:
            pass

    PNG_DIR = OUTPUT_KNOB.value()

    import NukePSD.Nuke_to_PSD_Group
    reload(NukePSD.Nuke_to_PSD_Group)

    check = NukePSD.Nuke_to_PSD_Group._pre_render_sanity_checks()
    if check:
        import NukePSD.Nuke_to_PSD_Submitter
        reload(NukePSD.Nuke_to_PSD_Submitter)
        NukePSD.Nuke_to_PSD_Submitter.Nuke_to_PSD_SubmitPanel(PNG_DIR, GroupNode).show()

#-------------------------------------------------------------------------
if Knob == OUTPUT_KNOB or Knob == SCAN_KNOB:
    try:
        OutputDir = OUTPUT_KNOB.value()

        if OutputDir:
            if OutputDir.endswith('/'):
                pass
            else:
                OutputDir = OutputDir + '/'

            for WriteNode in Writes:
                ShuffleNode = WriteNode.input(0)
                layername = ShuffleNode['in'].value()
                # We're only using one view, most likely the default, "main"...
                if len(nuke.views()) == 1:
                    WriteNode['file'].setValue(OutputDir + 'PNG' + '/' + layername + '/' + layername + '_%04d' + '.png')
                # We're using multiple views...
                elif len(nuke.views()) > 1:
                    WriteNode['file'].setValue(OutputDir + 'PNG' + '/' + '%V' + '/' + layername + '/' + layername + '_%04d' + '.png')
        else:
            for WriteNode in Writes:
                WriteNode['file'].setValue('')
    except:
        raise

#-------------------------------------------------------------------------
if Knob == VIEWS_KNOB:
    try:
        for WriteNode in Writes:
            WriteNode['views'].setValue(VIEWS_KNOB.value())
    except:
        pass

if GroupNode['disable']:
    try:
        for node in Writes:
            node['disable'].setValue(GroupNode['disable'].value())
    except:
        pass
'''


Node = nuke.selectedNode()
Knob = Node.knob('knobChanged')
Knob.setValue(code)