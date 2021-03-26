
////////////////////////////////////////////////////////////////
//// Hide Photoshop UI... Doesn't seem to help.
// app.Visible = false;

////////////////////////////////////////////////////////////////
//// This hides everything, almost, but also does not save a file!!
// app.scriptPreferences.enableRedraw = false; 

////////////////////////////////////////////////////////////////
//// Supposedly turns on Performance mode. Maybe only works when using ActionScripts...?
//
// cTID = function(s) { return app.charIDToTypeID(s); };  
// sTID = function(s) { return app.stringIDToTypeID(s); };  
//
// Stdlib = function Stdlib() {};  
//
// Stdlib.setActionPlaybackOptions = function(opt, arg) {  
//   function _ftn() {  
//     var desc = new ActionDescriptor();  
//     var ref = new ActionReference();  
//     ref.putProperty(cTID("Prpr"), cTID("PbkO"));  
//     ref.putEnumerated(cTID("capp"), cTID("Ordn"), cTID("Trgt"));  
//     desc.putReference(cTID("null"), ref );  
//     var pdesc = new ActionDescriptor();  
//     pdesc.putEnumerated(sTID("performance"), sTID("performance"), sTID(opt));  
//     if (opt == "pause" && arg != undefined) {  
//       pdesc.putInteger(sTID("pause"), parseInt(arg));  
//     }  
//     desc.putObject(cTID("T "), cTID("PbkO"), pdesc );  
//     executeAction(cTID("setd"), desc, DialogModes.NO);  
//   }  
//   _ftn();  
// };  
// Stdlib.setPlaybackAcclerated = function() {  
//   Stdlib.setActionPlaybackOptions("accelerated");  
// };  
// Stdlib.setPlaybackStepByStep = function() {  
//   Stdlib.setActionPlaybackOptions("stepByStep");  
// };  
// Stdlib.setPlaybackPaused = function(delaySec) {  
//   Stdlib.setActionPlaybackOptions("pause", delaySec);  
// };

////////////////////////////////////////////////////////////////
//// Doesn't seem to help...
// togglePalettes();


// =======================================================
// Check for the OS we're on...
os = $.os.toLowerCase().indexOf('mac') >= 0 ? "MAC": "WINDOWS";
alert(os)

// =======================================================
// Data passing from file, generated via python script...
if(os == "WINDOWS")
	var DataFile = new File("C:\\Users\\rbobo\\Box Sync\\CODE_aw_projects (Rich.Bobo@armstrong-white.com)\\aw_projects\\NukePSD\\JavaScript\\Photoshop\\data.txt");
else if (os == "MAC")
	var DataFile = new File("/Users/richbobo/Box Sync/CODE_aw_projects (Rich.Bobo@armstrong-white.com)/aw_projects/NukePSD/JavaScript/Photoshop/data.txt");

// Open and read lines from data file. Assign to script variables...
DataFile.open('r');
var PNG_FOLDER = "";
while(!DataFile.eof)
PNG_FOLDER += DataFile.readln();
DataFile.close();
alert(PNG_FOLDER);

// if (arguments.length > 0) 
// 	alert("ARGUMENT 0 = " + arguments[0]);
// else
// 	alert("Nope!")

// var newPath = arguments;
// alert(newPath)


// =======================================================
// Path to server...
var libPath = $.getenv("AW_COMMON_UTILITIES");

// Path to Color Settings...
var ColorSettingsPath = (libPath + "/Photoshop/AW_Nuke_Tools/Color_Settings")

// Color settings files...
var ACES_SETTINGS = (ColorSettingsPath + "/ACES-CG-Linear_NO_PROFILE_PROMPTS.csf" )
var sRGB_SETTINGS = (ColorSettingsPath + "/sRGB.csf" )

// =======================================================
// Set to use pixels...
app.preferences.rulerUnits = Units.PIXELS
app.preferences.typeUnits = TypeUnits.PIXELS

// =======================================================
// Display no dialogs...
app.displayDialogs = DialogModes.NO

// =======================================================
// Loads "ACES-CG-Linear" colorSettings that the user has saved...
// Test for the os we're on...
if(os == "WINDOWS")
    var FileName = new File (sRGB_SETTINGS);
    // Apparently MacOS doesn't support UNC pathnames, so the volume has to be mounted first and accessed via the /Volumes mount directory...
else if (os == "MAC")
	var FileName = new File ("/Volumes/library/Scripts/Photoshop_Scripts/Color_Settings/sRGB.csf");

function loadColorSettings( file ) {  
     var desc = new ActionDescriptor();  
        var ref = new ActionReference();  
        ref.putProperty( charIDToTypeID('Prpr'), stringIDToTypeID('colorSettings') );  
        ref.putEnumerated( charIDToTypeID('capp'), charIDToTypeID('Ordn'), charIDToTypeID('Trgt') );  
    desc.putReference( charIDToTypeID('null'), ref );  
        var fileDesc = new ActionDescriptor();  
        fileDesc.putPath( charIDToTypeID('Usng'), file );  
    desc.putObject( charIDToTypeID('T   '), stringIDToTypeID('colorSettings'), fileDesc );  
    executeAction( charIDToTypeID('setd'), desc, DialogModes.NO );  
}; 
// Run it.
loadColorSettings( FileName );

alert("Loaded 'sRGB.csf' into WORKING Color Settings...")

// =======================================================
// Folder containing PNG files...
if(os == "WINDOWS")
	var PNG_FOLDER = ("D:\\rbobo\\Dropbox\\richbobo\\NUKE\\Scripts\\Save_PSD_From_Nuke_TESTING\\img\\PNG");
	//alert(PNG_FOLDER)
else if (os == "MAC")
	//var PNG_FOLDER = ("/Users/richbobo/Dropbox/richbobo/NUKE/Scripts/Save_PSD_From_Nuke_TESTING/img/PNG");
	//alert(PNG_FOLDER)
	alert("Got here.")

// =======================================================
function png_loop (PNG_FOLDER){
	png_files = (Folder(PNG_FOLDER)).getFiles("*.png")
	return png_files
	}

// =======================================================
function single_psd (PNG_FOLDER){
	// user settings
	var prefs = new Object();
	prefs.sourceFolder         = PNG_FOLDER;  // runs
	prefs.removeFileExtensions = true; // remove filename extensions for imported layers (default: true)
	prefs.savePrompt           = false; // display save prompt after import is complete (default: false)
	prefs.closeAfterSave       = false; // close import document after saving (default: false)

	// get a list of files
	var fileArray = png_loop(PNG_FOLDER)
	//alert ("fileArray -->" + fileArray)
	
	// assemble pngs to psd
	saveName = png_to_psd(PNG_FOLDER,fileArray,prefs)
    //alert("saveName -->" + saveName)
	
	return saveName
	}

// =======================================================
function png_to_psd (PNG_FOLDER,fileArray,prefs){
	// Check if there are any pngs... if not, exit.
	if (fileArray.length == 0) {return 0}
	
	// Create a new document...
	var newDoc = documents.add(300, 300, 72, 'Imported Layers', NewDocumentMode.RGB, DocumentFill.TRANSPARENT, 1);
	var newLayer = newDoc.activeLayer;
	var pnglayers = new Array (); // Array for holding layer info...

	// Loop through all files in the source folder...
	for (var i = 0; i < fileArray.length; i++) {
		// open document
		var doc = open(fileArray[i]);

		// Get document name and remove file extension...
		var name = doc.name;
		if (prefs.removeFileExtensions) {
			name = name.replace(/(?:\.[^.]*$|$)/, '');
		}

		// Convert to RGB; convert to 8-bpc; merge visible...
		doc.changeMode(ChangeMode.RGB);
		doc.bitsPerChannel = BitsPerChannelType.EIGHT;
		doc.artLayers.add();
		doc.mergeVisibleLayers();

		// Rename layer; duplicate to new document...
		var layer = doc.activeLayer;
		layer.name = name;
		layer.duplicate(newDoc, ElementPlacement.PLACEATBEGINNING);
		
		// Add layer name to  list...
		var namesplit = (name.split("_")); // Seperate file name into an array...
		pnglayers.push(namesplit.join("_")); // Add layer name to pnglayers...

		// Close imported document...
		doc.close(SaveOptions.DONOTSAVECHANGES);
	}	

	// Reveal and trim to fit all layers...
	newDoc.revealAll();
	newDoc.trim(TrimType.TRANSPARENT, true, true, true, true);
	
	var PixCount = newDoc.width.as('px') * newDoc.height.as('px');
	var layers = activeDocument.artLayers;
	var groups = activeDocument.layerSets;

	if (layers.length > 1){layers.getByName("Layer 1").remove()};
	
	// Save file and close...
	saveName = new File(PNG_FOLDER + ".psd");
	newDoc.saveAs(saveName, new PhotoshopSaveOptions() );
	newDoc.close();

	return saveName
	}

// =======================================================
function main(){
    single_psd(PNG_FOLDER)
	return 0
	}

// Call main function...
main()