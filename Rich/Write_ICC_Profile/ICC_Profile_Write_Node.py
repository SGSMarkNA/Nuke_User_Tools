import nuke

#import colorsys

#def ICC_Profile_Write_Node():
	#''''''
	## Set some color transforms...
	#r,g,b = 1.0, 1.0, 1.0
	#WhiteTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)
	#r,g,b = .66, 0.0, 0.0
	#RedTextColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,255),16)

	### Note that the beforeRender and afterFrameRender values include newline characters...
	##Write_ICC = nuke.nodes.Write(name='Write_with_sRGB_Color_Profile', label='\nAdds an "sRGB IEC61966-2.1" ICC\ncolor profile to the image. This will\nensure that color-managed applications,\nsuch as Photoshop, Firefox, Safari and\nChrome display the image as intended.')
	#Write_ICC = nuke.nodes.Write(name='Write_sRGB_ICC_Profile', label='\nAdds an "sRGB IEC61966-2.1"\nICC color profile to the image.\\n\nNOTE: DO NOT USE WITH EXRs!\n\nPNG, TIF and JPG ONLY!')
	#Write_ICC['note_font_color'].setValue(RedTextColor)
	#Write_ICC.knob('afterFrameRender').setValue('''from Write_ICC_Profile import Write_ICC_profile
#Write_ICC_profile.Write_ICC_Profile().copy_ICC_profile_to_image()''')

def ICC_Profile_Write_Node():
	''''''
	Write_ICC = nuke.nodes.Write(name='Write_sRGB_ICC_Profile')
	Write_ICC.knob('ICC_knob').setValue('sRGB_profile_from_Photoshop.icc')	

