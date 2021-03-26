import nuke, os, errno

####________________________________________________________________________
#### Custom Write node with code for automatically creating output directories...
def Custom_Write_Node():
  nuke.createNode('Write', 'beforeFrameRender "%s"' %'def createWriteDirs():\n  import nuke, os, errno\n  file = nuke.filename(nuke.thisNode())\n  dir = os.path.dirname( file )\n  osdir = nuke.callbacks.filenameFilter( dir )\n  try:\n    os.makedirs( osdir )\n  except OSError, e:\n    if e.errno != errno.EEXIST:\n      raise\nnuke.addBeforeFrameRender(createWriteDirs)')
####________________________________________________________________________
