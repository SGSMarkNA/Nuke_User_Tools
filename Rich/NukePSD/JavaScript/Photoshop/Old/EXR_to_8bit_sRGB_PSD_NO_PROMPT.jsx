// Path to server...
var libPath = $.getenv("AW_COMMON_UTILITIES");

// Path to Color Settings...
var ColorSettingsPath = (libPath + "/Photoshop/AW_Nuke_Tools/Color_Settings")

var ACES_SETTINGS = (ColorSettingsPath + "/ACES-CG-Linear_NO_PROFILE_PROMPTS.csf" )
var sRGB_SETTINGS = (ColorSettingsPath + "/sRGB.csf" )

// enable double-clicking from Mac Finder or Windows Explorer
// this command only works in Photoshop CS2 and higher
///////////////#target photoshop
// bring application forward for double-click events
app.bringToFront();
// Set Adobe Photoshop CS4 to use pixels and display no dialogs
//////////////app.preferences.rulerUnits = Units.PIXELS
//////////////app.preferences.typeUnits = TypeUnits.PIXELS


// =======================================================
// Loads "ACES-CG-Linear" colorSettings that the user has saved...
// Test for the os we're on...
// =======================================================
os = $.os.toLowerCase().indexOf('mac') >= 0 ? "MAC": "WINDOWS";
//alert (os)
if(os == "WINDOWS")
    var FileName = new File (ACES_SETTINGS);
    // Apparently MacOS doesn't support UNC pathnames, so the volume has to be mounted first and accessed via the /Volumes mount directory...
else if (os == "MAC")
	var FileName = new File ("/Volumes/library/Scripts/Photoshop_Scripts/Color_Settings/ACES-CG-Linear_NO_PROFILE_PROMPTS.csf");

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

////
////alert("Loaded 'ACES-CG-Linear_NO_PROFILE_PROMPTS' into WORKING Color Settings...")


///////////////////////////////////////////////////////////
// INPUT CONVERSION STARTS HERE...
///////////////////////////////////////////////////////////


////
////alert("Select an EXR file to load...")
// =======================================================
// Opens file browser...
// =======================================================
var myFile = File.openDialog("Selection prompt");
if(myFile != null) app.open(myFile);


// =======================================================
var idassignProfile = stringIDToTypeID( "assignProfile" );
    var desc37 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref5 = new ActionReference();
        var idDcmn = charIDToTypeID( "Dcmn" );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref5.putEnumerated( idDcmn, idOrdn, idTrgt );
    desc37.putReference( idnull, ref5 );
    var idprofile = stringIDToTypeID( "profile" );
    desc37.putString( idprofile, """sRGB IEC61966-2.1""" );
executeAction( idassignProfile, desc37, DialogModes.NO );


////
////alert("Assigned sRGB ICC Color Profile.")


// =======================================================
// Convert to 16 bit - No Merge...
// =======================================================
var idCnvM = charIDToTypeID( "CnvM" );
    var desc2 = new ActionDescriptor();
    var idDpth = charIDToTypeID( "Dpth" );
    desc2.putInteger( idDpth, 16 );
    var idMrge = charIDToTypeID( "Mrge" );
    desc2.putBoolean( idMrge, false );
executeAction( idCnvM, desc2, DialogModes.NO );


// =======================================================
// Returns active document bits perchannel...
// =======================================================
////alert(activeDocument.bitsPerChannel)



///////////////////////////////////////////////////////////
// ...DO PHOTOSHOP WORK HERE, IF NECESSARY...
///////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////
// OUTPUT CONVERSION STARTS HERE...
///////////////////////////////////////////////////////////


// =======================================================
// Convert to sRGB IEC61966-2.1 profile...
// =======================================================
var idconvertToProfile = stringIDToTypeID( "convertToProfile" );
    var desc3 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref1 = new ActionReference();
        var idDcmn = charIDToTypeID( "Dcmn" );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref1.putEnumerated( idDcmn, idOrdn, idTrgt );
    desc3.putReference( idnull, ref1 );
    var idT = charIDToTypeID( "T   " );
    desc3.putString( idT, """sRGB IEC61966-2.1""" );
    var idInte = charIDToTypeID( "Inte" );
    var idInte = charIDToTypeID( "Inte" );
    var idClrm = charIDToTypeID( "Clrm" );
    desc3.putEnumerated( idInte, idInte, idClrm );
    var idMpBl = charIDToTypeID( "MpBl" );
    desc3.putBoolean( idMpBl, true );
    var idFltt = charIDToTypeID( "Fltt" );
    desc3.putBoolean( idFltt, false );
    var idsdwM = charIDToTypeID( "sdwM" );
    desc3.putInteger( idsdwM, 2 );
executeAction( idconvertToProfile, desc3, DialogModes.NO );


////
////alert("Converted document to sRGB ICC color profile.")


// =======================================================
// Script from Brendan Bolles at fnord Software, maker of the ProEXR plugin,
// to change all layer names from something like "layer.RGBA" to just "layer"...
// Quote from Brendan, "if you use ProEXR, you know what I mean".
// =======================================================
function recursive_apply(layerObject) {
	if(layerObject.typename == "LayerSet") {
		var theLayers = layerObject.layers;
		for(var i=0; i < theLayers.length; i++) {
			var theLayer = theLayers[i];
			recursive_apply(theLayer);
		}
	}
	else {
		var searchStrings = new Array;
		searchStrings[0] = "(.*)\\.RGB";
		searchStrings[1] = "(.*)\\.RGBA";
		searchStrings[2] = "(.*)\\.\\[red\\]\\[green\\]\\[blue\\]";
		searchStrings[3] = "(.*)\\.\\[red\\]\\[green\\]\\[blue\\]\\[alpha\\]";
		var layerName = layerObject.name;
		var didReplace = false;
		for(var i = 0; i < searchStrings.length && !didReplace; i++) {
			var exp = new RegExp(searchStrings[i], 'gi');
			var foundString = layerName.match(exp);
			if(foundString != undefined) {
				layerObject.name = foundString[0].replace(exp, '$1');
				didReplace = true;
			}
		}
	}
}
if(app.documents.length) {
	var theDoc = app.activeDocument;
	var theLayers = theDoc.layers;
	for(var i = 0; i < theLayers.length; i++) {
		var theLayer = theLayers[i];
		recursive_apply(theLayer);
	}
}
else
	alert("No document open");


// =======================================================
// Convert to 8 bits...
// =======================================================
var idCnvM = charIDToTypeID( "CnvM" );
    var desc7 = new ActionDescriptor();
    var idDpth = charIDToTypeID( "Dpth" );
    desc7.putInteger( idDpth, 8 );
    var idMrge = charIDToTypeID( "Mrge" );
    desc7.putBoolean( idMrge, false );
executeAction( idCnvM, desc7, DialogModes.NO );

// =======================================================
// Returns active document bits perchannel...
// =======================================================
////alert(activeDocument.bitsPerChannel)



// =======================================================
// USER DOES A SAVE AS HERE... OR Photoshop will prompt to save after the Close All...
// =======================================================
// SIMPLE SAVE...
//executeAction( charIDToTypeID( "save" ), undefined, DialogModes.ALL );

////
//alert("Document saved.")


var doc = app.activeDocument;
var docName = doc.name;
docName = docName.match(/(.*)(\.[^\.]+)/) ? docName = docName.match(/(.*)(\.[^\.]+)/):docName = [docName, docName];
var suffix = '_FULL';
var saveName = new File(decodeURI(doc.path)+'/'+docName[1]+suffix+'.psd');

function saveAsPSD(Name) {
    var psd_Opt = new PhotoshopSaveOptions();
    psd_Opt.layers = true; // Preserve layers.
    psd_Opt.embedColorProfile = true; // Preserve color profile.
    app.activeDocument.saveAs(Name, psd_Opt, true);
}

saveAsPSD(saveName);


// =======================================================
// Close All documents without saving changes...
// =======================================================
function closeAllDocuments() {
	while (documents.length > 0) {
		activeDocument.close(SaveOptions.DONOTSAVECHANGES);
	}
}
// Run it...
closeAllDocuments();
////
////alert("All docs closed.")

// =======================================================
// Load "sRGB" colorSettings or whatever the typical working space that has been saved by the user...
// =======================================================
// Test for the os we're on...
os = $.os.toLowerCase().indexOf('mac') >= 0 ? "MAC": "WINDOWS";
//alert (os)
if(os == "WINDOWS")
    var FileName = new File(sRGB_SETTINGS);
    // Apparently MacOS doesn't support UNC pathnames, so the volume has to be mounted first and accessed via the /Volumes mount directory...
else if (os == "MAC")
	var FileName = new File ("/Volumes/library/Scripts/Photoshop_Scripts/Color_Settings/sRGB.csf");

// Run it.
loadColorSettings( FileName );

////
////alert("Loaded 'sRGB' color settings into WORKING Color Settings...")


// Reopen the PSD file we just saved
app.open( new File( saveName ) );
// Prompt user for possible layer reordering...
alert("PLEASE NOTE --->>> REORDER LAYERS, IF NECESSARY, and RE-SAVE!!")

////
//alert("Done.")