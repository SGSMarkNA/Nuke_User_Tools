## Get the Nuke script's first_frame and last_frame values...
## NOTE: This needs to be copied into:
##          //isln-smb/aw_config/Git_Live_Code/Software/Nuke/Deadline_Scripts/MultiSubmit

import nuke
import sys


if sys.argv[1]:
	nuke.scriptOpen(sys.argv[1])
else:
	raise

# Print the script's Nuke version info, so we can tell Deadline which version to use for rendering. Version is set in the job_options_file.
print nuke.NUKE_VERSION_MAJOR, nuke.NUKE_VERSION_MINOR

# Print the script's first_frame and last_frame values, so we can get the Frames value for the job_info_file.
print int(nuke.root()['first_frame'].value()), int(nuke.root()['last_frame'].value())