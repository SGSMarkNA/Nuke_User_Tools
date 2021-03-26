# Copy this to your menu.py file in ~.nuke
# In your Write node, in the Python tab - in the "after render" field, type "TagImages()"
# This function will be executed after all of the renders have finished.

import nuke, sys, os, string, shutil, commands, subprocess

def TagImages():

	''' Uses exiftool to add XMP style photometadata to images. These data tags may be read in Photoshop.'''
	
	# Set the directory where the TagImages() function will write and read its files...
	TagImagesDir = "C:\\Users\\rbobo\\Desktop"
	
	# Operates on a Nuke Write node by the TagImages() function being added to the Python/after render tab...
	file = nuke.filename(nuke.thisNode())
	# Get the OS-correct slashes in the pathname...
	dir = os.path.realpath( file )	
	render_dir = os.path.dirname(dir)
	# exiftool command reads arguments from tag_data.txt file, which is built below...
	exec_string = '"C:\\Users\\rbobo\\Desktop\\exiftool.exe" -@ tag_data.txt '
	# Build full windows shell command...
	command_string = exec_string + render_dir

	# Run the Windows date command via a batch file to get the current date in the format that exiftool likes...
	date = subprocess.Popen("C:\\Users\\rbobo\\Desktop\\Get_Windows_Date.bat",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	result = date.stdout.readlines()
	date_created = result[2]

	# Write out the tag_data.txt file for exiftool to read as command line arguments...
	os.chdir("C:\\Users\\rbobo\\Desktop")
	file = open("tag_data.txt", "w")
	file.write("-xmp-Photoshop:DateCreated=%s\n" % date_created)
	file.write("-xmp-dc:Creator=Armstrong White\n")
	file.write("-xmp-iptcCore:CreatorAddress=2125 E. Lincoln\n")
	file.write("-xmp-iptcCore:CreatorCity=Birmingham\n")
	file.write("-xmp-iptcCore:CreatorRegion=Michigan\n")
	file.write("-xmp-iptcCore:CreatorPostalCode=48009\n")
	file.write("-xmp-iptcCore:CreatorCountry=USA\n")
	file.write("-xmp-iptcCore:CreatorWorkTelephone=(248) 594-1818\n")
	file.write("-xmp-iptcCore:CreatorWorkEmail=arielle.helfman@armstrong-white.com, kati.white@armstrong-white.com\n")
	file.write("-xmp-iptcCore:CreatorWorkURL=http://armstrong-white.com\n")
	# Additional possible tags I've investigated...
	#-xmp-Photoshop:AuthorsPosition=Artist
	#-xmp-Photoshop:Credit=Armstrong White
	#-xmp-Photoshop:State=Michigan
	file.close()

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