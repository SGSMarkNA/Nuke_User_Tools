
import os
import errno
import nuke
import sys
sys.path.append('//isln-smb/aw_config/Git_Live_Code/Software/Deadline')
import Deadline_Command_Access


class multi_submit(object):
	""""""

	def __init__(self):

		Node = nuke.toNode('Multi_Script_Submit')

		POOLS = Deadline_Command_Access.Get_PoolNames()
		pools = POOLS.result
		Node.knob('pool').setValues(pools)
		print 'pool knob -----> ', Node.knob('pool').values()
		Node.knob('secondary_pool').setValues(pools)
		try:
			Node.knob('pool').setValue('aw')
			Node.knob('secondary_pool').setValue('thr3d')
		except:
			raise

		GROUPS = Deadline_Command_Access.Get_GroupNames()
		groups = GROUPS.result
		Node.knob('group').setValues(groups)
		print 'group knob -----> ', Node.knob('group').values()
		try:
			Node.knob('group').setValue('64gb')
		except:
			raise

		LIMITS = Deadline_Command_Access.Get_LimitGroupNames()
		limits = LIMITS.result
		Node.knob('limits').setValues(limits)
		print 'limits knob -----> ', Node.knob('limits').values()
		try:
			Node.knob('limits').setValue('nuke')
		except:
			raise

	# ----------------------------------------------------------
	# Set the Nuke executable to be used for rendering...
	# Nuke 9.0...
	if os.name == 'nt':
		Executable = "C:/Program Files/Nuke9.0v7/Nuke9.0.exe"
	elif os.name == 'posix':
		Executable = "/Applications/Nuke9.0v7/Nuke9.0v7.app/Contents/MacOS/Nuke9.0v7"
	# ...or Nuke 10.5.4...
	#if os.name == 'nt':
		#self.Executable = "C:\Program Files\Nuke10.5v4\Nuke10.5.exe"
	#elif os.name == 'posix':
		#self.Executable = "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4"

	# ----------------------------------------------------------
	# Set the submit directory so we can make it, if it doesn't exist...
	if os.name == "nt":
		Parent_Dir = os.environ.get('TEMP')
	else:
		Parent_Dir = os.environ.get('HOME')

	Dir1 = '.nuke'
	Dir2 = 'Deadline_Submit'
	Submit_Name = 'Submit'
	Execute_Name = 'Execute'
	Suffix = '.py'
	DirSegs = [Parent_Dir, Dir1, Dir2]
	Dirs = os.path.join(*DirSegs)

	Submit_Script = os.path.join(Dirs + os.sep + Submit_Name + Suffix)
	Submit_Dir = os.path.dirname(Submit_Script)

	# Try to create the Submit_Dir...
	if os.path.isdir(Submit_Dir):
		print "Directory %s already exists..." % (Submit_Dir)
	else:
		try:
			os.makedirs(Submit_Dir)
		except OSError, e:
			if e.errno != errno.EEXIST:
				raise
		if os.path.isdir(Submit_Dir):
			print "Created output directory: %s " % (Submit_Dir)
		else:
			print "ERROR: Directory %s cannot be created." % (Submit_Dir)
			if nuke:
				nuke.message("Directory cannot be created. Press OK to cancel." % (Submit_Dir))

	# Build the python script pathname...
	# Execute_Script = os.path.join(Dirs + os.sep + Execute_Name + Suffix)  # Not needed now.

	temp = os.path.join('"' + Dirs + os.sep + Execute_Name + Suffix + '"')
	Set_Script = temp.replace("\\", "\\\\")

	NumScripts = ""
	NukeScriptsList = []

	# ----------------------------------------------------------
	# User select Nuke scripts to be submitted to Deadline for render...

	def select_nuke_scripts(self):
		"""
		"""
		self.NukeScriptsList = nuke.getFilename('Select Multiple Nuke Files to be Rendered.', pattern='*.nk', type='select', multiple=True)
		print self.NukeScriptsList
		NumScriptsSelected = len(self.NukeScriptsList)
		print NumScriptsSelected
		first_script_num = "1"
		last_script_num = str(NumScriptsSelected)
		self.NumScripts = '"' + first_script_num + '-' + last_script_num + '"'
		print self.NumScripts

	# ----------------------------------------------------------

	def write_deadline_submit_file(self):
		"""
		"""
		# Write the Submit.py file...
		try:
			os.makedirs(self.Submit_Dir)
			print "Created Deadline_Submit Directory: %s " % (self.Submit_Dir)
		except OSError, e:
			if e.errno != errno.EEXIST:
				raise
		try:
			submit_save = open(self.Submit_Script, 'w')
			for line in self.Submit_File_Code:
				submit_save.write(line)
				submit_save.write("\n")
			submit_save.close()
		except Exception as e:
			nuke.message("Submission file cannot be saved to: %s. Press OK to cancel." % (self.Submit_Script))
			print e
			return None

	# # ----------------------------------------------------------
	# 
	# def write_deadline_execute_file(self):
	#     """ 
	#     """
	#     # Create and save the Execute.py file...
	#     try:
	#         os.makedirs(self.Submit_Dir)
	#         print "Created Deadline_Submit Directory: %s " % (self.Submit_Dir)
	#     except OSError, e:
	#         if e.errno != errno.EEXIST:
	#             raise
	#     try:
	#         # Open the Nuke script...
	#         execute_save = open(self.Execute_Script, 'w')
	#         # Module imports...
	#         execute_save.write("import os")
	#         execute_save.write("\n")
	#         execute_save.write("import nuke")
	#         execute_save.write("\n")
	#         # Select and assign a list of Nuke scripts to submit...
	#         execute_save.write("Nuke_Files = ")
	#         execute_save.write("[")
	#         execute_save.write("\n")
	#         print self.NukeScriptsList
	#         for scriptpath in self.NukeScriptsList:
	#             execute_save.write("'" + scriptpath + "'" + ",")
	#             execute_save.write("\n")
	#         execute_save.write("]")
	#         execute_save.write("\n")
	#         # Set the STARTFRAME...
	#         execute_save.write("nuke.scriptOpen(Nuke_Files[(int(os.environ['STARTFRAME'])) - 1])")
	#         execute_save.write("\n")
	#         # Execute the Write nodes...
	#         execute_save.write("for node in nuke.allNodes('Write'):")
	#         execute_save.write("\n\t")
	#         execute_save.write("if node.knob('disable').value() == True:")
	#         execute_save.write("\n\t\t")
	#         execute_save.write("pass")
	#         execute_save.write("\n\t")
	#         execute_save.write("else:")
	#         execute_save.write("\n\t\t")
	#         execute_save.write("nuke.execute(node, 1, 1)")
	#         execute_save.close()
	#     except Exception as e:
	#         nuke.message("Execute file cannot be saved to: %s. Press OK to cancel." % (self.Execute_Script))
	#         print e
	#         return None

	# ----------------------------------------------------------

	def submit_to_deadline(self):
		"""
		Gets called when a user presses the 'Submit' button
		"""
		Node = nuke.thisNode()

		Name = Node.knob('submit_name').value()
		print Name
		Comment = Node.knob('comment').value()
		print Comment
		Department = Node.knob('department').value()
		print Department
		Pool = Node.knob('pool').value()
		print Pool
		SecondaryPool = Node.knob('secondary_pool').value()
		print SecondaryPool
		Group = Node.knob('group').value()
		print Group
		Priority = int(Node.knob('priority').value())
		print Priority
		ConcurrentTasks = int(Node.knob('concurrent_tasks').value())
		print ConcurrentTasks
		LimitGroups = Node.knob('limits').value()
		print LimitGroups
		##### TO DO: Needs to be how many frames to divide the script task into... (chunks?) also selected by the user on the GUI...
		ByNum = int(4)
		print ByNum

		# Deadline submission parameters - written to Submit.py file...
		self.Submit_File_Code = [
		    "import sys",
		    "import os",
		    ##"sys.path.append('//isln-smb/thr3dcgi_config')",
		    "import RenderUtils",
		    "job = RenderUtils.RenderJob()",
		    # Set up the plugin to use, can be the standard Nuke or Maya plugin.
		    # To use a custom script, plugin is set to 'Script'...
		    "job.setPlugin('Script')",
		    # Executable
		    "job.plugin.set_executable('%s')" % self.Executable,
		    # Path to the Execute.py script...
		    "job.plugin.set_script('-t %s')" % r'//isln-smb/aw_config/Git_Live_Code/Global_Systems/User_Tools/Nuke_User_Tools/Deadline_Script_Execute/Execute.py',
		    # Set up arguments that will be passed to your script ('Execute.py')
		    # These can be accessed through the argparse module within your Execute.py file
		    "job.plugin.add_argument('-nf {}')".format('|'.join(self.NukeScriptsList).replace('\\', '/')),
		    # "X" is the number of Nuke Scripts to execute. (This is a cheat that hijacks the setFrameRange function.)
		    # job.setFrameRange("1-X", by=1)
		    # This will equal the number of nuke scripts you select to be processed...
		    "job.setFrameRange(%s, by=%s)" % (self.NumScripts, ByNum),
		    # Set Job specific values, names, priorities, pools, etc....
		    "job.setValue('Name', '%s')" % Name,
		    "job.setValue('Comment', '%s')" % Comment,
		    "job.setValue('Department', '%s')" % Department,
		    "job.setValue('Pool', '%s')" % Pool,
		    "job.setValue('SecondaryPool', '%s')" % SecondaryPool,
		    "job.setValue('Group', '%s')" % Group,
		    "job.setValue('Priority', '%s')" % Priority,
		    "job.setValue('ConcurrentTasks', '%s')" % ConcurrentTasks,
		    "job.setValue('LimitGroups', '%s')" % LimitGroups,
		    "job.setValue('MachineLimit', 0)",
		    "job.setValue('LimitConcurrentTasksToNumberOfCpus', 'True')",
		    # Submit the job...
		    # 1 is passed in to help name the temp files. It will create a job_info_1 file...
		    # The submitJob() function is also in self.job_data in RenderUtils\render_job.py...
		    "job.submitJob(1)"
		]

		# Write the Submit.py file...
		self.write_deadline_submit_file()

		# Write the Execute.py file...
		# self.write_deadline_execute_file()  # Not needed

		print self.Submit_Dir
		print self.Submit_Script

		# Run the Submit.py file...
		sys.path.append(self.Submit_Dir)
		#self.SubmitFile = os.path.basename(os.path.splitext(self.Submit_Script)[0])
		#print self.SubmitFile
		#__import__(self.SubmitFile)
		#reload(self.SubmitFile)
		print self.Submit_Script
		execfile(self.Submit_Script)
