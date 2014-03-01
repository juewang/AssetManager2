'''
Created on Dec 20, 2013

@author: juewang
'''
import datetime as _datetime
import functools as _functools
import pymel.core as _pmCore
import Database as _Database
import os as _os
import MayaFunctions as _MayaFunctions

class _UiWidgetEnum(object):
    addAssetBtn = "addAssetBtn"
    updateAssetBtn = "updateAssetBtn"
    deleteAssetBtn = "deleteAssetBtn"
    addVersionBtn = "addVersionBtn"
    updateVersionBtn = "updateVersionBtn"
    deleteVersionBtn = "deleteVersionBtn"
    addCommentBtn = "addCommentBtn"
    assetBtnList = "assetBtnList"
    sceneNameTextField = "sceneNameTextField"
    filePathTextField = "filePathTextField"
    versionNumCombox = "versionNumCombox"
    versionNumText = "versionNumText"
    descriptionTextField = "descriptionTextField"
    categoryCombox = "categoryCombox"
    categoryMenuList = "categoryMenuList"
    manageCategoryBtn = "manageCategoryBtn"
    categoryTabLayout = "categoryTabLayout"
    
    
class AssetManagerDialog(object):
    _window = None
    _dockControl = None
    _winTitle = 'Asset Manager'
    _iconSize = 85
    def __init__(self):
        self._uiWidget = {}
        self._currentSelectedAsset = None
        self._versionComboMenu = {}
        self._highlightColor = (0.5, 0.5, 0.5)
        self._defaultColor = (0.27, 0.27, 0.27)
        self._buildupWindow()
        
    def _buildupWindow(self):
        if self._dockControl and self._dockControl.exists(self._winTitle):
            _pmCore.deleteUI(self._dockControl)
        self._window = _pmCore.window(title=self._winTitle)
        
        _pmCore.columnLayout()
        self._dockControl = _pmCore.dockControl(area='right', content=self._window, label=self._winTitle)
        tabLayout = _pmCore.tabLayout()
        self._uiWidget[_UiWidgetEnum.categoryTabLayout] = tabLayout
        for category in _Database.getCategoryList():
            childLayout = _pmCore.scrollLayout(width=300, height=300, childResizable=True)
            self._uiWidget[category] = _pmCore.gridLayout(numberOfColumns=3, cellHeight = self._iconSize, cellWidth=self._iconSize)
            for assetInfo in _Database.getAssetUnderCategory(category):
                id, sceneName, _, versionID, _, _, _ = assetInfo
                self._addAssetButton(id, sceneName, versionID)
            _pmCore.tabLayout(tabLayout, tabLabel=((childLayout, category),), edit=True)
            _pmCore.setParent('..')
            _pmCore.setParent('..')
            
        _pmCore.setParent('..')
        
        self._uiWidget[_UiWidgetEnum.sceneNameTextField] = _pmCore.textFieldGrp(label='Scene Name: ', width=300, columnAlign2=['left', 'left'], columnWidth2=[100, 195])
        self._uiWidget[_UiWidgetEnum.filePathTextField] = _pmCore.textFieldGrp(label='File Path: ', width=300, columnAlign2=['left', 'left'], columnWidth2=[100, 195])
        _pmCore.rowLayout(numberOfColumns=2)
        _pmCore.text(label="Current Version:", width=100, align='left')
        self._uiWidget[_UiWidgetEnum.versionNumText] = _pmCore.text(label="")
        _pmCore.setParent('..')
        self._uiWidget[_UiWidgetEnum.categoryCombox] = _pmCore.optionMenuGrp(label='Category: ', width=300, columnAlign2=['left', 'left'], columnWidth2=[100, 195])
        for category in _Database.getCategoryList():
            self._uiWidget.setdefault(_UiWidgetEnum.categoryMenuList, []).append(_pmCore.menuItem(label=category))
        _pmCore.text(label='Description:')
        self._uiWidget[_UiWidgetEnum.descriptionTextField] = _pmCore.scrollField(width=300, height=50)
    
        _pmCore.separator(style='single', horizontal=True)
        _pmCore.gridLayout(numberOfColumns=2, cellWidth=150)
        self._uiWidget[_UiWidgetEnum.updateAssetBtn] = _pmCore.button(label='Update Asset Info', command=_pmCore.Callback(self._updateAssetClicked))
        self._uiWidget[_UiWidgetEnum.addCommentBtn] = _pmCore.button(label='View Version & Comment', command=_pmCore.Callback(self._viewVersionListClicked))
        self._uiWidget[_UiWidgetEnum.addAssetBtn] = _pmCore.button(label='Add New Asset', command=_pmCore.Callback(self._addAssetClicked))
        self._uiWidget[_UiWidgetEnum.deleteAssetBtn] = _pmCore.button(label='Delete Asset', command=_pmCore.Callback(self._deleteAssetClicked))
        self._uiWidget[_UiWidgetEnum.addVersionBtn] = _pmCore.button(label='Add Version', command=_pmCore.Callback(self._addVersionClicked))
        self._uiWidget[_UiWidgetEnum.manageCategoryBtn] = _pmCore.button(label='Manage Category', command=self._manageCategoryClicked)
        
        _pmCore.setParent('..')
        
        
    def _addAssetButton(self, fileID, sceneName, versionID):
        thumbnailPath = _Database.getThumbnailPath(fileID, versionID)
        if not _os.path.exists(thumbnailPath):
            thumbnailPath = "cube.png"
        buttonName = self._assetBtnName(fileID)
        button = _pmCore.iconTextButton(buttonName, style='iconAndTextVertical', image1=thumbnailPath, label=sceneName, command=_pmCore.Callback(self._assetSelected, fileID))
        self._uiWidget.setdefault(_UiWidgetEnum.assetBtnList, {})[buttonName] = button
        _pmCore.popupMenu()  
        _pmCore.menuItem(label='Open', command=_pmCore.Callback(_functools.partial(_MayaFunctions.openScene, _Database.getFilePath(fileID))))
        _pmCore.menuItem(label='Import', command=_pmCore.Callback(_functools.partial(_MayaFunctions.importScene, _Database.getFilePath(fileID))))
        _pmCore.menuItem(label='Reference', command=_pmCore.Callback(_functools.partial(_MayaFunctions.referenceScene, _Database.getFilePath(fileID))))
        _pmCore.menuItem(label='Versions/Comments', command=_pmCore.Callback(_functools.partial(_AssetVersionDialog, fileID)))
                
    def _assetBtnName(self, fileID):
        return 'assetBtn' + str(fileID)
    
    # Button click callbacks
    def _addAssetClicked(self):
        newAssetDialog = _NewAssetDialog(addedCallback=self._assetAdded)
       
    def _deleteAssetClicked(self):
        if self._currentSelectedAsset == None:
            raise RuntimeError('Nothing selected for deletion.')
        _, _, filePath, _, _, _, _ = _Database.getFileInfo(self._currentSelectedAsset)
        _Database.deleteFile(filePath)
        self._refreshAssetButtonView()
    
    def _updateAssetClicked(self):
        if self._currentSelectedAsset == None:
            raise RuntimeError('Nothing selected.')
        sceneName = _pmCore.textFieldGrp(self._uiWidget[_UiWidgetEnum.sceneNameTextField], query=True, text=True)
        filePath = _pmCore.textFieldGrp(self._uiWidget[_UiWidgetEnum.filePathTextField], query=True, text=True)
        category = _pmCore.optionMenuGrp(self._uiWidget[_UiWidgetEnum.categoryCombox], query=True, value=True)
        description = _pmCore.scrollField(self._uiWidget[_UiWidgetEnum.descriptionTextField], query=True, text=True)
        _Database.setFileCategory(self._currentSelectedAsset, category)
            
        _Database.setFileDescription(self._currentSelectedAsset, description)
        _Database.setFilename(self._currentSelectedAsset, sceneName)
        _Database.setFilePath(self._currentSelectedAsset, filePath)
        _pmCore.iconTextButton(self._uiWidget[_UiWidgetEnum.assetBtnList][self._assetBtnName(self._currentSelectedAsset)], edit=True, label=sceneName)
    
        self._refreshAssetButtonView()
        
    def _addVersionClicked(self):
        fileID, versionNum, thumbnailPath = _MayaFunctions.saveSceneForVersion()
        ## Update version number
        _pmCore.iconTextButton(self._uiWidget[_UiWidgetEnum.assetBtnList][self._assetBtnName(fileID)], edit=True, image1=thumbnailPath)
        _pmCore.text(self._uiWidget[_UiWidgetEnum.versionNumText], edit=True, label=str(versionNum))
    
    def _viewVersionListClicked(self):
        dialog = _AssetVersionDialog(self._currentSelectedAsset)
    
    def _refreshAssetButtonView(self):
        for _, button in self._uiWidget[_UiWidgetEnum.assetBtnList].iteritems():
            _pmCore.deleteUI(button)
        self._uiWidget[_UiWidgetEnum.assetBtnList] = {}
        for category in _Database.getCategoryList():
            _pmCore.setParent(self._uiWidget[category])
            for assetInfo in _Database.getAssetUnderCategory(category):
                id, sceneName, _, versionID, _, _, _ = assetInfo
                self._addAssetButton(id, sceneName, versionID)
    
    # List items updates.
    def _assetSelected(self, fileID):
        # Update background color for buttons.
        if self._currentSelectedAsset != None:
            _pmCore.iconTextButton(self._uiWidget[_UiWidgetEnum.assetBtnList][self._assetBtnName(self._currentSelectedAsset)], edit=True, backgroundColor=self._defaultColor)
        btnName = self._assetBtnName(fileID)
        button = self._uiWidget[_UiWidgetEnum.assetBtnList].get(btnName)
        _pmCore.iconTextButton(button, edit=True, backgroundColor=self._highlightColor)
        
        # Get file info from database.
        fileInfo = _Database.getFileInfo(fileID)
        _pmCore.textFieldGrp(self._uiWidget[_UiWidgetEnum.sceneNameTextField], edit=True, text=fileInfo[1])
        _pmCore.textFieldGrp(self._uiWidget[_UiWidgetEnum.filePathTextField], edit=True, text=fileInfo[2])
        _pmCore.scrollField(self._uiWidget[_UiWidgetEnum.descriptionTextField], edit=True, text=fileInfo[4])
        _pmCore.optionMenuGrp(self._uiWidget[_UiWidgetEnum.categoryCombox], edit=True, value=fileInfo[5])
        
        # Update version text.
        versionNum = _Database.getCurrentVersion(fileID)
        _pmCore.text(self._uiWidget[_UiWidgetEnum.versionNumText], edit=True, label=str(versionNum))
        self._currentSelectedAsset = fileID
    
    def _assetAdded(self, fileID, category):
        categoryLayout = self._uiWidget[category]
        _pmCore.setParent(categoryLayout)
        _, sceneName, _, versionID, _, _, _ = _Database.getFileInfo(fileID)
        self._addAssetButton(fileID, sceneName, versionID)
    
    def _manageCategoryClicked(self, *args):
        categoryEditor = _ManageCategoryDialog(updateCallback=self._categoryUpdated)
        ## update category list in main ui
        
    def _categoryUpdated(self, add=None, rename=None, delete=None):
        _pmCore.setParent(self._uiWidget[_UiWidgetEnum.categoryTabLayout])
        if add:
            # Add a tab in main asset view.
            childLayout = _pmCore.scrollLayout(width=300, height=200, childResizable=True)
            self._uiWidget[add] = _pmCore.gridLayout(numberOfColumns=3, cellHeight = self._iconSize, cellWidth=self._iconSize)
            _pmCore.tabLayout(self._uiWidget[_UiWidgetEnum.categoryTabLayout], tabLabel=((childLayout, add),), edit=True)
            # Add a menu item in category list. From example in Maya doc optionMenuGrp.
            newMenuItem = _pmCore.menuItem(label=add, parent=self._uiWidget[_UiWidgetEnum.categoryCombox]+'|OptionMenu')
            self._uiWidget[_UiWidgetEnum.categoryMenuList].append(newMenuItem)
        if rename:
            tabNameList = _pmCore.tabLayout(self._uiWidget[_UiWidgetEnum.categoryTabLayout], query=True, tabLabel=True)
            childLayoutList = _pmCore.tabLayout(self._uiWidget[_UiWidgetEnum.categoryTabLayout], query=True, childArray=True)
            _pmCore.tabLayout(self._uiWidget[_UiWidgetEnum.categoryTabLayout], edit=True, tabLabel=((childLayoutList[tabNameList.index(rename[0])], rename[1])))
            for item in self._uiWidget[_UiWidgetEnum.categoryMenuList]:
                if _pmCore.menuItem(item, query=True, label=True) != rename[0]:
                    continue
                _pmCore.menuItem(item, edit=True, label=rename[1])
                break
        if delete:
            tabNameList = _pmCore.tabLayout(self._uiWidget[_UiWidgetEnum.categoryTabLayout], query=True, tabLabel=True)
            childLayoutList = _pmCore.tabLayout(self._uiWidget[_UiWidgetEnum.categoryTabLayout], query=True, childArray=True)
            _pmCore.deleteUI(childLayoutList[tabNameList.index(delete)])
            for item in self._uiWidget[_UiWidgetEnum.categoryMenuList]:
                if _pmCore.menuItem(item, query=True, label=True) != delete:
                    continue
                _pmCore.deleteUI(item)
                break
    
class _NewAssetDialog(object):
    _window = None
    _winTitle = "Add Asset"
    def __init__(self, addedCallback=None):
        self._sceneName = None
        self._filePath = None
        self._category = None
        self._description = None
        self._addedCallback = addedCallback
        
        self._buildupWindow()
        self._window.show()
    
    def _buildupWindow(self):
        if isinstance(self._window, _pmCore.uitypes.Window) and self._window.exists(self._window.name()):
            _pmCore.deleteUI(self._window, window=True)
        self._window = _pmCore.window(title=self._winTitle)
        _pmCore.columnLayout()
        self._sceneName = _pmCore.textFieldGrp(label='Scene Name: ', columnAlign2=('left', 'left'), columnWidth2=(80, 200))
        _pmCore.rowLayout(numberOfColumns=2)
        self._filePath = _pmCore.textFieldGrp(label='Directory: ', columnAlign2 = ('left', 'left'), columnWidth2=(80, 180))
        _pmCore.button(label='...', width=20, command=_functools.partial(self._directorySelection, self._filePath))
        _pmCore.setParent('..')
        self._category = _pmCore.optionMenuGrp(label='Category: ', columnAlign2=('left', 'left'), columnWidth2=(80, 200))
        for category in _Database.getCategoryList():
            _pmCore.menuItem(label=category)
        _pmCore.text(label='Description: ')
        self._description = _pmCore.scrollField(width = 300, height=100)
        _pmCore.rowLayout(numberOfColumns=2)
        _pmCore.button(label='OK', width=150, align='left', command=self._newAssetInfoConfirmed)
        _pmCore.button(label='Cancel', width=150, align='left', command=self._newAssetInfoClose)
        
    def _directorySelection(self, *args):
        directory = _pmCore.fileDialog2(fileMode=3)
        _pmCore.textFieldGrp(self._filePath, edit=True, text=str(directory[0]))
        
    def _newAssetInfoConfirmed(self, args):
        sceneName = _pmCore.textFieldGrp(self._sceneName, query=True, text=True)
        directory = _pmCore.textFieldGrp(self._filePath, query=True, text=True)
        description = _pmCore.scrollField(self._description, query=True, text=True)
        category = _pmCore.optionMenuGrp(self._category, value=True, query=True)
        if not sceneName or not directory or not description:
            _pmCore.confirmDialog(title='Invalid Asset Info', message='Asset info for "Scene Name", "Directory" and "Description" can not be empty.', button='OK')
            return
        self._newAssetInfoClose()
        fileID = _MayaFunctions.saveScene(sceneName, directory, description, category)
        if self._addedCallback:
            self._addedCallback(fileID, category)
        
    def _newAssetInfoClose(self, *arg):
        _pmCore.deleteUI(self._window)
        

class _AssetVersionDialog(object):
    _window = None
    _winTitle = "Version Viewer"
    _iconSize = 130
    
    def __init__(self, fileID):
        self._fileID = fileID
        self._currentSelected = None
        self._highlightColor = (0.5, 0.5, 0.5)
        self._defaultColor = (0.27, 0.27, 0.27)
        self._uiWidget = {}
        self._buildupWindow()
        self._window.show()
        
    def _buildupWindow(self):
        if isinstance(self._window, _pmCore.uitypes.Window) and self._window.exists(self._window.name()):
            _pmCore.deleteUI(self._window, window=True)
        self._window = _pmCore.window(title=self._winTitle)
        _pmCore.columnLayout(adjustableColumn=True)
        _pmCore.scrollLayout(width=300, height=250, childResizable=True)
        _pmCore.gridLayout(numberOfColumns=2, cellHeight = self._iconSize, cellWidth=self._iconSize)
        for versionNum in _Database.getVersionList(self._fileID):
            versionInfo = _Database.getVersionInfo(self._fileID, versionNum)
            print versionInfo
            thumbnailPath = versionInfo[3]
            if not _os.path.exists(versionInfo[3]):
                thumbnailPath = "cube.png"
            button = _pmCore.iconTextButton(self._versionBtnName(versionNum), style='iconAndTextVertical', image1=thumbnailPath, 
                                            label=self._versionBtnName(versionNum), command=_pmCore.Callback(self._versionSelected, versionNum))
            self._uiWidget[self._versionBtnName(versionNum)] = button
        _pmCore.setParent('..')
        _pmCore.setParent('..')
        _pmCore.separator(style='none', height=10)
        _pmCore.text(label="Comments: ", align='left')
        self._uiWidget['commentLayout'] = _pmCore.scrollLayout(width=300, height=120, childResizable=True)
        _pmCore.setParent('..')
        _pmCore.separator(style='none', height=10)
        self._uiWidget['comment'] = _pmCore.scrollField(width=300, height=80)
        _pmCore.button(label='Add Comment', command=_pmCore.Callback(self._commentAdded))
        
    def _versionSelected(self, versionNum):
        if self._currentSelected != None:
            _pmCore.iconTextButton(self._uiWidget[self._versionBtnName(self._currentSelected)], edit=True, backgroundColor=self._defaultColor)
        _pmCore.iconTextButton(self._uiWidget[self._versionBtnName(versionNum)], edit=True, backgroundColor=self._highlightColor)
        
        _pmCore.setParent(self._uiWidget['commentLayout'])
        for commentInfo in _Database.getCommentListByVersion(self._fileID, versionNum):
            _, _, user, date, content = commentInfo
            _pmCore.text(label="{0} @ {1}:".format(user, date), align='left')
            _pmCore.text(label=content, wordWrap=True, align='left')
            _pmCore.separator(style='singleDash', height=10)
        self._currentSelected = versionNum
        
    def _versionBtnName(self, versionNum):
        return 'version_' + str(versionNum)
    
    def _commentAdded(self):
        if self._currentSelected == None:
            raise RuntimeError('Must select a version to add comment.')
        newComment = _pmCore.scrollField(self._uiWidget['comment'], query=True, text=True)
        userName = _os.environ.get('AM_USERNAME')
        _Database.addComment(self._fileID, self._currentSelected, newComment, userName)
        _pmCore.setParent(self._uiWidget['commentLayout'])
        _pmCore.text(label="{0} @ {1}:".format(userName, _datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), align='left')
        _pmCore.text(label=newComment, wordWrap=True, align='left')
        _pmCore.scrollField(self._uiWidget['comment'], edit=True, text='')
                

class _ManageCategoryDialog(object):
    _window = None
    _winTitle = "Category Editor"
    
    def __init__(self, updateCallback=None):
        self._textScrollList = None
        self._updateCallback = updateCallback
        self._buildupWindow()
        self._window.show()
    
    def _buildupWindow(self):
        if isinstance(self._window, _pmCore.uitypes.Window) and self._window.exists(self._window.name()):
            _pmCore.deleteUI(self._window, window=True)
        self._window = _pmCore.window(title=self._winTitle)
        
        _pmCore.rowLayout(numberOfColumns=2, columnWidth2=[200, 100])
        self._textScrollList = _pmCore.textScrollList(height=100)
        for category in _Database.getCategoryList():
            _pmCore.textScrollList(self._textScrollList, edit=True, append=category)
        _pmCore.columnLayout()
        _pmCore.button(label='Add', width=100, height=30, command=self._addClicked)
        _pmCore.button(label='Rename', width=100, height=30, command=self._renameClicked)
        _pmCore.button(label='Delete', width=100, height=30, command=self._deleteClicked)
        
    def _addClicked(self, *args):
        result = _pmCore.promptDialog(title='New Category', message="Enter Name: ", button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
        if result == 'OK':
            newCategory = _pmCore.promptDialog(query=True, text=True)
            _Database.addCategory(newCategory)
            _pmCore.textScrollList(self._textScrollList, edit=True, append=newCategory)
            self._updateCallback(newCategory)
        
    def _renameClicked(self, *args):
        current = _pmCore.textScrollList(self._textScrollList, query=True, selectItem=True)
        if not current:
            raise RuntimeError('Must select a category to rename.')
        
        result = _pmCore.promptDialog(title='Rename Category', message="Enter Name: ", button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
        if result != 'OK':
            return
        newName = _pmCore.promptDialog(query=True, text=True)
        _Database.renameCategory(current[0], newName)
        
        index = _pmCore.textScrollList(self._textScrollList, query=True, selectIndexedItem=True)[0]
        _pmCore.textScrollList(self._textScrollList, edit=True, removeIndexedItem=index)
        _pmCore.textScrollList(self._textScrollList, edit=True, appendPosition=[index, newName])
        _pmCore.textScrollList(self._textScrollList, edit=True, selectIndexedItem=index)
        
        self._updateCallback(None, (current[0], newName))
            
    def _deleteClicked(self, *args):
        current = _pmCore.textScrollList(self._textScrollList, query=True, selectItem=True)
        if not current:
            raise RuntimeError('Must select a category to delete.')
        current = current[0]
        if _Database.getAssetUnderCategory(current):
            raise RuntimeError('Can not delete category {0}, there are asset under this category.'.format(current))
        _Database.deleteCategory(current)
        _pmCore.textScrollList(self._textScrollList, edit=True, removeItem=current)
        
        self._updateCallback(None, None, current)
        