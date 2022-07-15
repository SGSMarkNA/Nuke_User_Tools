import os
import errno
import nuke

#----------------------------------------------------------
# User select Nuke scripts to be submitted to Deadline for render...
####### TO DO: Integrate nuke script picking into GUI...
def select_nuke_scripts():
	NukeScriptsList = nuke.getFilename('Select Multiple Nuke Files to be Rendered.', pattern='*.nk', type='select', multiple=True)
	print(NukeScriptsList)
	return NukeScriptsList
####### FOR TESTING...
##NukeScriptsList = ['R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x001.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x002.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x003.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x004.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x005.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x006.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x007.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x008.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x009.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x010.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x011.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x012.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x013.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x014.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x015.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x016.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x017.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x018.nk', 'R:/Jobs/SGS/Archive/Archive_2016/SGSC-16-004_Bud_Light_Sample/work/budLight/_common/2d/_workarea/Old/Bud_Light_Comps_v001_x019.nk']

#----------------------------------------------------------
# Set the Nuke executable to be used for rendering...
# Nuke 9.0...
if os.name == 'nt':
	Executable = "C:\Program Files\Nuke9.0v7\Nuke9.0.exe"
elif os.name == 'posix':
	Executable = "/Applications/Nuke9.0v7/Nuke9.0v7.app/Contents/MacOS/Nuke9.0v7"
# ...or Nuke 10.5.4
#if os.name == 'nt':
	#Executable = "C:\Program Files\Nuke10.5v4\Nuke10.5.exe"
#elif os.name == 'posix':
	#Executable = "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4"

#----------------------------------------------------------
# Build the python script pathnames...
##### TO DO: Figure out where on the server to save these files, so the render nodes can find them...
if os.name == "nt":
	##Parent_Dir = os.environ.get('TEMP')
	Parent_Dir = "X:\\Critical-Mass\\CRMS-17-001_Nissan_TLJ8_Configurators_and_Print_Images\\users\\rbobo\\TEST"
else:
	##Parent_Dir = os.environ.get('HOME')
	Parent_Dir = "/Volumes/jobs/Critical-Mass/CRMS-17-001_Nissan_TLJ8_Configurators_and_Print_Images/users/rbobo/TEST"
Dir1 = '.nuke'
Dir2 = 'Deadline_Submit'
Submit_Name = 'Submit'
Execute_Name = 'Execute'
Suffix = '.py'
DirSegs = [Parent_Dir, Dir1, Dir2]
Dirs = os.path.join(*DirSegs)

Submit_Script = os.path.join(Dirs + os.sep + Submit_Name + Suffix)
Execute_Script = os.path.join(Dirs + os.sep + Execute_Name + Suffix)

Submit_Dir = os.path.dirname(Submit_Script)

##### TO DO: Needs to be the number of Nuke scripts selected by the user from the Nuke script file browser...
NumScripts = '"1-3"'
##### TO DO: Needs to be how many frames to divide the script task into... (chunks?) also selected by the user on the GUI...
ByNum = int(1)
##### TO DO: Figure out what a suitable default name should be - or allow user to type one...?
SubmitName = '"__Multiple_Nuke_Scripts__"'

#----------------------------------------------------------
# Deadline submission parameters - written to Submit.py file...

###### TO DO: Many of these will need to be tied to values selected on the GUI, by the user...
Submit_File_Code = [
    "import sys",
    "import os",
    "sys.path.append('//isln-smb/thr3dcgi_config')",
    "import RenderUtils",
    "job = RenderUtils.RenderJob()",
    # Set up the plugin to use, can be the standard Nuke or Maya plugin. To use a custom script, plugin is set to 'Script'...
    "job.setPlugin('Script')",
    # Executable
    "job.plugin.set_executable('%s')" % Executable,
    # Path to the Execute.py script...
    "job.plugin.set_script('%s')" % Execute_Script,
    # "X" is the number of Nuke Scripts to execute. (This is a cheat that hijacks the setFrameRange function.)
    # job.setFrameRange("1-X", by=1)
    # This will equal the number of nuke scripts you select to be processed...
    "job.setFrameRange(%s, by=%s)" % (NumScripts, ByNum),
    # Set Job specific values, names, priorities, pools, etc....
    "job.setValue('Name', %s)" % SubmitName,
    "job.setValue('Group', '64gb')",
    "job.setValue('Department', 'Comp')",
    "job.setValue('Pool', 'aw')",
    "job.setValue('SecondaryPool', 'aw')",
    "job.setValue('Priority', '50')",
    "job.setValue('MachineLimit', 0)",
    "job.setValue('Limits', 'nuke')",
    "job.setValue('LimitGroups', 'nuke')",
    "job.setValue('ConcurrentTasks', 4)",
    "job.setValue('LimitConcurrentTasksToNumberOfCpus', 'True')",
    # Submit the job...
    # 1 is passed in to help name the temp files. It will create a job_info_1 file...
    # The submitJob() function is also in self.job_data in RenderUtils\render_job.py...
    "job.submitJob(1)"
]

#----------------------------------------------------------
def write_deadline_submit_file():
	''''''
	# Write the Submit.py file...
	try:
		os.makedirs(Submit_Dir)
		print("Created Deadline_Submit Directory: %s " % (Submit_Dir))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	try:
		submit_save = open(Submit_Script, 'w')
		for line in Submit_File_Code:
			submit_save.write(line)
			submit_save.write("\n")
		submit_save.close()
	except Exception as e:
		nuke.message("Submission file cannot be saved to: %s. Press OK to cancel." % (Submit_Script))
		print(e)
		return None

## Write the Script.py file...	
write_deadline_submit_file()

#----------------------------------------------------------
def read_deadline_submit_file():
	''''''
	# Read the Submit.py file...	
	if os.path.isfile(Submit_Script):
		try:
			submit_read = open(Submit_Script, 'r')
			submit_read.close()
		except Exception as e:
			nuke.message("File cannot be read:\n\n Press OK to continue.")
			print(e)
			submit_read.close()
		finally:
			print("Submit file loaded successfully.")
			print(submit_read)
			return submit_read	
	else:
		return None

# Read the Submit_Script.py file...	
#read_deadline_submit_file()

###################################################################################
###################################################################################


##----------------------------------------------------------------------
### Launch the Nuke script...
## nuke.scriptOpen(NukeScript)

#nuke.scriptOpen(Nuke_Files[(int(os.environ['STARTFRAME'])) - 1].replace('\\', '/'))

### Execute the Write nodes...   
#for node in nuke.allNodes('Write'):
	#if node.knob('disable').value() == True:
		#pass
	#else:
		#nuke.execute(node, 1, 1)
###----------------------------------------------------------------------



#----------------------------------------------------------
def write_deadline_execute_file():
	''''''
	# Write the Execute.py file...
	try:
		os.makedirs(Submit_Dir)
		print("Created Deadline_Submit Directory: %s " % (Submit_Dir))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	try:
		execute_save = open(Execute_Script, 'w')
		execute_save.write("import os")
		execute_save.write("\n")
		execute_save.write("import nuke")
		execute_save.write("\n")		
		execute_save.write("Nuke_Files = ")
		execute_save.write("[")
		execute_save.write("\n")
		NukeScriptsList = select_nuke_scripts()
		for scriptpath in NukeScriptsList:
			execute_save.write("'" + scriptpath + "'" + ",")
			execute_save.write("\n")
		execute_save.write("]")
		execute_save.write("\n")
		execute_save.write("nuke.scriptOpen(Nuke_Files[(int(os.environ['STARTFRAME'])) - 1])")
		execute_save.write("\n")
		# Execute the Write nodes...   
		execute_save.write("for node in nuke.allNodes('Write'):")
		execute_save.write("\n\t")
		execute_save.write("if node.knob('disable').value() == True:")
		execute_save.write("\n\t\t")
		execute_save.write("pass")
		execute_save.write("\n\t")
		execute_save.write("else:")
		execute_save.write("\n\t\t")
		execute_save.write("nuke.execute(node, 1, 1)")
		execute_save.close()
	except Exception as e:
		nuke.message("Execute file cannot be saved to: %s. Press OK to cancel." % (Execute_Script))
		print(e)
		return None

## Write the Execute.py file...	
write_deadline_execute_file()
