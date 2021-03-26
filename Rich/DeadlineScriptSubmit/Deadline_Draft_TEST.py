import sys

#C:\Program Files\Thinkbox\Deadline9\bin\dpython.exe
#PYTHONPATH='//isln-smb.ad.sgsco.int/Pipeline/Deadline/DeadlineRepository9/draft/Windows/64bit'
#MAGICK_CONFIGURE_PATH='//isln-smb.ad.sgsco.int/Pipeline/Deadline/DeadlineRepository9/draft/Windows/64bit'

#sys.path.append('//isln-smb/Pipeline/Deadline/DeadlineRepository9/submission/Draft')
sys.path.append('//isln-smb/Pipeline/Deadline/DeadlineRepository9/draft/Windows/64bit')

import Draft
from DraftParamParser import ReplaceFilenameHashesWithNumber

encoder = Draft.VideoEncoder(r'X:\Hogarth\HOGH-17-001_GSK_Sensimist_Animation\work\Still\Medicine_Cabinet\img\mov\Medicine_Cabinet_Flonase_Sensimist.mov' )   # Initialize the video encoder.

for currFrame in range( 1, 207 ):
	##currFile = ReplaceFilenameHashesWithNumber( 'Patches_ball_###.jpg', currFrame )
	currFile = ReplaceFilenameHashesWithNumber(r'X:\Hogarth\HOGH-17-001_GSK_Sensimist_Animation\work\Still\Medicine_Cabinet\img\comp\v005C\Medicine_Cabinet_Flonase_Sensimist_####.png', currFrame)
	frame = Draft.Image.ReadFromFile( currFile )
	encoder.EncodeNextFrame( frame )    # Add each frame to the video.

encoder.FinalizeEncoding()    # Finalize and save the resulting video.