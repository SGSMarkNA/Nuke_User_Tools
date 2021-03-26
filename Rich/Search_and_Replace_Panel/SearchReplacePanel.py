from xml.etree import ElementTree
import nuke
import nukescripts
import os
import re

class SearchReplacePanel( nukescripts.PythonPanel ):
    def __init__( self, historyFile='~/.nuke/srhistory.xml', maxSteps=10 ):
        '''
        Search and Replace panel - Original written by Frank Reuter -- Website: www.ohufx.com -- 14 Mar 2012
        args:
           historyFile  -  file to manage recent search&replace actions
           maxSteps  -  amount of steps to keep in history file

        Note: To load the panel into the "Pane" menu and make it save with layouts properly, drop something like this into your menu.py:
        import SearchReplacePanel
        def addSRPanel():
                myPanel = SearchReplacePanel.SearchReplacePanel()
                return myPanel.addToPane()
        #THIS LINE WILL ADD THE NEW ENTRY TO THE PANE MENU
        nuke.menu('Pane').addCommand('SearchReplace', addSRPanel)
        #THIS LINE WILL REGISTER THE PANEL SO IT CAN BE RESTORED WITH LAYOUTS
        nukescripts.registerPanel('com.richbobo.SearchReplace', addSRPanel)
        Created by Rich Bobo - 08/05/2014
        richbobo@mac.com
        http://richbobo.com		
        '''
        nukescripts.PythonPanel.__init__(self, 'Search and Replace', 'com.richbobo.SearchReplace')

        # VARS
        self.historyFile = os.path.expandvars(os.path.expanduser(historyFile))
        self.maxSteps = maxSteps
        self.delimiter = ' -->  '
        # CREATE KNOBS
        self.nodesChoice = nuke.Enumeration_Knob('nodes', 'Source Nodes: ', ['All', 'Selected', 'Reads', 'Writes', 'ReadGeos'])
        self.nodesChoice.setTooltip('Choose to perform action on all nodes with file knobs or only selected ones')
        self.searchScope = nuke.Enumeration_Knob('scope', 'Search Scope: ', ['Entire Script', 'Current Node Graph Only'])
        self.searchScope.setTooltip('Choose whether to perform the search on all the nodes in the script or only on the current node graph (either the main node graph or another group).')
        self.searchScope.clearFlag(nuke.STARTLINE)
        self.history = nuke.Enumeration_Knob('history', 'Recent Replacements: ', self.loadHistory())
        self.history.setTooltip('Use the history to quicky access previous search&replace actions.\n By default the history file is stored as "~/.nuke/srhistory.xml" but this can be changed via the "historyFile" argument when creating the panel object. It is also possible to change the size of the history via the "maxSteps" argument to the panel object. Default is 10')
        self.case = nuke.Boolean_Knob('case', 'case sensitive')
        self.case.setFlag(nuke.STARTLINE)
        self.case.setValue(True)
        self.case.setTooltip('Set whether or not the search should be case sensitive')
        self.searchStr = nuke.File_Knob('searchStr', 'Search for:')
        self.searchStr.setTooltip('The text to search for')
        self.update = nuke.PyScript_Knob('update', 'Update')
        self.update.setTooltip('Update the search result and preview. This is automaticaly performed and usually should only be required when the node selection has changed')
        self.replaceStr = nuke.File_Knob('replaceStr', 'Replace with:')
        self.replaceStr.setTooltip('Text to replace the found text with')
        self.replace = nuke.PyScript_Knob('replace', 'Replace')
        self.replace.setTooltip('Perform replace action. The preview will update afterwards and the action is added to the history')
        self.divider = nuke.Text_Knob('divider', '')
        ####self.info = nuke.Multiline_Eval_String_Knob('info', 'Found')
        self.info = nuke.Text_Knob('info', '')
        ####self.info.setEnabled(False)
        self.info.setTooltip('See the search results and a preview of the replace action before it is performed')
        # ADD KNOBS
        for k in (self.nodesChoice, self.searchScope, self.history, self.case, self.searchStr, self.update, self.replaceStr, self.replace, self.divider, self.info):
            self.addKnob(k)
        self.matches = None

    def loadHistory(self):
        '''load history file to update knob'''
        print 'loading search&replace history'
        # GET EXISTING HISTORY
        if not os.path.isfile(self.historyFile):
            return []
        # READ EXISTING FILE
        xmlTree = ElementTree.parse( self.historyFile )
        itemList = ['%s%s%s' % (n.attrib['search'], self.delimiter, n.attrib['replace']) for n in xmlTree.findall('ITEM')][-self.maxSteps:]
        itemList.reverse()
        itemList.insert(0, '-- Select --')
        return itemList

    def updateHistory(self, sString, rString):
        '''
        updates history file
        args:
           sString - search string to add to history
           rString - replace string to add to history
        '''
        itemList = []
        # READ EXISTING FILE
        if os.path.isfile(self.historyFile):
            xmlTree = ElementTree.parse(self.historyFile)
            for n in xmlTree.findall('ITEM'):
                attr = n.attrib
                itemList.append(attr)
        # IGNORE ATTRIBUTES THAT ARE ALREADY IN HISTORY
        entryExists = False
        for i in itemList:
            if i['search'] == sString and i['replace']==rString:
                entryExists = True
                break
        # IF ATTRIBUTES DONT EXIST IN HISTORY, ADD THEM
        if not entryExists:
            # PREP DICTIONARY FOR XML DUMP
            srItem = dict(search=sString, replace=rString)
            itemList.append(srItem)
            # BUILD XML TREE
            root = ElementTree.Element('SearchReplacePanel')
            for i in itemList[-self.maxSteps:]:
                ElementTree.SubElement(root, 'ITEM', attrib=i)
            tree = ElementTree.ElementTree(root)
            # DUMP XML TREE
            print 'WRITING TO:', self.historyFile
            tree.write(self.historyFile)

    def recursiveFindNodes(self, nodeClass, startNode):
        '''Recursive node class find function from Drew Loveridge.
           EXAMPLE USAGE:
                for d in recursiveFindNodes("Dot", nuke.root()):
                    print d.name()
        '''
        if startNode.Class() == nodeClass:
            yield startNode
        elif isinstance(startNode, nuke.Group):
            for child in startNode.nodes():
                for foundNode in self.recursiveFindNodes(nodeClass, child):
                    yield foundNode

    def collectReadNodes(self):
        '''Collect all of the "Read" nodes...'''
        read_nodes = []
        for n in self.recursiveFindNodes("Read", nuke.root()):
            read_nodes.append(n)
        return read_nodes

    def collectReadGeo2Nodes(self):
        '''Collect all of the "ReadGeo2" nodes...'''
        readgeo2_nodes = []
        for n in self.recursiveFindNodes("ReadGeo2", nuke.root()):
            readgeo2_nodes.append(n)
        return readgeo2_nodes

    def collectWriteNodes(self):
        '''Collect all of the "Write" nodes...'''
        write_nodes = []
        for n in self.recursiveFindNodes("Write", nuke.root()):
            write_nodes.append(n)
        return write_nodes

    def getAllNodes(self, topLevel):
        '''
        Recursively return all the nodes in the script, starting at topLevel.
        Looks in all groups. Default topLevel to use is nuke.root()
        '''
        allNodes = nuke.allNodes(group=topLevel)
        for n in allNodes:
            allNodes = allNodes + self.getAllNodes(n)
        return allNodes

    def getAllSelectedNodes(self, topLevel):
        '''
        Recursively return all the nodes in the script, starting at topLevel.
        Looks in all groups. Default topLevel to use is nuke.root()
        '''
        # Get all of the nodes in the script...
        allNodes = nuke.allNodes(group=topLevel)
        for n in allNodes:
            allNodes = allNodes + self.getAllSelectedNodes(n)
        # Get just the ones that are selected...
        allSelectedNodes = []
        for n in allNodes:
            if n.knob('selected').value() == True:
                allSelectedNodes.append(n)
        return allSelectedNodes

    def findNodesWithFileKnob(self, nodes):
        '''Find all of the nodes that have a file knob...'''
        fileKnobNodes = []
        if not nodes: 
            #nuke.message('No nodes selected') 
            return None
        else:
            for node in nodes:
                if 'file' in node.knobs():
                    fileKnobNodes.append(node)
        return fileKnobNodes

    def findNodesWithProxyKnob(self, nodes):
        '''Find all of the nodes that have a proxy knob...'''
        proxyKnobNodes = []
        if not nodes:
            #nuke.message('No nodes selected') 
            return None
        else:
            for node in nodes:
                if 'proxy' in node.knobs():
                    proxyKnobNodes.append(node)
        return proxyKnobNodes

    def search(self, searchstr, nodes):
        """ Search in nodes with file knobs. """
        nodeMatches = []
        knobMatches = []
        fileKnobNodes = self.findNodesWithFileKnob(nodes)
        proxyKnobNodes = self.findNodesWithProxyKnob(nodes)
        if not fileKnobNodes and not proxyKnobNodes:
            ##nuke.message("No Source Nodes Selected. Try again.")
            ##nodeMatches, knobMatches = None, None
            # Return empty lists...
            return nodeMatches, knobMatches
        for i in fileKnobNodes:
            if self.__findNode(searchstr, i['file']):
                nodeMatches.append(i)
                knobMatches.append(i['file'])            
        for i in proxyKnobNodes:
            if self.__findNode(searchstr, i['proxy']):
                nodeMatches.append(i)
                knobMatches.append(i['proxy'])
        return nodeMatches, knobMatches        

    def getSearchResults(self, nodes):
        # PERFORM SEARCH AND UPDATE INFO KNOB
        if not self.search(self.searchStr.value(), nodes):
            nuke.message("No Source Nodes Selected. Try again.")
            return None
        else:
            nodeMatches, knobMatches = self.search(self.searchStr.value(), nodes)
            knobMatches = sorted(knobMatches)
        if nodeMatches is not None:
            nodes = [n.name() for n in nodeMatches]
            nodes = sorted(nodes)
        else:
            nodes = []
        infoStr1 = '%s node(s) found:\n\t%s\n' % (len(nodes), ', '.join(nodes))
        infoStr2 = ''
        if knobMatches is not None:
            infoStr2List = []
            for k in knobMatches:
                newStr = nukescripts.replaceHashes(self.__doReplace(k))
                # CHECK IF PATH IS VALID FOR CURRENT FRAME
                curFrame = int(nuke.Root()['frame'].value()) # there is a bug which prevents nuke.frame() to work properly inside of python panels (6.3v5)
                try:
                    curPath = newStr % curFrame
                except:
                    curPath = newStr
                exists = {True:' ++++++  Valid path at frame %s.  ++++++' % curFrame, False:'  ----->  !!! PATH NOT VALID AT CURRENT FRAME %s !!!  <-----' % curFrame}[os.path.exists(curPath)]
                # BUILD INFO STRING
                infoStr2 += '%s.%s:\n\tBEFORE\t%s\n\tAFTER\t%s\n\t%s\n' % (k.node().name(), k.name(), k.value(), newStr, exists)
                infoStr2List.append('%s.%s:\n\tBEFORE\t%s\n\tAFTER\t%s\n\t%s' % (k.node().name(), k.name(), k.value(), newStr, exists))
            infoStr2List = sorted(infoStr2List)
            infoStr2Sorted = ('\n'.join(infoStr2List))
            self.info.setValue('\n'.join([infoStr1, infoStr2Sorted]))
            return knobMatches
        else:
            self.info.setValue('\n'.join([infoStr1, infoStr2]))

    def __findNode(self, searchstr, knob):
        v = knob.value()
        if not self.case.value():
            v = v.lower()
            searchstr = searchstr.lower()
        if v and searchstr and searchstr in v:
            return True    

    def __doSearch(self):
        # LAUNCH SEARCH
        if self.searchScope.value() == "Entire Script":
            srcNodes = {'All': self.getAllNodes(nuke.root()), 'Selected': self.getAllSelectedNodes(nuke.root()), 'Reads': self.collectReadNodes(), 'Writes': self.collectWriteNodes(), 'ReadGeos': self.collectReadGeo2Nodes()}
        elif self.searchScope.value() == "Current Node Graph Only":
            srcNodes = {'All': nuke.allNodes(), 'Selected': nuke.selectedNodes(), 'Reads': [n for n in nuke.allNodes() if n.Class() == "Read"], 'Writes': [n for n in nuke.allNodes() if n.Class() == "Write"], 'ReadGeos': [n for n in nuke.allNodes() if n.Class() == "ReadGeo2"]}

        ##srcNodes = {'All': nuke.allNodes(), 'Selected': nuke.selectedNodes(), 'Reads': self.collectReadNodes(), 'Writes': self.collectWriteNodes(), 'ReadGeos': self.collectReadGeo2Nodes()}
        self.matches = self.getSearchResults(srcNodes[self.nodesChoice.value()])

    def __doReplace(self, knob):
        # PERFORM REPLACE
        if self.case.value():
            # CASE SENSITIVE
            newStr = re.sub(self.searchStr.value(), self.replaceStr.value(), knob.value())
        else:
            # IGNORE CASE
            newStr = knob.value()
            for m in re.findall(self.searchStr.value(), knob.value(), re.IGNORECASE):
                newStr = re.sub(m, self.replaceStr.value(), newStr)

        return newStr

    def knobChanged(self, knob):
        if knob in (self.searchStr, self.replaceStr, self.update, self.nodesChoice, self.searchScope, self.case):
            # PERFORM SEARCH
            self.__doSearch()
        elif knob is self.replace and self.matches is not None:
            if nuke.ask("Really replace all the listed file paths?"):
                # PERFORM REPLACE AND UPDATE HISTORY
                print 'replacing'
                for k in self.matches:
                    k.setValue(self.__doReplace( k ))
                # Update the search history...
                self.updateHistory(self.searchStr.value(), self.replaceStr.value())
                self.history.setValues(self.loadHistory())
                self.history.setValue(0)
                self.__doSearch()
            else:
                nuke.message("No Replacements Made.")            
        elif knob is self.history:
            try:
                search, replace = knob.value().split(self.delimiter)
            except ValueError:
                search, replace = None, None
            else:
                self.searchStr.setValue(search)
                self.replaceStr.setValue(replace)
                self.__doSearch()


## Main function to create the SearchReplace panel...
def Create_SearchReplacePanel():
    p = SearchReplacePanel()
    p.show()