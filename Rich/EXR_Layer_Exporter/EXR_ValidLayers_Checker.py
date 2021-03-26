import nuke

def EXR_ValidLayers_Checker(Node):
    '''
    Use CurveTool node's "Max Luma Pixel" function to check each layer of an EXR file for empty layers.
    Returns a tuple of the list of ValidLayers and EmptyLayers.
    '''
    EmptyLayers = []
    ValidLayers = []
    MaxData = []
    MinData = []
    # Get the layers from the EXR...
    channels = Node.channels()
    #print 'channels', channels
    layers = list(set([c.split('.')[0] for c in channels]))
    layers.sort()
    #print 'layers SORTED', layers
    # Create the utility nodes for checking each layer with CurveTool's Min/Max Luma function...
    Shuffle = nuke.createNode('Shuffle', inpanel=False)
    Shuffle.setInput(0, Node)
    CurveTool = nuke.createNode('CurveTool', inpanel=False)
    w = CurveTool.width()
    h = CurveTool.height()
    # Check the layers Min/Max values and sort them into valid and empty lists...
    for layer in layers:
        Shuffle['in'].setValue(layer)
        CurveTool['operation'].setValue('Max Luma Pixel')
        CurveTool['ROI'].setValue((0,0,w,h))
        nuke.execute(CurveTool, nuke.frame(), nuke.frame())
        MaxData = CurveTool['maxlumapixvalue'].value()
        #print layer, (' Max luma is %s' % MaxData)
        MinData = CurveTool['minlumapixvalue'].value()
        #print layer, (' Min luma is %s' % MinData)
        MaxData = max(MaxData)
        MinData = min(MinData)
        Values = (MaxData, MinData)
        # If there's anything other than zero in the max or min, then we'll keep the layer...
        if MinData != 0.0 or MaxData != 0.0:
            ValidLayers.append(layer)
            #print layer, Values, 'VALID'
        else:
            # Edge Case: check if the Min/Max values are not zero, but their sum is zero - it should still be considered a valid layer...
            if sum(Values) == 0.0:
                if Values[0] != 0.0 and Values[1] != 0.0:
                    print ''
                    print 'Layer "%s" is Valid.\nThe MaxData and MinData values cancel each other out.\nAdding it to the ValidLayers list...' % layer
                    ValidLayers.append(layer)
                    #print layer, Values, 'VALID'
                # Otherwise, there is no data to keep...
                else:
                    EmptyLayers.append(layer)
                    #print layer, Values, 'EMPTY'
    ValidLayers = list(set([x for x in ValidLayers]))
    print 'ValidLayers --> ', ValidLayers
    EmptyLayers = list(set([x for x in EmptyLayers]))
    print 'EmptyLayers --> ', EmptyLayers
    nuke.delete(CurveTool)
    nuke.delete(Shuffle)
    return (ValidLayers, EmptyLayers)


#########################################
## EXAMPLE USAGE:
#########################################

#LAYERS = EXR_ValidLayers_Checker(Node)

#print 'ValidLayers -->', LAYERS[0]
#print ''
#print 'EmptyLayers -->', LAYERS[1]

