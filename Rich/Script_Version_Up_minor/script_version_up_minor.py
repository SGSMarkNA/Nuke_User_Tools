import nuke
import nukescripts

def script_version_up_minor():
  '''
  Adds 1 to the _x## at the end of the script name and saves a new version.
  This adds the ability to use a major_minor type of filename template, such as myscript_v004_x008.nk
  You can use a shortcut key combination to run this function and increment the _x### or "minor" portion of the script name,
  independently of the default _v### or "major" version number. The user can then make incremental working copy saves - prior
  to saving a new major version...
  '''
  root_name = nuke.toNode("root").name()
  (prefix, x) = nukescripts.version_get(root_name, "x")
  if x is None: return
  
  x = int(x)
  nuke.scriptSaveAs(nukescripts.version_set(root_name, prefix, x, x + 1))
  
  
  
  
  
'''
#### Original version up script from C:\Program Files\Nuke7.0v4\plugins\nukescripts\script.py

def script_version_up():
  """Adds 1 to the _v## at the end of the script name and saves a new version."""
  root_name = nuke.toNode("root").name()
  (prefix, v) = nukescripts.version_get(root_name, "v")
  if v is None: return
  
  v = int(v)
  nuke.scriptSaveAs(nukescripts.version_set(root_name, prefix, v, v + 1))


'''