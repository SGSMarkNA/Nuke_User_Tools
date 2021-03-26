try:
	import nuke
except ImportError:
	nuke = None
import random
import colorsys

def auto_backdrop(rand_color=False, bd_label='auto_backdrop'):
	'''
	Automatically puts a backdrop behind the selected nodes. The backdrop will be just big enough
	to fit all of the selected nodes, with some room at the top for text.
	Note: This is originally from The Foundry's autoBackdrop code, in the nukescripts module.
	I modified it to fix a bug with the backdrop not covering the entire width and height of all of the
	selected nodes. I borrowed some random color code and added a switch for random backdrop color on/off.
	Also, I added a Viewer node filter, so that any connected viewers will not be calculated as part of the backdrop coverage... RKB -- 01-03-13
	'''

	selNodes = nuke.selectedNodes()
	
	if selNodes:
		# Filter out any Viewers from our selection, so they don't get included in the backdrop size calculations...
		Nodes = [n for n in nuke.selectedNodes() if n.Class() != 'Viewer']
	else:
		raise ValueError('No selected nodes to work with...')
	
	# Calculate bounds for the backdrop node...
	bdX = min([node.xpos() for node in Nodes])
	bdY = min([node.ypos() for node in Nodes])
	bdW = max([node.xpos() + node.screenWidth() for node in Nodes]) - bdX
	bdH = max([node.ypos() + node.screenHeight() for node in Nodes]) - bdY

	# Expand the bounds to leave a little border. Elements are standoffs for left, top, right and bottom edges respectively 
	##left, top, right, bottom = (-10, -80, 10, 10)					# Original values.
	left, top, right, bottom = (-80, -80, 140, 100)					# My new values.
	bdX += left
	bdY += top
	bdW += (right - left)
	bdH += (bottom - top)

	if rand_color:
		# Better random color option I stole from Deke Kincaid who stole it from a Ben Dickson post on a listserve somewhere... 
		h = random.randrange(90, 270) / 360.0
		s = random.randrange(1, 75) / 100.0
		v = 0.35
		r,g,b = colorsys.hsv_to_rgb(h, s, v)
		color = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
	else:
		r = 75
		g = 75
		b = 75
		color = int('%02x%02x%02x%02x' % (r,g,b,0),16)

	backdrop_node = nuke.nodes.BackdropNode(xpos = bdX,
						bdwidth = bdW,
						ypos = bdY,
						bdheight = bdH,
						label = bd_label,
						##tile_color = int((random.random()*(13 - 11))) + 11,	# Original.
						##note_font_size=42)
						tile_color = color,							# New.
						note_font_size=30)

	# Unselect the nodes...
	backdrop_node['selected'].setValue(False)
	for node in selNodes:
		node['selected'].setValue(False)
	return backdrop_node

	
	