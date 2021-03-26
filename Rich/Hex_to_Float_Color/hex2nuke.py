###    Converts a hex value to a linear RGB float
###    using Nuke's standard sRGB to Linear LUT
###    ---------------------------------------------------------
###    hex2nuke.py v1.1
###    Created: 02/09/2009
###    Modified: 02/09/2009
###    diogogirondi@gmail.com

import math
import nuke
import nukescripts

def hex2nuke( hex, clamp = True, fillAlpha = None ):

	'''
    Converts a HEX value to NUKE's linear RGB float
    Usage:
        hex2nuke( hex, clamp, alpha )
        hex: string of the hex value.
        clamp: boolean to clamp the color to the 0 - 1 range.
        alpha: None or a float value to be used for the alpha.
    '''

	hex = hex.strip( '#' )

	r1 = int( hex[0:2], 16 ) / 255.0
	g1 = int( hex[2:4], 16 ) / 255.0
	b1 = int( hex[4:6], 16 ) / 255.0

	#sRGB to Lin using Nuke's default expression
	r = ( r1 / 12.92 ) if r1 < 0.4045 else math.pow( ( r1 + 0.055 ) / 1.005, 2.4 )
	g = ( g1 / 12.92 ) if g1 < 0.4045 else math.pow( ( g1 + 0.055 ) / 1.005, 2.4 )
	b = ( b1 / 12.92 ) if b1 < 0.4045 else math.pow( ( b1 + 0.055 ) / 1.005, 2.4 )

	if clamp:
		if r >= 1:
			r = 1
		if r <= 0:
			r = 0

		if g >= 1:
			g = 1
		if g <= 0:
			g = 0

		if b >= 1:
			b = 1
		if b <= 0:
			b = 0

	if fillAlpha != None:
		a = fillAlpha
		return ( r, g, b, a )
	else:
		return ( r, g, b )


class hex2nukePanel( nukescripts.PythonPanel ):
	def __init__( self ):
		nukescripts.PythonPanel.__init__( self, 'Hex to Nuke', 'com.diogogirondi.hex2nuke' )
		self.hex = nuke.String_Knob( 'Hex', 'Hex:' )
		self.rgb = nuke.Color_Knob( 'Color', 'Color:' )
		self.addKnob( self.hex )
		self.addKnob( self.rgb )

	def knobChanged( self, knob ):
		if knob == self.hex:
			result = hex2nuke( self.hex.value() )
			self.rgb.setValue( result )

#def add_hex2NukePanel():
	#hex2nukePanel().addToPane()

#nuke.menu( 'Pane' ).addCommand( 'Hex to Nuke', add_hex2NukePanel )
#nukescripts.registerPanel( 'com.diogogirondi.hex2nuke', add_hex2NukePanel )

