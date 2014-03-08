#target photoshop
#include "DatabaseConn.jsx"
#include "PhotoshopFunctions.jsx"

var addAssetWindow = new Window("dialog");
addAssetWindow.text = "Add New Asset";
//addAssetWindow.preferredSize = [350, ""];
addAssetWindow.margins = [3, 3, 3, 3];
addAssetWindow.alignChildren = "left";

var addAssetPanel = addAssetWindow.add("panel");
addAssetPanel.alignChildren = "left";
var descriptionLabel = addAssetPanel.add("statictext", undefined, "Add a new asset to Asset Manager.");

var assetNameGroup = addAssetPanel.add("group");
assetNameGroup.add("statictext", [0,0,70,18], "Asset Name: ");
var assetNameText = assetNameGroup.add("edittext");
assetNameText.characters = 30;
assetNameText.active = true;
var currentName = "";
try{currentName = app.activeDocument.name;}
catch(err){}
assetNameText.text = currentName;

var assetPathGroup = addAssetPanel.add("group");
assetPathGroup.add("statictext", [0,0,70,18], "Directory: ");
var assetPathText = assetPathGroup.add("edittext");
assetPathText.characters = 25;
var currentPath = "";
try{currentPath = app.activeDocument.path;}
catch(err){}
assetPathText.text = Folder(currentPath).fsName;

var f = File("C:/Users/juewa_000/Google Drive/AssetManager2/pySrc/ps/opened-folder.png");
var fileOpenButton = assetPathGroup.add("iconbutton", undefined, f, {style:"toolbutton"});
fileOpenButton.onClick = function() 
                                    {var directory = Folder.selectDialog ("Select a directory"); 
                                        if(directory!=null)
                                        {
                                            // get directory object and use .fsName to get full path to the folder.
                                            assetPathText.text = directory.fsName;
                                         }
                                      }

var assetCategoryGroup = addAssetPanel.add("group");
assetCategoryGroup.alignChildren = "left";
assetCategoryGroup.add("statictext", [0,0,70,18], "Category: ");
var categoryList = getCategoryList();
var assetCategoryDropDown = assetCategoryGroup.add("dropdownlist", undefined, categoryList);
assetCategoryDropDown.selection = 0;

addAssetPanel.add("statictext", undefined, "Description: ");
var descText = addAssetPanel.add("edittext", [0,0,300, 70], "", {multiline:true, scrolling:true});

var buttonGroup = addAssetPanel.add("group");
buttonGroup.alignChildren = "right";
var okButton = buttonGroup.add("button", undefined, "OK");
buttonGroup.add("button", undefined, "Cancel");
okButton.onClick = function(){var assetName = assetNameText.text; if(assetName == null) alert("Asset name can not be empty.");
                                              var assetPath = assetPathText.text; if(assetPath == null) alert("Asset path can not be empty.");
                                              var assetCategory = assetCategoryDropDown.selection.text; 
                                              var assetDesc = descText.text; if(assetDesc == null) alert("Asset description can not be empty.");
                                              addAssetWindow.close();
                                              saveCurrentAs(assetPath + "/" + assetName, null, null);
                                              addAssetToDatabase(assetName, assetPath, assetCategory, assetDesc);
                                              }

addAssetWindow.show();
