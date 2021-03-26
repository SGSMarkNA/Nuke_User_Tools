import nuke

def Hyundai_Write_Node():
  
	''' 
	Custom Write node with code for automatically tagging rendered images.
	The TagImages class uses the exiftool metadata utility to add XMP style metadata to images. These data tags may be viewed in Photoshop.
	Two methods are used as callbacks in a Nuke Write node's Python tab: The first method, create_args_file(), operates as a beforeRender
	callback and generates a text file containing tag arguments for exiftool to use. On a Nuke Write node, add "TagImages.TagImages().create_args_file()"
	in the Write node's Python tab in the "before render" field. The second method, tag_images(), operates as an afterFrameRender callback.
	On the same Nuke Write node, add "TagImages.TagImages().tag_images()" in the Write node's Python tab in the "after each frame" field.
	For further info on exiftool, go to --> http://www.sno.phy.queensu.ca/~phil/exiftool/
	
	This custom Write node automatically adds the two required TagImages methods.
	
	WARNING: Metadata tagging for Photoshop does *not* work with PNG Files! It is recommended to use TIF files. Other formats may work, but have not been tested...
	
	Created by Rich Bobo - 04/04/2014
	richbobo@mac.com
	http://richbobo.com
	'''
	## Note that the beforeRender and afterFrameRender values include newline characters...
	n = nuke.createNode('Write')
	n.knob('channels').setValue("rgba")
	n.knob('beforeRender').setValue('''from TagImages import TagImages
TagImages.TagImages().create_args_file()''')
	n.knob('afterFrameRender').setValue('''from TagImages import TagImages
TagImages.TagImages().tag_images()''')	
	
