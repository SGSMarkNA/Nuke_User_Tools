#python

import nukescripts
import nuke
import nuke_crop_assemble
#-------------------------------------------------------------------
# Menu_Item
## [menu_item]
##   label: Nuke Crop Assemble
##   tooltip: Tool Tip Needed
def cropAssmble():
    ### this works or does it, damn it###
    p = nuke.Panel('Nuke Crop Assembler')
    p.addFilenameSearch('path_to_tiles', '')
    if p.show():
        print p.value('path_to_tiles')
        nuke_crop_assemble.main(p.value('path_to_tiles'))