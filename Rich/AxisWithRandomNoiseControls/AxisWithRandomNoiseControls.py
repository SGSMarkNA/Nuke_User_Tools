import nuke

def Create_Axis_With_Random_Noise_Controls():  
	
	n=nuke.createNode("Axis")
	n["label"].setValue('Random Noise Generator')

	xtext = nuke.Text_Knob("X_Noise")
	n.addKnob(xtext)
	xfrequency = nuke.Double_Knob("xfrequency","frequency")
	n.addKnob(xfrequency)
	xamplitude = nuke.Double_Knob("xamplitude","amplitude")
	n.addKnob(xamplitude)
	xoctaves = nuke.Double_Knob("xoctaves","octaves")
	n.addKnob(xoctaves)

	ytext = nuke.Text_Knob("Y_Noise")
	n.addKnob(ytext)
	yfrequency = nuke.Double_Knob("yfrequency","frequency")
	n.addKnob(yfrequency)
	yamplitude = nuke.Double_Knob("yamplitude","amplitude")
	n.addKnob(yamplitude)
	yoctaves = nuke.Double_Knob("yoctaves","octaves")
	n.addKnob(yoctaves)

	ztext = nuke.Text_Knob("Z_Noise")
	n.addKnob(ztext)
	zfrequency = nuke.Double_Knob("zfrequency","frequency")
	n.addKnob(zfrequency)
	zamplitude = nuke.Double_Knob("zamplitude","amplitude")
	n.addKnob(zamplitude)
	zoctaves = nuke.Double_Knob("zoctaves","octaves")
	n.addKnob(zoctaves)
	
	newline_knob = nuke.Text_Knob("")        
	n.addKnob(newline_knob)
	newline2_knob = nuke.Text_Knob("")        
	n.addKnob(newline2_knob)	
	
	Noise = nuke.PyScript_Knob("Noise","Generate Noise")
	n.addKnob(Noise)
	n['Noise'].setValue('n=nuke.selectedNode()\nn["translate"].setExpression("fBm(frame*xfrequency,10.5,11.5,xoctaves,2,.5)*xamplitude",0)\nn["translate"].setExpression("fBm(frame*yfrequency,10.5,11.5,yoctaves,2,.5)*yamplitude",1)\nn["translate"].setExpression("fBm(frame*zfrequency,10.5,11.5,zoctaves,2,.5)*zamplitude",2)')    




