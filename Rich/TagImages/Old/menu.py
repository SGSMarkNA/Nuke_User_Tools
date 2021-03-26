import nuke, sys, os, string, shutil, commands, subprocess

def TagImages():

    file = nuke.filename(nuke.thisNode())
    dir = os.path.realpath( file )
    render_dir = os.path.dirname(dir)
    exec_string = '"C:\\Users\\rbobo\\Desktop\\exiftool.exe" -@ data.txt '
    command_string = exec_string + render_dir
    
	# Run the Windows date command to get the current date...
	run_date = subprocess.Popen("C:\\Users\\rbobo\\Desktop\\Get_Windows_Date.bat",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	result = run_date.stdout.readlines()
	date = result[2]
	print date
	
    # Run the Windows exiftool command on the rendered files...
    os.system(command_string)
    
    # Remove the xxxxxx.xxx_original files that exiftool creates as backups...
    for filename in os.listdir(render_dir):
        filepath = os.path.join(render_dir, filename)
        if "_original" in filename:
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)