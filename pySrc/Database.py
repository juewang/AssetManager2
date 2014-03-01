'''
Created on Dec 8, 2013

@author: juewa_000
'''
import datetime as _datetime
import MySQLdb as _MySQLdb
import os as _os
import shutil as _shutil
import warnings as _warnings


_USERNAME = _os.environ['AM_USERNAME']
_PASSWORD = _os.environ['AM_PASSWORD']
_DBNAME = _os.environ['AM_DBNAME']
_IP = _os.environ['AM_SERVER_IP']

_FILE_TYPE_MAPPING = {"mb": "Maya",
                      "ma": "Maya",
                      "tga": "Photoshop",
                      "psd": "Photoshop",
                      }

_BACK_UP_DIR = _os.environ['AM_BACK_UP_DIR']
    
class _AssetTable(object):
    tableName = "Asset"
    
    ID = "ID"
    sceneName = "SceneName"
    filePath = "FilePath"
    versionID = "VersionID"
    description = "Description"
    category = "Category"
    fileType = "FileType"
    
    @staticmethod
    def create():
        _execute("DROP TABLE IF EXISTS {0}".format(_AssetTable.tableName))
        _execute("CREATE TABLE `{0}`({1} INT PRIMARY KEY AUTO_INCREMENT, {2} VARCHAR(255), {3} VARCHAR(255), {4} INT, {5} VARCHAR(1023), {6} INT, {7} VARCHAR(50));".format(
                _AssetTable.tableName,
                _AssetTable.ID,
                _AssetTable.sceneName,
                _AssetTable.filePath,
                _AssetTable.versionID,
                _AssetTable.description,
                _AssetTable.category,
                _AssetTable.fileType,
                ))
        
class _VersionTable(object):
    tableName = "Version"
    assetID = "AssetID"
    versionNumber = "VersionNumber"
    versionFile = "VersionFile"
    thumbnailFile = "ThumbnailFile"
    userName = "UserName"
    
    @staticmethod
    def create():
        _execute("DROP TABLE IF EXISTS {0}".format(_VersionTable.tableName))
        _execute("CREATE TABLE `{0}`({1} INT, {2} INT, {3} VARCHAR(255), {4} VARCHAR(255), {5} VARCHAR(255))".format(
                 _VersionTable.tableName,
                 _VersionTable.assetID,
                 _VersionTable.versionNumber,
                 _VersionTable.versionFile,
                 _VersionTable.thumbnailFile,
                 _VersionTable.userName))
                                                                                                            
class _CommentTable(object):
    tableName = "Comment"
    assetID = "AssetID"
    versionNumber = "VersionNumber"
    commentor = "Commenter"
    date = "Date"
    content = "Content"
    
    @staticmethod
    def create():
        _execute("DROP TABLE IF EXISTS {0}".format(_CommentTable.tableName))
        _execute("CREATE TABLE `{0}`({1} INT, {2} INT, {3} VARCHAR(255), {4} DATE, {5} VARCHAR(1023))".format(
                                                                     _CommentTable.tableName,
                                                                     _CommentTable.assetID,
                                                                     _CommentTable.versionNumber,
                                                                     _CommentTable.commentor,
                                                                     _CommentTable.date,
                                                                     _CommentTable.content))
    
class _UserTable(object):
    tableName = "EditUser"
    assetID = "AssetID"
    versionNumber = "VersionNumber"
    userName = "UserName"
    
    @staticmethod
    def create():
        _execute("DROP TABLE IF EXISTS {0}".format(_UserTable.tableName))
        _execute("CREATE TABLE `{0}`({1} INT, {2} INT, {3} VARCHAR(255))".format(
                                                                     _UserTable.tableName,
                                                                     _UserTable.assetID,
                                                                     _UserTable.versionNumber,
                                                                     _UserTable.userName))
        
class _CategoryTable(object):
    tableName = "Category"
    categoryID = "ID"
    categoryName = "CategoryName"
    @staticmethod
    def create():
        _execute("DROP TABLE IF EXISTS {0}".format(_CategoryTable.tableName))
        _execute("CREATE TABLE `{0}`({1} INT PRIMARY KEY AUTO_INCREMENT, {2} VARCHAR(255))".format(
                                                                                                   _CategoryTable.tableName,
                                                                                                   _CategoryTable.categoryID,
                                                                                                   _CategoryTable.categoryName,
                                                                                                   ))
        
    
def addFile(filePath, sceneName, description, category, userName):
    if not _os.path.exists(filePath):
        raise RuntimeError("File does not exist. {0}".format(filePath))
    
    filePath = _normalizePath(filePath)
    fileType = _getFileExt(filePath)
    # check if this scene already exists in the database
    if _execute('SELECT * FROM {5} WHERE `{1}`="{2}" AND `{3}`="{4}"'.format(_DBNAME, _AssetTable.filePath, filePath, _AssetTable.sceneName, sceneName, _AssetTable.tableName)):
        raise RuntimeError("Scene name {0} with file path {1} already exists.".format(sceneName, filePath))
    if fileType not in _FILE_TYPE_MAPPING:
        raise RuntimeError("File type does not exist, got {0}".format(fileType))
    
    categoryID = getCategoryID(category)
    
    valueMapping = ((_AssetTable.filePath, filePath), 
                    (_AssetTable.versionID, 0),
                    (_AssetTable.sceneName, sceneName),
                    (_AssetTable.description, description),
                    (_AssetTable.category, categoryID),
                    (_AssetTable.fileType, fileType))
    command = "INSERT {0} SET {1}".format(_AssetTable.tableName, ','.join(['`' + a + '`="' + str(b) + '"' for (a, b) in valueMapping]))
    _execute(command)
    return addVersion(filePath, userName)
    
def deleteFile(filePath):
    filePath = _normalizePath(filePath)
    fileID = getIDByFilePath(filePath)
    if not fileID:
        _warnings.warn('File {0} does not exist in database. Deletion skipped.'.format(filePath))
        return
    for tableName, entryID in ((_AssetTable.tableName, _AssetTable.ID),
                               (_VersionTable.tableName, _VersionTable.assetID),
                               (_CommentTable.tableName, _CommentTable.assetID),
                               ):
        _execute('DELETE FROM {table} WHERE `{ID}`="{fileID}"'.format(table=tableName, ID=entryID, fileID=fileID[0]))
    backupDir = _os.path.join(_BACK_UP_DIR, str(fileID[0]))
    _shutil.rmtree(backupDir)

def addVersion(filePath, userName):
    filePath = _normalizePath(filePath)
    ID = getIDByFilePath(filePath)[0]
    currentVersionList = _makeList(_execute('SELECT `{versionNum}` FROM {versionTable} WHERE `{assetID}`="{ID}"'.format(versionNum=_VersionTable.versionNumber, versionTable=_VersionTable.tableName,
                                                                                                             assetID=_VersionTable.assetID, ID=ID), fetchall=True), flatten=True)
    if not currentVersionList:
        versionID = 0
    else:
        versionID = max(currentVersionList) + 1
    
    versionPath = _copyFileToBackup(filePath, ID, versionID)
    thumbnailPath = getThumbnailPath(ID, versionID)
    
    valueMapping = ((_VersionTable.assetID, ID),
                    (_VersionTable.versionFile, _normalizePath(versionPath)),
                    (_VersionTable.versionNumber, versionID),
                    (_VersionTable.thumbnailFile, _normalizePath(thumbnailPath)),
                    (_VersionTable.userName, userName))
    _execute('INSERT {0} SET {1}'.format(_VersionTable.tableName, ','.join(['`' + a + '`="' + str(b) + '"' for (a, b) in valueMapping])))
    setCurrentVersion(ID, versionID)
    return versionID, versionPath, thumbnailPath

def deleteVersion(filePath, versionNumber):
    fileID = getIDByFilePath(_normalizePath(filePath))[0]
    if not fileID:
        _warnings.warn('File {0} does not exist in database. Deletion skipped.'.format(filePath))
        return
    if versionNumber not in getVersionList(fileID):
        _warnings.warn('Version {0} does not exist in database. Deletion skipped.'.format(versionNumber))
        return
    for tableName, ID, versionNum in ((_VersionTable.tableName, _VersionTable.assetID, _VersionTable.versionNumber),
                                      (_CommentTable.tableName, _CommentTable.assetID, _CommentTable.versionNumber),
                                      ):
        _execute('DELETE FROM {table} WHERE `{ID}`="{fileID}" and `{versionNum}`="{versionNumberValue}"'.format(table=tableName, ID=ID,
                                                                                                            fileID=fileID, versionNum=versionNum,
                                                                                                            versionNumberValue=versionNumber))
    ## TODO: delete local files and update version ID in asset table. 
    if getCurrentVersion(fileID) == versionNumber:
        # We have deleted this version.
        setCurrentVersion(fileID, versionNumber-1)
    
def addComment(ID, versionNumber, comment, user):
    valueMapping = ((_CommentTable.assetID, ID),
                    (_CommentTable.versionNumber, versionNumber),
                    (_CommentTable.content, comment),
                    (_CommentTable.commentor, user),
                    (_CommentTable.date, _datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )
    _execute('INSERT {0} SET {1}'.format(_CommentTable.tableName, ','.join(['`' + a + '`="' + str(b) + '"' for (a, b) in valueMapping])))
    
def deleteComment(comment):
    _execute('DELETE FROM {table} WHERE `{comment}`="{content}"'.format(table=_CommentTable.tableName, comment=_CommentTable.content, content=comment))
    
def deleteCommentByUser(userName):
    _execute('DELETE FROM {table} WHERE `{user}`="{userName}"'.format(table=_CommentTable.tableName, user=_CommentTable.commentor, userName=userName))
    
def deleteCommentByDate(date):
    pass

def openByUser(ID, versionNumber):
    pass

def getIDByFilePath(filePath):
    filePath = _normalizePath(filePath)
    result = _execute('SELECT `{ID}` FROM {tableName} WHERE `{filePathColumn}` = "{filePath}"'.format(ID=_AssetTable.ID, tableName=_AssetTable.tableName, filePathColumn=_AssetTable.filePath, filePath=filePath),
                      fetchall=True)
    if len(result) > 1:
        raise RuntimeError("Found more than one item with file path {0}, they are {1}.".format(filePath, result))
    elif result:
        return result[0]
    
def getFilePath(fileID):
    result = getFileInfo(fileID)
    return _denormalizePath(result[2])
    
def getCategoryList():
    return _makeList(_execute('SELECT `{category}` FROM {tableName}'.format(category=_CategoryTable.categoryName, tableName=_CategoryTable.tableName), fetchall=True), flatten=True)

def getCategoryID(category):
    if category not in getCategoryList():
        raise RuntimeError("Failed to find category {0}.".format(category))
    return int(_execute('SELECT `{categoryID}` FROM {tableName} WHERE `{categoryName}`="{category}"'.format(categoryID=_CategoryTable.categoryID, 
                                                                                                            tableName=_CategoryTable.tableName, 
                                                                                                            categoryName=_CategoryTable.categoryName, 
                                                                                                            category=category))[0])

def addCategory(newCategory):
    if newCategory in getCategoryList():
        raise RuntimeError("Can not add existing category {0}.".format(newCategory))
    _execute('INSERT {0} SET {1}'.format(_CategoryTable.tableName, '`' + _CategoryTable.categoryName + '`="' + newCategory + '"'))
    
def renameCategory(oldName, newName):
    if newName in getCategoryList():
        raise RuntimeError("Can not rename to existing category {0}.".format(newName))
    categoryID = getCategoryID(oldName)
    _execute('UPDATE {tableName} SET `{category}`="{newName}" WHERE `{ID}`="{categoryID}"'.format(tableName=_CategoryTable.tableName, 
                                                                                                  category=_CategoryTable.categoryName, 
                                                                                                  newName=newName,
                                                                                                  ID=_CategoryTable.categoryID, 
                                                                                                  categoryID=categoryID))

def deleteCategory(category):
    _execute('DELETE FROM {table} WHERE `{categoryName}`="{category}"'.format(table=_CategoryTable.tableName, categoryName=_CategoryTable.categoryName, category=category))
    
def setFilename(fileID, newSceneName):
    _execute('UPDATE {tableName} SET `{sceneName}`="{newSceneName}" WHERE `{ID}`="{fileID}"'.format(tableName=_AssetTable.tableName, sceneName=_AssetTable.sceneName,
                                                                                                    newSceneName=newSceneName, ID=_AssetTable.ID, fileID=fileID))
    
def setFilePath(fileID, newFilePath):
    newFilePath = _normalizePath(newFilePath)
    _execute('UPDATE {tableName} SET `{filePath}`="{newFilePath}" WHERE `{ID}`="{fileID}"'.format(tableName=_AssetTable.tableName, filePath=_AssetTable.filePath,
                                                                                                    newFilePath=newFilePath, ID=_AssetTable.ID, fileID=fileID))
def getAssetUnderCategory(category):
    categoryID = getCategoryID(category)
    return _execute('SELECT * FROM {tableName} WHERE `{category}`="{categoryID}"'.format(tableName=_AssetTable.tableName, category=_AssetTable.category, categoryID=categoryID), fetchall=True)
    
def setFileCategory(fileID, newCategory):
    categoryID = getCategoryID(newCategory)
    _execute('UPDATE {tableName} SET `{category}`="{categoryID}" WHERE `{ID}`="{fileID}"'.format(tableName=_AssetTable.tableName, category=_AssetTable.category, categoryID=categoryID, 
                                                                                                  ID=_AssetTable.ID, fileID=fileID))

def getFileCategory(fileID):
    categoryID = _execute('SELECT `{category}` FROM {tableName} WHERE `{ID}`="{fileID}"'.format(category=_AssetTable.category, tableName=_AssetTable.tableName,
                                                                                        ID=_AssetTable.ID, fileID=fileID))
    return _execute('SELECT `{categoryName}` FROM {tableName} WHERE `{ID}`="{categoryID}"'.format(categoryName=_CategoryTable.categoryName,
                                                                                                  tableName=_CategoryTable.tableName,
                                                                                                  ID=_CategoryTable.categoryID,
                                                                                                  categoryID=categoryID[0]))[0]
    
def getCurrentVersion(fileID):
    return int(_execute('SELECT `{version}` FROM {tableName} WHERE `{ID}`="{fileID}"'.format(version=_AssetTable.versionID, tableName=_AssetTable.tableName,
                                                                                         ID=_AssetTable.ID, fileID=fileID))[0])

def setCurrentVersion(fileID, versionNumber):
    _execute('UPDATE {tableName} SET `{versionNum}`="{versionNumber}" WHERE `{ID}`="{fileID}"'.format(tableName=_AssetTable.tableName, versionNum=_AssetTable.versionID,
                                                                                                      versionNumber=versionNumber, ID=_AssetTable.ID,
                                                                                                      fileID=fileID))

def getVersionList(fileID):
    result = _execute('SELECT `{versionNumber}` FROM {tableName} WHERE `{assetID}`="{assetIDValue}"'.format(versionNumber=_VersionTable.versionNumber, 
                                                                                                            tableName=_VersionTable.tableName, 
                                                                                                            assetID=_VersionTable.assetID,
                                                                                                            assetIDValue=fileID), fetchall=True)
    return map(int, _makeList(result, flatten=True))

def getVersionFile(fileID, versionNumber):
    result = _execute('SELECT `{versionPath}` FROM {tableName} WHERE `{ID}`="{fileID}" and `{versionNum}`="{versionNumber}"'.format(
                                                                                            versionPath=_VersionTable.versionFile, tableName=_VersionTable.tableName,
                                                                                            ID=_VersionTable.assetID, fileID=fileID,
                                                                                            versionNum=_VersionTable.versionNumber, versionNumber=versionNumber))
    return _denormalizePath(result[0])

def getVersionInfo(fileID, versionNumber):
    result = _execute('SELECT * FROM {tableName} WHERE `{assetID}`="{assetIDValue}" and `{versionNum}`="{versionNumber}"'.format(tableName=_VersionTable.tableName, 
                                                                                            assetID=_VersionTable.assetID,
                                                                                            assetIDValue=fileID,
                                                                                            versionNum=_VersionTable.versionNumber,
                                                                                            versionNumber=versionNumber))
    return result

def getFileInfo(fileID):
    result = list(_execute('SELECT * FROM {tableName} WHERE `{ID}`="{fileID}"'.format(tableName=_AssetTable.tableName, ID=_AssetTable.ID,
                                                                               fileID=fileID)))
    result[5] = getFileCategory(result[0])
    return result

def setFileDescription(fileID, description):
    _execute('UPDATE {tableName} SET `{desc}`="{description}" WHERE `{ID}`="{fileID}"'.format(tableName=_AssetTable.tableName, desc=_AssetTable.description,
                                                                                              description=description, ID=_AssetTable.ID,
                                                                                              fileID=fileID))
    
def getCommentList(fileID):
    result = _execute('SELECT `{comment}` FROM {tableName} WHERE `{ID}`="{fileID}"'.format(comment=_CommentTable.content, tableName=_CommentTable.tableName,
                                                                                  ID=_CommentTable.assetID, fileID=fileID), fetchall=True)
    return _makeList(result, flatten=True)

def getCommentListByVersion(fileID, versionNumber):
    return _execute('SELECT * FROM {tableName} WHERE `{ID}`="{fileID}" AND `{versionNum}`="{versionNumber}"'.format(
                                                                                tableName=_CommentTable.tableName,
                                                                                ID=_CommentTable.assetID, fileID=fileID,
                                                                                versionNum=_CommentTable.versionNumber, versionNumber=versionNumber), fetchall=True)

def editComment(fileID, versionNumber, userName, newComment):
    _execute('UPDATE `{tableName}` SET `{content}`="{comment}" WHERE `{ID}`="{fileID}" AND `{versionNum}`="{versionNumber}" AND `{user}`="{username}"'.format(
                                                                                tableName=_CommentTable.tableName, content=_CommentTable.content,
                                                                                comment=newComment, ID=_CommentTable.assetID,
                                                                                fileID=fileID, versionNum=_CommentTable.versionNumber,
                                                                                versionNumber=versionNumber, user=_CommentTable.commentor,
                                                                                username=userName))

def getCommentListByUser(fileID, commentor):
    result = _execute('SELECT `{comment}` FROM {tableName} WHERE `{user}`="{userName}"'.format(comment=_CommentTable.content, tableName=_CommentTable.tableName,
                                                                                  user=_CommentTable.commentor, userName=commentor))
    return _makeList(result, flatten=True)
    
def initalSetup():
    command = "SHOW DATABASES LIKE '{0}';".format(_DBNAME)
    result = _execute(command)
    if not result:
        _execute("CREATE DATABASE {0}".format(_DBNAME))
    _AssetTable.create()
    _VersionTable.create()
    _CommentTable.create()
    _UserTable.create()
    _CategoryTable.create()

def _execute(command, fetchall=False):
    conn = _MySQLdb.connect(_IP, _USERNAME, _PASSWORD, _DBNAME)
    with conn:
        c = conn.cursor()
        c.execute(command)
        
        if fetchall:
            result = c.fetchall()
        else:
            result = c.fetchone()
        return result
        
def _copyFileToBackup(filePath, fileID, fileVersion):
    backupDir = _os.path.join(_BACK_UP_DIR, str(fileID))
    backupFilePath = _os.path.join(backupDir, str(fileVersion) + '.' + _getFileExt(filePath))
    if not _os.path.exists(backupDir):
        _os.makedirs(backupDir)
    _shutil.copyfile(filePath, backupFilePath) 
    return backupFilePath

def getThumbnailPath(fileID, fileVersion):
    thumbnailExt = '.png'
    return _os.path.join(_BACK_UP_DIR, str(fileID), str(fileVersion) + thumbnailExt)
    
def _getFileExt(filePath):
    return filePath.rsplit('.')[-1]

def _normalizePath(filePath):
    filePath = filePath.replace('\\\\', '/')
    return filePath.replace('\\', '/')

def _denormalizePath(filePath):
    return filePath.replace('/', '\\\\')

def _makeList(item, flatten=False):
    if hasattr(item, "__iter__"):
        if not flatten:
            return item
        flattenList = []
        for i in item:
            if hasattr(i, "__iter__") and len(i) == 1:
                i = i[0]
            flattenList.append(i)
        return flattenList
    
    elif item == None:
        return []
    else:
        return [item]
        