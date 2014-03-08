#include "Utils.jsx" // or //@include "Utils.jsx" for backwards compatibility with CS.
#target photoshop

function createWindow()
{
    var myWindow = new Window("dialog");
    var myMessage = myWindow.add("statictext");
    myMessage.text = "Hello, world!";
    var myPanel = myWindow.add("panel");
    var myList = myPanel.add("listbox");
    var imageList = ["C:/Users/juewa_000/Google Drive/AssetManager/backup/1/0_tmp.png", "C:/Users/juewa_000/Google Drive/AssetManager/backup/14/0.png"];
    var descList = ["test1", "test2"];
    for (var i=0; i<descList.length; i++)
    {
        var item = myList.add("item", descList[i]);
        try{
        myList.items[i].image = File(imageList[i]);}
        catch(err)
        {
            alert("Failed to open thumbnail file {0}".format(imageList[i]));
            }
     }
    myPanel.add("button", undefined, "OK");
    myPanel.add("button", undefined, "Cancel");
    if(myWindow.show() == 1)
    {
        $.writeln ("OK clicked");
     }
    else
    {
        $.writeln ("Cancel clicked");
     }
    
}

//createWindow()

