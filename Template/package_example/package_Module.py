#!/usr/bin/env python
import nuke

def Package_Example_Command():
    dot = nuke.createNode("Dot")
    nuke.zoom(4,[dot.xpos(),dot.ypos()])