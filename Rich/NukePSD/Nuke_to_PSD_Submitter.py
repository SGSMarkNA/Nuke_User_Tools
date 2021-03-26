import os
import sys
import nuke
import nukescripts
import subprocess

# --------------------------------------------
# Import Drew's Deadline_Command_Access module, which calls Deadline executable commands...
if os.name == 'nt':
	sys.path.append('//isln-smb/aw_config/Git_Live_Code/Software/Deadline/')
elif os.name == 'posix':
	sys.path.append('/Volumes/Tera/Users/richbobo/Dropbox/CODE/aw_ISILON_CODE/Git_Live_Code/Software/Deadline/')
import Deadline_Command_Access
# ----------------------------------------------------------------------------
try:
	import traceback
	import ConfigParser	
except:
	print( "Could not load ConfigParser module, sticky settings will not be loaded/saved" )
# ----------------------------------------------------------------------------


class Nuke_to_PSD_SubmitPanel(nukescripts.PythonPanel):
	"""Custom submission panel for submitting Nuke_to_PSD Write nodes via Deadline."""

	def __init__(self, PNG_DIR="", GroupNode=""):
		"""Initialize knobs and default values for panel creation."""

		# Get the PNG_DIR, so we can give it to the dependent job (PSD assembly) for an environment variable...
		self.PNG_DIR = PNG_DIR + 'PNG'
		#print "Here is self.PNG_DIR from the Submitter ----> ", self.PNG_DIR

		# Get the Nuke_to_PSD group node, so we can find all the Write nodes inside it...
		#print 'GroupNode ---->>> ', GroupNode
		self.GroupNode = GroupNode
		#print "Here is self.GroupNode from the Submitter ----> ", self.GroupNode.name()

		nukescripts.PythonPanel.__init__(self, 'Submit Nuke_to_PSD Panel', 'com.richbobo.Nuke_to_PSD_SubmitPanel')

		# ----------------------------------------------------------
		# Set the Nuke executable to be used for rendering...
		Major = nuke.NUKE_VERSION_MAJOR
		Minor = nuke.NUKE_VERSION_MINOR
		# Nuke 9.0...
		if Major == 9 and Minor >= 0:
			if os.name == 'nt':
				self.Executable = "C:\Program Files\Nuke9.0v7\Nuke9.0.exe"
			elif os.name == 'posix':
				self.Executable = "/Applications/Nuke9.0v7/Nuke9.0v7.app/Contents/MacOS/Nuke9.0v7"
		# ...or Nuke 10.5v7...
		elif Major == 10 and Minor >= 5:
			if os.name == 'nt':
				self.Executable = "C:\Program Files\Nuke10.5v7\Nuke10.5.exe"
			elif os.name == 'posix':
				self.Executable = "/Applications/Nuke10.5v7/Nuke10.5v7.app/Contents/MacOS/Nuke10.5v7"

		# ----------------------------------------------------------
		# Set the Sticky Settings file path...
		if os.name == "nt":
			Parent_Dir = os.environ.get('TEMP')
		else:
			Parent_Dir = os.environ.get('HOME')
		self.configFile = os.path.join( Parent_Dir, "Nuke_to_PSD_Submitter_Sticky_Settings.ini" )

		# ----------------------------------------------------------
		# Build the UI panel:

		# Get current Deadline values to populate certain knob values...
		POOLS = Deadline_Command_Access.Get_PoolNames()
		pools = POOLS.result		

		GROUPS = Deadline_Command_Access.Get_GroupNames()
		groups = GROUPS.result

		LIMITS = Deadline_Command_Access.Get_LimitGroupNames()
		limits = LIMITS.result

		# Create the PythonPanel...
		nukescripts.PythonPanel.__init__(self, "'Submit Nuke_to_PSD Panel'", "com.richbobo.Nuke_to_PSD_SubmitPanel")

		# Add knobs to the panel...
		self.NameKnob = nuke.String_Knob('NameKnob', 'Name:', '')
		self.addKnob(self.NameKnob)
		self.NameKnob.setValue('')

		self.CommentKnob = nuke.String_Knob('CommentKnob', 'Comment:', '')
		self.addKnob(self.CommentKnob)
		self.CommentKnob.setValue('')

		self.DepartmentKnob = nuke.String_Knob('DepartmentKnob', 'Department:', '')
		self.addKnob(self.DepartmentKnob)
		self.DepartmentKnob.setValue('Comp')

		self.PoolKnob = nuke.Enumeration_Knob('PoolKnob', 'Pool:', ['none', 'test', 'aw', 'thr3d', 'critical'])
		self.addKnob(self.PoolKnob)
		self.PoolKnob.setValue('aw')

		self.SecondaryPoolKnob = nuke.Enumeration_Knob('SecondaryPoolKnob', 'Secondary Pool:', ['none', 'test', 'aw', 'thr3d', 'critical'])
		self.addKnob(self.SecondaryPoolKnob)
		self.SecondaryPoolKnob.clearFlag(nuke.STARTLINE)
		self.SecondaryPoolKnob.setValue('aw')

		self.GroupKnob = nuke.Enumeration_Knob('GroupKnob', 'Group:', ['64gb', '128gb'])
		self.addKnob(self.GroupKnob)
		self.GroupKnob.setValue('64gb')

		self.PriorityKnob = nuke.Int_Knob('PriorityKnob', 'Priority:', )
		self.addKnob(self.PriorityKnob)
		self.PriorityKnob.setValue(50)

		# self.FramesPerTaskKnob = nuke.Int_Knob('FramesPerTaskKnob', 'Frames Per Task:', )
		# self.addKnob(self.FramesPerTaskKnob)
		# self.FramesPerTaskKnob.setValue(1)
		#
		# self.ConcurrentTasksKnob = nuke.Int_Knob('ConcurrentTasksKnob', 'Concurrent Tasks:', )
		# self.addKnob(self.ConcurrentTasksKnob)
		# self.ConcurrentTasksKnob.clearFlag(nuke.STARTLINE)
		# self.ConcurrentTasksKnob.setValue(1)

		self.LimtsKnob = nuke.Enumeration_Knob('LimtsKnob', 'Limts:', ['nuke', 'nuke_thr3d'])
		self.addKnob(self.LimtsKnob)
		self.LimtsKnob.setValue('nuke')

		# ----------------------------------------------------------
		# Set knob values to Deadline's values and set some other sensible defaults...

		# Pools...
		self.PoolKnob.setValues(pools)
		self.SecondaryPoolKnob.setValues(pools)
		try:
			self.PoolKnob.setValue('aw')
			self.SecondaryPoolKnob.setValue('aw')
		except:
			raise
		# GroupNames...
		self.GroupKnob.setValues(groups)
		try:
			self.GroupKnob.setValue('64gb')
		except:
			raise
		# LimitGroups...
		self.LimtsKnob.setValues(limits)
		try:
			self.LimtsKnob.setValue('nuke')
		except:
			raise

		self.SelectMachinesKnob = nuke.PyScript_Knob('SelectMachines', 'Blacklist')
		self.addKnob(self.SelectMachinesKnob)
		self.Machines = ''

		self.WhitelistKnob = nuke.Boolean_Knob('Whitelist', 'Whitelist')
		self.addKnob(self.WhitelistKnob)
		self.MachineListType = "Blacklist="

		self.divider1 = nuke.Text_Knob('divider1', '')
		self.addKnob(self.divider1)

		self.SubmitKnob = nuke.PyScript_Knob('Submit', 'Submit to Deadline')
		self.addKnob(self.SubmitKnob)

		self.SuspendedKnob = nuke.Boolean_Knob('Suspended', 'Suspended')
		self.addKnob(self.SuspendedKnob)
		self.SuspendedKnob.setValue(False)

		self.SuspendedKnob.clearFlag(nuke.STARTLINE)

		# ----------------------------------------------------------
		# Get the sticky knob settings from the configFile and load them into the panel...
		self.read_sticky_settings(self.configFile)


	def select_blacklist_machines(self):
		"""Call Deadline panel for selecting render machines for Blacklist/Whitelist."""
		self.StickyMachines = None
		result = Deadline_Command_Access.Select_MachineList(self.StickyMachines)
		self.Machines = result.orig_output.strip()
		if self.Machines == "Action was cancelled by user":
			self.Machines = ''


	def build_submission_files(self):
		"""Get knob values from the panel and values from the Nuke script via subprocess. Set values for use in Deadline submission files."""

		# Get the current Nuke script path...
		self.nuke_script = nuke.scriptName()

		self.BatchName = self.NameKnob.value()
		if self.BatchName == '':
			self.BatchName = os.path.basename(self.nuke_script)		
		# ------------------------------------------------------
		self.Name = self.NameKnob.value()
		if self.Name == '':
			#self.Name = os.path.basename(self.nuke_script)
			self.Name = 'Render Layer PNGs'
		# ------------------------------------------------------
		self.Comment = self.CommentKnob.value()
		if self.Comment == '':
			self.Comment = 'Best. Comp. Ever.'
		# ------------------------------------------------------
		self.Department = self.DepartmentKnob.value()
		if self.Department == '':
			self.Department = 'Comp'
		# ------------------------------------------------------
		if os.name == 'nt':
			# Get the first_frame and last_frame values from the Nuke script...
			python_script = "//isln-smb/aw_config/Git_Live_Code/Software/Nuke/Deadline_Scripts/MultiSubmit/get_frames_from_nuke_script.py"
			# subprocess Nuke in terminal mode and check the output of the commands...
			Executable = self.Executable + ' -t'
			#command = ' '.join([self.Executable, python_script, self.nuke_script])
			command = ' '.join([Executable, python_script, self.nuke_script])
			#print 'command --> ', command
			proc = subprocess.check_output(command)		
			result = proc.splitlines()[-1]
			#print 'result --> ', result
			FirstFrame, LastFrame = result.split(' ')
			self.Frames = self.Frames = '{}-{}'.format(FirstFrame, LastFrame)
			#print 'self.Frames --> ', self.Frames
			if self.Frames == '':
				self.Frames = '1-1'
			# ------------------------------------------------------
			# Get the Nuke executable Version number from the Nuke script, so we can tell Deadline which one to use for rendering...
			result2 =  proc.splitlines()[-2]
			Major, Minor = result2.split(' ')
			self.Version = '.'.join([str(Major), str(Minor)])
			if self.Version == '':
				self.Version = '10.5'
		elif os.name == 'posix':
			# Get the first and last frames from the Nuke script...
			NukeX = "-t"
			python_script = "/Volumes/Tera/Users/richbobo/Dropbox/CODE/aw_ISILON_CODE/Git_Live_Code/Software/Nuke/Deadline_Scripts/MultiSubmit/get_frames_from_nuke_script.py"
			command = [self.Executable, NukeX, python_script, self.nuke_script]
			try:
				proc = subprocess.check_output(command)
			except:
				raise
			result =  proc.splitlines()[-1]
			FirstFrame, LastFrame = result.split(' ')
			self.Frames = self.Frames = '{}-{}'.format(FirstFrame, LastFrame)
			if self.Frames == '':
				self.Frames = '1-1'
			# ------------------------------------------------------
			# Get the Nuke executable Version number from the Nuke script, so we can tell Deadline which one to use for rendering...
			result2 =  proc.splitlines()[-2]
			Major, Minor = result2.split(' ')
			self.Version = '.'.join([str(Major), str(Minor)])
			if self.Version == '':
				self.Version = '10.5'

		# ------------------------------------------------------
		self.Pool = self.PoolKnob.value()
		if self.Pool == '':
			self.Pool = 'aw'
		# ------------------------------------------------------
		self.SecondaryPool = self.SecondaryPoolKnob.value()
		if self.SecondaryPool == '':
			self.SecondaryPool = 'aw'
		# ------------------------------------------------------
		self.Group = self.GroupKnob.value()
		if self.Group == '':
			self.Group = '64gb'
		# ------------------------------------------------------
		self.Priority = int(self.PriorityKnob.value())
		if self.Priority == '':
			self.Priority = 50
		# ------------------------------------------------------
		#self.ConcurrentTasks = int(self.ConcurrentTasksKnob.value())
		#if self.ConcurrentTasks == '':
			#self.ConcurrentTasks = 1
		# ------------------------------------------------------
		self.LimitGroups = self.LimtsKnob.value()
		if self.LimitGroups == "":
			self.LimitGroups = 'nuke'
		# ------------------------------------------------------
		self.MachineListType = self.WhitelistKnob.value()
		if self.WhitelistKnob.value() == True:
			self.MachineListType = "Whitelist="
			self.IsBlacklist = False
		elif self.WhitelistKnob.value() == False:
			self.MachineListType = "Blacklist="	
			self.IsBlacklist = True
		# ------------------------------------------------------
		#self.FramesPerTask = int(self.FramesPerTaskKnob.value())
		#if self.FramesPerTask == '':
			#self.FramesPerTask = 1
		# ------------------------------------------------------
		if self.SuspendedKnob.value() == True:
			self.InitialStatus = 'Suspended'
		elif self.SuspendedKnob.value() == False:
			self.InitialStatus = 'Active'

		# ----------------------------------------------------------
		# job_info_file data:
		# ----------------------------------------------------------
		self.Job_Info_File_Code = [
		    "BatchName=%s" % self.BatchName,
		    "Name=%s" % self.Name,
		    "Comment=%s" % self.Comment,
		    "Department=%s" % self.Department,    
		    "Frames=%s" % self.Frames,
		    #"ChunkSize=%i" % self.FramesPerTask,
		    "Pool=%s" % self.Pool,
		    "SecondaryPool=%s" % self.SecondaryPool,
		    #"ConcurrentTasks=%i" % self.ConcurrentTasks,
		    "LimitGroups=%s" % self.LimitGroups,
		    "%s%s" % (self.MachineListType, self.Machines),
		    "Group=%s" % self.Group,
		    "Priority=%i" % self.Priority,
		    "Plugin=CommandLine",
		    "MachineLimit=0",
		    "LimitConcurrentTasksToNumberOfCpus=True",
		    # Used when AW environment variables are not being resoved properly...
		    "EnvironmentKeyValue0=NUKE_PATH=//isln-smb.ad.sgsco.int/aw_config/Git_Live_Code/Software/Nuke",
		    "InitialStatus=%s" % self.InitialStatus
		]

		# ----------------------------------------------------------
		# plugin_info_file:
		# ----------------------------------------------------------

		# REF: https://docs.thinkboxsoftware.com/products/deadline/10.0/1_User%20Manual/manual/manual-submission.html#arbitrary-command-line-jobs-ref-label
		# The <STARTFRAME>-<ENDFRAME> will get its values from self.Frames. The commandline script will be run for a total of the number of frames.
		# For example, if the Nuke script is frames 1-10, then ten commandline scripts will be executed, one per frame.

		# Get the Write nodes...
		with self.GroupNode:
			WriteNodes = [node for node in self.GroupNode.nodes() if node.Class() == 'Write']
			#print 'WriteNodes --> ', WriteNodes
		# Build an Write nodes args list, constructed from "-X", plus the name of a Write node...
		numNodes = len(WriteNodes)
		self.WritesArgs = ' -X '
		for node in WriteNodes:
			if node is not WriteNodes[-1]:
				arg = node.fullName() + ','
				self.WritesArgs += arg
			else:
				arg = node.fullName()
				self.WritesArgs += arg
		#print self.WritesArgs

		self.args = " -V 2 -F <STARTFRAME>-<ENDFRAME> --nukex -t -x" + self.WritesArgs + ' ' + self.nuke_script
		#print 'self.args ---->>', self.args

		self.Plugin_Info_File_Code = [
		    "Arguments=%s" % self.args,
		    "Executable=%s" % self.Executable,
		    "Shell=default",
		    "ShellExecute=False",
		    "SingleFramesOnly=False",
		    #"SceneFile=%s" % self.nuke_script,
		    #"Version=%s" % self.Version,
		    #"Threads=0",
		    #"RamUse=0",
		    "BatchMode=True",
		    #"BatchModeIsMovie=False",
		    #"NukeX=True",
		    #"UseGpu=False",
		    #"GpuOverride=0",
		    #"RenderMode=Use Scene Settings",
		    #"EnforceRenderOrder=False",
		    "ContinueOnError=True",
		    #"PerformanceProfiler=False",
		    #"PerformanceProfilerDir=",
		    #"ProxyMode=False",
		    #"Views=",
		    #"StackSize=0",
		]


	def write_deadline_submission_files(self):
		"""Write out the job_info and plugin_info Deadline submission files."""

		# ----------------------------------------------------------
		# Set the Deadline job_info and plugin_info file paths...
		if os.name == "nt":
			Parent_Dir = os.environ.get('TEMP')
			self.job_info_file = os.path.join(Parent_Dir, "job_info.txt")
			self.plugin_info_file = os.path.join(Parent_Dir, "plugin_info.txt")
		else:
			Parent_Dir = os.environ.get('HOME')
			self.job_info_file = os.path.join(Parent_Dir, "job_info.txt")
			self.plugin_info_file = os.path.join(Parent_Dir, "plugin_info.txt")

		# ----------------------------------------------------------
		# Write the job_info and plugin_info Deadline submission files...
		try:
			# Save the job_info_file file...
			job_info_save = open(self.job_info_file, 'w')
			for line in self.Job_Info_File_Code:
				job_info_save.write(line)
				job_info_save.write("\n")
			job_info_save.close()
			# Save the plugin_info_file file...
			plugin_info_save = open(self.plugin_info_file, 'w')
			for line in self.Plugin_Info_File_Code:
				plugin_info_save.write(line)
				plugin_info_save.write("\n")
			plugin_info_save.close()
		except Exception as e:
			nuke.message("Submission files cannot be saved to: %s. Press OK to cancel." % (Parent_Dir))
			print e
			return None


	def write_sticky_settings(self, configFile):
		"""Use Deadline ConfigParser module to write out sticky panel settings to configFile. """

		# Write Sticky Settings...
		try:
			print( "Writing sticky settings..." )
			config = ConfigParser.ConfigParser()

			config.add_section( "Sticky" )
			# config.set( "Sticky", "FrameListMode", dialog.frameListMode.value() )
			# config.set( "Sticky", "CustomFrameList", dialog.frameList.value().strip() )
			config.set( "Sticky", "Department", self.Department )
			config.set( "Sticky", "Pool", self.Pool )
			config.set( "Sticky", "SecondaryPool", self.SecondaryPool )
			config.set( "Sticky", "Group", self.Group )
			config.set( "Sticky", "Priority", self.Priority )
			# config.set( "Sticky", "MachineLimit", str( dialog.machineLimit.value() ) )
			config.set( "Sticky", "IsBlacklist", self.IsBlacklist )
			config.set( "Sticky", "MachineList", self.Machines )
			config.set( "Sticky", "LimitGroups", self.LimitGroups )
			# config.set( "Sticky", "SubmitSuspended", self.Suspended )
			# config.set( "Sticky", "ChunkSize", self.FramesPerTask )
			# config.set( "Sticky", "ConcurrentTasks", self.ConcurrentTasks )
			# #config.set( "Sticky", "InitialStatus", self.InitialStatus )
			# config.set( "Sticky", "LimitConcurrentTasks", str( dialog.limitConcurrentTasks.value() ) )
			# config.set( "Sticky", "Threads", str( dialog.threads.value() ) )
			# config.set( "Sticky", "SubmitScene", str( dialog.submitScene.value() ) )
			# config.set( "Sticky", "BatchMode", str( dialog.batchMode.value() ) )
			# config.set( "Sticky", "ContinueOnError", str( dialog.continueOnError.value() ) )
			# config.set( "Sticky", "UseNodeRange", str( dialog.useNodeRange.value() ) )
			# config.set( "Sticky", "UseGpu", str( dialog.useGpu.value() ) )
			# config.set( "Sticky", "ChooseGpu", str( dialog.chooseGpu.value() ) )
			# config.set( "Sticky", "EnforceRenderOrder", str( dialog.enforceRenderOrder.value() ) )
			# config.set( "Sticky", "RenderMode", str(dialog.renderMode.value() ) )
			# config.set( "Sticky", "PerformanceProfiler", str(dialog.performanceProfiler.value() ) )
			# config.set( "Sticky", "ReloadPlugin", str( dialog.reloadPlugin.value() ) )
			# config.set( "Sticky", "PerformanceProfilerPath", dialog.performanceProfilerPath.value() )

			fileHandle = open( self.configFile, "w" )
			config.write( fileHandle )
			fileHandle.close()

		except:
			print( "Could not write sticky settings!" )
			print( traceback.format_exc() )

	def read_sticky_settings(self, configFile):
		"""Use Deadline ConfigParser module to read sticky panel settings from configFile. """

		# Read Sticky Settings...
		try:
			print( "Reading sticky settings from %s" % self.configFile )
			if os.path.isfile( self.configFile ):
				config = ConfigParser.ConfigParser()
				config.read( self.configFile )

				if config.has_section( "Sticky" ):
					# if config.has_option( "Sticky", "FrameListMode" ):
					# 	initFrameListMode = config.get( "Sticky", "FrameListMode" )
					# if config.has_option( "Sticky", "CustomFrameList" ):
					# 	initCustomFrameList = config.get( "Sticky", "CustomFrameList" )
					if config.has_option( "Sticky", "Department" ):
						self.DepartmentKnob.setValue(config.get( "Sticky", "Department" ))
					if config.has_option( "Sticky", "Pool" ):
						self.PoolKnob.setValue(config.get( "Sticky", "Pool" ))
					if config.has_option( "Sticky", "SecondaryPool" ):
						self.SecondaryPoolKnob.setValue(config.get( "Sticky", "SecondaryPool" ))
					if config.has_option( "Sticky", "Group" ):
						self.GroupKnob.setValue(config.get( "Sticky", "Group" ))	
					if config.has_option( "Sticky", "Priority" ):
						self.PriorityKnob.setValue(config.getint( "Sticky", "Priority" ))
					# if config.has_option( "Sticky", "MachineLimit" ):
					# 	DeadlineGlobals.initMachineLimit = config.getint( "Sticky", "MachineLimit" )
					if config.has_option( "Sticky", "IsBlacklist" ):
						IsBlacklist = config.getboolean( "Sticky", "IsBlacklist" )
						if IsBlacklist == True:
							self.WhitelistKnob.setValue(False)
						elif IsBlacklist == False:
							self.WhitelistKnob.setValue(True)
					if config.has_option( "Sticky", "MachineList" ):
						self.StickyMachines = config.get( "Sticky", "MachineList" )
					if config.has_option( "Sticky", "LimitGroups" ):
						self.LimtsKnob.setValue(config.get( "Sticky", "LimitGroups" ))
					# if config.has_option( "Sticky", "SubmitSuspended" ):
						# self.SuspendedKnob.setValue(config.get( "Sticky", "SubmitSuspended" ))
					# if config.has_option( "Sticky", "ChunkSize" ):
						# self.FramesPerTaskKnob.setValue(config.getint( "Sticky", "ChunkSize" ))
					# if config.has_option( "Sticky", "ConcurrentTasks" ):
						# self.ConcurrentTasksKnob.setValue(config.getint( "Sticky", "ConcurrentTasks" ))
					# if config.has_option( "Sticky", "InitialStatus"):
						# self.SuspendedKnob.setValue(config.get("Sticky", "InitialStatus"))
					# if config.has_option( "Sticky", "LimitConcurrentTasks" ):
						# DeadlineGlobals.initLimitConcurrentTasks = config.getboolean( "Sticky", "LimitConcurrentTasks" )
					# if config.has_option( "Sticky", "Threads" ):
						# DeadlineGlobals.initThreads = config.getint( "Sticky", "Threads" )
					# if config.has_option( "Sticky", "SubmitScene" ):
						# DeadlineGlobals.initSubmitScene = config.getboolean( "Sticky", "SubmitScene" )
					# if config.has_option( "Sticky", "BatchMode" ):
						# DeadlineGlobals.initBatchMode = config.getboolean( "Sticky", "BatchMode" )
					# if config.has_option( "Sticky", "ContinueOnError" ):
						# DeadlineGlobals.initContinueOnError = config.getboolean( "Sticky", "ContinueOnError" )
					# if config.has_option( "Sticky", "UseNodeRange" ):
						# DeadlineGlobals.initUseNodeRange = config.getboolean( "Sticky", "UseNodeRange" )
					# if config.has_option( "Sticky", "UseGpu" ):
						# DeadlineGlobals.initUseGpu = config.getboolean( "Sticky", "UseGpu" )
					# if config.has_option( "Sticky", "ChooseGpu" ):
						# DeadlineGlobals.initChooseGpu = config.getint( "Sticky", "ChooseGpu" )
					# if config.has_option( "Sticky", "EnforceRenderOrder" ):
						# DeadlineGlobals.initEnforceRenderOrder = config.getboolean( "Sticky", "EnforceRenderOrder" )
					# if config.has_option( "Sticky", "RenderMode" ):
						# DeadlineGlobals.initRenderMode = config.get( "Sticky", "RenderMode" )
					# if config.has_option( "Sticky", "PerformanceProfiler" ):
						# DeadlineGlobals.initPerformanceProfiler = config.getboolean( "Sticky", "PerformanceProfiler")
					# if config.has_option( "Sticky", "ReloadPlugin" ):
						# DeadlineGlobals.initReloadPlugin = config.getboolean( "Sticky", "ReloadPlugin" )
					# if config.has_option( "Sticky", "PerformanceProfilerPath" ):
						# DeadlineGlobals.initPerformanceProfilerPath = config.get( "Sticky", "PerformanceProfilerPath" )
					# if config.has_option( "Sticky", "PrecompFirst" ):
						# DeadlineGlobals.initPrecompFirst = config.getboolean( "Sticky", "PrecompFirst")
					# if config.has_option( "Sticky", "PrecompOnly" ):
						# DeadlineGlobals.initPrecompOnly = config.get( "Sticky", "PrecompOnly" )    
					# if config.has_option( "Sticky", "SmartVectorOnly" ):
						# DeadlineGlobals.initSmartVectorOnly = config.get( "Sticky", "SmartVectorOnly" )
		except Exception:
			print("Could not read sticky settings!")
			print(traceback.format_exc())

	def submit_to_deadline(self):
		"""Submit script to Deadline via CommandLine plugin. Called when the user presses the "Submit to Deadline" button..."""

		# Assemble the data for the render submission files...
		self.build_submission_files()

		# Write out the render submission files...
		self.write_deadline_submission_files()

		# Write out the sticky menu settings...
		self.write_sticky_settings(self.configFile)

		# Submit the render job to Deadline, using Drew's Deadline_Command_Access module...
		try:
			result, jobid, out = Deadline_Command_Access.Submit_Deadline_Job(self.job_info_file, self.plugin_info_file)	
			if result:				
				print result, jobid, out
		except:
			raise

		# Check the value of GroupNode.knob('create_PSD_files') to see if we run the PSD assembly script or not...
		PSD_KNOB = self.GroupNode.knob('create_PSD_files')
		if PSD_KNOB.value() == 'now, on render completion':

			# Get the Job ID For the dependent job so we can write it to the dependent submission file...
			self.nuke_png_job_id = jobid		

			# Assemble the data for the submission files...
			self.build_submission_files_dependent()

			# Write out the submission files...
			self.write_deadline_submission_files_dependent()

			# Submit the dependent job...
			self.submit_to_deadline_dependent()

			nuke.message('Render and PSD Assembly Jobs Submitted to Deadline.')

		elif PSD_KNOB.value() == 'later, with post process function':

			nuke.message('Render Job Submitted to Deadline.')


	def knobChanged(self, knob):
		"""Press the buttons."""
		if knob is self.SelectMachinesKnob:
			self.select_blacklist_machines()
		elif knob is self.SubmitKnob:
			self.submit_to_deadline()


# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
#  DEPENDENT JOB SUBMISSION SECTION for JSX SCRIPT PSD FILE ASSEMBLY:
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------

	def build_submission_files_dependent(self):
		""""""
		# ----------------------------------------------------------
		# job_info_file_dependent data:
		# ----------------------------------------------------------

		self.Name_dependent = "Assemble Layered PSD Files"
		self.MachineListType_dependent = "Whitelist="
		self.Machines_dependent = "saw-pdig0083"
		self.LimitGroups_dependent = 'photoshop'
		#self.InitialStatus_dependent = "Suspended"
		self.EnvironmentKeyValue0 = "PNG_DIR=" + self.PNG_DIR
		self.EnvironmentKeyValue0 = "PNG_DIR=" + self.PNG_DIR		

		self.Job_Info_File_Code_dependent = [
		    "BatchName=%s" % self.BatchName,
		    "Name=%s" % self.Name_dependent,
		    "Comment=PSD Files Postprocessing...",
		    "Department=%s" % self.Department,    
		    "Frames=1-1",
		    "Pool=%s" % self.Pool,
		    "SecondaryPool=%s" % self.SecondaryPool,
		    "LimitGroups=%s" % self.LimitGroups_dependent,
		    "%s%s" % (self.MachineListType_dependent, self.Machines_dependent),
		    "Group=%s" % self.Group,
		    "Priority=%i" % self.Priority,
		    "Plugin=CommandLine",
		    "MachineLimit=0",
		    "EnvironmentKeyValue0=%s" % self.EnvironmentKeyValue0,
		    "InitialStatus=%s" % self.InitialStatus,
		    "JobDependencies=%s" % self.nuke_png_job_id
		]

		# ----------------------------------------------------------
		# plugin_info_file_dependent:
		# ----------------------------------------------------------

		self.args_dependent = "//isln-smb/aw_config/Git_Live_Code/Global_Systems/User_Tools/Nuke_User_Tools/Rich/NukePSD/Nuke_to_PSD_PostProcess_Deadline_Dependent_Job.py"
		#print 'self.args_dependent ---->>', self.args_dependent

		self.PyExec = '//isln-smb/aw_config/Apps/Python/Python27/python.exe'

		self.Plugin_Info_File_Code_dependent = [
		    "Arguments=%s" % self.args_dependent,
		    "Executable=%s" % self.PyExec,
		    "Shell=default",
		    "ShellExecute=False",
		    "SingleFramesOnly=False",
		    "ContinueOnError=True"
		]

	def write_deadline_submission_files_dependent(self):
		"""Write out the job_info_dependent and plugin_info_dependent Deadline submission files."""

		# ----------------------------------------------------------
		# Set the Deadline job_info_dependent and plugin_info_dependent file paths...
		if os.name == "nt":
			Parent_Dir = os.environ.get('TEMP')
			self.job_info_file_dependent = os.path.join(Parent_Dir, "job_info_dependent.txt")
			self.plugin_info_file_dependent = os.path.join(Parent_Dir, "plugin_info_dependent.txt")
		else:
			Parent_Dir = os.environ.get('HOME')
			self.job_info_file_dependent = os.path.join(Parent_Dir, "job_info_dependent.txt")
			self.plugin_info_file_dependent = os.path.join(Parent_Dir, "plugin_info_dependent.txt")

		# ----------------------------------------------------------
		# Write the job_info_dependent and plugin_info_dependent Deadline submission files...
		try:
			# Save the job_info_file_dependent file...
			job_info_dependent_save = open(self.job_info_file_dependent, 'w')
			for line in self.Job_Info_File_Code_dependent:
				job_info_dependent_save.write(line)
				job_info_dependent_save.write("\n")
			job_info_dependent_save.close()
			# Save the plugin_info_file_dependent file...
			plugin_info_dependent_save = open(self.plugin_info_file_dependent, 'w')
			for line in self.Plugin_Info_File_Code_dependent:
				plugin_info_dependent_save.write(line)
				plugin_info_dependent_save.write("\n")
			plugin_info_dependent_save.close()
		except Exception as e:
			nuke.message("Submission files cannot be saved to: %s. Press OK to cancel." % (Parent_Dir))
			print e
			return None

	def submit_to_deadline_dependent(self):
		"""Submit via CommandLine plugin. Called when the user presses the "Submit to Deadline" button..."""

		# Assemble the data for the submission files...
		self.build_submission_files_dependent()

		# Write out the submission files...
		self.write_deadline_submission_files_dependent()

		# Submit the job to Deadline, using Drew's Deadline_Command_Access module...
		try:
			result, jobid, out = Deadline_Command_Access.Submit_Deadline_Job(self.job_info_file_dependent, self.plugin_info_file_dependent)	
			if result == True:
				print result, jobid, out
		except:
			raise




# ----------------------------------------------------------
# TESTING in Nuke Script Editor - Start up the UI panel...
# ----------------------------------------------------------
#def Create_Nuke_to_PSD_SubmitPanel():
	#""""""
	#p = Nuke_to_PSD_SubmitPanel()
	#p.show()
