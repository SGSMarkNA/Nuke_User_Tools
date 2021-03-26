import nuke

def Camera_3d_Scene_Start():
    
    sceneNode = nuke.createNode('Scene')
    
    cameraNode = nuke.createNode('Camera2')
    cameraNode.setXYpos(sceneNode.xpos()-150, sceneNode.ypos())
    cameraNode.knob('translate').setValue([0.0, 1.0, 5.0])

    scanlineNode = nuke.createNode('ScanlineRender')
    scanlineNode.setXYpos(sceneNode.xpos()-9, sceneNode.ypos()+150)

    lightNode = nuke.createNode('Light2')
    lightNode.setXYpos(sceneNode.xpos()+175, sceneNode.ypos())
    lightNode.knob('translate').setValue([1.0, 2.0, 1.0])
    
    constantNode = nuke.createNode('Constant')
    #constantNode.setXYpos(scanlineNode.xpos()+175, scanlineNode.ypos()-24)
    constantNode.setXYpos(scanlineNode.xpos()+90, scanlineNode.ypos()-90)
    
    scanlineNode.setInput(0, constantNode)
    scanlineNode.setInput(1, sceneNode)
    scanlineNode.setInput(2, cameraNode)
    
    sceneNode.setInput(0, cameraNode)
    sceneNode.setInput(1, lightNode)


#### To run...
#Camera_3d_Scene_Start()

    
    
    
    
 


