try:
    import nuke
except ImportError:
    nuke = None
import nukescripts


class CreateScaledImageFormat(nukescripts.PythonPanel):

    def __init__(self):

        # Initialize the panel...
        nukescripts.PythonPanel.__init__(self, 'Create Scaled Image Format', 'com.richbobo.CreateScaledImageFormat')		
        self.setMinimumSize(525, 125)

        #####################################################################
        ##                    CREATE THE KNOBS
        #####################################################################
        ##                       Top Title
        ##-------------------------------------------------------------------
        self.TopTitle = nuke.Text_Knob('TopTitle', 'FORMAT SCALING:')

        ##-------------------------------------------------------------------
        ##                       1st Tab group
        ##-------------------------------------------------------------------
        self.Even_Divisor_BeginTabGroup = nuke.Tab_Knob('', 'Even Divisor')
        self.Even_Divisor_BeginTabGroup.setFlag(nuke.STARTLINE)

        # Add width entry knobs...
        self.width_entry_knob = nuke.Int_Knob('width_entry', 'Width:')
        self.width_entry_knob.setTooltip('Enter width of original format.')
        self.width_entry_knob.clearFlag( nuke.STARTLINE )
        # Eliminate the slider to the right of the numerical entry field.
        self.width_entry_knob.clearFlag(2)
        self.width_entry_knob.setRange(1, 100000)
        # Grab the current Root format as the default value, since it's what is most likely to be what the user wants...
        self.root_width = nuke.root()['format'].value().width()
        self.width_entry_knob.setValue(self.root_width)

        # Add height entry knobs...
        self.height_entry_knob = nuke.Int_Knob('height_entry', 'Height:')
        self.height_entry_knob.setTooltip('Enter height of original format.')
        self.height_entry_knob.clearFlag( nuke.STARTLINE )
        # Eliminate the slider to the right of the numerical entry field.
        self.height_entry_knob.clearFlag(2)
        self.height_entry_knob.setRange(1, 100000)
        # Grab the current Root format as the default value, since it's what is most likely to be what the user wants...
        self.root_height = nuke.root()['format'].value().height()
        self.height_entry_knob.setValue(self.root_height)

        # Add Python button to execute the divisor calculations...
        self.calculateDivisors_knob = nuke.PyScript_Knob('calculateDivisors', 'Calculate Common Divisors')
        self.calculateDivisors_knob.setTooltip('Calculate common divisors for the height and width.')

        # Add dropdown menu to hold the divisor-calculated formats...
        # Use the current root format as a temp. placeholder...
        self.OriginalSize = [str(self.root_width) + ' x ' + str(self.root_height)]
        self.format_selector_knob = nuke.Enumeration_Knob('format_names', 'Format Sizes :', self.OriginalSize)
        self.format_selector_knob.setFlag(nuke.STARTLINE)

        # Divider...
        self.Divider = nuke.Text_Knob('divider', '')

        # Add Python button to create the currently selected format in the dropdown menu...
        self.create_format_knob = nuke.PyScript_Knob( 'create_format', 'Create Format')
        self.create_format_knob.setTooltip('Create new image format from the values selected in the Format Sizes dropdown menu.')
        self.create_format_knob.setFlag(nuke.STARTLINE)

        ##-------------------------------------------------------------------
        ##                        2nd Tab group
        ##-------------------------------------------------------------------
        self.Scaling_BeginTabGroup = nuke.Tab_Knob('', 'Scaling')
        self.Scaling_BeginTabGroup.setFlag(nuke.STARTLINE)

        # Add width entry knobs...
        self.width_entry_knob2 = nuke.Int_Knob('width_entry2', 'Width:')
        self.width_entry_knob2.setTooltip('Enter width of original format.')
        self.width_entry_knob2.clearFlag( nuke.STARTLINE )
        # Eliminate the slider to the right of the numerical entry field.
        self.width_entry_knob2.clearFlag(2)
        self.width_entry_knob2.setRange(1, 100000)
        # Grab the current Root format as the default value, since it's what is most likely to be what the user wants...
        self.root_width = nuke.root()['format'].value().width()
        self.width_entry_knob2.setValue(self.root_width)

        # Add height entry knobs...
        self.height_entry_knob2 = nuke.Int_Knob('height_entry2', 'Height:')
        self.height_entry_knob2.setTooltip('Enter height of original format.')
        self.height_entry_knob2.clearFlag( nuke.STARTLINE )
        # Eliminate the slider to the right of the numerical entry field.
        self.height_entry_knob2.clearFlag(2)
        self.height_entry_knob2.setRange(1, 100000)
        # Grab the current Root format as the default value, since it's what is most likely to be what the user wants...
        self.root_height = nuke.root()['format'].value().height()
        self.height_entry_knob2.setValue(self.root_height)

        # Scaling knob...
        self.scaling_knob = nuke.Double_Knob('scaling', 'Scale')
        self.scaling_knob.setRange(.01, 1.0)
        self.scaling_knob.setDefaultValue([0.5])
        self.scaling_knob.setTooltip('Scales the current format interactively.')

        # ScaledFormat section title...
        self.ScaledFormatTitle = nuke.Text_Knob('ScaledFormatTitle', 'Scaled Format:')

        self.scaled_width = nuke.Int_Knob('scaled_width', 'Width:')
        self.scaled_width.setDefaultValue([(int(self.width_entry_knob2.value()*self.scaling_knob.value()))])
        self.scaled_height = nuke.Int_Knob('scaled_height', 'Height:')
        self.scaled_height.setDefaultValue([(int(self.height_entry_knob2.value()*self.scaling_knob.value()))])
        self.scaled_height.clearFlag( nuke.STARTLINE )

        # Divider...
        self.Divider2 = nuke.Text_Knob('divider2', '')

        # Add Python button to create the currently selected format in the dropdown menu...
        self.create_format_knob2 = nuke.PyScript_Knob( 'create_format', 'Create Format')
        self.create_format_knob2.setTooltip('Create new image format from the values for the Scaled Format.')
        self.create_format_knob2.setFlag(nuke.STARTLINE)

        #####################################################################
        ##                ADD THE KNOBS TO THE PANEL
        #####################################################################
        ##                     Top Title
        ##-------------------------------------------------------------------
        self.addKnob(self.TopTitle)

        ##-------------------------------------------------------------------
        ##                        TAB 1
        ##-------------------------------------------------------------------
        for k in (self.Even_Divisor_BeginTabGroup,
                  self.width_entry_knob,
                  self.height_entry_knob,
                  self.calculateDivisors_knob,
                  self.format_selector_knob,
                  self.Divider,
                  self.create_format_knob):
            self.addKnob(k)

        ##-------------------------------------------------------------------
        ##                       TAB 2
        ##-------------------------------------------------------------------
        for k in (self.Scaling_BeginTabGroup,
                  self.width_entry_knob2,
                  self.height_entry_knob2,
                  self.scaling_knob,
                  self.ScaledFormatTitle,
                  self.scaled_width,
                  self.scaled_height,
                  self.Divider2,
                  self.create_format_knob2):
            self.addKnob(k)        

    #####################################################################
    ##                       MAIN FUNCTIONS 
    #####################################################################
    def _find_divisors(self):
        '''Find even divisors for scaling an image...'''
        self.width_entry = self.width_entry_knob.value()
        self.height_entry = self.height_entry_knob.value()

        self.formats = []
        self.width_entry_div = []
        self.height_entry_div = []

        # Find width_entry divisors...
        for div in range(2,9):
            if (self.width_entry % div) == 0:
                self.width_entry_div.append(div)

        # Find height_entry divisors...
        for div in range(2,9):
            if (self.height_entry % div) == 0:
                self.height_entry_div.append(div)

        # Make a list of the common divisors...
        self.common_divisors = [item for item in self.height_entry_div if item in self.width_entry_div]

        print("Width Divisors: ", self.width_entry_div)
        print("Height Divisors:", self.height_entry_div)
        print("Common Divisors:", self.common_divisors)
        print("Original Size:  ", self.OriginalSize)

        # Assemble the new format names... 
        for divisor in self.common_divisors:
            # Make a format name, based on the image size...
            self.format_name = str(self.width_entry/divisor) + ' x ' + str(self.height_entry/divisor)
            self.formats.append(self.format_name)
            print("Divisor " + str(divisor) + ' : -->  ' + self.format_name)

        # Populate the pulldown format selector menu with the new format names...
        if self.formats:
            self.format_selector_knob.setValues(self.formats)
        else:
            self.current_width_entry = self.width_entry_knob.value()
            self.current_height_entry = self.height_entry_knob.value()
            self.CurrentFormatName = str(self.current_width_entry) + 'x' + str(self.current_height_entry)
            nuke.message("Sorry, could not find any common divisors for the format " + self.CurrentFormatName)

    def _create_new_image_format(self):
        '''Given a height and width value, create a new Nuke image format...'''
        #Create a new image format in Nuke... EXAMPLE: MyNewFormat = '16000 12192 1.0 Format_Name'
        self.New = self.format_selector_knob.value()
        self.NewFormatWidth = self.New.split(' ')[0]
        self.NewFormatHeight = self.New.split(' ')[2]
        self.NewFormatName = str(self.NewFormatWidth) + 'x' + str(self.NewFormatHeight)
        self.NewFormat = (" %s %s 1.0 %s") % (self.NewFormatWidth, self.NewFormatHeight, self.NewFormatName)
        nuke.addFormat(self.NewFormat)
        print(self.NewFormat)
        nuke.message("Created new format: " + self.NewFormatName)
        ## Assign as the script's new root format...
        ##nuke.root()['format'].setValue(self.NewFormatName)

    def _create_new_image_format2(self):
        '''Given a height and width value, create a new Nuke image format...'''
        # Create a new image format in Nuke --> EXAMPLE: MyNewFormat = '16000 12192 1.0 Format_Name'
        self.NewFormatName2 = str(self.scaled_width.value()) + 'x' + str(self.scaled_height.value())
        self.NewFormat2 = (" %s %s 1.0 %s") % (self.scaled_width.value(), self.scaled_height.value(), self.NewFormatName2)
        nuke.addFormat(self.NewFormat2)
        print(self.NewFormat2)
        nuke.message("Created new format: " + self.NewFormatName2)
        ## Assign as the script's new root format...
        ##nuke.root()['format'].setValue(self.NewFormatName2)        

    def knobChanged(self, knob):
        '''Connect all the buttons to the actions...'''
        if knob is self.calculateDivisors_knob:
            self._find_divisors()
        if knob is self.create_format_knob:
            self._create_new_image_format()
        if knob is self.scaling_knob:
            self.scaled_width.setValue(int(self.width_entry_knob2.value()*self.scaling_knob.value()))
            self.scaled_height.setValue(int(self.height_entry_knob2.value()*self.scaling_knob.value()))
        if knob is self.create_format_knob2:
            self._create_new_image_format2()
        if knob is self.width_entry_knob2:
            self.scaled_width.setValue(int(self.width_entry_knob2.value()*self.scaling_knob.value()))
        if knob is self.height_entry_knob2:
            self.scaled_height.setValue(int(self.height_entry_knob2.value()*self.scaling_knob.value()))        


######################################################################
###                         TESTING... 
######################################################################
#def Start():
    #'''Main function to create the panel.'''
    #p = CreateScaledImageFormat()
    #p.showModal()

### RUN IT.
#Start()