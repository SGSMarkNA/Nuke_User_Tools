import nuke
import nukescripts
import os

def Save_Viewer_Image():
	# creating panel and assign buttons
	ef = nuke.Panel("Save Viewer Image As...", 600)
	ef.addFilenameSearch("Save Image As:\nchoose path & file type", "")
	ef.addButton("Cancel")
	ef.addEnumerationPulldown('EXR data type:\n(Used for EXR only.)', "16bit-half 32bit-float")
	ef.addButton("OK")
	window=ef.show()
	exrtype = ef.value('Exr data type')
	path = ef.value("Save Image As:\nchoose path & file type")
	fileType = path.split('.')[-1]
	if window == 0 :
		return

	# getting path from user input
	if path == "":
		nuke.message('no file path selected ')
	if path == "":
		return

	# getting active node
	curViewer = nuke.activeViewer()
	curView = curViewer.view()		# Added for multi-view support - RKB
	curNode = curViewer.node()
	activeInput = curViewer.activeInput()
	curN = curNode.input(activeInput)

	# creating temp write
	w = nuke.createNode("Write")
	w.setName("tempWrite")
	w.setInput(0, curN)
	w['views'].setValue(curView)		# Added for multi-view support - RKB
	w['file'].setValue(path)

	# if file type is png
	if fileType == 'png' :
		w['datatype'].setValue(0)

	# if file type is dpx
	if fileType == 'dpx' :
		w['datatype'].setValue(1)
		w['bigEndian'].setValue(True)

	# if file type is tiff
	if fileType == 'tiff' :
		w['datatype'].setValue(0)
		w['compression'].setValue(3)

	# if file type is targa
	if fileType == 'tga' :
		w['compression'].setValue(1)

	# if file type is jpg
	if fileType == 'jpg' :
		w['_jpeg_quality'].setValue(1)
		w['_jpeg_sub_sampling'].setValue(2)

	# if file type is exr
	if fileType == 'exr' :
		w['datatype'].setValue(exrtype)
		w['compression'].setValue(1)
		w['metadata'].setValue(1)	

	# setting current frame for render
	result = nuke.frame()
	if result =="":
		result = result

	# execute write node
	if not os.path.isfile( path ):
		try:
			nuke.execute(nuke.selectedNode(), (int(result)), result)
			name = w.knob('file').value()
			nukescripts.node_delete(popupOnError=True)
		except RuntimeError:
			nukescripts.node_delete(popupOnError=True)
			nuke.message("Error:  Cannot Save Image File!\n\n%s\n\n Press OK to cancel." % (path))
			return
	else:
		nukescripts.node_delete(popupOnError=True)
		nuke.message("Error:  Image File Exists...\n\n%s\n\n Press OK to cancel." % (path))
		return

	if not os.path.isfile( path ):
		nuke.execute(nuke.selectedNode(), (int(result)), result)
		name = w.knob('file').value()
		nukescripts.node_delete(popupOnError=True)

	# create Read node
	r = nuke.createNode("Read")
	r['file'].setValue(name)
	result = nuke.frame()
	r['first'].setValue(int(result))
	r['last'].setValue(int(result))
	r['xpos'].setValue( 200 )

	if fileType == "":
		return