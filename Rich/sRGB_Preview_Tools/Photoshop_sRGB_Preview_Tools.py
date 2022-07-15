import os
if "AW_GLOBAL_SYSTEMS" in os.environ:
	if not os.environ["AW_GLOBAL_SYSTEMS"] in os.sys.path:
		os.sys.path.append(os.environ["AW_GLOBAL_SYSTEMS"])
from Environment_Access import System_Settings
import colorsys
import nuke
# Customized auto_backdrop function...
from auto_backdrop.auto_backdrop import auto_backdrop


class Add_sRGB_Preview_Tools(object):
	''''''
	def __init__(self):
		''''''	
		# Build path to sRGB Photoshop LUT...
		try:
			LUT = 'Nuke_Round_Trip.3dl'
			print(LUT)
			LUT_DIR = System_Settings.LUT_FILES
			print(LUT_DIR)
			LUT_PATH = os.path.join(LUT_DIR, LUT)
			print(LUT_PATH)
			self.PATH = self.filenameFix(LUT_PATH)
			print('self.PATH ---> ', self.PATH)
		except:
			print("ERROR: Cannot find path to LUT file! Exiting now.")
			nuke.message('ERROR: Cannot find path to LUT file!\nExiting now.')
			return

		# Get active Viewer node...
		self.CurrentViewer = nuke.activeViewer()
		##self.CurrentView = self.CurrentViewer.view()		# Added for multi-view support - RKB
		self.CurrentViewerNode = self.CurrentViewer.node()
		####self.activeInput = self.CurrentViewer.activeInput()
		####self.CurrentViewerNodeInput = self.CurrentViewerNode.input(self.activeInput)
		# Get input_process_node knob, so we can set the Vectorfield LUT to be active...
		self.InputProcessNode = self.CurrentViewerNode.knob('input_process_node')

		# Set some color transforms for the Backdrop node...
		r,g,b = .6, .118, .118
		self.RedBackdropColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
		r,g,b = .5, .5, .5
		self.GrayBackdropColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)        
		r,g,b = 1.0, 1.0, 1.0
		self.WhiteTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
		r,g,b = .66, 0.0, 0.0
		self.RedTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)        


	def filenameFix(self, filename):
		'''Nuke-ify path separators...'''
		return filename.replace( "\\", "/" )


	def _create_sRGB_3dLUT_vectorfield_node(self):
		''''''		
		# Add a Vectorfield node for the Viewer LUT...
		self.Vectorfield_sRGB_LUT = nuke.nodes.Vectorfield(name='Photoshop_sRGB_3dLUT_Vectorfield', label="Emulate Photoshop sRGB look in Nuke's Viewer...")
		self.Vectorfield_sRGB_LUT['hide_input'].setValue(True)
		# Set the LUT file path...
		self.Vectorfield_sRGB_LUT.knob('vfield_file').setValue(self.PATH)
		# Just select the new Vectorfield node...
		for Node in nuke.allNodes():
			Node.setSelected(False)
		self.Vectorfield_sRGB_LUT.setSelected(True)
		# Add a backdrop for the Vectorfield node...
		self.VectorfieldBackdrop = auto_backdrop(bd_label = 'sRGB Photoshop LUT\n\n\n\n(Do not connect.)')
		# Set some colors for the Backdrop node...
		self.VectorfieldBackdrop['tile_color'].setValue(self.RedBackdropColor)
		self.VectorfieldBackdrop['note_font_color'].setValue(self.WhiteTextColor)
		# Activate the new Vectorfield LUT for the Viewer as an Input Process...
		self.InputProcessNode.setValue('Photoshop_sRGB_3dLUT_Vectorfield')


	#def _create_ICC_Profile_Write_Node(self):
		#''''''
		### Note that the beforeRender and afterFrameRender values include newline characters...
		##Write_ICC = nuke.nodes.Write(name='Write_with_sRGB_Color_Profile', label='\nAdds an "sRGB IEC61966-2.1" ICC\ncolor profile to the image. This will\nensure that color-managed applications,\nsuch as Photoshop, Firefox, Safari and\nChrome display the image as intended.')
		#self.Write_ICC = nuke.nodes.Write(name='Write_sRGB_ICC_Profile', label='\nAdds an "sRGB IEC61966-2.1"\nICC color profile to the image.\\n\nNOTE: DO NOT USE WITH EXRs!\n\nPNG, TIF and JPG ONLY!')
		#self.Write_ICC['note_font_color'].setValue(self.RedTextColor)
		#self.Write_ICC.knob('afterFrameRender').setValue('''from Write_ICC_Profile import Write_ICC_profile
#Write_ICC_profile.Write_ICC_Profile().copy_ICC_profile_to_image()''')
		#self.Write_ICC.setXYpos(self.VectorfieldBackdrop.xpos()+400, self.VectorfieldBackdrop.ypos())
		
	def _create_ICC_Profile_Write_Node(self):
		''''''
		self.Write_ICC = nuke.nodes.Write(name='Write_sRGB_ICC_Profile')
		self.Write_ICC.knob('ICC_knob').setValue('sRGB_profile_from_Photoshop.icc')
		self.Write_ICC.setXYpos(self.VectorfieldBackdrop.xpos()+500, self.VectorfieldBackdrop.ypos()+100)


	def _create_comp_preview_node_group(self):
		''''''
		offsetX = 34
		offsetY = 10
		separation = 120

		self.StartDot = nuke.nodes.Dot()
		self.StartDot.setXYpos(self.Vectorfield_sRGB_LUT.xpos(), self.Vectorfield_sRGB_LUT.ypos()+separation*2)

		self.Names = ['Background', 'Reflection', 'Shadow', 'Beauty']

		# Create a new Names list iterator that is one element shorter (minus the first item). Use it for the list of Merge nodes...
		iterNames = iter(self.Names)
		next(iterNames)

		for index, Name in enumerate(self.Names):
			if (index == 0):
				##ShuffleNode = nuke.nodes.Shuffle(name='Shuffle_'+Name)
				ShuffleNode = nuke.nodes.Shuffle()
				ShuffleNode.knob('label').setValue('[value in]')
				ShuffleNode.setInput(0, self.StartDot)
				ShuffleNode.setXYpos(self.StartDot.xpos()-offsetX, self.StartDot.ypos()+separation)

				MergeName = next(iterNames)
				##MergeNode = nuke.nodes.Merge2(name='Merge_'+MergeName)
				MergeNode = nuke.nodes.Merge2()
				MergeNode.knob('sRGB').setValue(True)
				# To accurately emulate the transparency/alpha blending, which Photoshop does in sRGB colorspace (gamma 2.2), we turn on this handy knob...
				MergeNode.knob('label').setValue('"Video colorspace" enabled for sRGB blending.')
				# Connect B input to shuffle node...
				MergeNode.setInput(0, ShuffleNode)
				# Wait to connect A input until after the next Shuffle/Dot pair are created with next loop...                

				self.PrevShuffle = ShuffleNode
				self.PrevMerge = MergeNode
			else:
				if (index == 1):
					##ShuffleNode = nuke.nodes.Shuffle(name='Shuffle_'+Name)
					ShuffleNode = nuke.nodes.Shuffle()
					ShuffleNode.knob('label').setValue('[value in]')
					ShuffleNode.setInput(0, self.PrevShuffle)
					ShuffleNode.setXYpos(self.PrevShuffle.xpos()+separation, self.PrevShuffle.ypos())

					Dot = nuke.nodes.Dot()
					Dot.setInput(0, ShuffleNode)
					Dot.setXYpos(ShuffleNode.xpos()+offsetX, ShuffleNode.ypos()+(index*separation))

					# Connect A input of our previous Merge here...
					self.PrevMerge.setInput(1, Dot)
					# Set its position relative to the previous Merge and Shuffle nodes...
					self.PrevMerge.setXYpos(self.StartDot.xpos()-offsetX, Dot.ypos()-offsetY)

					MergeName = next(iterNames)
					##MergeNode = nuke.nodes.Merge2(name='Merge_'+MergeName)
					MergeNode = nuke.nodes.Merge2()
					MergeNode.knob('sRGB').setValue(True)
					# To accurately emulate the transparency/alpha blending, which Photoshop does in sRGB colorspace (gamma 2.2), we turn on this handy knob...
					MergeNode.knob('label').setValue('"Video colorspace" enabled for sRGB blending.')
					MergeNode.setInput(0, self.PrevMerge)
					# Wait to connect A input until after the next Shuffle/Dot pair are created with next loop...

					self.PrevShuffle = ShuffleNode
					self.PrevMerge = MergeNode
				else:
					##ShuffleNode = nuke.nodes.Shuffle(name='Shuffle_'+Name)
					ShuffleNode = nuke.nodes.Shuffle()
					ShuffleNode.knob('label').setValue('[value in]')
					ShuffleNode.setInput(0, self.PrevShuffle)
					ShuffleNode.setXYpos(self.PrevShuffle.xpos()+separation, self.PrevShuffle.ypos())

					Dot = nuke.nodes.Dot()
					Dot.setInput(0, ShuffleNode)
					Dot.setXYpos(ShuffleNode.xpos()+offsetX, ShuffleNode.ypos()+(index*separation))

					# Connect A input of our previous Merge here...
					self.PrevMerge.setInput(1, Dot)					
					# Set its position relative to the previous Merge and Shuffle nodes...
					self.PrevMerge.setXYpos(self.StartDot.xpos()-offsetX, Dot.ypos()-offsetY)
					try:
						# When we run out of items in iterNames, we will end gracefully...
						MergeName = next(iterNames)
						##MergeNode = nuke.nodes.Merge2(name='Merge_'+MergeName)
						MergeNode = nuke.nodes.Merge2()
						MergeNode.setInput(0, self.PrevMerge)
						MergeNode.setInput(1, Dot)
						MergeNode.knob('sRGB').setValue(True)
						# To accurately emulate the transparency/alpha blending, which Photoshop does in sRGB colorspace (gamma 2.2), we turn on this handy knob...
						MergeNode.knob('label').setValue('"Video colorspace" enabled for sRGB blending.')

						self.PrevShuffle = ShuffleNode
						self.PrevMerge = MergeNode
					except:
						pass


		self.EndDot = nuke.nodes.Dot(label='sRGB_COMP_PREVIEW', note_font_size = 30, note_font_color = self.RedTextColor)
		self.EndDot.setInput(0, self.PrevMerge)
		self.EndDot.setXYpos(self.StartDot.xpos(), Dot.ypos()+separation)

		# Just select the EndDot node...
		for Node in nuke.allNodes():
			Node.setSelected(False)
		self.EndDot.setSelected(True)
		# Select all of the connected nodes we made...
		nuke.selectConnectedNodes()

		# Add a backdrop for the selected nodes...
		self.CompPreviewBackdrop = auto_backdrop(bd_label = 'Photoshop/sRGB Comp Preview')
		# Set some colors for the Backdrop node...
		self.CompPreviewBackdrop['tile_color'].setValue(self.GrayBackdropColor)
		self.CompPreviewBackdrop['note_font_color'].setValue(self.WhiteTextColor)        



##############################################################
## RUN IT...

def start():

	x = Add_sRGB_Preview_Tools()

	x._create_sRGB_3dLUT_vectorfield_node()

	x._create_ICC_Profile_Write_Node()

	x._create_comp_preview_node_group()



'''

##----------------------------------------------##
## Test Run it in the Nuke Script Editor...
##----------------------------------------------##

import os
# This line adds the Mac-HOME search path...
# /Users/richbobo/Dropbox/CODE/aw_projects/sRGB_Preview_Tools/Photoshop_sRGB_Preview_Tools.py
os.sys.path.append("/Users/richbobo/Dropbox/CODE")

# This line adds the Mac-WORK search path...
# /Users/rbobo/Dropbox/CODE/aw_projects/sRGB_Preview_Tools/Photoshop_sRGB_Preview_Tools.py
os.sys.path.append("/Users/rbobo/Dropbox/CODE")

# This line adds the Windows search path...
# D:\rbobo\Dropbox\CODE\aw_projects\sRGB_Preview_Tools\Photoshop_sRGB_Preview_Tools.py
os.sys.path.append(r"D:\rbobo\Dropbox\CODE")


# Loads the python file into the environment...
import aw_projects.sRGB_Preview_Tools.Photoshop_sRGB_Preview_Tools
# After editing and saving the file in the text editor, this reloads it into the environment...
reload(aw_projects.sRGB_Preview_Tools.Photoshop_sRGB_Preview_Tools)

x = aw_projects.sRGB_Preview_Tools.Photoshop_sRGB_Preview_Tools.Add_sRGB_Preview_Tools()
x._create_sRGB_3dLUT_vectorfield_node()
x._create_ICC_Profile_Write_Node()
x._create_comp_preview_node_group()


'''
