#target photoshop

// script to change all layer names from something like "layer.RGBA" to just "layer
// if you use ProEXR, you know what I mean

function recursive_apply(layerObject)
{
	if(layerObject.typename == "LayerSet")
	{
		var theLayers = layerObject.layers;
		
		for(var i=0; i < theLayers.length; i++)
		{
			var theLayer = theLayers[i];
			
			recursive_apply(theLayer);
		}
	}
	else
	{
		var searchStrings = new Array;
		
		searchStrings[0] = "(.*)\\.RGB";
		searchStrings[1] = "(.*)\\.RGBA";
		searchStrings[2] = "(.*)\\.\\[red\\]\\[green\\]\\[blue\\]";
		searchStrings[3] = "(.*)\\.\\[red\\]\\[green\\]\\[blue\\]\\[alpha\\]";
		
		var layerName = layerObject.name;
		
		var didReplace = false;
		
		for(var i = 0; i < searchStrings.length && !didReplace; i++)
		{
			var exp = new RegExp(searchStrings[i], 'gi');
			
			var foundString = layerName.match(exp);
			
			if(foundString != undefined)
			{
				layerObject.name = foundString[0].replace(exp, '$1');
				
				didReplace = true;
			}
		}
	}
}

if(app.documents.length)
{
	var theDoc = app.activeDocument;
	
	var theLayers = theDoc.layers;
	
	for(var i = 0; i < theLayers.length; i++)
	{
		var theLayer = theLayers[i];
		
		recursive_apply(theLayer);
	}
}
else
	alert("No document open");
