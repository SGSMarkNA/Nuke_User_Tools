import nuke


class Node_Tools(object):
    '''A collection of useful node tools for Nuke.
    So I don't have to re-write them for every script...'''

    def __init__(self):
        pass

    ##-------------------------------------------------------------------------
    ## Recursive methods for finding and collecting nodes in the entire script...
    ## Searches *all* of script, including any Groups.
    ##-------------------------------------------------------------------------

    def _recursive_find_nodes(self, nodeClass, startNode):
        '''Recursive node class find function from Drew Loveridge.
           EXAMPLE USAGE:
                for d in _recursive_find_nodes("Dot", nuke.root()):
                    print d.name()
        '''
        if startNode.Class() == nodeClass:
            yield startNode
        elif isinstance(startNode, nuke.Group):
            for child in startNode.nodes():
                for foundNode in self._recursive_find_nodes(nodeClass, child):
                    yield foundNode


    def _collect_class_nodes(self, nodeClass=''):
        '''Collect all of the nodes of a given Class in the entire script, including groups.
        Example Usage:
            _collect_class_nodes('Write')
        '''
        class_nodes = []
        for n in self._recursive_find_nodes(nodeClass, nuke.root()):
            class_nodes.append(n)
        return class_nodes


    def _collect_Read_nodes(self):
        '''Collect all of the "Read" nodes in the entire script, including groups.'''
        read_nodes = []
        for n in self._recursive_find_nodes("Read", nuke.root()):
            read_nodes.append(n)
        return read_nodes


    def _collect_ReadGeo2_nodes(self):
        '''Collect all of the "ReadGeo2" nodes in the entire script, including groups.'''
        readgeo2_nodes = []
        for n in self._recursive_find_nodes("ReadGeo2", nuke.root()):
            readgeo2_nodes.append(n)
        return readgeo2_nodes


    def _collect_Write_nodes(self):
        '''Collect all of the "Write" nodes in the entire script, including groups.'''
        write_nodes = []
        for n in self._recursive_find_nodes("Write", nuke.root()):
            write_nodes.append(n)
        return write_nodes


    ## Like nuke.allNodes(), gets all nodes - but allows searching in a designated group...
    ## By default, will start at topLevel=nuke.root() and recurse through entire script.
    ## Can specify another Group name, instead, e.g. -- getAllNodes(nuke.toNode('Group1'))

    def _get_all_nodes(self, topLevel=nuke.root()):
        '''
        Recursively return all nodes starting at "topLevel".
        Looks in all groups. Default topLevel to use is nuke.root().
        Could be group name, instead -- topLevel="Group2"
        '''
        #allNodes = nuke.allNodes(group=topLevel)
        #for n in allNodes:
            #allNodes = allNodes + self.getAllNodes(n)
        #allNodes = sorted(allNodes)

        allNodes = nuke.allNodes(recurseGroups=True, group=topLevel)
        allNodes = sorted(allNodes)
        return allNodes

    ##-------------------------------------------------------------------------
    ## Methods for finding and selecting or deselecting nodes...
    ##-------------------------------------------------------------------------

    def _deselectAllNodes(self):
        allNodes = self._get_all_nodes(nuke.root())
        for n in allNodes:
            n.knob('selected').setValue(False)


    def _selectAllNodes(self):
        allNodes = self._get_all_nodes(nuke.root())
        for n in allNodes:
            n.knob('selected').setValue(True)

    ##-------------------------------------------------------------------------
    ## Methods for knobs... Requires list of nodes.
    ##-------------------------------------------------------------------------

    def _find_nodes_with_knob_name(self, nodes, knob=''):
        '''Find all of the nodes that have a certain named knob...
        Example Usage:
            _find_nodes_with_knob_name(nuke.selectedNodes(), 'file')
        '''
        KnobNodes = []
        if not nodes:
            return None
        else:
            for node in nodes:
                if knob in node.knobs():
                    KnobNodes.append(node)
        return KnobNodes


    def _find_nodes_with_file_knob(self, nodes):
        '''Find all of the nodes that have a file knob...'''
        fileKnobNodes = []
        if not nodes:
            return None
        else:
            for node in nodes:
                if 'file' in node.knobs():
                    fileKnobNodes.append(node)
        return fileKnobNodes


    def _find_nodes_with_vfield_file_knob(self, nodes):
        '''
        Find all of the nodes that have a vfield_file knob (Vectorfield node)...
        '''
        vfield_fileKnobNodes = []
        if not nodes:
            return None
        else:
            for node in nodes:
                if 'vfield_file' in node.knobs():
                    vfield_fileKnobNodes.append(node)
        return vfield_fileKnobNodes


    def _find_nodes_with_proxy_knob(self, nodes):
        '''Find all of the nodes that have a proxy knob...'''
        proxyKnobNodes = []
        if not nodes:
            return None
        else:
            for node in nodes:
                if 'proxy' in node.knobs():
                    proxyKnobNodes.append(node)
        return proxyKnobNodes


    def _find_all_source_nodes(self, nodes):
        '''
        Given a list of nodes, check for those with file knobs and
        return all the nodes that are not Write, Viewer or Group nodes...
        '''
        sourceNodes = []

        fileKnobNodes = self._find_nodes_with_file_knob(nodes)
        vfield_fileKnobNodes = self._find_nodes_with_vfield_file_knob(nodes)

        for Node in fileKnobNodes:
            if Node.Class() not in ('Write', 'Viewer', 'Group'):
                sourceNodes.append(Node)
        for Node in vfield_fileKnobNodes:
            if Node.Class() not in ('Write', 'Viewer', 'Group'):
                sourceNodes.append(Node)
        return sourceNodes


    def _find_nodes_with_errors(self, nodes):
        '''
        Given a list of nodes, return a list of the nodes which have errors - like an incorrect file path for a file knob...
        '''
        # Note: For some reason, just putting nodes in groups can cause the hasError() method to trigger.
        # So, by using the fullName of the node, I can work around the problem...
        nodes_with_errors = []
        for node in nodes:
            # Check to see if node is actually in a group and run .hasError() method in that context...
            if '.' in node.fullName():
                node_group = nuke.toNode('.'.join(node.fullName().split('.')[:-1]))
                with node_group:
                    if node.hasError() == True:
                        nodes_with_errors.append(node)
            # Node not in a group, so just check it for errors...
            else:
                if node.hasError() == True:
                    nodes_with_errors.append(node)

        return nodes_with_errors

    ##-------------------------------------------------------------------------
    ## Methods for listing things...
    ##-------------------------------------------------------------------------

    def _sorted_names(self, nodeList=None):
        '''Takes a list of nodes (objects) and returns a sorted list of the node names...'''
        nameList = []
        if nodeList is not None:
            for n in nodeList:
                nameList.append(n.name())
                nameList = sorted(nameList)
        return nameList


    def _show_Read_node_paths(self, nodes):
        for n in nodes:
            if n.Class() == 'Read':
                file_path = n.knob('file').value()
                print(file_path)



'''
##########################################
## EXAMPLES -- TESTING IN Nuke...
##########################################

import Node_Tools.Node_Tools
reload(Node_Tools.Node_Tools)
tools = Node_Tools.Node_Tools.Node_Tools()

tools._get_all_nodes()
tools._get_all_nodes(nuke.toNode('Group1'))
tools._collect_class_nodes('Viewer')
tools._collect_Read_nodes()
tools._collect_ReadGeo2_nodes()
tools._collect_Write_nodes()
tools._sorted_names(tools._collect_Read_nodes())

tools._find_nodes_with_knob_name(tools._get_all_nodes(), 'file_type')
tools._find_nodes_with_file_knob(tools._get_all_nodes())
tools._find_nodes_with_file_knob(nuke._selectedNodes())
tools._find_nodes_with_vfield_file_knob(tools._get_all_nodes())

sourceNodes = tools._find_all_source_nodes(tools._get_all_nodes())

nodes_with_errors = tools._find_nodes_with_errors(sourceNodes)
tools._sorted_names(nodes_with_errors)

tools._selectAllNodes()
tools._deselectAllNodes()


'''


'''
#################################################################
## Potentially Useful Snippets...
#################################################################

[n.name() for n in collected_nodes]


n = nuke.selectedNode()
n.Class()


for node in read_nodes:
    node.knob('selected').setValue(True)


def print_node_collection(self):
    self.collected_nodes = []
    self.collected_nodes = self.read_nodes + self.readgeo2_nodes + self.write_nodes
    list = [n.name() for  n in self.collected_nodes]
    print list


for n in nuke.allNodes():
    if n.Class() == "Write":
        n.knob('channels').setValue("all")

'''

