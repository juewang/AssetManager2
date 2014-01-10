'''
Created on Jan 4, 2014

@author: juewa_000
'''

import pymel.core as _pmCore
import Database as _Database
import os as _os
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

def saveScene(sceneName, directory, description, category):
    fullScenePath = _os.path.join(directory, sceneName+'.mb')
    _pmCore.renameFile(fullScenePath)
    _pmCore.saveFile()
    userName = _os.environ.get('AM_USERNAME')
    _, _, thumbNailPath = _Database.addFile(fullScenePath, sceneName, description, category, userName)
    _makeThumbnail(128, 128, thumbNailPath)
    fileID = _Database.getIDByFilePath(fullScenePath)
    return fileID[0]
   
def _makeThumbnail(width, height, path):
    view = OpenMayaUI.M3dView.active3dView()
    #read the color buffer from the view, and save the MImage to disk
    image = OpenMaya.MImage()
    view.readColorBuffer(image, True)
    image.resize(width, height, True)
    image.writeToFile(path, 'bmp')
    
def saveSceneForVersion():
    filePath = _pmCore.sceneName()
    fileID = _Database.getIDByFilePath(filePath)[0]
    _pmCore.saveFile()
    versionNum, _, thumbnailPath = _Database.addVersion(filePath, _os.environ.get('AM_USERNAME'))
    _makeThumbnail(128, 128, thumbnailPath)
    return fileID, versionNum, thumbnailPath
