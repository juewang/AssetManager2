#target photoshop
#include "Utils.jsx"

// TODO: need to get a environment path for defining those files.
var tempPyFile = "C:/Users/juewa_000/Google Drive/AssetManager2/pySrc/pyscript.py";
var outputFile =  "C:/Users/juewa_000/Google Drive/AssetManager2/pySrc/output.json";
var errorFile = "C:/Users/juewa_000/Google Drive/AssetManager/backup/errorLog.txt";
var batchFilePath = "C:/Users/juewa_000/Google Drive/AssetManager2/pySrc/runPython.bat";


function pythonStrToCall()
{
    // Clear error file.
    var errorFileObj = File(errorFile);
    if(errorFileObj.exists == true)
    {
        writeToFile("", errorFile);
     }
    var callString = "import sys;";
    callString += "sys.path.append(r'C:/Users/juewa_000/eclipse/workspace/AssetManager2');";
    callString += "import Startup;";
    callString += "from pySrc.Database import *;";
    callString += "from pySrc.JavascriptUtil import *;"
    return callString;
}

function writeToFileWithCall(callString)
{
    writeToFile(callString, tempPyFile);
    var batchFile = File(batchFilePath);
    batchFile.execute();
    // Delay half second to read error file.
    $.sleep (500);
    var error = readFromFile(errorFile);
    if(error != null && error != "")
    {
        alert("Error occured during python call: {0}.".format(error));
        return null;
    }
    else
        // Delay half second to read the output file
        $.sleep (500);
        return readFromFile(outputFile);
 }

function addAssetToDatabase(assetName, assetDir, assetCategory, assetDesc)
{
    var callString = pythonStrToCall ();
    callString += "writeToJson(r'{0}', addFile, r'{1}', '{2}', '{3}', '{4}', '{5}')".format(outputFile, assetDir+"/"+assetName, assetName, assetDesc, assetCategory, "testuser");
    var output = writeToFileWithCall (callString);
    if(output == null)
    {
        alert("Error for adding asset, check errorLog file.")
    }
    else
    {
        var thumbnailPath = eval(output)[2];
        $.writeln(thumbnailPath);
        saveCurrentAs(thumbnailPath, 32, 32);
    }
 }

function getCategoryList()
{
    var callString = pythonStrToCall();
    callString += "writeToJson(r'{0}', getCategoryList)".format(outputFile, );
    var category = writeToFileWithCall (callString);
    if(category == null)
    {
        alert("Failed to get category list, check errorLog file.");
    }
    else
        return eval(category);
 }

//$.writeln($.getenv("%AM_USERNAME%"));