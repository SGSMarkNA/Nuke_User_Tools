// enable double-clicking from Mac Finder or Windows Explorer
// this command only works in Photoshop CS2 and higher
#target photoshop
// bring application forward for double-click events
app.bringToFront();
// Set Adobe Photoshop CS4 to use pixels and display no dialogs
app.preferences.rulerUnits = Units.PIXELS
app.preferences.typeUnits = TypeUnits.PIXELS
app.displayDialogs = DialogModes.NO
// Hide Photoshop UI...
////app.Visible = false;

// get path from script
////var newPath = arguments[1];
var newPath = ("D:\\rbobo\\Dropbox\\richbobo\\NUKE\\Scripts\\Save_PSD_From_Nuke_TESTING\\img\\PSD");

// Folder containing TIF files...
var PNG_FOLDER = ("D:\\rbobo\\Dropbox\\richbobo\\NUKE\\Scripts\\Save_PSD_From_Nuke_TESTING\\img\\PNG");
alert(PNG_FOLDER)

function png_loop (PNG_FOLDER){
	png_files = (Folder(PNG_FOLDER)).getFiles("*.png")
	return png_files
	}

function single_psd (PNG_FOLDER){
	// user settings
	var prefs = new Object();
	prefs.sourceFolder         = PNG_FOLDER;  // runs
	prefs.removeFileExtensions = true; // remove filename extensions for imported layers (default: true)
	prefs.savePrompt           = false; // display save prompt after import is complete (default: false)
	prefs.closeAfterSave       = false; // close import document after saving (default: false)

	// get a list of files
	var fileArray = png_loop(PNG_FOLDER)
	alert ("fileArray -->" + fileArray)
	
	//assemble tiffs to psd
	saveName = png_to_psd(PNG_FOLDER,fileArray,prefs)
    alert("saveName -->" + saveName)
	
	return saveName
	}

function png_to_psd (PNG_FOLDER,fileArray,prefs){
	// check if there are any pngs... if not exit
	if (fileArray.length == 0) {return 0}
	
	// create a new document
	var newDoc = documents.add(300, 300, 72, 'Imported Layers', NewDocumentMode.RGB, DocumentFill.TRANSPARENT, 1);
	var newLayer = newDoc.activeLayer;
	var dmflayers = new Array (); //array for holding layer info
    //var exrName = exr_name(PNG_FOLDER);

	// loop through all files in the source folder
	for (var i = 0; i < fileArray.length; i++) {
		// open document
		var doc = open(fileArray[i]);

		// get document name (and remove file extension)
		var name = doc.name;
		if (prefs.removeFileExtensions) {
			name = name.replace(/(?:\.[^.]*$|$)/, '');
		}

		// convert to RGB; convert to 8-bpc; merge visible
		doc.changeMode(ChangeMode.RGB);
		doc.bitsPerChannel = BitsPerChannelType.EIGHT;
		doc.artLayers.add();
		doc.mergeVisibleLayers();

		// rename layer; duplicate to new document
		var layer = doc.activeLayer;
		layer.name = name;
		layer.duplicate(newDoc, ElementPlacement.PLACEATBEGINNING);
		
		//add layer name to  list
		var namesplit = (name.split("_")); // seperate file name into an array
		dmflayers.push(namesplit.join("_")); // add layer name to dmf layers
		

		// close imported document
		doc.close(SaveOptions.DONOTSAVECHANGES);
	}	

	// reveal and trim to fit all layers
	newDoc.revealAll();
	newDoc.trim(TrimType.TRANSPARENT, true, true, true, true);
	
	// make group 
    gGroup =  newDoc.layerSets.add();
    groupName = (dmflayers[0].split("_"));
    groupName = groupName.slice(0, (groupName.length -1));
    groupName = groupName.join("_");
    gGroup.name = groupName;
	
	var PixCount =newDoc.width.as('px') * newDoc.height.as('px');
	var layers = activeDocument.artLayers;
	var groups =activeDocument.layerSets;
	
 	// turn off all layers
 	for (var c = layers.length-1; 0 <= c;c--){
 		layers[c].visible = false
		}

	//set variable for if the rgb layer was deleted
	rgbLayer = true

	//move layers into group if it is not black
	gGroup.visible = false
	for (var c = layers.length-1; 0 <= c;c--){
		var currentLayer = layers[c];
		// check if layer is all black
		newDoc.activeLayer = currentLayer
		currentLayer.visible = true
		// add up all the color channels..  to compare against black
		var colorChannels = (newDoc.channels["Red"].histogram[0] + newDoc.channels["Green"].histogram[0] + newDoc.channels["Blue"].histogram[0])
		if (colorChannels != (PixCount *3))
			{
				currentLayer.visible = false;
				currentLayer.moveToEnd(gGroup);
			}
				else
					{
						if (currentLayer.name == (gGroup.name+"_rgb")){rgbLayer = false}
						currentLayer.remove()
					}
				}
					
	//remove empyty layer if groups length is greater than 1, with 1 being Layer1
	if (gGroup.layers.length > 1){gGroup.layers.getByName("Layer 1").remove()};
	
	//turn on group
	gGroup.visible = true
	
	// set active layer to the group or else the psd merge will fail
	newDoc.activeLayer = gGroup
	
	//save file and close
	saveName = new File(PNG_FOLDER + ".psd");
	newDoc.saveAs(saveName, new PhotoshopSaveOptions() );
	newDoc.close();

	return saveName
	}

function main(){
	// find all the render folers
	//folderArray = list_folder (locate())
	//location = newPath
	//alert(location)
	//create single psd
	//single_psd(location)
    single_psd(PNG_FOLDER)

	return 0
	}
//Call main function
main()