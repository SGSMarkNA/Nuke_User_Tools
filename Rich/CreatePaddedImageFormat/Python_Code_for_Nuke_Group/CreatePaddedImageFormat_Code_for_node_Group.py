###############################################################################################
####----------------------------------------------------------------------------------------
#### ---- This goes in the group node's hidden knobChanged knob...
#### ---- Use the two lines below to set it.

exec_val ='''ParentGroup = nuke.thisNode()
ReadNode = ParentGroup.input(0)

UserKnobWidth = ParentGroup.knob('percentage_of_width')
DisplayKnobWidth = ParentGroup.knob('padded_width_display')

UserKnobHeight = ParentGroup.knob('percentage_of_height')
DisplayKnobHeight = ParentGroup.knob('padded_height_display')

CalculatorNode = nuke.toNode(ParentGroup.name() + '.Padding_Size_Calculator')
ResultKnobWidth = CalculatorNode.knob('padded_width_result')
ResultKnobHeight = CalculatorNode.knob('padded_height_result')

CreateOutputFormatKnob = ParentGroup.knob('output_format_selector')

FinalReformatNode = nuke.toNode(ParentGroup.name() + '.Reformat_to_Final_Output_Size')
FinalReformatKnob = FinalReformatNode.knob('format')

WarningKnob = ParentGroup.knob('image_scaled_warning')

def knobChanged():
	if nuke.thisKnob() == CreateOutputFormatKnob:
		FinalReformatKnob.setValue(CreateOutputFormatKnob.value())
		DisplayKnobWidth.setValue(str(int(ResultKnobWidth.value())))
		DisplayKnobHeight.setValue(str(int(ResultKnobHeight.value())))
		InputFormat = ReadNode.knob('format').value()
		OutputFormat = ParentGroup.knob('output_format_selector').value()
		if InputFormat.width() < OutputFormat.width() or InputFormat.height() < OutputFormat.height():
			print '\\nWARNING! Output format is larger than Input format!\\nImage will be scaled up!'
			WarningKnob.setValue('<FONT COLOR=\"#CB2222\">WARNING: Image will be scaled up!<\FONT>')
		else:
			WarningKnob.setValue('')
	if nuke.thisKnob() == UserKnobWidth:
		DisplayKnobWidth.setValue(str(int(ResultKnobWidth.value())))
	if nuke.thisKnob() == UserKnobHeight:
		DisplayKnobHeight.setValue(str(int(ResultKnobHeight.value())))
knobChanged()'''


#### NOTE: Via Nuke's Script Editor, use the following to set the Group node's knobChanged knob to the above script...

App_Group = nuke.toNode('Create_Padded_Output_Format')
App_Group.knob('knobChanged').setValue(exec_val)



###############################################################################################
####----------------------------------------------------------------------------------------
#### ---- This goes in the 'Go!' Python Button and performs the autocrop...

GroupNode = nuke.thisNode()
ReadNode = GroupNode.input(0)

# Make sure we're operating inside the group...
GroupNode.begin()

# Select the Input node, so that autocrop places the new Crop node after that...
InputNode = nuke.toNode('Input1')
InputNode.knob("selected").setValue(True)

# Remove existing Crop node, since autocrop makes a new one...
AllNodes = [node for node in GroupNode.nodes()]
for Node in AllNodes:
    if Node.Class()==('Crop'):
        nuke.delete(Node)

# Get the Read node that is connected to the group's input and execute the autocrop...
NodeToCrop = []
NodeToCrop.append(ReadNode)
for Node in NodeToCrop:
    nukescripts.autocrop(first=None, last=None, inc=None, layer='rgba')

# Get the new Crop node...
CropNode = nuke.toNode('Crop1')
# Format to the cropped values, so we have a tight fit...
CropNode['reformat'].setValue(True)
# Set to 'black outside'...
CropNode['crop'].setValue(True)
# Get the current crop values...
CropValues = CropNode['box'].value()
# Subtract one pixel from the x and y values and add a pixel to r and t...
NewValues = []
for index, value in enumerate(CropValues):
    if index <= 1:
        value = value - 1
        NewValues.append(value)
    else:
        value = value + 1
        NewValues.append(value)
CropNode['box'].setValue(tuple(NewValues))

# End our editing inside the group...
GroupNode.end()



###############################################################################################
####----------------------------------------------------------------------------------------
#### ---- This goes in "Do it!" Python button which creates the padded format...

ParentGroup = nuke.thisNode()

DisplayKnobWidth = ParentGroup.knob('padded_width_display')
DisplayKnobHeight = ParentGroup.knob('padded_height_display')

ResultKnobWidth = Node.knob('padded_width_result')
ResultKnobHeight = Node.knob('padded_height_result')


def create_new_image_format():
    # Create a new image format in Nuke --> EXAMPLE: MyNewFormat = '16000 119 1.0 Format_Name'
    NewFormatName = str(DisplayKnobWidth.value()) + 'x' + str(DisplayKnobHeight.value())
    NewFormat = (" %s %s 1.0 %s") % (int(ResultKnobWidth.value()), int(ResultKnobHeight.value()), NewFormatName )
    nuke.addFormat(NewFormat)
    print(NewFormat)
    nuke.message("Created new format: " + NewFormatName)

create_new_image_format()




###############################################################################################
####----------------------------------------------------------------------------------------
#### ---- This expression goes inside the Group node, in the "Padding_Size_Calculator" knode's "padded_width_result" knob to calculate the width...

Parent = nuke.thisParent()

OutputFormatWidth = Parent.knob('output_format_selector').value().width()

WidthInput = Parent.knob('percentage_of_width').value()

PaddingWidthPixels = OutputFormatWidth*((WidthInput*2)/100)

CalculatedWidth = OutputFormatWidth - PaddingWidthPixels

ret = CalculatedWidth


###############################################################################################
####----------------------------------------------------------------------------------------
#### ---- This expression goes inside the Group node, in the "Padding_Size_Calculator" knode's "padded_height_result" knob to calculate the height...

Parent = nuke.thisParent()

OutputFormatHeight = Parent.knob('output_format_selector').value().height()

HeightInput = Parent.knob('percentage_of_height').value()

PaddingHeightPixels = OutputFormatHeight*((HeightInput*2)/100)

CalculatedHeight = OutputFormatHeight - PaddingHeightPixels

ret = CalculatedHeight