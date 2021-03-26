#!/usr/bin/env python
import nuke

def Example_02_Command():
    dot = nuke.createNode("Dot")
    nuke.zoom(4,[dot.xpos(),dot.ypos()])