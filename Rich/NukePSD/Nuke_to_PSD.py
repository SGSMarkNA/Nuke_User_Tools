import nuke
import os
import subprocess
import errno
import glob
import re
import operator

# ---------------------------------------------------------------------------------------------------------

class NukePSD(object):

    def __init__(self):
        '''Create a layered Photoshop file from layers in a Nuke script. This class and its methods, write_data_file() and_run_JS_command() are
        called as an afterRender callback in a Nuke Write node inside a special Group node, using parameters set by the user.'''

        # Get the Write node this class is called from. Since it's inside the group node, we can get the fullName, which gives us the group node's name...
        self.CallbackWriteNode = nuke.thisNode()
        print 'CallbackWriteNode --> ', self.CallbackWriteNode.name()
        print 'fullName --> ', self.CallbackWriteNode.fullName()

        # Get the group node object...
        # self.GroupNode = nuke.toNode(self.CallbackWriteNode.fullName().split('.')[0])
        self.GroupNode = nuke.thisParent()
        print 'self.GroupNode --> ', self.GroupNode.name()

        # Photoshop Executable - OS-specific...
        if os.name == 'nt':
            import _winreg
            self.PS_APP = 'start photoshop.exe'

        elif os.name == 'posix':
            # Set the Photoshop application to run...
            self.PS_APP = 'open -b "com.adobe.Photoshop"'

        # Set the location for the JSX file to run...
        if os.name == 'nt':
            #self.jsx_file = os.environ["NUKE_USER_TOOLS_DIR"] + os.sep + 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx'
            self.jsx_file = os.path.join(os.environ["NUKE_USER_TOOLS_DIR"], 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx')
            self.jsx_file = self.jsx_file.replace('/', '\\')
        elif os.name == 'posix':
            #self.jsx_file = "'" + os.environ["NUKE_USER_TOOLS_DIR"] + os.sep + 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx' + "'"
            self.jsx_file = os.path.join(os.environ["NUKE_USER_TOOLS_DIR"], 'Rich/NukePSD/JavaScript/Photoshop/Nuke_to_PSD_from_PNGs.jsx')
        #print 'self.jsx_file --> ', self.jsx_file

        ##---------------------------------------------------------------------------------------------------------
        ## Check whether we have multiple views or not...

        if len(nuke.views()) == 1:
            # We're only using one view, most likely the default, "main"...
            self.multiple_views = False
        elif len(nuke.views()) > 1:
            # We're using multiple views...
            self.multiple_views = True

            # Create a global counter for keeping track of how many times the afterRender callback has fired.
            # By comparing the total to the number of selected views, the _write_data_file and
            # _run_JS_command methods are prevented from running, until ALL the views have rendered...

            # Make a new instance and increment it...
            if not "_afterRenderCount" in nuke.__dict__.keys():
                nuke.__dict__["_afterRenderCount"] = 0
            nuke.__dict__["_afterRenderCount"] += 1
            #print 'nuke.__dict__["_afterRenderCount"] --> ', nuke.__dict__["_afterRenderCount"]

            # Get the num_views, so it can be checked against the afterRenderCount global value...
            self.selected_views = (self.GroupNode.knob('views').value()).split()
            print 'self.selected_views --> ', self.selected_views

            # If the GroupNode gets pasted into a new comp, it can carry over selected 'ghost' views.
            # We need to make sure we only get the selected views that are really in nuke.views()...
            self.filtered_views = []
            for view in self.selected_views:
                if view in nuke.views():
                    self.filtered_views.append(view)
            self.GroupNode.knob('views').setValue(' '.join(self.filtered_views))
            self.num_views = len(self.filtered_views)
            print 'self.num_views --> ', self.num_views

        ##---------------------------------------------------------------------------------------------------------


    def _get_data_file_values(self):
        '''Build a list of data describing the image sequence to be processed by the JSX file.'''

        #---------------------------------------------------------------------------------------------------------
        # Get the layer name list...

        self.Layers = self._get_group_input_layers()
        #print 'self.Layers --> ', self.Layers

        #---------------------------------------------------------------------------------------------------------
        # Get the output path directory from the UI and set the PNG_DIR. Set the PNG_FOLDER value for the JSX file to process...

        dir_text = self.GroupNode.knob('dir_text').value()
        #print 'dir_text --> ', dir_text

        if not dir_text:
            nuke.message("Please enter an output directory.")
            return None
        else:
            if dir_text.endswith('/'):
                pass
            else:
                dir_text = dir_text + '/'
            #print 'dir_text --> ', dir_text

            # Make sure that the PNG_DIR is evaluated if using views. Use a temp Write node's file knob to get an evaluated path.
            # Need to do this for comps that use views and have '%V' in the dir_text knob...
            tempnode = nuke.nodes.Write(name='temp_eval_file_knob')
            tempnode['file'].setValue(dir_text)
            dir_text_evaluated = tempnode['file'].evaluate()
            self.dir_text = dir_text_evaluated
            nuke.delete(tempnode)

            self.PNG_DIR = self.dir_text + 'PNG'
            # Protect against pasting Windows path...
            self.PNG_DIR.replace('\\', '/')

            #print 'self.PNG_DIR --> ', self.PNG_DIR

            self.PNG_PATH = "'" + self.PNG_DIR + "'"
            #print 'self.PNG_PATH --> ', self.PNG_PATH
            PNG_FOLDER = 'var PNG_FOLDER = ' + self.PNG_PATH

        #---------------------------------------------------------------------------------------------------------
        # Build the path to the color settings files on the server...

        libPath = os.environ["AW_COMMON_UTILITIES"]
        ColorSettingsPath = (libPath + "/Photoshop/AW_Nuke_Tools/Color_Settings")
        ColorSettingsPath = ColorSettingsPath.replace('\\', '/')

        # Get the ICC profile name that is assigned to the PNG files...
        ICC_PROFILE = self.GroupNode.knob('ICC_knob').value()

        # Build the var commands to be evaluated by the JSX script...
        if ICC_PROFILE == "ACESCG Linear.icc":
            COLOR_SETTINGS = 'var COLOR_SETTINGS = ' + '"' + (ColorSettingsPath + "/" + "ACES-CG-Linear_NO_PROFILE_PROMPTS.csf") + '"';
        elif ICC_PROFILE == "sRGB.icc":
            COLOR_SETTINGS = 'var COLOR_SETTINGS = ' + '"' + (ColorSettingsPath + "/" + "sRGB.csf") + '"';
        elif ICC_PROFILE == "AdobeRGB1998.icc":
            COLOR_SETTINGS = 'var COLOR_SETTINGS = ' + '"' + (ColorSettingsPath + "/" + "ADOBE_RGB_1998.csf") + '"';
        elif ICC_PROFILE == "REC709.icc":
            COLOR_SETTINGS = 'var COLOR_SETTINGS = ' + '"' + (ColorSettingsPath + "/" + "REC709.csf") + '"';
        elif ICC_PROFILE == "REC2020.icc":
            COLOR_SETTINGS = 'var COLOR_SETTINGS = ' + '"' + (ColorSettingsPath + "/" + "REC2020.csf") + '"';
        elif ICC_PROFILE == "Empty":
            COLOR_SETTINGS = 'var COLOR_SETTINGS = ' + '"' + (ColorSettingsPath + "/" + "sRGB.csf") + '"';

        #---------------------------------------------------------------------------------------------------------
        # Get the first frame, last frame and number of frames via get_image_seq_info function...
        # Windows only - escaped backslashes...

        if os.name == 'nt':
            self.PNG_DIR = self.PNG_DIR.replace('/', '\\')
        #print 'self.PNG_DIR --> ', self.PNG_DIR

        # Just grab the first image to get the sequence info from, since all the other layer folders should be the same for the stuff we need...
        # Need to check for the first folder that exists if using views, since the first one might not be rendered.
        ## We're only using one view, most likely the default "main" view...
        if not self.multiple_views:
            # Multiple views boolean for JSX script...
            self.MULTI_VIEW = 'var MULTI_VIEW = ' + '"' + str(self.multiple_views) + '"'
            self.selected_views = (self.GroupNode.knob('views').value()).split()
            # If the GroupNode gets pasted into a new comp, it can carry over selected 'ghost' views.
            # We need to make sure we only get the selected views that are really in nuke.views()...
            self.filtered_views = []
            for view in self.selected_views:
                if view in nuke.views():
                    self.filtered_views.append(view)
            self.GroupNode.knob('views').setValue(' '.join(self.filtered_views))
            self.num_views = len(self.filtered_views)
            #print 'self.num_views --> ', self.num_views
            # Views folder names for the JSX script. This gets ignored by the JSX script,in the case of a single view.
            # However, I needed a placeholder, so the JSX script doesn't error out...
            VIEWS_FOLDERS = 'var VIEWS_FOLDERS = ' + str(self.filtered_views)
            # Check to stop iteration when looking for a filename to sample for the data file...
            success = False
            for layername in self.Layers:
                if not success:
                    dir_path = os.path.join(self.PNG_DIR, layername)
                    #print 'dir_path --> ', dir_path
                    if os.path.isdir(dir_path):
                        #print 'True -- dir_path --> ', dir_path
                        for filename in os.listdir(dir_path):
                            if filename.endswith('.png'):
                                filepath = os.path.join(dir_path, filename)
                                #print 'filepath --> ', filepath
                                self.ImageSeqInfoList = self._get_image_seq_info(filepath)
                                #print 'self.ImageSeqInfoList --> ', self.ImageSeqInfoList
                                success = True
        ## We're using multiple views...
        elif self.multiple_views:
            # Multiple views boolean for JSX script...
            self.MULTI_VIEW = 'var MULTI_VIEW = ' + '"' + str(self.multiple_views) + '"'
            self.selected_views = (self.GroupNode.knob('views').value()).split()
            # If the GroupNode gets pasted into a new comp, it can carry over selected 'ghost' views.
            # We need to make sure we only get the selected views that are really in nuke.views()...
            self.filtered_views = []
            for view in self.selected_views:
                if view in nuke.views():
                    self.filtered_views.append(view)
            self.GroupNode.knob('views').setValue(' '.join(self.filtered_views))
            self.num_views = len(self.filtered_views)
            #print 'self.num_views --> ', self.num_views
            # Views folder names for the JSX script...
            VIEWS_FOLDERS = 'var VIEWS_FOLDERS = ' + str(self.filtered_views)
            # Check to stop iteration when looking for a filename to sample for the data file...
            success = False
            for viewname in self.filtered_views:
                if success == False:
                    # Get the Output Dir. value from the dir_text knob and format it...
                    dir_path = self.dir_text.split('/')
                    dir_path = '/'.join(dir_path[:-1])
                    dir_path = os.path.join(dir_path, 'PNG', viewname)
                    if os.path.isdir(dir_path):
                        #print 'True -- PATH --> ', dir_path
                        for folder in os.listdir(dir_path):
                            self.layer_folder_path = os.path.join(dir_path, folder)
                            #print 'layer_folder_path --> ', self.layer_folder_path
                            for filename in os.listdir(self.layer_folder_path):
                                if filename.endswith('.png'):
                                    filepath = os.path.join(self.layer_folder_path, filename)
                                    #print 'filepath --> ', filepath
                                    self.ImageSeqInfoList = self._get_image_seq_info(filepath)
                                    #print 'self.ImageSeqInfoList --> ', self.ImageSeqInfoList
                                    success = True

        FRAMES = self.ImageSeqInfoList[3]
        NUM_FRAMES = 'var NUM_FRAMES = ' + str(FRAMES)

        FIRST = (self.ImageSeqInfoList[4]).replace('\\', '/')
        FIRST_FRAME = 'var FIRST_FRAME = ' + '"' + FIRST + '"'

        LAST = (self.ImageSeqInfoList[5]).replace('\\', '/')
        LAST_FRAME = 'var LAST_FRAME = ' + '"' + LAST + '"'

        #---------------------------------------------------------------------------------------------------------
        # Get the Photoshop PSD filename from the group UI (minus the extension, which gets supplied by the JSX script)...

        if not self.multiple_views:
            PSD_NAME = self.GroupNode.knob('PSD_filename').value()
            if not PSD_NAME:
                nuke.message("Please enter a name for the PSD file.")
                return None
            else:
                PSD_NAME = self.GroupNode.knob('PSD_filename').value()
                PSD_PATH = "'" + self.dir_text + PSD_NAME + "'"
                #print 'PSD_PATH --> ', PSD_PATH
                PSD_FILENAME = 'var PSD_FileName = ' + PSD_PATH

        elif self.multiple_views:
            # Placeholder value, since multi-view does not use the PSD_NAME, it uses the view names, instead...
            PSD_NAME = 'NOT_USED_FOR_MULTIVIEW'
            PSD_PATH = "'" + self.dir_text + PSD_NAME + "'"
            PSD_FILENAME = 'var PSD_FileName = ' + PSD_PATH

        #---------------------------------------------------------------------------------------------------------
        # Get the user's ordering of the layers from the group node's UI...
        layer_order_dict = self._create_layer_order_dict()

        # Check to see if all the layers are still set to zero...
        if all(value == 0 for value in layer_order_dict.values()):
            nuke.message("Please set the layer order for the PSD files.")
            return None
        else:
            sorted_layer_order = sorted(layer_order_dict.items(), key=operator.itemgetter(1))	# Example result ---> [('Background', 0), ('Floor_Reflection', 1), ('Floor_Shadow', 2), ('Beauty', 3)]

        # Sort the layer names according to their number ranking...
        layers_in_order = []
        for layer in sorted_layer_order:
            layers_in_order.append(layer[0])
        #print layers_in_order

        # The final layer order.
        LAYER_FOLDERS = 'var LAYER_FOLDERS = ' + str(layers_in_order)

        #---------------------------------------------------------------------------------------------------------
        # Get "Delete Temp Files" value from GroupNode...
        #delete_temp_files = self.GroupNode.knob('delete_temp_files').value()
        #print 'delete_temp_files --> ', delete_temp_files
        #DELETE_FILES = 'var DELETE_FILES = ' + '"' + str(delete_temp_files) + '"'

        #---------------------------------------------------------------------------------------------------------
        # Assign the data to be written into the data_file...
        MULTI_VIEW = self.MULTI_VIEW

        #---------------------------------------------------------------------------------------------------------
        # Get the name of the layer to be replaced by the view name, if any...
        try:
            layer_name_replacement = self.GroupNode.knob('replace_layername').value()
        except:
            layer_name_replacement = 'none'

        LAYERNAME_REPLACEMENT = 'var LAYERNAME_REPLACEMENT = ' + '"' + layer_name_replacement + '"'

        #---------------------------------------------------------------------------------------------------------
        #self.Data = [PNG_FOLDER, LAYER_FOLDERS, COLOR_SETTINGS, PSD_FILENAME, NUM_FRAMES, FIRST_FRAME, LAST_FRAME, DELETE_FILES, MULTI_VIEW, VIEWS_FOLDERS, LAYERNAME_REPLACEMENT]
        self.Data = [PNG_FOLDER, LAYER_FOLDERS, COLOR_SETTINGS, PSD_FILENAME, NUM_FRAMES, FIRST_FRAME, LAST_FRAME, MULTI_VIEW, VIEWS_FOLDERS, LAYERNAME_REPLACEMENT]
        print 'self.Data --> ', self.Data
        return self.Data


    def _input_check(self):
        '''Check if there's anything connected to the Group's input.'''
        try:
            ConnectedNode = self.GroupNode.input(0)
            #print 'ConnectedNode --> ', ConnectedNode.name()
            return ConnectedNode
        except AttributeError:
            nuke.message("Please connect something to the input!")
            return None


    def _get_group_input_layers(self):
        '''Get unique layers list from the GroupNode's input.'''
        self.ConnectedNode = self._input_check()
        if self.ConnectedNode:
            Layers = []
            Channels = self.ConnectedNode.channels()
            #print 'Channels --> ', Channels
            for name in Channels:
                name = name.split('.')[0]
                Layers.append(name)
            Layers = list(set(Layers))
            #print 'Layers --> ', Layers
            return Layers
        else:
            return None


    def _create_layer_order_dict(self):
        '''Create a dict of the layer names and their numerical order number the user has assigned for use in building the Photoshop files.'''
        layer_order_dict = {}
        # Get knobname and knob object from self.GroupNode.knobs() dictionary...
        for knobname, knob in self.GroupNode.knobs().iteritems():
            if '_ORDER_' in knobname:
                knobname = (knobname.split('_ORDER_'))[1]
                if knobname in self.Layers:
                    #print ''
                    #print knobname, knob.value()
                    layer_order_dict[knobname] = knob.value()
            else:
                pass
        #print 'layer_order_dict --> ', layer_order_dict
        return layer_order_dict


    def _get_image_seq_info(self, filepath):
        '''Given a single image path, get image sequence info for all of the images in the folder.'''
        #print 'filepath --> ', filepath
        dirPath = os.path.dirname(filepath)
        #print 'dirPath --> ', dirPath
        Filename = os.path.basename(filepath)
        #print 'Filename --> ', Filename
        segNum = re.findall(r'\d+', Filename)[-1]
        #print 'segNum --> ', segNum
        numPad = len(segNum)
        #print 'numPad --> ', numPad
        baseName = Filename.split(segNum)[0]
        #print 'baseName --> ', baseName
        fileType = Filename.split('.')[-1]
        #print 'fileType --> ', fileType
        globString = baseName
        for i in range(0,numPad): globString += '?'
        #print 'globString --> ', globString
        #print 'Filename.split(segNum)[1] --> ', Filename.split(segNum)[1]
        theGlob = glob.glob(dirPath + '/' + globString + Filename.split(segNum)[1])
        #print 'theGlob --> ', theGlob
        numFrames = len(theGlob)
        #print 'numFrames --> ', numFrames
        FileList = list(theGlob)
        FileList.sort()
        #print 'FileList --> ', FileList
        firstFrame = FileList[0]
        #print 'theGlob firstFrame ---> ', firstFrame
        lastFrame = FileList[-1]
        #print 'theGlob lastFrame ---> ', lastFrame
        return [baseName, numPad, fileType, numFrames, firstFrame, lastFrame]


    def _write_data_file(self):
        '''Save out a list of javascript commands to be evaluated by the _run_JS_command()'s jsx_file.'''

        # Process all the data_file values and assign them to self.Data...
        self._get_data_file_values()

        # Path for the data file...
        self.data_file = os.path.join(self.PNG_DIR + os.sep +'NukePSD_Data.txt')
        #print 'self.data_file --> ', self.data_file

        # Set the data directory...
        self.data_dir = os.path.dirname(self.data_file)
        #print self.data_dir

        # Write the NukePSD_Data.txt file...
        try:
            # Save the file...
            self.data_save = open(self.data_file, 'w')
            for item in self.Data:
                #print 'item -->', item
                self.data_save.write(item)
                self.data_save.write("\n")
            self.data_save.close()
            self.Data_Save_Success = True
            #print 'self.Data_Save_Success --> ', self.Data_Save_Success

            # Write out a data_location_file in a known temp dir. that holds the location of the data_file, so that the JSX file knows where to find it...
            self._write_data_location_file()

        except Exception as e:
            self.Data_Save_Success = False
            print e
            nuke.message("Data File cannot be saved to %s!" % (self.data_file))


    def _write_data_location_file(self):
        '''Write out a file in a known temp directory that holds the location of the main data_file, so that the JSX file knows where to find it.'''

        # String to write to file, which is a var definition for the JSX file to process...
        if os.name == 'nt':
            DATA_FILE_LOCATION = 'var DATA_FILE_LOCATION = ' + "'" + self.data_file + "'"
            DATA_FILE_LOCATION = DATA_FILE_LOCATION.replace('\\', '/')
        elif os.name == 'posix':
            DATA_FILE_LOCATION = 'var DATA_FILE_LOCATION = ' + "'" + self.data_file + "'"
        #print 'DATA_FILE_LOCATION --> ', DATA_FILE_LOCATION
        self.Data_Location = [DATA_FILE_LOCATION]
        #print 'self.Data_Location --> ', self.Data_Location

        if os.name == "nt":
            self.data_location_file = os.path.join((os.environ.get('TEMP')), '.nuke\NukePSD\data_file_location.txt')
        else:
            self.data_location_file = os.path.join((os.environ.get('HOME')), '.nuke/NukePSD/data_file_location.txt')

        # Set the directory so we can make it, if it doesn't exist...
        self.data_location_dir = os.path.dirname(self.data_location_file)

        # Try to create the directory and cope with the directory already existing by ignoring that exception...
        try:
            os.makedirs(self.data_location_dir)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        #finally:
            #print "Created data location directory: %s " % (self.data_location_dir)

        # Save the file...
        try:
            self.data_location_save = open(self.data_location_file, 'w')
            for item in self.Data_Location:
                #print 'item -->', item
                self.data_location_save.write(item)
                self.data_location_save.write("\n")
            self.data_location_save.close()
            self.Data_Location_Save_Success = True
        except Exception as e:
            self.Data_Location_Save_Success = False
            print e
            nuke.message("Data Location File cannot be saved to %s!" % (self.data_location_file))


    def _JS_command(self):
        '''Launch Photoshop and run the JSX file via the subprocess module.'''

        if self.Data_Save_Success and self.Data_Location_Save_Success:
            if os.name == 'nt':
                ####### THIS WORKS!!!! ###################################################################################################################################################################################
                ## self.target = 'start photoshop.exe "\\\\isln-smb.ad.sgsco.int\\aw_config\\Git_Live_Code\\Global_Systems\\User_Tools\\Nuke_User_Tools\\Rich\\NukePSD\\JavaScript\\Photoshop\\Nuke_to_PSD_from_PNGs.jsx"'
                ##########################################################################################################################################################################################################
                self.target = self.PS_APP + " " + '"' + self.jsx_file + '"'
                self.target = self.target.replace('/', '\\')
                #print 'self.target --> ', self.target
                process = subprocess.Popen(self.target, shell=True)
            elif os.name == 'posix':
                self.target = self.PS_APP + " " + self.jsx_file
                #print 'self.target --> ', self.target
                process = subprocess.Popen(self.target, shell=True)
                process.wait()
        else:
            return None


    def _run_write_data_file(self):
        '''Check for Single or Multiple Views before running _write_data_file.'''
        if not self.multiple_views:
            self._write_data_file()
        else:
            if nuke.__dict__["_afterRenderCount"] == self.num_views:
                self._write_data_file()
            else:
                pass


    def _run_JS_command(self):
        '''Multiple view checks before running _JS_command'''
        if not self.multiple_views:
            self._JS_command()
        else:
            if nuke.__dict__["_afterRenderCount"] == self.num_views:
                self._JS_command()
            else:
                pass