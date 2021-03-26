import nukescripts
import nuke
import nukeAssemble
import nukeAssemble.nuke_crop_assemble

if nuke.env["gui"]:

      class ModalFramePanel( nukescripts.PythonPanel ):
          def __init__( self ):
            nukescripts.PythonPanel.__init__( self, "Get Directory for Tiles", "aw.tileAssemble" )
            self.tiles = nuke.File_Knob( "path", "Tile Path:" )
            self.addKnob( self.tiles )
            self.processBTN = nuke.PyScript_Knob("Process_BTN", "Process Tiles")
            self.addKnob(self.processBTN)
         
         
          def knobChanged(self, knob):
             if knob == self.processBTN:
                 nukeAssemble.nuke_crop_assemble.main(self.tiles.getValue())

      def showModalDialog( self ):
         result = nukescripts.PythonPanel.showModalDialog( self )


      def testModalPanel():
          return ModalFramePanel().showModalDialog()

      def main():
           testModalPanel()

if "__name__" == "__main__":
    main()