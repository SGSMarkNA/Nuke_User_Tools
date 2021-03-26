import nuke, struct, os

####________________________________________________________________________
#### Function to test EXR file Compression scheme...
def EXR_Compression_Test():	
	try:
		n = nuke.selectedNode()
		if nuke.selectedNode().Class()!='Read' or nuke.selectedNode() == "" :
			nuke.message('No Read node selected.')
		elif os.path.splitext(nuke.filename(nuke.selectedNode()))[-1]!=".exr" :
			nuke.message('Selected Read is not an EXR')
		else:
			filePath = nuke.filename(n, nuke.REPLACE)
			file = open(filePath, 'rb')
			compressionTypes = ['RAW', 'RLE', 'ZIP1', 'ZIP16', 'PIZ', 'PXR24', 'B44']
			compression = 0
			if struct.unpack("i4", file.read(4))[0] == 20000630:
				versionFlag = struct.unpack("i4", file.read(4))
				loop = True
				while loop == True:
					i = 0
					size = 0
					headerStart = file.tell()
					headerName = ""
					headerType = ""
					while i <= 50:
						buffer = file.read(1)
						if ord(buffer) == 0 and headerName == "":
							nameSize = file.tell() - headerStart
							file.seek(0-nameSize, 1)
							headerName = file.read(nameSize)[0:-1]
							if len(headerName) == 0:
								loop = False
								break
						elif ord(buffer) == 0 and headerType == "":
							nameSize = file.tell() - len(headerName) - 1 - headerStart
							file.seek(0-nameSize, 1)
							headerType = file.read(nameSize)[0:-1]
							headerSize = struct.unpack("i4", file.read(4))[0]
							if headerName == "compression":
								compression = file.read(1)
							else:
								file.seek(headerSize, 1)
							break
						if i == 50 or headerStart > 1024:
							loop = False
						i=+1
			compressMethod = (compressionTypes[ord(compression)])		   
			print compressMethod
			nuke.message('EXR compression is %s' %(compressMethod))

	except ValueError:
		nuke.message('Please select a Read node...')
		