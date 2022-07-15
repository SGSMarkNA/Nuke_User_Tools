import nuke, os

#### Function to create Write node output directories...
def Create_Write_Dirs_For_All_Write_Nodes():
	created = []
	skipped = []
	
	if nuke.ask("Do you want to create missing directories for all enabled Write nodes now...?"):
	
		for w in nuke.allNodes('Write'):
			name = nuke.Node.name(w)
			file = nuke.filename(w)
			if w['disable'].value() == True:
				print("%s is disabled, skipping..." % (name))
				skipped.append("%s -- disabled" % (name))
			elif not w.inputs():
				print("%s has no input, skipping..." % (name))
				skipped.append("%s -- no input connected" % (name))
			elif not file:
				print("%s has an empty output path, skipping..." % (name))
				skipped.append("%s -- empty output path" % (name))
			elif (os.path.isdir(os.path.dirname(file))):
				print("%s path exists, skipping..." %(name))
				skipped.append("%s -- directory exists" % (name))
			else:
				dir = os.path.dirname(file)
				osdir = nuke.callbacks.filenameFilter(dir)
				try:
					os.makedirs(osdir)
				except OSError as e:
					if e.errno != errno.EEXIST:
						raise
				finally:
					print("%s - created output directory:\n %s" % (name,osdir))
					created.append((w.name(), osdir))
		result = []
		if created:
			result.append('Created %d output directories:\n' % len(created))
			result.extend(['%s: %s\n' % x for x in created])
		if skipped:
			result.append('\n\n\nSkipped %d nodes:\n' % len(skipped))
			result.append('\n'.join(skipped))
		if result:
			nuke.message('\n'.join(result))
		else:
			nuke.message('No Write nodes found')
	
	else:
		return