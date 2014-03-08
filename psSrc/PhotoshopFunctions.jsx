#target photoshop
#include "Utils.jsx"

function saveCurrentAs(filePath, width, height)
{
    var ext = getExtension(filePath).toLocaleLowerCase();
    $.writeln(ext);
    var saveOpt;
    switch(ext){
        case "tga":
            saveOpt = new TargaSaveOptions();
            saveOpt.alphaChannels=true;
            break;
        case "psd":
            saveOpt = new PhotoshopSaveOptions();
            saveOpt.alphaChannels = true;
            saveOpt.layers = true;
            break;
        case "png":
            saveOpt = new PNGSaveOptions();
            break;
        // may have more options depend on need
        default:
            saveOpt = undefined;
    }
    if(saveOpt == undefined)
        alert("File format {0} is not supported yet.".format(ext));
    else
    { 
        var file = new File(filePath)
        app.activeDocument.saveAs(file, saveOpt, true, Extension.LOWERCASE);
        if ((width != undefined)&&(height != undefined))
        {
            var currentDocument = app.activeDocument;
            var resizeFile = new File(filePath);
            app.open(resizeFile);
            var currentUnit = app.preferences.rulerUnits;
            app.preferences.rulerUnits = Units.PIXELS;
            app.activeDocument.resizeImage (width, height, app.activeDocument.resolution);
            app.activeDocument.save();
            app.activeDocument.close();
            app.activeDocument = currentDocument;
            app.preferences.rulerUnits = currentUnit;
        }
    }
}

