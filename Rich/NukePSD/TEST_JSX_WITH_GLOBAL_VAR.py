import os
import subprocess
import time

jsx_script_status_file = os.path.join((os.environ.get('TEMP')), '.nuke\NukePSD\jsx_script_status.txt')		

jsx_file = r"U:\rbobo\TEST\JSX_TEST\TEST.jsx"
jsx_file = jsx_file.replace('/', '\\')

PS_APP = 'start photoshop.exe'

target = PS_APP + " " + '"' + jsx_file + '"'
target = target.replace('/', '\\')

process = subprocess.call(target, shell=True)

# Start checking loop...
while not os.path.exists(jsx_script_status_file):
	print 'Checking...'
	time.sleep(5)
# File exists. Let's see if we can read it...
if os.path.isfile(jsx_script_status_file):
	try:
		with open(jsx_script_status_file, 'r') as data_read:
			for line in data_read:
				if "Complete." in line:
					print line
	except:
		print "Error: JSX Script Status File cannot be read!"
		data_read.close()

print process