import nuke
import os
import math


def createExrCamVray(node=None):
	'''
	Create a camera node based on VRay metadata.
	This works specifically on VRay data coming from maya.

	http://polygonspixelsandpaint.tumblr.com/post/40175774250
	http://pastebin.com/4vmAmARU#

	'''
	try:
		node = nuke.selectedNode()
	except ValueError:
		print('No Read node selected.')
		nuke.message('No Read node selected.')
		return

	mDat = node.metadata()
	reqFields = ['exr/camera%s' % i for i in ('FocalLength', 'Aperture', 'Transform')]
	if not set(reqFields).issubset(mDat):
		print('No metadata for camera found.')
		nuke.message('No metadata for camera found.')
		return

	first = node.firstFrame()
	last = node.lastFrame()
	ret = nuke.getFramesAndViews('Create Camera from Metadata', '%s-%s' %(first, last))
	fRange = nuke.FrameRange(ret[0])

	cam = nuke.createNode('Camera2')
	cam['useMatrix'].setValue(False)

	for k in ('focal', 'haperture', 'translate', 'rotate'):
		cam[k].setAnimated()


	for curTask, frame in enumerate(fRange):

		## IB. If you get both focal and aperture as they are in the metadata, there's no guarantee
		## your Nuke camera will have the same FOV as the one that rendered the scene (because the render could have been fit to horizontal, to vertical, etc)
		## Nuke always fits to the horizontal aperture. If you set the horizontal aperture as it is in the metadata,
		## then you should use the FOV in the metadata to figure out the correct focal length for Nuke's camera
		## Or, you could keep the focal as is in the metadata, and change the horizontal_aperture instead.
		## I'll go with the former here. Set the haperture knob as per the metadata, and derive the focal length from the FOV

		# Get horizontal aperture...
		val = node.metadata('exr/cameraAperture', frame)
		# Get camera FOV...
		fov = node.metadata('exr/cameraFov', frame)
		# Convert the fov and aperture into focal length...
		focal = val / (2 * math.tan(math.radians(fov)/2.0))

		cam['focal'].setValueAt(float(focal),frame)
		cam['haperture'].setValueAt(float(val),frame)
		# Get camera transform data...
		matrixCamera = node.metadata('exr/cameraTransform', frame)

		# Create a matrix to shove the original data into...
		matrixCreated = nuke.math.Matrix4()

		for k,v in enumerate(matrixCamera):
			matrixCreated[k] = v

		# This is needed for VRay.  It's a counter clockwise rotation...
		matrixCreated.rotateX(math.radians(-90))
		# Get a vector that represents the camera translation...
		translate = matrixCreated.transform(nuke.math.Vector3(0,0,0))
		# Give us xyz rotations from cam matrix... (must be converted to degrees)
		rotate = matrixCreated.rotationsZXY()

		cam['translate'].setValueAt(float(translate.x),frame,0)
		cam['translate'].setValueAt(float(translate.y),frame,1)
		cam['translate'].setValueAt(float(translate.z),frame,2)
		cam['rotate'].setValueAt(float(math.degrees(rotate[0])),frame,0)
		cam['rotate'].setValueAt(float(math.degrees(rotate[1])),frame,1)
		cam['rotate'].setValueAt(float(math.degrees(rotate[2])),frame,2)

	# Added label info with filename and frame range -- RKB 02/06/17
	# NOTE: Can't know if last portion of filename has an underscore or a dot separator or if it's part of the filename,
	# so I have to leave it there... Decided to use first frame of sequence as the evaluated name, rather than the last.
	##filePath = node.knob('file').evaluate()
	filePath = node.knob('file').evaluate(first)
	filename = os.path.basename(filePath)
	name = filename.split(".")[0]
	cam['label'].setValue(name + "\n" + "Frame Range: " + str(fRange))