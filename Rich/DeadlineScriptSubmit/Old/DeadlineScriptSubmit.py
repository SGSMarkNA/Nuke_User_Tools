import os
import errno
import pickle

#----------------------------------------------------------
# User select Nuke scripts to be submitted to Deadline for render...
def select_nuke_scripts():
	NukeScriptsList = nuke.getFilename('Select Multiple Nuke Files to be Rendered.', pattern='*.nk', type='select', multiple=True)
	print(NukeScriptsList)
	return NukeScriptsList

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
if os.name == "nt":
	Submit_Dir = os.environ.get('TEMP')        
else:
	Submit_Dir = os.environ.get('HOME')
Dir1 = '.nuke'
Dir2 = 'Deadline_Submit'
Submit_Name = 'Submit'
Execute_Name = 'Execute'
Suffix = '.py'
DirSegs = [Submit_Dir, Dir1, Dir2]
Dirs = os.path.join(*DirSegs)
Submit_Script = os.path.join(Dirs + os.sep + Submit_Name + Suffix)
Execute_Script = os.path.join(Dirs + os.sep + Execute_Name + Suffix)
##### TO DO: Needs to be the number of Nuke scripts selected by the user from the Nuke script file browser...
NumScripts = '"1-17"'
##### TO DO: Needs to be how many frames to divide the script task into... (chunks?) also selected by the user on the GUI...
ByNum = int(1)
##### TO DO: Figure out what a suitable default name should be - or allow user to type one...?
SubmitName = "__Multiple_Nuke_Scripts__"

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
    #### FIX: Should be Execute.py path...
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
    ##job.submitJob(1)
]

#----------------------------------------------------------
def write_deadline_submit_file():
	''''''
	if os.name == "nt":
		submit_file = os.path.join((os.environ.get('TEMP')), Submit_Script)		
	else:
		submit_file = os.path.join((os.environ.get('HOME')), Submit_Script)
	# Set the submit directory so we can make it, if it doesn't exist...
	Submit_Dir = os.path.dirname(submit_file)
	# Create the submit directory...
	try:
		os.makedirs(Submit_Dir)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	finally:
		print("Created Deadline Submit Directory: %s " % (Submit_Dir))
	try:
		submit_save = open(submit_file, 'w')
		for line in Submit_File_Code:
			submit_save.write(line)
			submit_save.write("\n")
		submit_save.close()
	except Exception as e:
		nuke.message("Submission file cannot be saved to: %s. Press OK to cancel." % (submit_file))
		print(e)
		return None

## Write the Deadline_Submit_Script.py file...	
write_deadline_submit_file()

#----------------------------------------------------------
def read_deadline_submit_file():
	''''''
	if os.name == "nt":
		submit_file = os.path.join((os.environ.get('TEMP')), Submit_Script)
	else:
		submit_file = os.path.join((os.environ.get('HOME')), Submit_Script)
		submit_dir = os.path.dirname(submit_file)
	# Read the prefs file...	
	if os.path.isfile(submit_file):
		try:
			submit_read = open(submit_file, 'r')
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

## Read the Deadline_Submit_Script.py file...	
read_deadline_submit_file()

###################################################################################
###################################################################################

##----------------------------------------------------------
#def write_deadline_execute_file():
	#''''''
	#if os.name == "nt":
		#execute_file = os.path.join((os.environ.get('TEMP')), Submit_Script)		
	#else:
		#execute_file = os.path.join((os.environ.get('HOME')), Submit_Script)
	## Set the submit directory so we can make it, if it doesn't exist...
	#Submit_Dir = os.path.dirname(execute_file)
	## Create the submit directory...
	#try:
		#os.makedirs(Submit_Dir)
	#except OSError, e:
		#if e.errno != errno.EEXIST:
			#raise
	#finally:
		#print "Created Deadline Submit Directory: %s " % (Submit_Dir)
	#try:
		#submit_save = open(execute_file, 'w')
		#for line in Submit_File_Code:
			#submit_save.write(line)
			#submit_save.write("\n")
		#submit_save.close()
	#except Exception as e:
		#nuke.message("Submission file cannot be saved to: %s. Press OK to cancel." % (execute_file))
		#print e
		#return None

### Write the Deadline_Submit_Script.py file...	
#write_deadline_execute_file()


