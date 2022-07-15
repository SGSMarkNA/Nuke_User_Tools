

#####################################################################################################

import re

trim_dirs = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']
base_folders = ['Base_Red', 'Base_Green', 'Base_Blue', 'Base_SL_Red', 'Base_SL_Green', 'Base_SL_Blue', 'Base_XL_Red', 'Base_XL_Green', 'Base_XL_Blue', 'Limited_Red', 'Limited_Green', 'Limited_Blue', 'Limited_Tech_Red', 'Limited_Tech_Green', 'Limited_Tech_Blue', 'Sport_Red', 'Sport_Green', 'Sport_Blue', 'Sport_Z_Red', 'Sport_Z_Green', 'Sport_Z_Blue']

for trim in trim_dirs:
	for base in base_folders:
		match = re.findall(trim, base)
		if match:
			print('')
			print(trim)
			print(base)
			print('')


#####################################################################################################
			
import re

trim_dirs = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']

base_folders = "Base_Red Base_Green Base_Blue Base_SL_Red Base_SL_Green Base_SL_Blue Base_XL_Red Base_XL_Green Base_XL_Blue Limited_Red Limited_Green Limited_Blue Limited_Tech_Red Limited_Tech_Green Limited_Tech_Blue Sport_Red Sport_Green Sport_Blue Sport_Z_Red Sport_Z_Green Sport_Z_Blue"


trim = 'Limited'
match = re.findall(trim, base_folders)
print(match)

#####################################################################################################

import re

trim_dirs = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']

base_folders = "Base_Red [P] Base_Green [/P] Base_Blue [P] Base_SL_Red [/P] Base_SL_Green [P] Base_SL_Blue [/P] Base_XL_Red [P] Base_XL_Green [/P] Base_XL_Blue [P] Limited_Red [/P] Limited_Green [P] Limited_Blue [/P] Limited_Tech_Red [P] Limited_Tech_Green [/P] Limited_Tech_Blue [P] Sport_Red [/P] Sport_Green [P] Sport_Blue [/P] Sport_Z_Red [P] Sport_Z_Green [/P] Sport_Z_Blue"


trim = 'Limited'
match = re.findall(trim, base_folders)
print(match)

#####################################################################################################

import re

trim_dirs = ['Base', 'Base_SL', 'Base_XL', 'Limited', 'Limited_Tech', 'Sport', 'Sport_Z']

base_folders = "Base_Red [P] Base_Green [/P] Base_Blue [P] Base_SL_Red [/P] Base_SL_Green [P] Base_SL_Blue [/P] Base_XL_Red [P] Base_XL_Green [/P] Base_XL_Blue [P] Limited_Red [/P] Limited_Green [P] Limited_Blue [/P] Limited_Tech_Red [P] Limited_Tech_Green [/P] Limited_Tech_Blue [P] Sport_Red [/P] Sport_Green [P] Sport_Blue [/P] Sport_Z_Red [P] Sport_Z_Green [/P] Sport_Z_Blue"


trim = 'Limited'

pattern = '\[P\].+?\[\/P\]'


re.findall('\[P\].+?\[\/P\]', base_folders)
