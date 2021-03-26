import nuke
import os
import errno

def ResaveWriteNode(node):
    #### Define pathname parts...
    script_path = nuke.filename(node)
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename( script_path)
    resave_dir = script_dir+'/resave/'
    resave_path = resave_dir+script_name
    
    #### Create Write node...
    w = nuke.nodes.Write(inputs = [node])
    w.knob('channels').setValue('all')
    w.knob('file').setValue( resave_path )
    w.knob('views').setValue('main')
    w.knob('file_type').setValue('exr')
    w.knob('selected').setValue(True)

    #### Create any missing /resave/ directories...
    if (os.path.isdir(resave_dir)):
        print "%s path exists, skipping..." %(resave_dir)
    else:
        try:
            os.makedirs(resave_dir)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        finally:
            print "%s - created output directory:\n %s" % (resave_path, resave_dir)

    #### Render Write node(s)...
    nuke.execute( w, node['first'].value(), node['last'].value() )
    
    #### Set Write node to "read file"...
    w.knob('reading').setValue(True)


def Resave_EXR_as_Zip1():
    if not nuke.selectedNodes():
        nuke.message("Please select an EXR Read node...")
        return
    for node in nuke.selectedNodes():
        ResaveWriteNode(node)


#### To run:
#      Resave_EXR_as_Zip1()


