import nuke
import sys
import os
import errno
import pickle
import colorsys
import random

'''NOTE: To run CompBuilder, select an EXR Read node and execute --> exr_CompBuilder()'''


class CompBuilder(object):
	'''
	Automatically assemble a Nuke node tree into one of a number of templates, based on the VRay render layers available in an EXR file.
	
	'exr_comp' is the main method which calls the 'layer_extractor' method, the 'layer_check', 'layer_mapper' and build_type methods.
	The exr_shuffle method is called last and does all of the work to generate and connect the Nuke schematic nodes, based on information
	gathered by the other methods. The user can also save preferences for the general layout and appearance of the node schematic.
	
	Several types of templates are supported: Basic - an additive layers composite; BasicDiffuse - which includes a section for breaking out
	the global illumination, diffuse and lighting passes; BasicRaw - includes a section for combining Raw lighting and Raw GI with a diffuse pass.
	BasicDiffuseCarBody, BasicRawCarBody and BasicCarBody add a car paint section to each of the preceeding for auto-specific paint color
	tweaking.
	
	If the passes found in the EXR file do not match any of the named configurations, the user can manually select correspondences between
	standard VRay render pass names and the names of the passes found in the EXR file.
	
	Created by Rich Bobo - 01/12/2013
	richbobo@mac.com
	http://richbobo.com
	'''
	#### Constants: The names of the VRay render passes we are looking for in the EXR file.
	#Base = ['VRayTotalLighting']																	#### The minimum base layer for a simple additive comp... Required.
	#PlusSet = ['VRayReflection', 'VRaySpecular', 'VRayTotalLighting', 'VRaySelfIllumination', 'VRayRefraction']				#### Additive layers, which can be plussed together...
	#DiffuseSet = ['VRayDiffuseFilter', 'VRayGlobalIllumination', 'VRayLighting']									#### Layers needed for a comp that splits up the TotalLighting pass into its components for more color control...
	#RawSet = ['VRayDiffuseFilter', 'VRayRawGlobalIllumination', 'VRayRawLighting']								#### Layers that are multiplied against the VRayDiffuseFilter pass to obtain the VRayTotalLighting pass...
	#CarBodySet = ['Paint_Window_Rimz', 'VRayMtlSelect_Car_Paint', 'VRayMtlSelect_Clearcoat', 'VRayMtlSelect_Metalic']		#### Layers needed to isolate the car body for finer control over the color...
	
	#### Constants: The names of the VRay render passes we are looking for in the EXR file.
	#Base = ['totalLight']																	#### The minimum base layer for a simple additive comp... Required.
	#PlusSet = ['reflect', 'specular', 'totalLight', 'selfIllum', 'refract']				#### Additive layers, which can be plussed together...
	#DiffuseSet = ['rawDiffuseFilter', 'GI', 'lighting']									#### Layers needed for a comp that splits up the TotalLighting pass into its components for more color control...
	#RawSet = ['rawDiffuseFilter', 'rawGI', 'rawLight']								#### Layers that are multiplied against the VRayDiffuseFilter pass to obtain the VRayTotalLighting pass...
	#CarBodySet = ['Paint_Window_Rimz', 'Base', 'ClearCoat', 'Metallic']		#### Layers needed to isolate the car body for finer control over the color...
	
	def __init__(self,option=0):
		if option == 0:
			self.Base = ['VRayTotalLighting']																	#### The minimum base layer for a simple additive comp... Required.
			self.PlusSet = ['VRayReflection', 'VRaySpecular', 'VRayTotalLighting', 'VRaySelfIllumination', 'VRayRefraction']				#### Additive layers, which can be plussed together...
			self.DiffuseSet = ['VRayDiffuseFilter', 'VRayGlobalIllumination', 'VRayLighting']									#### Layers needed for a comp that splits up the TotalLighting pass into its components for more color control...
			self.RawSet = ['VRayDiffuseFilter', 'VRayRawGlobalIllumination', 'VRayRawLighting']								#### Layers that are multiplied against the VRayDiffuseFilter pass to obtain the VRayTotalLighting pass...
			self.CarBodySet = ['Paint_Window_Rimz', 'VRayMtlSelect_Car_Paint', 'VRayMtlSelect_Clearcoat', 'VRayMtlSelect_Metalic']		#### Layers needed to isolate the car body for finer control over the color...
		elif option == 1:
			self.Base = ['totalLight']																	#### The minimum base layer for a simple additive comp... Required.
			self.PlusSet = ['reflect', 'specular', 'totalLight', 'selfIllum', 'refract']				#### Additive layers, which can be plussed together...
			self.DiffuseSet = ['rawDiffuseFilter', 'GI', 'lighting']									#### Layers needed for a comp that splits up the TotalLighting pass into its components for more color control...
			self.RawSet = ['rawDiffuseFilter', 'rawGI', 'rawLight']								#### Layers that are multiplied against the VRayDiffuseFilter pass to obtain the VRayTotalLighting pass...
			self.CarBodySet = ['Paint_Window_Rimz', 'Base', 'ClearCoat', 'Metallic']
		self.Layout = None
		self.spacing_x = None
		self.spacing_y = None
		self.postage_stamps = False
		self.backdrop_off = False
		self.rand_color = False
		self.layer_override = False
		self.save_prefs = False
		
		self.layers = []
		self.channels = []
		
		self.base_comp_layer = []
		self.plus_comp_layers = []
		self.diffuse_comp_layers = []
		self.raw_comp_layers = []
		self.car_body_comp_layers = []
		self.car_body_alpha_channel = []
		
		self.base_found = False
		self.plus_set_found = False
		self.diffuse_set_found = False
		self.raw_set_found = False
		self.car_body_set_found = False
		
		self.layer_map = False
		
		self.ShuffleLayers = []
		self.DiffuseLayers = []
		self.RawLayers = []
		self.BodyLayers = []
		self.CarBodyAlpha = []
		
		self.Basic = False
		self.Diffuse = False
		self.Raw = False
		self.CarBody = False
		
		self.BasicDiffuse = False
		self.BasicDiffuseCarBody = False
		self.BasicRaw = False
		self.BasicRawCarBody = False
		self.BasicCarBody = False

		self.prefs_file = []
		self.prefs_dir = []
		self.prefs = []
		self.saved_prefs =[]
		self.prefs_save = []
		self.prefs_read = []
		
		#### The exr_comp function below is the main method. However, the launch function for everything is exr_CompBuilder,
		#### which instantiates the CompBuilder class, which starts __init__ and ends up here, running self.exr_comp.
		self.exr_comp()
	
	def write_prefs_file(self, prefs):
		'''Save out a list of the user's preferences for items such as node spacing, shuffle node postage stamps on/off, backdrop on/off, random backdrop color and manual override for layer mapping... '''
		
		if os.name == "nt":
			self.prefs_file = os.path.join((os.environ.get('TEMP')), '.nuke\CompBuilder\CompBuilder_Prefs.pref')		
		else:
			self.prefs_file = os.path.join((os.environ.get('HOME')), '.nuke/CompBuilder/CompBuilder_Prefs.pref')
		#### Set the prefs directory so we can make it, if it doesn't exist...
		self.prefs_dir = os.path.dirname(self.prefs_file)
		#### Try to create the prefs directory and cope with the directory already existing by ignoring that exception...
		try:
			os.makedirs(self.prefs_dir)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		finally:
			print("Created output directory: %s " % (self.prefs_dir))
		try:
			self.prefs_save = open(self.prefs_file, 'w')
			pickle.dump(self.prefs, self.prefs_save)
			self.prefs_save.close()
		except:
			nuke.message("Prefs cannot be saved to: %s. Press OK to cancel." % (self.prefs_file))
			return None
	
	def read_prefs_file(self):
		'''Read a saved list of the user's preferences such as node spacing, shuffle node postage stamps on/off, backdrop on/off, random backdrop color and manual override for layer mapping... '''
		
		if os.name == "nt":
			self.prefs_file = os.path.join((os.environ.get('TEMP')), '.nuke\CompBuilder\CompBuilder_Prefs.pref')
		else:
			self.prefs_file = os.path.join((os.environ.get('HOME')), '.nuke/CompBuilder/CompBuilder_Prefs.pref')
			self.prefs_dir = os.path.dirname( self.prefs_file )
		#### Try to read the prefs file, if it exists...	
		if os.path.isfile(self.prefs_file):
			try:
				self.prefs_read = open(self.prefs_file, 'r')
				self.saved_prefs = pickle.load(self.prefs_read)
				self.prefs_read.close()
			except:
				nuke.message("Prefs file cannot be read:\n %s\n\n Press OK to continue.\n\n You will need to save a new Prefs file.\n On the next panel, check the box for  [x] <----- SAVE PREFS." % (self.prefs_file))
				self.prefs_read.close()
			finally:
				print("exr_CompBuilder Prefs file loaded successfully.")
				return self.saved_prefs
		else:
			return None
		
	def layer_extractor(self, node):
		''' Get all the layers and channels contained in an EXR image file and put them into a layers list.'''
		
		self.channels = node.channels()
		self.layers = list( set([c.split('.')[0] for c in self.channels]) )
		self.layers.sort()
		return self.layers
	
	def layer_check(self, layers, channels):
		'''
		Loop through the layers list created by the layer_extractor method to see what matches the sets of layers we're looking for, such as Base, PlusSet, DiffuseSet, RawSet and CarBodySet.
		
		Check to see if we have the minimum required layers to make one of the defined node layout templates. If not, ask the user to associate the layer names from the EXR file with the
		equilavent VRay render pass names via the layer_mapper method.
		'''
		#print "HERE ARE THE layers:"
		#print layers
		
		###################################################
		#### Check to see if we found theVRayTotalLighting pass or the DiffuseSet or the RawSet.
		#### At least one of these must be present to serve as a base for the comp.
		#### If not, then go to layer_mapper and have the user pick from what was found....
		testBox1 = []
		test1 = False
		for p in layers:
			if p in self.Base:
				testBox1.append(p)
		#### Compare what was found in the EXR to the Base list...
		if testBox1 == self.Base:
			test1 = True
		###################################################
		#### Loop through the "DiffuseSet" list...
		testBox2 = []
		test2 = False
		for p in layers:
			if p in self.DiffuseSet:
				testBox2.append(p)
		#### Compare what we found in the EXR to the DiffuseSet...
		if testBox2 == self.DiffuseSet:
			test2 = True
		###################################################
		testBox3 = []
		test3 = False
		#### Loop through the "RawSet" list...
		for p in layers:
			if p in self.RawSet:
				testBox3.append(p)
		#### Compare what we found in the EXR to the PlusSet...
		if testBox3 == self.RawSet:
			test3 = True

		### If any of the minimum requirements are met, we can proceed...
		if test1 == True or test2 == True or test3 == True:
			#### We have the minimum requirements, so let's compare what we found for all of the lists...
			
			for p in layers:
				if p in self.Base:
					self.base_comp_layer.append(p)
			#### Compare what we found to the Base list...
			if self.base_comp_layer == self.Base:
				self.base_found = True
	
			#### Loop through the "PlusSet" list...
			for p in layers:
				if p in self.PlusSet:
					self.plus_comp_layers.append(p)
			#### Compare what we found to the PlusSet...
			if len(self.plus_comp_layers) > 0:
				self.plus_set_found = True
				
			#### Loop through the "DiffuseSet" list...
			for p in layers:
				if p in self.DiffuseSet:
					self.diffuse_comp_layers.append(p)
			#### Compare what we found to the DiffuseSet...
			if self.diffuse_comp_layers == self.DiffuseSet:
				self.diffuse_set_found = True
				#### We need these layers to be in this order - not alphabetical - for the CompBuilder...
				self.diffuse_comp_layers = ['VRayGlobalIllumination', 'VRayDiffuseFilter', 'VRayLighting']
				
			#### Loop through the "RawSet" list...
			for p in layers:
				if p in self.RawSet:
					self.raw_comp_layers.append(p)
			#### Compare what we found to the PlusSet...
			if self.raw_comp_layers == self.RawSet:
				self.raw_set_found = True
				#### We need these to be in this order - not alphabetical - for the CompBuilder...
				self.raw_comp_layers = ['VRayRawGlobalIllumination', 'VRayDiffuseFilter', 'VRayRawLighting']
				
			#### Loop through the"CarBodySet" list...
			for p in layers:
				if p in self.CarBodySet:
					self.car_body_comp_layers.append(p)
			#### Compare what we found to the CarBodySet...
			if self.car_body_comp_layers == self.CarBodySet:
				self.car_body_set_found = True
				#### We need these to be in this order - not alphabetical - for the CompBuilder...
				self.car_body_comp_layers = ['VRayMtlSelect_Car_Paint', 'VRayMtlSelect_Metalic', 'VRayMtlSelect_Clearcoat']
				self.car_body_alpha_channel = ['Paint_Window_Rimz.red']
				
			#print self.base_found
			#print self.plus_set_found
			#print self.diffuse_set_found
			#print self.raw_set_found
			#print self.car_body_set_found
			
			#print "HERE IS THE self.base_comp_layer", self.base_comp_layer
			#print "HERE ARE THE self.plus_comp_layers", self.plus_comp_layers
			#print "HERE ARE THE self.diffuse_comp_layers", self.diffuse_comp_layers
			#print "HERE ARE THE self.raw_comp_layers", self.raw_comp_layers
			#print "HERE ARE THE self.car_body_comp_layers", self.car_body_comp_layers
			#print "HERE IS THE self.car_body_alpha_channel", self.car_body_alpha_channel
			
			self.layer_map = True
			
			return True, self.layer_map
	
		else:
		
			self.layer_mapper(layers, channels)

	def layer_mapper(self, layers, channels):
		'''
		Create a pop-up panel for the user to manually map the EXR layers, found by the layer_extractor method, to their VRay equivalents.
		Check for the existence of certain render layers and groups of layers to determine which of several comp templates may be built.
		
		The user may decide to go here first and not let the layer_check method search for matching layer names or the user may end up
		here if the layer names do not match standard VRay render pass names in the layer_chack method.
		'''
		#print "THE VALUE OF layers and channels is :"
		#print layers
		#print channels
		
		nuke.message ("Please pick the layer mapping yourself. I'll try to figure something out...")
		
		#### Add 'none' as a layer choice on the menus...
		layers = [ 'none' ] + layers			
		channels = [ 'none' ] + channels

		p = nuke.Panel( 'Map AOVs' )
		p.addEnumerationPulldown( 'VRAY LAYERS <<--- map to --->> EXR LAYERS', ' ')
		p.addEnumerationPulldown( 'VRayTotalLighting', ' '.join( layers ) )
		p.addEnumerationPulldown( 'ALL 3 OR NONE OF THESE:  ______________', ' ' )
		p.addEnumerationPulldown( 'VRayGlobalIllumination', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRayDiffuseFilter', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRayLighting', ' '.join( layers ) )
		p.addEnumerationPulldown( 'ALL 3 OR NONE OF THESE:  ______________', ' ' )
		p.addEnumerationPulldown( 'VRayRawGlobalIllumination', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRayDiffuseFilter ', ' '.join( layers ) )					#### Note: one extra space at end of thisVRayDiffuseFilter label to differentiate from the previous VRayDiffuseFilter choice...
		p.addEnumerationPulldown( 'VRayRawLighting', ' '.join( layers ) )
		p.addEnumerationPulldown( '1 OR MORE OF THESE:  ___________________', ' ' )
		p.addEnumerationPulldown( 'VRayReflection', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRayRefraction', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRaySelfIllumination', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRaySpecular', ' '.join( layers ) )
		p.addEnumerationPulldown( 'ALL 4 OR NONE OF THESE:  _______________', ' ' )
		p.addEnumerationPulldown( 'VRayMtlSelect_Car_Paint', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRayMtlSelect_Clearcoat', ' '.join( layers ) )
		p.addEnumerationPulldown( 'VRayMtlSelect_Metalic', ' '.join( layers ) )
		p.addEnumerationPulldown( 'Paint_Window_Rimz', ' '.join( channels ) )
		
		#### Pop up a layer chooser to allow the user to map the found EXR layers to their VRay equivalents...
		if not p.show():
			return
		
		#### Build a new dictionary list, based on the user's choices, to hold the layers selected...
		layersDict ={}
		
		if p.value( 'VRayTotalLighting' ) != 'none':
			layersDict.update({"VRayTotalLighting":p.value( 'VRayTotalLighting' )})
		
		if p.value( 'VRayGlobalIllumination' ) != 'none':
			layersDict.update({"VRayGlobalIllumination":p.value( 'VRayGlobalIllumination' )})
		
		if p.value( 'VRayDiffuseFilter' ) != 'none':
			layersDict.update({"VRayDiffuseFilter":p.value( 'VRayDiffuseFilter' )})
		
		if p.value( 'VRayLighting' ) != 'none':
			layersDict.update({"VRayLighting":p.value( 'VRayLighting' )})
		
		if p.value( 'VRayRawGlobalIllumination' ) != 'none':
			layersDict.update({"VRayRawGlobalIllumination":p.value( 'VRayRawGlobalIllumination' )})
		
		if p.value( 'VRayDiffuseFilter ' ) != 'none':										#### Note: one extra space at end of thisVRayDiffuseFilter label to differentiate from the previous VRayDiffuseFilter choice...
			layersDict.update({"VRayDiffuseFilter":p.value( 'VRayDiffuseFilter ' )})					#### Note: one extra space at end of thisVRayDiffuseFilter label to differentiate from the previous VRayDiffuseFilter choice...
			
		if p.value( 'VRayRawLighting' ) != 'none':
			layersDict.update({"VRayRawLighting":p.value( 'VRayRawLighting' )})	
		
		if p.value( 'VRayReflection' ) != 'none':
			layersDict.update({"VRayReflection":p.value( 'VRayReflection' )})
		
		if p.value( 'VRayRefraction' ) != 'none':
			layersDict.update({"VRayRefraction":p.value( 'VRayRefraction' )})
		
		if p.value( 'VRaySelfIllumination' ) != 'none':
			layersDict.update({"VRaySelfIllumination":p.value( 'VRaySelfIllumination' )})
		
		if p.value( 'VRaySpecular' ) != 'none':	
			layersDict.update({"VRaySpecular":p.value( 'VRaySpecular' )})
		
		if p.value( 'VRayMtlSelect_Car_Paint' ) != 'none':
			layersDict.update({"VRayMtlSelect_Car_Paint":p.value( 'VRayMtlSelect_Car_Paint' )})
		
		if p.value( 'VRayMtlSelect_Metalic' ) != 'none':
			layersDict.update({"VRayMtlSelect_Metalic":p.value( 'VRayMtlSelect_Metalic' )})
		
		if p.value( 'VRayMtlSelect_Clearcoat' ) != 'none':
			layersDict.update({"VRayMtlSelect_Clearcoat":p.value( 'VRayMtlSelect_Clearcoat' )})
		
		if p.value( 'Paint_Window_Rimz' ) != 'none':
			layersDict.update({"Paint_Window_Rimz":p.value( 'Paint_Window_Rimz' )})
			self.car_body_alpha_channel.append(p.value( 'Paint_Window_Rimz' ))
			
			#print "THIS IS self.car_body_alpha_channel IN layer_mapper------------->>>>>"
			#print self.car_body_alpha_channel
			#print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
		
		#print "THIS IS THE VALUE OF layersDict:"
		#print layersDict
		
		###################################################
		#### Check to see if we found theVRayTotalLighting pass or the DiffuseSet or the RawSet.
		#### At least one of these must be present to serve as a base for the comp.
		
		#### Set test variables for the minimum requirements...
		test1 = False
		test2 = False
		test3 = False
		#### Make some dummy lists to hold the associated VRay layer names for testing against, since the names we found in the EXR are different than the ones we're looking for...		
		testbase_comp_layer = []
		testplus_comp_layers =[]
		testdiffuse_comp_layers = []
		testraw_comp_layers = []
		testcar_body_comp_layers = []
		#### Initialize variable for VRayTotalLighting pass - to be removed if we find it in both the base set and the diffuse or raw set...
		RemoveTotalLight = ''
			
		#### Loop through the "BaseSet" list...
		for k, v in layersDict.items():
			if k in self.Base:
				testbase_comp_layer.append(k)
				self.base_comp_layer.append(v)
		#### Compare what we found to the Base list...
		if testbase_comp_layer == self.Base:
			test1 = True
		#### Reset the variable...
		self.base_comp_layer = []

		#### Loop through the "DiffuseSet" list...
		for k, v in layersDict.items():
			if k in self.DiffuseSet:
				if k == 'VRayGlobalIllumination':
					testdiffuse_comp_layers.append(k)
					self.diffuse_comp_layers.append(v)
		for k, v in layersDict.items():
			if k in self.DiffuseSet:
				if k == 'VRayDiffuseFilter':
					testdiffuse_comp_layers.append(k)
					self.diffuse_comp_layers.append(v)
		for k, v in layersDict.items():
			if k in self.DiffuseSet:
				if k == 'VRayLighting':
					testdiffuse_comp_layers.append(k)
					self.diffuse_comp_layers.append(v)
		#### Compare what we found to the DiffuseSet...
		testdiffuse_comp_layers.sort()
		if testdiffuse_comp_layers == self.DiffuseSet:
			test2 = True
		#### Reset the variable...
		self.diffuse_comp_layers = []

		#### Loop through the "RawSet" list...
		for k, v in layersDict.items():
			if k in self.RawSet:
				if k == 'VRayRawGlobalIllumination':
					testraw_comp_layers.append(k)
					self.raw_comp_layers.append(v)
		for k, v in layersDict.items():
			if k in self.RawSet:
				#print "THIS IS k------------->>>>>>>>", k
				if k == 'VRayDiffuseFilter':
					testraw_comp_layers.append(k)
					self.raw_comp_layers.append(v)
		for k, v in layersDict.items():
			if k in self.RawSet:
				if k == 'VRayRawLighting':
					testraw_comp_layers.append(k)
					self.raw_comp_layers.append(v)
		#### Compare what we found to the RawSet...
		testraw_comp_layers.sort()
		if testraw_comp_layers == self.RawSet:
			test3 = True
		#### Reset the variable...
		self.raw_comp_layers = []

		#### Reset the test variables...
		testbase_comp_layer = []
		testplus_comp_layers =[]
		testdiffuse_comp_layers = []
		testraw_comp_layers = []
		testcar_body_comp_layers = []
		
		#print "THIS IS test1-------------------->", test1
		#print "THIS IS test2-------------------->", test2
		#print "THIS IS test3-------------------->", test3
		
		
		### If any of the minimum requirements are met, we can proceed...
		if test1 == True or test2 == True or test3 == True:
			#### The testing for minimum requirements is over, now check the layers to see what we found...
			
			#### Loop through the "BaseSet" list...
			for k, v in layersDict.items():
				if k in self.Base:
					testbase_comp_layer.append(k)
					self.base_comp_layer.append(v)
			#### Compare what we found to the Base list...
			if testbase_comp_layer == self.Base:
				self.base_found = True
	
			#### Loop through the "PlusSet" list...
			for k, v in layersDict.items():
				if k in self.PlusSet:
					if k == 'VRayTotalLighting':
						testplus_comp_layers.append(k)
						self.plus_comp_layers.append(v)
						RemoveTotalLight = v						#### Set a variable to whatever the user associates with 'VRayTotalLighting'. If we have DiffuseSet lor RawSet layers, we'll need to remove this from the ShuffleLayers list...
						#print "THE VALUE OF RemoveTotalLight--------->>>>>>", RemoveTotalLight
					else:
						testplus_comp_layers.append(k)
						self.plus_comp_layers.append(v)
			#### Compare what we found to the PlusSet...
			testplus_comp_layers.sort()
			if len(testplus_comp_layers) > 0:
				self.plus_set_found = True

			#### Loop through the "DiffuseSet" list...
			for k, v in layersDict.items():
				if k in self.DiffuseSet:
					if k == 'VRayGlobalIllumination':
						testdiffuse_comp_layers.append(k)
						self.diffuse_comp_layers.append(v)
			for k, v in layersDict.items():
				if k in self.DiffuseSet:
					if k == 'VRayDiffuseFilter':
						testdiffuse_comp_layers.append(k)
						self.diffuse_comp_layers.append(v)
			for k, v in layersDict.items():
				if k in self.DiffuseSet:
					if k == 'VRayLighting':
						testdiffuse_comp_layers.append(k)
						self.diffuse_comp_layers.append(v)
			#### Compare what we found to the DiffuseSet...
			testdiffuse_comp_layers.sort()
			if testdiffuse_comp_layers == self.DiffuseSet:
				self.diffuse_set_found = True
				#print "THIS IS self.plus_comp_layers BEFORE .remove------->>>>>", self.plus_comp_layers
				try:
					self.plus_comp_layers.remove( RemoveTotalLight )		#### Since we have the all DiffuseSet layers, we will not need this layer. We'll build a TotalLighting pass ourselves, from the GI, Diffuse and Lighting passes...
				except ValueError:
					pass								
				if len(self.plus_comp_layers) > 0:						#### Check again to see if there's anything left in the plus_comp_layers...
					self.plus_set_found = True
				else:
					self.plus_set_found = False
			
			#### Loop through the "RawSet" list...
			for k, v in layersDict.items():
				if k in self.RawSet:
					if k == 'VRayRawGlobalIllumination':
						testraw_comp_layers.append(k)
						self.raw_comp_layers.append(v)
			for k, v in layersDict.items():
				if k in self.RawSet:
					#print "THIS IS k------------->>>>>>>>", k
					if k == 'VRayDiffuseFilter':
						testraw_comp_layers.append(k)
						self.raw_comp_layers.append(v)
			for k, v in layersDict.items():
				if k in self.RawSet:
					if k == 'VRayRawLighting':
						testraw_comp_layers.append(k)
						self.raw_comp_layers.append(v)
			#### Compare what we found to the RawSet...
			#print "THIS IS testraw_comp_layers------------->>>>>", testraw_comp_layers
			testraw_comp_layers.sort()
			#print "THIS IS testraw_comp_layers------------->>>>>", testraw_comp_layers
			if testraw_comp_layers == self.RawSet:
				self.raw_set_found = True
				#print "THIS IS self.plus_comp_layers BEFORE .remove------->>>>>", self.plus_comp_layers
				try:
					self.plus_comp_layers.remove( RemoveTotalLight )		#### Since we have the all RawSet layers, we will not need this layer. We'll build a TotalLighting pass ourselves, from the Raw GI, Diffuse and Raw Lighting passes...
				except ValueError:
					pass								
				if len(self.plus_comp_layers) > 0:						#### Check again to see if there's anything left in the plus_comp_layers...
					self.plus_set_found = True
				else:
					self.plus_set_found = False
			
			#### Loop through the"CarBodySet" list...
			for k, v in layersDict.items():
				if k in self.CarBodySet:
					if k == 'Paint_Window_Rimz':
						testcar_body_comp_layers.append(k)
			for k, v in layersDict.items():	
				if k in self.CarBodySet:
					if k == 'VRayMtlSelect_Car_Paint':
						testcar_body_comp_layers.append(k)
						self.car_body_comp_layers.append(v)
			for k, v in layersDict.items():
				if k in self.CarBodySet:
					if k == 'VRayMtlSelect_Metalic':
						testcar_body_comp_layers.append(k)
						self.car_body_comp_layers.append(v)
			for k, v in layersDict.items():
				if k in self.CarBodySet:
					if k == 'VRayMtlSelect_Clearcoat':
						testcar_body_comp_layers.append(k)
						self.car_body_comp_layers.append(v)
			#### Compare what we found to the CarBodySet...
			testcar_body_comp_layers.sort()
			if testcar_body_comp_layers == self.CarBodySet:
				self.car_body_set_found = True
			
			#print self.base_found
			#print self.plus_set_found
			#print self.diffuse_set_found
			#print self.raw_set_found
			#print self.car_body_set_found
			
			#print "HERE IS THE self.base_comp_layer", self.base_comp_layer
			#print "HERE ARE THE self.plus_comp_layers", self.plus_comp_layers
			#print "HERE ARE THE self.diffuse_comp_layers", self.diffuse_comp_layers
			#print "HERE ARE THE self.raw_comp_layers", self.raw_comp_layers
			#print "HERE ARE THE self.car_body_comp_layers", self.car_body_comp_layers
			#print "HERE IS THE self.car_body_alpha_channel", self.car_body_alpha_channel
				
			#### If we still couldn't find the Base layer, then we return False to the main exr_comp method...
			#### Else, we return True with a list of layers to be used in the comp...

			self.layer_map = True
			
			return True, self.layer_map
		
		else:
			
			self.layer_map = False
			
			return False, self.layer_map
		
	def build_type(self):
		'''
		Check to see what layer sets were found by the layer_check or layer_mapper methods.
		Set variables for the node schematic templates to send to the exr_shuffle method, which will build the node schematic.
		'''
		if (self.base_found == True and self.plus_set_found == True) and self.diffuse_set_found == False and self.raw_set_found == False and self.car_body_set_found == False:
			#print "BUILD TYPE IS --------->>>>>>Basic"
			return "Basic"
			
		elif ((self.base_found == True and self.plus_set_found == True) or (self.base_found == False and self.plus_set_found == True )) and self.diffuse_set_found == True and self.raw_set_found == False and self.car_body_set_found == False:
			#print "BUILD TYPE IS --------->>>>>>BasicDiffuse"
			return "BasicDiffuse"
		
		elif ((self.base_found == True and self.plus_set_found == True) or (self.base_found == False and self.plus_set_found == True )) and self.diffuse_set_found == True and self.raw_set_found == True and self.car_body_set_found == False:
			#print "BUILD TYPE IS --------->>>>>>BasicDiffuse"
			return "BasicDiffuse"
		
		elif ((self.base_found == True and self.plus_set_found == True) or (self.base_found == False and self.plus_set_found == True )) and self.diffuse_set_found == True and self.raw_set_found == False and self.car_body_set_found == True:
			#print "BUILD TYPE IS --------->>>>>>BasicDiffuseCarBody"
			return "BasicDiffuseCarBody"		
		
		elif ((self.base_found == True and self.plus_set_found == True) or (self.base_found == False and self.plus_set_found == True )) and self.diffuse_set_found == True and self.raw_set_found == True and self.car_body_set_found == True:
			#print "BUILD TYPE IS --------->>>>>>BasicDiffuseCarBody"
			return "BasicDiffuseCarBody"
		
		elif ((self.base_found == True and self.plus_set_found == True) or (self.base_found == False and self.plus_set_found == True )) and self.diffuse_set_found == False and self.raw_set_found == True and self.car_body_set_found == False:
			#print "BUILD TYPE IS --------->>>>>>BasicRaw"
			return "BasicRaw"
		
		elif ((self.base_found == True and self.plus_set_found == True) or (self.base_found == False and self.plus_set_found == True )) and self.diffuse_set_found == False and self.raw_set_found == True and self.car_body_set_found == True:
			#print "BUILD TYPE IS --------->>>>>>BasicRawCarBody"
			return "BasicRawCarBody"
		
		elif (self.base_found == True and self.plus_set_found == True) and self.diffuse_set_found == False and self.raw_set_found == False and self.car_body_set_found == True:
			#print "BUILD TYPE IS --------->>>>>>BasicCarBody"
			return "BasicCarBody"
		
		elif (self.base_found == False and self.plus_set_found == False) and ((self.diffuse_set_found == True and self.raw_set_found == False) or (self.diffuse_set_found == True and self.raw_set_found == True)) and self.car_body_set_found == True:
			#print "BUILD TYPE IS --------->>>>>>DiffuseCarBody"
			return "DiffuseCarBody"
		
		elif (self.base_found == False and self.plus_set_found == False) and self.diffuse_set_found == False and self.raw_set_found == True and self.car_body_set_found == True:
			#print "BUILD TYPE IS --------->>>>>>RawCarBody"
			return "RawCarBody"
			
	def auto_backdrop(self, rand_color):
		'''
		Automatically puts a backdrop behind the selected nodes. The backdrop will be just big enough
		to fit all of the selected nodes, with some room at the top for text.
		
		Note: This is originally from The Foundry's autoBackdrop code, in the nukescripts module.
		I modified it to fix a bug with the backdrop not covering the entire width and height of all of the
		selected nodes. I borrowed some random color code and added a switch for random backdrop color on/off.
		Also, I added a Viewer node filter, so that any connected viewers will not be calculated as part of the backdrop coverage... RKB -- 01-03-13
		''' 
		#### Filter out any Viewers from our selection, so they don't get included in the backdrop size calculations...
		selNodes = [n for n in nuke.selectedNodes() if n.Class() != 'Viewer']
		
		if not selNodes:
			return nuke.nodes.BackdropNode()
		
		#### Calculate bounds for the backdrop node...
		bdX = min([node.xpos() for node in selNodes])
		bdY = min([node.ypos() for node in selNodes])
		bdW = max([node.xpos() + node.screenWidth() for node in selNodes]) - bdX
		bdH = max([node.ypos() + node.screenHeight() for node in selNodes]) - bdY
		
		#### Expand the bounds to leave a little border. Elements are offsets for left, top, right and bottom edges respectively 
		#left, top, right, bottom = (-10, -80, 10, 10)					#### Original values.
		left, top, right, bottom = (-80, -80, 140, 100)					#### My new values.
		bdX += left
		bdY += top
		bdW += (right - left)
		bdH += (bottom - top)
		
		if rand_color:
			#### Better random color option I stole from Deke Kincaid who stole it from a Ben Dickson post on a listserve somewhere... 
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
		
		n = nuke.nodes.BackdropNode(xpos = bdX,
								bdwidth = bdW,
								ypos = bdY,
								bdheight = bdH,
								label = "exr_comp",
								#tile_color = int((random.random()*(13 - 11))) + 11,	#### Original.
								#note_font_size=42)
								tile_color = color,							#### New.
								note_font_size=42)
		
		#### Revert to previous selection...
		n['selected'].setValue(False)
		for node in selNodes:
			if n.Class() == 'Viewer':
				viewer = n
				n["selected"].setValue(False)
			else:	
				node['selected'].setValue(True)
		return n
		
	def exr_shuffle(self):
		'''
		Create the node schematic by taking a list of EXR file layers, using a number of additional variables that cause the node graph to be built in one of a number of predetermined ways.
		'''			
		print("--------------------------------")
		print("CompBuilder VARIABLES:")
		print("--------------------------------")
		print("Layout:", self.Layout)					#### Orientation of node tree - "Horizontal", "Vertical". Currently, only Horizontal is available.
		print("spacing_x:", self.spacing_x)				#### Pixel tiling values to change the spacing of nodes...
		print("spacing_y:", self.spacing_y)				#### Pixel tiling values to change the spacing of nodes...
		print("Basic:", self.Basic)					#### Flag to turn on creation of a basic additive comp...
		print("ShuffleLayers:", self.ShuffleLayers)			#### List of layers to use when creating the additive Shuffle nodes...
		print("Diffuse:", self.Diffuse)					#### Flag to turn on creation of the Diffuse comp section that builds a TotalLighting pass...
		print("DiffuseLayers:", self.DiffuseLayers)		#### Flag to turn on creation of the Diffuse comp section that builds a TotalLighting pass...
		print("Raw:", self.Raw)						#### Flag to turn on creation of the Raw Diffuse comp section that builds a TotalLighting pass...
		print("RawLayers:", self.RawLayers)				#### List of the raw GI and raw lighting layers used to build the TotalLighting pass, if found...
		print("CarBody:", self.CarBody)				#### Flag to turn on creation of a separate CarBody node section...
		print("CarBodyAlpha:", self.CarBodyAlpha)		#### List of the channel that holds the CarBody Paint alpha...
		print("BodyLayers:", self.BodyLayers)			#### List of the layers used to build the CarBody nodes, if found...
		print("postage_stamps:", self.postage_stamps)	#### Flag to turn on/off the Postage Stamp icons for Shuffle nodes...
		print("backdrop_off:", self.backdrop_off)			#### Flag to turn on/off the automatic backdrop creation...
		print("rand_color:", self.rand_color)			#### Flag to turn on/off the random color setting for backdrops created with the "auto_backdrop" method...
		print("--------------------------------")
		
		selNodes = nuke.selectedNodes()
		if (len(selNodes) < 1):
			nuke.message("Please select an EXR Read node...")
		
		#### Deselect the EXR Read node...
		selNodes[0]["selected"].setValue(False)
		
		#### Set the EXR Read node as the starting position for building our comp...
		exrPos = (selNodes[0].xpos(), selNodes[0].ypos())
		
		#### Set spacing for nodes that are created...
		if (self.Layout == "Horizontal"):
			nodeSpacingX = int(self.spacing_x)
			nodeSpacingY = int(self.spacing_y)
		elif (self.Layout == "Vertical"):
			nodeSpacingX = int(self.spacing_x)
			nodeSpacingY = int(self.spacing_y)
		else:
			nuke.message("Layout is unknown. Using Horizontal...")
			self.Layout = "Horizontal"
			nodeSpacingX = int(self.spacing_x)
			nodeSpacingY = int(self.spacing_y)
				
		###########################################################################################################################
		#### Build the comp, based on the available layers...
		###########################################################################################################################
		
		### Initialize inputB variable for B pipe connections...
		inputB = None
		#### Create a central dot below EXR Read node for common attachment point...
		dot = nuke.nodes.Dot()
		offset = 34
		dot.setXYpos(exrPos[0]+offset, (exrPos[1] + 150))
		dot.setInput(0, selNodes[0])
		
		###########################################################################################################################
		####  Basic:  We found enough layers for a Basic additive comp...
		###########################################################################################################################
		if (self.Basic == True and self.Diffuse == False and self.Raw == False and self.CarBody == False):
			
			for index, p in enumerate(self.ShuffleLayers):
				
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot = nuke.nodes.Dot()
				offset = 34
				ShuffleDot.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), dot.ypos() + 75)
				if (index == 0):	
					ShuffleDot.setInput(0, dot)
					inputB = ShuffleDot
				else:
					ShuffleDot.setInput(0, inputB)
					inputB = ShuffleDot
				
				##### Create the Shuffle nodes...
				ShuffleNode = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				ShuffleNode.setXYpos(ShuffleDot.xpos()-offset, ShuffleDot.ypos() + 25)
				#### Set which channel to shuffle...
				ShuffleNode.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode.setInput(0, ShuffleDot)
				
				##### Create the Merge nodes...
				if (index == 0):
					dot2 = nuke.nodes.Dot()
					offset = 34
					dot2.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), exrPos[1] + (nodeSpacingY*14))
					dot2.setInput(0, ShuffleNode)
					inputC = dot2
				else:
					myMerge = nuke.nodes.Merge2(operation='plus', label=p, output='rgb')
					myMerge.setXYpos(exrPos[0]+(index*nodeSpacingX*4), exrPos[1] + ((nodeSpacingY*14)-9))
					myMerge.setInput(0, inputC)
					myMerge.setInput(1, ShuffleNode)
					inputC = myMerge
					
					last = self.ShuffleLayers[-1]
					if (p == last):
						
						#########################################
						#### Create the Alpha Shuffle node and Copy nodes...
						ShuffleAlphaDot = nuke.nodes.Dot()
						offset = 34
						ShuffleAlphaDot.setXYpos((ShuffleNode.xpos()+offset+(nodeSpacingX*4)), ShuffleDot.ypos())
						ShuffleAlphaDot.setInput(0, ShuffleDot)
						
						ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
						ShuffleAlpha.setXYpos((ShuffleNode.xpos()+(nodeSpacingX*4)), ShuffleNode.ypos())
						ShuffleAlpha.knob('in').setValue('alpha')
						##### Connect to the dot node...
						ShuffleAlpha.setInput(0, ShuffleAlphaDot)
						#### Copy the Alpha back into the B stream...
						copyAlpha = nuke.nodes.Copy( from0='rgba.alpha', to0='rgba.alpha', inputs=[ myMerge, ShuffleAlpha ] )
						copyAlpha.setXYpos(ShuffleAlpha.xpos(), myMerge.ypos())
						
						#########################################
						#### Add a Backdrop node behind the whole graph...
						lastNode = copyAlpha
						lastNode["selected"].setValue(True)
						nuke.selectConnectedNodes()
						#### Create the backdrop, unless backdrop_off is set to True...
						if self.backdrop_off == False:
							self.auto_backdrop(self.rand_color)
					
		###########################################################################################################################
		####  BasicDiffuse:  We found enough layers for a Basic additive comp, plus a Diffuse comp. From those, we can build a new TotalLighting pass. Even if we also have the RawLayerSet, a Diffuse comp is preferred...
		###########################################################################################################################
		elif (self.Basic == True and self.Diffuse == True and self.Raw == False) or (self.Basic == True and self.Diffuse == True and self.Raw == True):
			
			for index, p in enumerate(self.DiffuseLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot = nuke.nodes.Dot()
				offset = 34
				ShuffleDot.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), dot.ypos() + 75)
				if (index == 0):	
					ShuffleDot.setInput(0, dot)
					inputB = ShuffleDot
				else:
					ShuffleDot.setInput(0, inputB)
					inputB = ShuffleDot
				
				##### Add the three Diffuse Comp Shuffle nodes...
				ShuffleNode = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				####node.setXYpos(exrPos[0]+(index*nodeSpacingX*4), dot.ypos() + 25)
				ShuffleNode.setXYpos(ShuffleDot.xpos()-offset, ShuffleDot.ypos() + 25)
				#### Set which channel to shuffle...
				ShuffleNode.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode.setInput(0, ShuffleDot)
				
				if index == 0:
					VRayGlobalIllumination = ShuffleNode
				if index == 1:
					VRayDiffuseFilter = ShuffleNode
				if index == 2:
					VRayLighting = ShuffleNode
			
			#########################################
			#### Build and connect the rest of the Diffuse comp section...
			dotDiffuse = nuke.nodes.Dot()
			offset = 34

			if self.postage_stamps:
				dotDiffuse.setXYpos(VRayDiffuseFilter.xpos()+offset, VRayDiffuseFilter.ypos() + 90)
			else:
				dotDiffuse.setXYpos(VRayDiffuseFilter.xpos()+offset, VRayDiffuseFilter.ypos() + 40)
				
			dotDiffuse.setInput(0, VRayDiffuseFilter)
			
			mergeDiffuseGI = nuke.nodes.Merge2( operation='divide', inputs=[ dotDiffuse, VRayGlobalIllumination ], label='RawGI', output='rgb' )
			mergeDiffuseGI.setXYpos(exrPos[0], (dotDiffuse.ypos()-9))
			
			mergeDiffuseLight = nuke.nodes.Merge2( operation='divide', inputs=[ dotDiffuse, VRayLighting ], label='RawLight', output='rgb' )
			mergeDiffuseLight.setXYpos(VRayLighting.xpos(), (dotDiffuse.ypos()-9))
			
			dotDiffuse2 = nuke.nodes.Dot()
			offset = 34
			dotDiffuse2.setXYpos(dotDiffuse.xpos(), dotDiffuse.ypos()+(nodeSpacingY*10))
			dotDiffuse2.setInput(0, dotDiffuse)
			
			mergeDiffuseRawGI = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, mergeDiffuseGI ], label='DiffuseGI', output='rgb' )
			mergeDiffuseRawGI.setXYpos(VRayGlobalIllumination.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeDiffuseRawLight = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, mergeDiffuseLight ], label='DiffuseLight', output='rgb' )
			mergeDiffuseRawLight.setXYpos(VRayLighting.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeTotalLight = nuke.nodes.Merge2( operation='plus', inputs=[ mergeDiffuseRawGI, mergeDiffuseRawLight ], label='TotalLight', output='rgb' )
			mergeTotalLight.setXYpos(VRayDiffuseFilter.xpos(), dotDiffuse2.ypos()+(nodeSpacingY*2))
			
			#########################################
			#### Create the Alpha Shuffle node and Copy nodes...
			ShuffleAlphaDot = nuke.nodes.Dot()
			offset = 34
			ShuffleAlphaDot.setXYpos((ShuffleNode.xpos()+offset+(nodeSpacingX*4)), ShuffleDot.ypos())
			ShuffleAlphaDot.setInput(0, ShuffleDot)

			ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
			ShuffleAlpha.setXYpos((VRayLighting.xpos()+(nodeSpacingX*4)), dot.ypos() + 100)
			ShuffleAlpha.knob('in').setValue('alpha')
			##### Connect to the dot node...
			ShuffleAlpha.setInput(0, ShuffleAlphaDot)
			#### Copy the Alpha back into the B stream...
			copyAlpha = nuke.nodes.Copy( from0='rgba.alpha', to0='rgba.alpha', inputs=[ mergeTotalLight, ShuffleAlpha ] )
			copyAlpha.setXYpos(mergeDiffuseRawLight.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))
			
			#########################################
			#### Create the additive/plus Shuffle nodes...
			shuffleList = []
			
			for index, p in enumerate(self.ShuffleLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot2 = nuke.nodes.Dot()
				offset = 34
				ShuffleDot2.setXYpos((ShuffleAlpha.xpos()+offset+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlphaDot.ypos())
				if (index == 0):	
					ShuffleDot2.setInput(0, ShuffleAlphaDot)
					inputC = ShuffleDot2
				else:
					ShuffleDot2.setInput(0, inputC)
					inputC = ShuffleDot2
				
				##### Create the Shuffle nodes...
				ShuffleNode2 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				#### Offset them from the last Shuffle we created...
				ShuffleNode2.setXYpos(ShuffleDot2.xpos()-offset, ShuffleAlpha.ypos())		
				#### Set which channel to shuffle...
				ShuffleNode2.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode2.setInput(0, ShuffleDot2)
				
				shuffleList.append((p, ShuffleNode2))
				
			last = shuffleList[-1]
			
			#########################################
			#### Create and connect the Merge nodes...
			for index, p in enumerate(shuffleList):
				
				if len(shuffleList) > 1:
					if index == 0:
						node = nuke.nodes.Merge2( operation='plus', inputs=[ copyAlpha, list(shuffleList[0])[1] ], label=p[0], output='rgb' )
						node.setXYpos(copyAlpha.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))
						inputB = node
					else:
						myMerge = nuke.nodes.Merge2(operation='plus', label=p[0], output='rgb')
						myMerge.setXYpos((copyAlpha.xpos()+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), dotDiffuse2.ypos()+(nodeSpacingY*2))
						myMerge.setInput(0, inputB)
						myMerge.setInput(1, p[1])
						inputB = myMerge
						
						lastNode = myMerge
						
				if len(shuffleList) == 1:
					if index == 0:
						node = nuke.nodes.Merge2( operation='plus', inputs=[ copyAlpha, list(shuffleList[0])[1] ], label=p[0], output='rgb' )
						node.setXYpos(copyAlpha.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))
						inputB = node

						lastNode = node
			
				if (p == last):
					
					#### If we don't have all the CarBody passes, we're done with the BasicDiffuse build...
					if (self.CarBody == False):
						#########################################
						#### Add a Backdrop node behind the whole graph...
						lastNode["selected"].setValue(True)
						nuke.selectConnectedNodes()
						#### Create the backdrop, unless backdrop_off is set to True...
						if self.backdrop_off == False:
							self.auto_backdrop(self.rand_color)

					else:
						###########################################################################################################################
						####  BasicDiffuseCarBody:  We have all of the CarBody passes - add the extra CarBody comp section to the BasicDiffuse configuration...
						###########################################################################################################################
						
						bodyPasses = []
			
						for index, p2 in enumerate(self.BodyLayers):
							#### Create dot for each Shuffle node to hang from...
							ShuffleDot3 = nuke.nodes.Dot()
							offset = 34
							ShuffleDot3.setXYpos((ShuffleDot2.xpos()+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlphaDot.ypos())
							if (index == 0):	
								ShuffleDot3.setInput(0, ShuffleDot2)
								inputC = ShuffleDot3
							else:
								ShuffleDot3.setInput(0, inputC)
								inputC = ShuffleDot3
						
							##### Create the CarBody Shuffle nodes...
							ShuffleNode3 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p2, label='[value in]', postage_stamp = self.postage_stamps)
							#### Offset them from the last Shuffle we created...
							ShuffleNode3.setXYpos(ShuffleDot2.xpos()-offset+(nodeSpacingX*4)+(index*(nodeSpacingX*4)), ShuffleNode2.ypos())
							#### Set which channel to shuffle...
							ShuffleNode3.knob('in').setValue(p2)
							##### Connect to the dot node...
							ShuffleNode3.setInput(0, ShuffleDot3)
							
							bodyPasses.append((p2, ShuffleNode3))
						
						#########################################
						#### Create and connect the rest of the BodyPaint Merge nodes...
						for index, p3 in enumerate(bodyPasses):
							if (index == 0):
								dot3 = nuke.nodes.Dot()
								offset = 34
								dot3.setXYpos((p[1].xpos()+offset+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()))
								dot3.setInput(0, (bodyPasses[0])[1])
								inputB2 = dot3
							else:
								myMerge2 = nuke.nodes.Merge2(operation='plus', label=p3[0], output='rgb')
								myMerge2.setXYpos(dot3.xpos()-offset+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()-9))
								myMerge2.setInput(0, inputB2)
								myMerge2.setInput(1, p3[1])
								inputB2 = myMerge2
								
						#########################################
						#### Create the Alpha Shuffle node and Copy node...
						dotBodyAlpha = nuke.nodes.Dot()
						offset = 34
						dotBodyAlpha.setXYpos((myMerge2.xpos()+offset+(nodeSpacingX*4)), ShuffleDot3.ypos())
						##### Connect to the dot node...
						dotBodyAlpha.setInput(0, ShuffleDot3)
						#### Copy the CarBody alpha into the stream...
						BodyAlpha = nuke.nodes.Copy( from0=self.CarBodyAlpha[0], to0='rgba.alpha', inputs=[ myMerge2, dotBodyAlpha ] )
						BodyAlpha.setXYpos(myMerge2.xpos()+(nodeSpacingX*4), myMerge2.ypos())
						#########################################
						#### Create the last Merge node...
						mergeCarBodyPaint = nuke.nodes.Merge2( operation='over', inputs=[ lastNode, BodyAlpha ], label='CarBodyPaint', output='rgb')
						mergeCarBodyPaint.setXYpos(BodyAlpha.xpos(), lastNode.ypos())
						#########################################
						#### Add a Backdrop node behind the whole graph...
						lastNode = mergeCarBodyPaint
						lastNode["selected"].setValue(True)
						nuke.selectConnectedNodes()
						#### Create the backdrop, unless backdrop_off is set to True...
						if self.backdrop_off == False:
							self.auto_backdrop(self.rand_color)
						
		###########################################################################################################################
		####  BasicRaw:  We found enough layers for a Basic additive comp, plus a Raw comp. From those, we can build a new TotalLighting pass...
		###########################################################################################################################
		elif (self.Basic == True and self.Diffuse == False and self.Raw == True):
			
			for index, p in enumerate(self.RawLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot = nuke.nodes.Dot()
				offset = 34
				ShuffleDot.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), dot.ypos() + 75)
				if (index == 0):
					ShuffleDot.setInput(0, dot)
					inputB = ShuffleDot
				else:
					ShuffleDot.setInput(0, inputB)
					inputB = ShuffleDot
				
				##### Add the three RawDiffuse Comp Shuffle nodes...
				ShuffleNode = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				ShuffleNode.setXYpos(ShuffleDot.xpos()-offset, ShuffleDot.ypos() + 25)
				#### Set which channel to shuffle...
				ShuffleNode.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode.setInput(0, ShuffleDot)
				
				if index == 0:
					VRayRawGlobalIllumination = ShuffleNode
				if index == 1:
					VRayDiffuseFilter = ShuffleNode
				if index == 2:
					VRayRawLighting = ShuffleNode
			
			#########################################
			#### Build and connect the rest of the RawDiffuse comp section...
			dotDiffuse2 = nuke.nodes.Dot()
			offset = 34
			dotDiffuse2.setXYpos(VRayDiffuseFilter.xpos()+offset, VRayDiffuseFilter.ypos()+(nodeSpacingY*10))
			dotDiffuse2.setInput(0, VRayDiffuseFilter)
			
			mergeDiffuseRawGI = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, VRayRawGlobalIllumination ], label='DiffuseGI', output='rgb' )
			mergeDiffuseRawGI.setXYpos(VRayRawGlobalIllumination.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeDiffuseRawLight = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, VRayRawLighting ], label='DiffuseLight', output='rgb' )
			mergeDiffuseRawLight.setXYpos(VRayRawLighting.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeTotalLight = nuke.nodes.Merge2( operation='plus', inputs=[ mergeDiffuseRawGI, mergeDiffuseRawLight ], label='TotalLight', output='rgb' )
			mergeTotalLight.setXYpos(VRayDiffuseFilter.xpos(), dotDiffuse2.ypos()+(nodeSpacingY*2))
			
			#########################################
			#### Create the Alpha Shuffle node and Copy nodes...
			ShuffleAlphaDot = nuke.nodes.Dot()
			offset = 34
			ShuffleAlphaDot.setXYpos((ShuffleNode.xpos()+offset+(nodeSpacingX*4)), ShuffleDot.ypos())
			ShuffleAlphaDot.setInput(0, ShuffleDot)
			
			ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
			ShuffleAlpha.setXYpos((VRayRawLighting.xpos()+(nodeSpacingX*4)), VRayRawLighting.ypos())
			ShuffleAlpha.knob('in').setValue('alpha')
			##### Connect to the dot node...
			ShuffleAlpha.setInput(0, ShuffleAlphaDot)
			#### Copy the Alpha back into the B stream...
			copyAlpha = nuke.nodes.Copy( from0='rgba.alpha', to0='rgba.alpha', inputs=[ mergeTotalLight, ShuffleAlpha ] )
			copyAlpha.setXYpos(mergeDiffuseRawLight.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))
			
			#########################################
			#### Create the additive/plus Shuffle nodes...
		
			shuffleList = []
			
			for index, p in enumerate(self.ShuffleLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot2 = nuke.nodes.Dot()
				offset = 34
				ShuffleDot2.setXYpos((ShuffleAlpha.xpos()+offset+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlphaDot.ypos())
				if (index == 0):	
					ShuffleDot2.setInput(0, ShuffleAlphaDot)
					inputC = ShuffleDot2
				else:
					ShuffleDot2.setInput(0, inputC)
					inputC = ShuffleDot2
				
				##### Create the Shuffle nodes...
				ShuffleNode2 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				#### Offset them from the last Shuffle we created...
				#ShuffleNode2.setXYpos((ShuffleAlpha.xpos()+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlpha.ypos())
				ShuffleNode2.setXYpos(ShuffleDot2.xpos()-offset, ShuffleAlpha.ypos())
				#### Set which channel to shuffle...
				ShuffleNode2.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode2.setInput(0, ShuffleDot2)
				
				shuffleList.append((p, ShuffleNode2))
			
			last = shuffleList[-1]
			
			#########################################
			#### Create and connect the Merge nodes...
			for index, p in enumerate(shuffleList):

				if len(shuffleList) > 1:
					if index == 0:
						node = nuke.nodes.Merge2( operation='plus', inputs=[ copyAlpha, list(shuffleList[0])[1] ], label=p[0], output='rgb' )
						node.setXYpos(copyAlpha.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))
						inputB = node
					else:
						myMerge = nuke.nodes.Merge2(operation='plus', label=p[0], output='rgb')
						myMerge.setXYpos((copyAlpha.xpos()+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), dotDiffuse2.ypos()+(nodeSpacingY*2))
						myMerge.setInput(0, inputB)
						myMerge.setInput(1, p[1])
						inputB = myMerge
						
						lastNode = myMerge
						
				if len(shuffleList) == 1:
					if index == 0:
						node = nuke.nodes.Merge2( operation='plus', inputs=[ copyAlpha, list(shuffleList[0])[1] ], label=p[0], output='rgb' )
						node.setXYpos(copyAlpha.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))
						inputB = node

						lastNode = node
					
				if (p == last):
					#### We don't have all the CarBody passes, so we're done.
					if (self.CarBody == False):
						#########################################
						#### Add a Backdrop node behind the whole graph...
						lastNode["selected"].setValue(True)
						nuke.selectConnectedNodes()
						#### Create the backdrop, unless backdrop_off is set to True...
						if self.backdrop_off == False:
							self.auto_backdrop(self.rand_color)
						
					else:
						###########################################################################################################################
						#### We have all of the CarBody passes - create the extra CarBody comp section...
						###########################################################################################################################
						
						bodyList = []
						
						##### Create the CarBody Shuffle nodes...
						for index, p2 in enumerate(self.BodyLayers):
							#### Create dot for each Shuffle node to hang from...
							ShuffleDot3 = nuke.nodes.Dot()
							offset = 34
							ShuffleDot3.setXYpos((ShuffleDot2.xpos()+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlphaDot.ypos())
							if (index == 0):	
								ShuffleDot3.setInput(0, ShuffleDot2)
								inputC = ShuffleDot3
							else:
								ShuffleDot3.setInput(0, inputC)
								inputC = ShuffleDot3					
								
							ShuffleNode3 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p2, label='[value in]', postage_stamp = self.postage_stamps)
							#### Offset them from the last Shuffle we created...
							ShuffleNode3.setXYpos(ShuffleDot2.xpos()-offset+(nodeSpacingX*4)+(index*(nodeSpacingX*4)), ShuffleNode2.ypos())
							#### Set which channel to shuffle...
							ShuffleNode3.knob('in').setValue(p2)
							##### Connect to the dot node...
							ShuffleNode3.setInput(0, ShuffleDot3)
							
							bodyList.append((p2, ShuffleNode3))
							
						#########################################
						#### Create and connect the rest of the BodyPaint Merge nodes...
						for index, p3 in enumerate(bodyList):
							if (index == 0):
								dot3 = nuke.nodes.Dot()
								offset = 34
								dot3.setXYpos((p[1].xpos()+offset+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()))
								dot3.setInput(0, (bodyList[0])[1])
								inputB2 = dot3
							else:
								myMerge2 = nuke.nodes.Merge2(operation='plus', label=p3[0], output='rgb')
								myMerge2.setXYpos(dot3.xpos()-offset+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()-9))
								myMerge2.setInput(0, inputB2)
								myMerge2.setInput(1, p3[1])
								inputB2 = myMerge2
								
						#########################################
						#### Create the Alpha Shuffle node and Copy node...
						dotBodyAlpha = nuke.nodes.Dot()
						offset = 34
						dotBodyAlpha.setXYpos((myMerge2.xpos()+offset+(nodeSpacingX*4)), ShuffleDot3.ypos())		
						##### Connect to the dot node...
						dotBodyAlpha.setInput(0, ShuffleDot3)
						#### Copy the CarBody alpha into the stream...
						BodyAlpha = nuke.nodes.Copy( from0=self.CarBodyAlpha[0], to0='rgba.alpha', inputs=[ myMerge2, dotBodyAlpha ] )
						BodyAlpha.setXYpos(myMerge2.xpos()+(nodeSpacingX*4), myMerge2.ypos())
						#########################################
						#### Create the last Merge node...
						mergeCarBodyPaint = nuke.nodes.Merge2( operation='over', inputs=[ lastNode, BodyAlpha ], label='CarBodyPaint', output='rgb' )
						mergeCarBodyPaint.setXYpos(BodyAlpha.xpos(), lastNode.ypos())
						#########################################
						#### Add a Backdrop node behind the whole graph...
						lastNode = mergeCarBodyPaint
						lastNode["selected"].setValue(True)
						nuke.selectConnectedNodes()
						#### Create the backdrop, unless backdrop_off is set to True...
						if self.backdrop_off == False:
							self.auto_backdrop(self.rand_color)
							
		###########################################################################################################################
		####  BasicCarBody:  We found enough layers for a Basic additive comp, not enough Diffuse comp layers, but we do have a CarBody set of layers we can build...
		###########################################################################################################################
		elif (self.Basic == True and self.Diffuse == False and self.CarBody == True):
			
			last = self.ShuffleLayers[-1]
			
			for index, p in enumerate(self.ShuffleLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot = nuke.nodes.Dot()
				offset = 34
				ShuffleDot.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), dot.ypos() + 75)
				if (index == 0):	
					ShuffleDot.setInput(0, dot)
					inputB = ShuffleDot
				else:
					ShuffleDot.setInput(0, inputB)
					inputB = ShuffleDot
					
				##### Create the Shuffle nodes...
				ShuffleNode = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				#node.setXYpos(exrPos[0]+(index*nodeSpacingX*4), dot.ypos() + 100)
				ShuffleNode.setXYpos(ShuffleDot.xpos()-offset, ShuffleDot.ypos() + 25)
				#### Set which channel to shuffle...
				ShuffleNode.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode.setInput(0, ShuffleDot)
				
				##### Create the Merge nodes...
				if (index == 0):
					dot2 = nuke.nodes.Dot()
					offset = 34
					dot2.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), exrPos[1] + (nodeSpacingY*14))
					dot2.setInput(0, ShuffleNode)
					inputC = dot2
				else:
					myMerge = nuke.nodes.Merge2(operation='plus', label=p, output='rgb')
					myMerge.setXYpos(exrPos[0]+(index*nodeSpacingX*4), exrPos[1] + ((nodeSpacingY*14)-9))
					myMerge.setInput(0, inputC)
					myMerge.setInput(1, ShuffleNode)
					inputC = myMerge
					
					last = self.ShuffleLayers[-1]
					if (p == last):
						
						#########################################
						#### Create the Alpha Shuffle node and Copy nodes...
						ShuffleAlphaDot = nuke.nodes.Dot()
						offset = 34
						ShuffleAlphaDot.setXYpos((ShuffleNode.xpos()+offset+(nodeSpacingX*4)), ShuffleDot.ypos())
						ShuffleAlphaDot.setInput(0, ShuffleDot)
						
						ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
						ShuffleAlpha.setXYpos((ShuffleNode.xpos()+(nodeSpacingX*4)), ShuffleNode.ypos())
						ShuffleAlpha.knob('in').setValue('alpha')
						##### Connect to the dot node...
						ShuffleAlpha.setInput(0, ShuffleAlphaDot)
						#### Copy the Alpha back into the B stream...
						copyAlpha = nuke.nodes.Copy( from0='rgba.alpha', to0='rgba.alpha', inputs=[ myMerge, ShuffleAlpha ] )
						copyAlpha.setXYpos(ShuffleAlpha.xpos(), myMerge.ypos())
						
						###########################################################################################################################
						#### We have all of the CarBody passes - create the extra CarBody comp section...
						###########################################################################################################################

						bodyList = []

						for index, p2 in enumerate(self.BodyLayers):
							#### Create dot for each Shuffle node to hang from...
							ShuffleDot3 = nuke.nodes.Dot()
							offset = 34
							ShuffleDot3.setXYpos((ShuffleAlpha.xpos()+offset+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlphaDot.ypos())
							if (index == 0):	
								ShuffleDot3.setInput(0, ShuffleAlphaDot)
								inputD = ShuffleDot3
							else:
								ShuffleDot3.setInput(0, inputD)
								inputD = ShuffleDot3
							
							##### Create the CarBody Shuffle nodes...
							ShuffleNode3 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p2, label='[value in]', postage_stamp = self.postage_stamps)
							#### Offset them from the last Shuffle we created...
							ShuffleNode3.setXYpos((ShuffleAlpha.xpos()+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlpha.ypos())
							#### Set which channel to shuffle...
							ShuffleNode3.knob('in').setValue(p2)
							##### Connect to the dot node...
							ShuffleNode3.setInput(0, ShuffleDot3)
							
							bodyList.append((p2, ShuffleNode3))
						
						#########################################
						#### Create and connect the rest of the BodyPaint Merge nodes...
						for index, p3 in enumerate(bodyList):
							if (index == 0):
								dot3 = nuke.nodes.Dot()
								offset = 34
								dot3.setXYpos(((bodyList[0])[1]).xpos() + offset, (copyAlpha.ypos() - nodeSpacingY*1))
								dot3.setInput(0, (bodyList[0])[1])
								inputB2 = dot3
							else:
								myMerge2 = nuke.nodes.Merge2(operation='plus', label=p3[0], output='rgb')
								myMerge2.setXYpos(dot3.xpos()-offset+(index*(nodeSpacingX*4)), (dot3.ypos()-9))
								myMerge2.setInput(0, inputB2)
								myMerge2.setInput(1, p3[1])
								inputB2 = myMerge2
							
						#########################################
						#### Create the Alpha Shuffle node and Copy node...
						dotBodyAlpha = nuke.nodes.Dot()
						offset = 34
						#dotBodyAlpha.setXYpos((myMerge2.xpos()+offset+(nodeSpacingX*4)), (bodyList[-1])[1].ypos())
						dotBodyAlpha.setXYpos((myMerge2.xpos()+offset+(nodeSpacingX*4)), ShuffleDot3.ypos())
						##### Connect to the dot node...
						dotBodyAlpha.setInput(0, ShuffleDot3)
						#### Copy the CarBody alpha into the stream...
						BodyAlpha = nuke.nodes.Copy( from0=self.CarBodyAlpha[0], to0='rgba.alpha', inputs=[ myMerge2, dotBodyAlpha ] )
						BodyAlpha.setXYpos(myMerge2.xpos()+(nodeSpacingX*4), myMerge2.ypos())	
						#########################################
						#### Create the last Merge node...
						mergeCarBodyPaint = nuke.nodes.Merge2( operation='over', inputs=[ copyAlpha, BodyAlpha ], label='CarBodyPaint', output='rgb' )
						mergeCarBodyPaint.setXYpos(BodyAlpha.xpos(), copyAlpha.ypos())
						#########################################
						#### Add a Backdrop node behind the whole graph...
						lastNode = mergeCarBodyPaint
						lastNode["selected"].setValue(True)
						nuke.selectConnectedNodes()
						#### Create the backdrop, unless backdrop_off is set to True...
						if self.backdrop_off == False:
							self.auto_backdrop(self.rand_color)

		###########################################################################################################################
		#### DiffuseCarBody:  We found enough layers for a separated Diffuse comp and a CarBody build...
		###########################################################################################################################
		elif (self.Basic == False and self.Diffuse == True and self.Raw == False and self.CarBody == True) or (self.Basic == False and self.Diffuse == True and self.Raw == True and self.CarBody == True):
			
			for index, p in enumerate(self.DiffuseLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot = nuke.nodes.Dot()
				offset = 34
				ShuffleDot.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), dot.ypos() + 75)
				if (index == 0):	
					ShuffleDot.setInput(0, dot)
					inputB = ShuffleDot
				else:
					ShuffleDot.setInput(0, inputB)
					inputB = ShuffleDot
				
				##### Add the three Diffuse Comp Shuffle nodes...
				ShuffleNode = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				####node.setXYpos(exrPos[0]+(index*nodeSpacingX*4), dot.ypos() + 25)
				ShuffleNode.setXYpos(ShuffleDot.xpos()-offset, ShuffleDot.ypos() + 25)
				#### Set which channel to shuffle...
				ShuffleNode.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode.setInput(0, ShuffleDot)
				
				if index == 0:
					VRayGlobalIllumination = ShuffleNode
				if index == 1:
					VRayDiffuseFilter = ShuffleNode
				if index == 2:
					VRayLighting = ShuffleNode
			
			#########################################
			#### Build and connect the rest of the Diffuse comp section...
			dotDiffuse = nuke.nodes.Dot()
			offset = 34

			if self.postage_stamps:
				dotDiffuse.setXYpos(VRayDiffuseFilter.xpos()+offset, VRayDiffuseFilter.ypos() + 90)
			else:
				dotDiffuse.setXYpos(VRayDiffuseFilter.xpos()+offset, VRayDiffuseFilter.ypos() + 40)
				
			dotDiffuse.setInput(0, VRayDiffuseFilter)
			
			mergeDiffuseGI = nuke.nodes.Merge2( operation='divide', inputs=[ dotDiffuse, VRayGlobalIllumination ], label='RawGI', output='rgb' )
			mergeDiffuseGI.setXYpos(exrPos[0], (dotDiffuse.ypos()-9))
			
			mergeDiffuseLight = nuke.nodes.Merge2( operation='divide', inputs=[ dotDiffuse, VRayLighting ], label='RawLight', output='rgb' )
			mergeDiffuseLight.setXYpos(VRayLighting.xpos(), (dotDiffuse.ypos()-9))
			
			dotDiffuse2 = nuke.nodes.Dot()
			offset = 34
			dotDiffuse2.setXYpos(dotDiffuse.xpos(), dotDiffuse.ypos()+(nodeSpacingY*10))
			dotDiffuse2.setInput(0, dotDiffuse)
			
			mergeDiffuseRawGI = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, mergeDiffuseGI ], label='DiffuseGI', output='rgb' )
			mergeDiffuseRawGI.setXYpos(VRayGlobalIllumination.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeDiffuseRawLight = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, mergeDiffuseLight ], label='DiffuseLight', output='rgb' )
			mergeDiffuseRawLight.setXYpos(VRayLighting.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeTotalLight = nuke.nodes.Merge2( operation='plus', inputs=[ mergeDiffuseRawGI, mergeDiffuseRawLight ], label='TotalLight', output='rgb' )
			mergeTotalLight.setXYpos(VRayDiffuseFilter.xpos(), dotDiffuse2.ypos()+(nodeSpacingY*2))
			
			#########################################
			#### Create the Alpha Shuffle node and Copy nodes...
			ShuffleAlphaDot = nuke.nodes.Dot()
			offset = 34
			ShuffleAlphaDot.setXYpos((ShuffleNode.xpos()+offset+(nodeSpacingX*4)), ShuffleDot.ypos())
			ShuffleAlphaDot.setInput(0, ShuffleDot)

			ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
			ShuffleAlpha.setXYpos((VRayLighting.xpos()+(nodeSpacingX*4)), dot.ypos() + 100)
			ShuffleAlpha.knob('in').setValue('alpha')
			##### Connect to the dot node...
			ShuffleAlpha.setInput(0, ShuffleAlphaDot)
			#### Copy the Alpha back into the B stream...
			copyAlpha = nuke.nodes.Copy( from0='rgba.alpha', to0='rgba.alpha', inputs=[ mergeTotalLight, ShuffleAlpha ] )
			copyAlpha.setXYpos(mergeDiffuseRawLight.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))

			###########################################################################################################################
			#### We have all of the CarBody passes - add the extra CarBody comp section to the Diffuse configuration...
			###########################################################################################################################
			
			bodyPasses = []

			for index, p2 in enumerate(self.BodyLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot3 = nuke.nodes.Dot()
				offset = 34
				ShuffleDot3.setXYpos((ShuffleAlphaDot.xpos()+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlphaDot.ypos())
				if (index == 0):	
					ShuffleDot3.setInput(0, ShuffleAlphaDot)
					inputC = ShuffleDot3
				else:
					ShuffleDot3.setInput(0, inputC)
					inputC = ShuffleDot3
			
				##### Create the CarBody Shuffle nodes...
				ShuffleNode3 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p2, label='[value in]', postage_stamp = self.postage_stamps)
				#### Offset them from the last Shuffle we created...
				ShuffleNode3.setXYpos(ShuffleAlphaDot.xpos()-offset+(nodeSpacingX*4)+(index*(nodeSpacingX*4)), ShuffleAlpha.ypos())
				#### Set which channel to shuffle...
				ShuffleNode3.knob('in').setValue(p2)
				##### Connect to the dot node...
				ShuffleNode3.setInput(0, ShuffleDot3)
				
				bodyPasses.append((p2, ShuffleNode3))
			
			#########################################
			#### Create and connect the rest of the BodyPaint Merge nodes...
			for index, p3 in enumerate(bodyPasses):
				if (index == 0):
					dot3 = nuke.nodes.Dot()
					offset = 34
					dot3.setXYpos((bodyPasses[0])[1].xpos()+offset+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()))
					dot3.setInput(0, (bodyPasses[0])[1])
					inputB2 = dot3
				else:
					myMerge2 = nuke.nodes.Merge2(operation='plus', label=p3[0], output='rgb')
					myMerge2.setXYpos(dot3.xpos()-offset+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()-9))
					myMerge2.setInput(0, inputB2)
					myMerge2.setInput(1, p3[1])
					inputB2 = myMerge2
					
			#########################################
			#### Create the Alpha Shuffle node and Copy node...
			dotBodyAlpha = nuke.nodes.Dot()
			offset = 34
			dotBodyAlpha.setXYpos((myMerge2.xpos()+offset+(nodeSpacingX*4)), ShuffleDot3.ypos())
			##### Connect to the dot node...
			dotBodyAlpha.setInput(0, ShuffleDot3)
			#### Copy the CarBody alpha into the stream...
			BodyAlpha = nuke.nodes.Copy( from0=self.CarBodyAlpha[0], to0='rgba.alpha', inputs=[ myMerge2, dotBodyAlpha ] )
			BodyAlpha.setXYpos(myMerge2.xpos()+(nodeSpacingX*4), myMerge2.ypos())
			#########################################
			#### Create the last Merge node...
			mergeCarBodyPaint = nuke.nodes.Merge2( operation='over', inputs=[ copyAlpha, BodyAlpha ], label='CarBodyPaint', output='rgb')
			mergeCarBodyPaint.setXYpos(BodyAlpha.xpos(), copyAlpha.ypos())
			#########################################
			#### Add a Backdrop node behind the whole graph...
			lastNode = mergeCarBodyPaint
			lastNode["selected"].setValue(True)
			nuke.selectConnectedNodes()
			#### Create the backdrop, unless backdrop_off is set to True...
			if self.backdrop_off == False:
				self.auto_backdrop(self.rand_color)

		###########################################################################################################################
		####  RawCarBody:  We found enough layers for a separated Raw comp and a CarBody build...
		###########################################################################################################################
		elif (self.Basic == False and self.Diffuse == False and self.Raw == True and self.CarBody == True):
			
			for index, p in enumerate(self.RawLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot = nuke.nodes.Dot()
				offset = 34
				ShuffleDot.setXYpos(exrPos[0]+offset+(index*nodeSpacingX*4), dot.ypos() + 75)
				if (index == 0):
					ShuffleDot.setInput(0, dot)
					inputB = ShuffleDot
				else:
					ShuffleDot.setInput(0, inputB)
					inputB = ShuffleDot
				
				##### Add the three RawDiffuse Comp Shuffle nodes...
				ShuffleNode = nuke.nodes.Shuffle(name = 'Shuffle_'+ p, label='[value in]', postage_stamp = self.postage_stamps)
				ShuffleNode.setXYpos(ShuffleDot.xpos()-offset, ShuffleDot.ypos() + 25)
				#### Set which channel to shuffle...
				ShuffleNode.knob('in').setValue(p)
				##### Connect to the dot node...
				ShuffleNode.setInput(0, ShuffleDot)
				
				if index == 0:
					VRayRawGlobalIllumination = ShuffleNode
				if index == 1:
					VRayDiffuseFilter = ShuffleNode
				if index == 2:
					VRayRawLighting = ShuffleNode
			
			#########################################
			#### Build and connect the rest of the RawDiffuse comp section...
			dotDiffuse2 = nuke.nodes.Dot()
			offset = 34
			dotDiffuse2.setXYpos(VRayDiffuseFilter.xpos()+offset, VRayDiffuseFilter.ypos()+(nodeSpacingY*10))
			dotDiffuse2.setInput(0, VRayDiffuseFilter)
			
			mergeDiffuseRawGI = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, VRayRawGlobalIllumination ], label='DiffuseGI', output='rgb' )
			mergeDiffuseRawGI.setXYpos(VRayRawGlobalIllumination.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeDiffuseRawLight = nuke.nodes.Merge2( operation='multiply', inputs=[ dotDiffuse2, VRayRawLighting ], label='DiffuseLight', output='rgb' )
			mergeDiffuseRawLight.setXYpos(VRayRawLighting.xpos(), (dotDiffuse2.ypos()-9))
			
			mergeTotalLight = nuke.nodes.Merge2( operation='plus', inputs=[ mergeDiffuseRawGI, mergeDiffuseRawLight ], label='TotalLight', output='rgb' )
			mergeTotalLight.setXYpos(VRayDiffuseFilter.xpos(), dotDiffuse2.ypos()+(nodeSpacingY*2))
			
			#########################################
			#### Create the Alpha Shuffle node and Copy nodes...
			ShuffleAlphaDot = nuke.nodes.Dot()
			offset = 34
			ShuffleAlphaDot.setXYpos((ShuffleNode.xpos()+offset+(nodeSpacingX*4)), ShuffleDot.ypos())
			ShuffleAlphaDot.setInput(0, ShuffleDot)
			
			ShuffleAlpha = nuke.nodes.Shuffle(name = 'Shuffle_Alpha', label='alpha', postage_stamp = self.postage_stamps)
			ShuffleAlpha.setXYpos((VRayRawLighting.xpos()+(nodeSpacingX*4)), VRayRawLighting.ypos())
			ShuffleAlpha.knob('in').setValue('alpha')
			##### Connect to the dot node...
			ShuffleAlpha.setInput(0, ShuffleAlphaDot)
			#### Copy the Alpha back into the B stream...
			copyAlpha = nuke.nodes.Copy( from0='rgba.alpha', to0='rgba.alpha', inputs=[ mergeTotalLight, ShuffleAlpha ] )
			copyAlpha.setXYpos(mergeDiffuseRawLight.xpos()+(nodeSpacingX*4), dotDiffuse2.ypos()+(nodeSpacingY*2))

			###########################################################################################################################
			#### We have all of the CarBody passes - create the extra CarBody comp section...
			###########################################################################################################################
			
			bodyList = []
			
			##### Create the CarBody Shuffle nodes...
			for index, p2 in enumerate(self.BodyLayers):
				#### Create dot for each Shuffle node to hang from...
				ShuffleDot3 = nuke.nodes.Dot()
				offset = 34
				ShuffleDot3.setXYpos((ShuffleAlpha.xpos()+offset+(nodeSpacingX*4))+(index*(nodeSpacingX*4)), ShuffleAlphaDot.ypos())
				if (index == 0):	
					ShuffleDot3.setInput(0, ShuffleAlphaDot)
					inputC = ShuffleDot3
				else:
					ShuffleDot3.setInput(0, inputC)
					inputC = ShuffleDot3					
					
				ShuffleNode3 = nuke.nodes.Shuffle(name = 'Shuffle_'+ p2, label='[value in]', postage_stamp = self.postage_stamps)
				#### Offset them from the last Shuffle we created...
				ShuffleNode3.setXYpos(ShuffleAlpha.xpos()+(nodeSpacingX*4)+(index*(nodeSpacingX*4)), ShuffleAlpha.ypos())
				#### Set which channel to shuffle...
				ShuffleNode3.knob('in').setValue(p2)
				##### Connect to the dot node...
				ShuffleNode3.setInput(0, ShuffleDot3)
				
				bodyList.append((p2, ShuffleNode3))
				
			#########################################
			#### Create and connect the rest of the BodyPaint Merge nodes...
			for index, p3 in enumerate(bodyList):
				if (index == 0):
					dot3 = nuke.nodes.Dot()
					offset = 34
					dot3.setXYpos(((bodyList[0])[1].xpos()+offset)+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()))
					dot3.setInput(0, (bodyList[0])[1])
					inputB2 = dot3
				else:
					myMerge2 = nuke.nodes.Merge2(operation='plus', label=p3[0], output='rgb')
					myMerge2.setXYpos(dot3.xpos()-offset+(index*(nodeSpacingX*4)), (dotDiffuse2.ypos()-9))
					myMerge2.setInput(0, inputB2)
					myMerge2.setInput(1, p3[1])
					inputB2 = myMerge2
					
			#########################################
			#### Create the Alpha Shuffle node and Copy node...
			dotBodyAlpha = nuke.nodes.Dot()
			offset = 34
			dotBodyAlpha.setXYpos((myMerge2.xpos()+offset+(nodeSpacingX*4)), ShuffleDot3.ypos())		
			##### Connect to the dot node...
			dotBodyAlpha.setInput(0, ShuffleDot3)
			#### Copy the CarBody alpha into the stream...
			BodyAlpha = nuke.nodes.Copy( from0=self.CarBodyAlpha[0], to0='rgba.alpha', inputs=[ myMerge2, dotBodyAlpha ] )
			BodyAlpha.setXYpos(myMerge2.xpos()+(nodeSpacingX*4), myMerge2.ypos())
			#########################################
			#### Create the last Merge node...
			mergeCarBodyPaint = nuke.nodes.Merge2( operation='over', inputs=[ copyAlpha, BodyAlpha ], label='CarBodyPaint', output='rgb' )
			mergeCarBodyPaint.setXYpos(BodyAlpha.xpos(), copyAlpha.ypos())
			#########################################
			#### Add a Backdrop node behind the whole graph...
			lastNode = mergeCarBodyPaint
			lastNode["selected"].setValue(True)
			nuke.selectConnectedNodes()
			#### Create the backdrop, unless backdrop_off is set to True...
			if self.backdrop_off == False:
				self.auto_backdrop(self.rand_color)

		else:
			
			nuke.message("I'm confused!")

	def exr_comp(self):
		'''
		The main method. Get all the layers and channels from a selected EXR Read node. Pick from several node graph templates,
		based on the VRay render layer names available in the EXR file. If the available layer names don't match any of the predetermined
		layer names and templates, the user is prompted via a popup menu to associate the available layers in the EXR file to their matching
		VRay render pass names. The script will attempt to create a sensible node graph from whatever is provided, if possible.
		
		The layer_extractor method first gets all of the layers in the selected EXR file. Then, the layer_check and layer_mapper methods
		check for predetermined sets of layers. The build_type method determines which of several templates can be built. After that,
		the exr_shuffle method generates the node graph.
		
		REQUIREMENTS:
		In automatic mode (the default), the script will not be able to build anything unless one of three conditions are met: the VRayTotalLighting pass is present,
		a triplet of either VRayDiffuseFilter, VRayGlobalIllumination and VRayLighting or VRayDiffuseFilter, VRayRawGlobalIllumination and VRayRawLighting.
		These are considered the "base" layers upon which everthing else is built. In addition, to create a Car Body Paint composite section, there are four passes
		that all must be present: Paint_Window_Rimz, VRayMtlSelect_Car_Paint, VRayMtlSelect_Clearcoat and VRayMtlSelect_Metalic. If the VRayTotalLighting pass
		is not present, as a kind of workaround, the user can tick the LAYER OVERRIDE box on the startup menu. It's possible then to substitute another layer for
		the VRayTotalLighting pass. After the schematic has been built, the user can make any changes necessary. There must be at least one or more of the additive
		passes, such as VRayReflection, VRaySpecular, VRaySelfIllumination or VRayRefraction in order to create a Merge.
		'''
		if len(nuke.selectedNodes()):
			n = nuke.selectedNode()
			if nuke.selectedNode().Class()!='Read' or nuke.selectedNode() == "" :
				nuke.message("No EXR Read node selected.")
			elif os.path.splitext(nuke.filename(nuke.selectedNode()))[-1]!=".exr" :
				nuke.message("Selected Read is not an EXR")
			else:
				
				if not self.read_prefs_file():
					#### Default values if no pref file found...
					self.Layout = "Horizontal"
					self.spacing_x = '50'
					self.spacing_y = '50'
					self.postage_stamps = False
					self.backdrop_off = False
					self.rand_color = False
					self.layer_override = False
					
					self.prefs = [self.Layout, self.spacing_x, self.spacing_y, self.postage_stamps, self.backdrop_off, self.rand_color, self.layer_override]
					
					nuke.message("Prefs file cannot be read:\n %s\n\n Press OK to continue.\n\n You will need to save a new Prefs file.\n On the next panel, check the box for  [x] <----- SAVE PREFS." % (self.prefs_file))

				else:
					#### If there's an existing prefs file, set the current prefs to those values...
					self.Layout = self.saved_prefs[0]
					self.spacing_x = self.saved_prefs[1]
					self.spacing_y = self.saved_prefs[2]
					self.postage_stamps = self.saved_prefs[3]
					self.backdrop_off = self.saved_prefs[4]
					self.rand_color = self.saved_prefs[5]
					self.layer_override = self.saved_prefs[6]
					
				#### Ask the user what node spacing they prefer and whether or not they want postage stamps for the
				#### Shuffle nodes... Also, if they want a backdrop and if it is a random color, rather than grey.
				#### And, if they want to override the automatic layer filtering and pick their own layer associations...
				
				p = nuke.Panel( 'Node Layout' )
				#p.addEnumerationPulldown( 'Graph Orientation', 'Horizontal Vertical' )	#### Currently, only Horizontal...
				p.addEnumerationPulldown( 'Spacing X:', ' '.join([self.spacing_x, '50', '25', '40', '80', '100', '120', '150', '200']))
				p.addEnumerationPulldown( 'Spacing Y:', ' '.join([self.spacing_y, '50', '25', '40', '80', '100', '120', '150', '200']))
				p.addBooleanCheckBox('Shuffle Postage Stamps ON', self.postage_stamps)
				p.addBooleanCheckBox('Backdrop OFF', self.backdrop_off)
				p.addBooleanCheckBox('Random Backdrop Color', self.rand_color)
				p.addBooleanCheckBox('Layer Override', self.layer_override)
				p.addBooleanCheckBox('<----- SAVE PREFS ', False)
				if not p.show():
					return
				#self.Layout = p.value( 'Graph Orientation' )
				self.Layout = "Horizontal"						#### Maybe some day I'll add Vertical layouts... For now, I'll just default the Layout to Horizontal.
				self.spacing_x = p.value( 'Spacing X:' )
				self.spacing_y = p.value( 'Spacing Y:' )
				self.postage_stamps = p.value('Shuffle Postage Stamps ON')
				self.backdrop_off = p.value('Backdrop OFF')
				self.rand_color = p.value('Random Backdrop Color')
				self.layer_override = p.value('Layer Override')
				self.save_prefs = p.value('<----- SAVE PREFS ')
				
				self.prefs = [self.Layout, self.spacing_x, self.spacing_y, self.postage_stamps, self.backdrop_off, self.rand_color, self.layer_override]
				
				if self.save_prefs:
					self.write_prefs_file(self.prefs)

				#### Run the layer_extractor method to get the EXR layers...
				channels = n.channels()
				layers = self.layer_extractor(n)
				
				if self.layer_override:
					#### The user wants to manually pick the layer mapping and skip the automatic layer name mapping...
					if not self.layer_mapper(layers, channels):
						#### The layer_mapper returned False. This means that it could not find the layers to make
						####  even a Basic comp from what the user picked. So, we're bailing out...
						nuke.message("I can't do anything with what I've been given. Sorry...")
						return None
					else:
						#### Run the"build_type" method to find out what kind of node layout template we can build...
						BuildType = self.build_type()
						print("--------------------------------")
						print("BuildType:", BuildType)
						
						#### Check to see what layers we have found and then set variables for the exr_shuffle command...
						if BuildType == "Basic":
							nuke.message ("We have just enough layers for a Basic comp only...")
							self.Basic = True
							self.ShuffleLayers = list(set(self.base_comp_layer).union( set(self.plus_comp_layers) ))	#### Gather up all of the base and plus set layers into one "ShuffleLayers" list...
							self.ShuffleLayers.sort()
							if len(self.ShuffleLayers) > 1:
								#### Make the comp...
								self.exr_shuffle()
							else:
								nuke.message("I only have one layer. That's not enough to build a comp from. Sorry...")
								return None
							
						elif BuildType == "BasicDiffuse":
							nuke.message ("We have enough layers for a Basic comp and a separated Diffuse comp...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...	
							self.Diffuse = True
							self.DiffuseLayers = self.diffuse_comp_layers
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicRaw":
							nuke.message ("We have enough layers for a Basic comp and a separated Diffuse comp, using Raw GI and Raw Lighting...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()	
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...	
							self.Raw = True
							self.RawLayers = self.raw_comp_layers
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicCarBody":
							nuke.message ("We have enough layers for a Basic comp with a CarBody build - but no separate Diffuse comp...")
							self.Basic = True
							self.ShuffleLayers = list(set(self.base_comp_layer).union( set(self.plus_comp_layers) ))	#### Gather up all of the base and plus set layers into one "ShuffleLayers" list...
							self.ShuffleLayers.sort()
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "DiffuseCarBody":
							nuke.message ("We have the layers we need to make a separated Diffuse comp with a CarBody build...")
							self.Diffuse = True
							self.DiffuseLayers = self.diffuse_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "RawCarBody":
							nuke.message ("We have the layers we need to make a separated Diffuse comp, using Raw GI and Raw Lighting with a CarBody build...")
							self.Raw = True
							self.RawLayers = self.raw_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicDiffuseCarBody":
							nuke.message ("We have all the layers we need to make a Basic comp, with a separated Diffuse comp and a CarBody build...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...
							self.Diffuse = True
							self.DiffuseLayers = self.diffuse_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicRawCarBody":
							nuke.message ("We have all the layers we need to make a Basic comp, with a separated Diffuse comp, using Raw GI and Raw Lighting and a CarBody build...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...
							self.Raw = True
							self.RawLayers = self.raw_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						else:
							nuke.message ("There's nothing written for this case, yet... No comp will be built. Perhaps you could try running it again with LAYER OVERRIDE checked and pick the layers to use?")
				else:
					#### Run the "layer_check" method to see what layers we found in the EXR file and determine the structure of the comp...
					self.layer_check(layers, channels)
					
					if self.layer_map == False:
						#### layer_check failed and the user's attempt at mapping the layers via layer_map failed as well. So, we're bailing out...
						nuke.message("I can't do anything with what I've been given. Sorry...")
						return None
					else:
						#### Run "build_type" to find out what kind of node layout template we can build...
						BuildType = self.build_type()
						
						print("--------------------------------")
						print("BuildType:", BuildType)
						
						#### Check to see what layers we have found and then set variables for the exr_shuffle command...
						if BuildType == "Basic":
							self.Basic = True
							self.ShuffleLayers = list(set(self.base_comp_layer).union( set(self.plus_comp_layers) ))	#### Gather up all of the base and plus set layers into one "ShuffleLayers" list...
							self.ShuffleLayers.sort()
							if len(self.ShuffleLayers) > 1:
								nuke.message ("We have just enough layers for a Basic comp only...")
								#### Make the comp...
								self.exr_shuffle()
							else:
								nuke.message("I only have one layer. That's not enough to build a comp from. Sorry...")
								return None
							
						elif BuildType == "BasicDiffuse":
							nuke.message ("We have enough layers for a Basic comp and a separated Diffuse comp...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()	
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...	
							self.Diffuse = True
							self.DiffuseLayers = self.diffuse_comp_layers
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicRaw":
							nuke.message ("We have enough layers for a Basic comp and a separated Diffuse comp, using Raw GI and Raw Lighting...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()	
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...	
							self.Raw = True
							self.RawLayers = self.raw_comp_layers
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicCarBody":
							
							self.Basic = True
							self.ShuffleLayers = list(set(self.base_comp_layer).union( set(self.plus_comp_layers) ))	#### Gather up all of the base and plus set layers into one "ShuffleLayers" list...
							self.ShuffleLayers.sort()
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							if len(self.ShuffleLayers) > 1:
								nuke.message ("We have enough layers for a Basic comp with a CarBody build - but no separate Diffuse comp...")	
								#### Make the comp...
								self.exr_shuffle()
							else:
								nuke.message("I only have one additive layer. That's not enough to build a comp from. Sorry...")
								return None
							
						elif BuildType == "DiffuseCarBody":
							nuke.message ("We have the layers we need to make a separated Diffuse comp with a CarBody build...")
							self.Diffuse = True
							self.DiffuseLayers = self.diffuse_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "RawCarBody":
							nuke.message ("We have the layers we need to make a separated Diffuse comp, using Raw GI and Raw Lighting with a CarBody build...")
							self.Raw = True
							self.RawLayers = self.raw_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicDiffuseCarBody":
							nuke.message ("We have all the layers we need to make a Basic comp, with a separated Diffuse comp and a CarBody build...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...
							self.Diffuse = True
							self.DiffuseLayers = self.diffuse_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						elif BuildType == "BasicRawCarBody":
							nuke.message ("We have all the layers we need to make a Basic comp, with a separated Diffuse comp, using Raw GI and Raw Lighting and a CarBody build...")
							self.Basic = True
							self.ShuffleLayers = self.plus_comp_layers
							self.ShuffleLayers.sort()
							for item in self.ShuffleLayers:
								if item == 'VRayTotalLighting':
									self.ShuffleLayers.remove('VRayTotalLighting')	#### Don't want this layer in here, since we're making our own via the Diffuse comp...
							self.Raw = True
							self.RawLayers = self.raw_comp_layers
							self.CarBody = True
							self.BodyLayers = self.car_body_comp_layers
							self.CarBodyAlpha = self.car_body_alpha_channel
							#### Make the comp...
							self.exr_shuffle()
							
						else:
							nuke.message ("There's nothing written for this case, yet. No comp will be built. ...Perhaps you could try running it again with LAYER OVERRIDE checked and pick the layers to use?")
		else:
			nuke.message("Please select an EXR Read node...")
		
def exr_CompBuilder(option):
	''' This kickstarter function creates a new instance of the CompBuilder class which will run __init__ and will, in turn, run the main exr_comp method.'''
	CompBuilder(option)
