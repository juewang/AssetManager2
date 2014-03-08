/* Convenient string format function */
String.prototype.format = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

function writeToFile(text, filePath){
    file = new File(filePath);
    file.encoding = "UTF-8";
    file.open("w");
    file.write(text);
    file.close();
}

function readFromFile(filePath){
    file = new File(filePath);
    if(file.exists != true)
    {
        alert("File {0} does not exist.".format(filePath));
        return null;
    }
    else
    {
        file.open("r");
        var content = file.read();
        file.close();
        return content;
    }
}

function getExtension(filePath){
    var index = filePath.lastIndexOf(".");
    var ext = "";
    if(index > -1)
    {
        ext = filePath.substr(index + 1);
     }
    return ext;
}