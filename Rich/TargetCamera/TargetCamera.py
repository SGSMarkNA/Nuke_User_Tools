###   TargetCamera for Nuke
###   
###   v1 - Last modified: 21/03/2009
###   Written by Olivier Lavenant & Lucien Fostier

#### Add to menu.py...
# import TargetCamera
#toolbar=nuke.toolbar("Nodes") 
#toolbar.addCommand( "Nodes/TargetCamera", "TargetCamera.TargetCamera()", icon = "TargetCamera.png")

import nuke

def TargetCamera():
    ## create the nodes
    scene = nuke.nodes.Scene ()
    setCam = nuke.nodes.Axis (name = "SetCamera")
    target = nuke.nodes.Axis (name = "Target")
    cam = nuke.nodes.Camera (name = "CameraLookAt", selected = "false")

    ## Hook them up
    scene.setInput(0, setCam)
    scene.setInput(1, target)
    scene.setInput(2, cam)
    target.setInput(0, setCam)
    cam.setInput(0, setCam)

    ## Get the camera expression
    cam['rotate'].setExpression("-degrees(atan2 ((CameraLookAt.translate.y-Target.translate.y),sqrt(pow2(CameraLookAt.translate.z-Target.translate.z)+pow2(CameraLookAt.translate.x-Target.translate.x))))",0)
    cam['rotate'].setExpression("(CameraLookAt.translate.z-Target.translate.z)<=0?180-degrees(atan2 ((CameraLookAt.translate.x-Target.translate.x),abs(CameraLookAt.translate.z-Target.translate.z))):-degrees(atan2 ((Target.translate.x-CameraLookAt.translate.x),abs(CameraLookAt.translate.z-Target.translate.z)))",1)
    cam['rotate'].setExpression("curve",2)

    ## Target Position 
    target['translate'].setValue(15,2)