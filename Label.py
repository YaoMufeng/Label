import sys
import codecs
import re
import subprocess
import sip

import os.path
import shutil

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from libs.MyGraphicView import *
from libs.ChooseNameForm import *
from libs.XMLIO import *
from libs.Settings import *
from libs.MyTableWidget import *
from libs.MyColor import *
#this version is connected to github
#hahahaha


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initVariables()
        self.initUI()
        self.initLog()


    def initVariables(self):
        self.ImgListIndex=0
        self.mImgList=[]
        self.currentImgPath=''
        self.classTextPath='./Caches/classes.txt'
        self.copyingDir=''

        self.classNameList=[]
        self.initClassNameList()

        self.rectItemList=[]
        self.imageFolderPath=''
        self.annoFolderPath=''

        self.currentImageName=''
        self.currentXMLName=''
        self.settings=Settings()

        self.pixmap=None
        self.isAutoSaving=True

        self.windowResizeEvent=pyqtSignal()
        self.saveState=False

        self.currentBoxIndex=0

    def initClassNameList(self):
        if os.path.exists(self.classTextPath):
            with open(self.classTextPath,'r') as f:
                for line in f.readlines():
                    line=line.strip('\n')
                    self.classNameList.append(line)
        
    def initToolBar(self):
        
        toolbar=QToolBar()
        toolBar=self.addToolBar(Qt.LeftToolBarArea,toolbar)

        openFolderButton=QToolButton()
        openFolderButton.setIcon(QIcon('./Icons/OpenImg3.png'))
        openFolderButton.setText(' Img Folder ')
        openFolderButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        openFolderButton.setAutoRaise(True)
        openFolderButton.clicked.connect(self.openImgFolder)


        openAnnoFolderButton=QToolButton()
        openAnnoFolderButton.setIcon(QIcon('./Icons/OpenAnno2.png'))
        openAnnoFolderButton.setText(' Anno Folder')
        openAnnoFolderButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        openAnnoFolderButton.setAutoRaise(True)
        openAnnoFolderButton.clicked.connect(self.openAnnoFolder)

        prevImgButton=QToolButton()
        prevImgButton.setIcon(QIcon('./Icons/ArrowLeft.png'))
        prevImgButton.setText('  prev Img  ')
        prevImgButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        prevImgButton.setAutoRaise(True)
        prevImgButton.clicked.connect(self.openPrevImg)
        prevImgButton.setShortcut('a')

        nextImgButton=QToolButton()
        nextImgButton.setIcon(QIcon('./Icons/ArrowRight.png'))
        nextImgButton.setText('  next Img  ')
        nextImgButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        nextImgButton.setAutoRaise(True)
        nextImgButton.clicked.connect(self.openNextImg)
        nextImgButton.setShortcut('d')


        rectButton=QToolButton()
        rectButton.setIcon(QIcon('./Icons/drawRect2.png'))
        rectButton.setText(' create rect')
        rectButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        rectButton.setAutoRaise(True)
        rectButton.clicked.connect(self.setDrawing)


        saveXMLButton=QToolButton()
        saveXMLButton.setIcon(QIcon('./Icons/SaveXML.png'))
        saveXMLButton.setText('  Save XML  ')
        saveXMLButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        saveXMLButton.setAutoRaise(True)
        saveXMLButton.clicked.connect(self.saveToXML)        


        fitWindowButton=QToolButton()
        fitWindowButton.setIcon(QIcon('./Icons/FitWindow1.png'))
        fitWindowButton.setText(' fit window ')
        fitWindowButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        fitWindowButton.setAutoRaise(True)
        fitWindowButton.clicked.connect(self.fitWindow)

        toolbar.addWidget(openFolderButton)  
        toolbar.addWidget(openAnnoFolderButton) 
        toolbar.addWidget(prevImgButton)
        toolbar.addWidget(nextImgButton) 
        toolbar.addWidget(rectButton)
        toolbar.addWidget(saveXMLButton)
        toolbar.addWidget(fitWindowButton)
        return toolBar    
    
    def initMenu(self):
        
        menuBar=self.menuBar()

        #file menu
        fileMenu=menuBar.addMenu('&File')
        openImgAction=fileMenu.addAction('open image')
        openImgAction.triggered.connect(self.printf)
        openImgAction.setIcon(QIcon('./Icons/OpenImg2.png'),)
        
        #menu
        menuMenu=menuBar.addMenu('&Menu')
        autoSavingAction=menuMenu.addAction('auto saving')
        autoSavingAction.setCheckable(True)
        autoSavingAction.setChecked(True)
        autoSavingAction.triggered[bool].connect(self.setAutoSaving)

        #image copy menu
        imageCopyMenu=menuBar.addMenu('&Image Copy')

        selectCopyDirAction=imageCopyMenu.addAction('select copy dir')
        selectCopyDirAction.triggered.connect(self.openCopyFolder)

        copyToDirAction=imageCopyMenu.addAction('copy to dir')
        copyToDirAction.setShortcut('k')
        copyToDirAction.triggered.connect(self.copyCurrentImgToDir)

        copyBoxAction=imageCopyMenu.addAction('copy box')
        copyBoxAction.setShortcut('ctrl+c')
        copyBoxAction.triggered.connect(self.copySelectedBox)

        #box menu
        boxMenu=menuBar.addMenu('&Box Menu')
        zoomToPrevBoxAction=boxMenu.addAction('zoom to prev box')
        zoomToPrevBoxAction.setShortcut('q')
        zoomToPrevBoxAction.triggered.connect(self.zoomToPrevBox)

        zoomToPrevBoxAction=boxMenu.addAction('zoom to next box')
        zoomToPrevBoxAction.setShortcut('e')
        zoomToPrevBoxAction.triggered.connect(self.zoomToNextBox)

        return menuBar
    

    def initStatusBar(self):
        statusBar=self.statusBar()
        
        statusBar.showMessage('Ready')
        return statusBar


    def initFileListWidget(self):

        self.fileListWidget = QListWidget()
        self.slider=QSlider(Qt.Horizontal)
        self.fileListLabel=QLabel('Processed: 0/0')

        filelistLayout = QVBoxLayout()
        filelistLayout.setContentsMargins(0, 0, 0, 0)
        filelistLayout.addWidget(self.slider)
        filelistLayout.addWidget(self.fileListLabel)
        filelistLayout.addWidget(self.fileListWidget)
        fileListContainer = QWidget()
        fileListContainer.setLayout(filelistLayout)
        self.filedock = QDockWidget(u'File List', self)
        self.filedock.setObjectName(u'Files')
        self.filedock.setWidget(fileListContainer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filedock)

        self.fileListWidget.itemDoubleClicked.connect(self.openSelectedImg)
        


    def initBoxTableWidget(self):
        tableLayout=QVBoxLayout()
        tableLayout.setContentsMargins(0,0,0,0)

        self.useDefaultLabelCheckbox = QCheckBox(u'Use default label')
        self.useDefaultLabelCheckbox.setChecked(False)
        self.defaultLabelTextLine = QLineEdit()
        useDefaultLabelQHBoxLayout = QHBoxLayout()
        useDefaultLabelQHBoxLayout.addWidget(self.useDefaultLabelCheckbox)
        useDefaultLabelQHBoxLayout.addWidget(self.defaultLabelTextLine)
        useDefaultLabelContainer = QWidget()
        useDefaultLabelContainer.setLayout(useDefaultLabelQHBoxLayout)

        tableLayout.addWidget(useDefaultLabelContainer)
        self.tableList=MyTableWidget(self)

        colCount=1
        self.tableList.setColumnCount(colCount)

        self.tableList.setHorizontalHeaderItem(0, QTableWidgetItem("class"))  
        self.tableList.clicked.connect(self.selectBox)
        self.tableList.itemChanged[QTableWidgetItem].connect(self.setBoxName)
        self.tableList.itemClicked.connect(self.setBoxLineColor)

        colWidth=10
        for i in range(colCount):
            self.tableList.setColumnWidth(i, colWidth)    

        tableListContainer=QWidget()
        tableListContainer.setLayout(tableLayout)
        self.tableList.setContextMenuPolicy(Qt.CustomContextMenu)

        
        tableLayout.addWidget(self.tableList)

        self.tableDock=QDockWidget(u'box table',self)
        self.tableDock.setObjectName(u'tables')
        self.tableDock.setWidget(tableListContainer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tableDock)


    def initPaintingWidget(self):


        self.paintWidget=paintWidget(self)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.paintWidget)
        #self.scroll.setFixedSize(600,600)
        self.scroll.setWidgetResizable(True)

        self.scrollBars = {
            Qt.Vertical: self.scroll.verticalScrollBar(),
            Qt.Horizontal: self.scroll.horizontalScrollBar()
        }
        self.setCentralWidget(self.scroll)



    

    def initGraphicView(self):
        
        self.ctrl_pressed=False

        graphicScene=QGraphicsScene()

        self.graphicView=MyGraphicView(graphicScene,self)
        self.graphicView.show()
        self.setCentralWidget(self.graphicView)



    def initLog(self):
        logFolder='./log/'
        if not os.path.exists(logFolder):
            os.makedirs(logFolder)
        
        dateTime=QDateTime.currentDateTime().toString().replace(' ','_').replace(':',';')
        fileName=dateTime+'.log'
        filePath=logFolder+fileName
        self.logFileHandle=open(filePath,'w')

        msg='open window'
        self.writeMsg(msg)

    def initUI(self):
        
        self.toolBar=self.initToolBar()
        self.menuBar=self.initMenu()
        self.statusBar=self.initStatusBar()


        self.initFileListWidget()
        self.initBoxTableWidget()
        #self.initPaintingWidget()
        self.initGraphicView()

        self.setWindowTitle('Label')
        self.setWindowIcon(QIcon('./Icons/WindowIcon1.png'))


        self.setMinimumSize(300,300)
        self.setGeometry(100,100,800,600)
        self.showMaximized()   



    def printf(self):
        print('triggered!')
    

    def openImgFolder(self):
        defaultOpenDirPath =self.settings.dict['imageFolderPath']

        dirpath = QFileDialog.getExistingDirectory(self,'- Open Img Folder', defaultOpenDirPath,QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dirpath=='':
            return

        self.settings.setDict('imageFolderPath',dirpath)
        self.settings.writeSettings()

        self.ClearBeforeOpenFolder()    

        self.imageFolderPath=dirpath
        self.mImgList = self.scanAllImages(dirpath)
   
        for imgPath in self.mImgList:
            item = QListWidgetItem(imgPath)
            self.fileListWidget.addItem(item)
        self.ImgListIndex=0

        self.openCurrentImg()


    def openAnnoFolder(self):
        defaultOpenDirPath = self.settings.dict['annoFolderPath']
        dirpath = QFileDialog.getExistingDirectory(self,'- Open Anno Folder', defaultOpenDirPath,QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dirpath=='':
            return

        self.settings.setDict('annoFolderPath',dirpath)
        self.settings.writeSettings()
        self.annoFolderPath=dirpath

    def openCopyFolder(self):
        defaultOpenDirPath=self.settings.dict['copyFolderPath']

        dirpath = QFileDialog.getExistingDirectory(self,'- Open Anno Folder', defaultOpenDirPath,QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dirpath=='':
            return
        self.copyingDir=dirpath
        self.settings.setDict('copyFolderPath',self.copyingDir)


        msg='copying dir={} '.format(self.copyingDir)
        self.writeMsg(msg)

        self.settings.writeSettings()

    def ClearBeforeOpenFolder(self):
        self.rectItemList.clear()
        self.fileListWidget.clear()
        self.tableList.clear()
        self.tableList.setRowCount(0)

    def ClearBeforeOpenAnotherImg(self):
        self.rectItemList.clear()
        self.tableList.clear()
        self.tableList.setRowCount(0)

    def scanAllImages(self, folderPath):
        #copy from labelImg

        extensions = ['.jpeg', '.jpg', '.png', '.bmp','.tif','.img']
        images = []

        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.join(root, file)
                    path = os.path.abspath(relativePath)
                    images.append(path)
        images.sort(key=lambda x: x.lower())
        return images
    
    def openNextImg(self):
        if len(self.mImgList)<=0:
            msg='No Image To Open'
            self.writeMsg(msg)
            
            return
        if self.isAutoSaving and self.saveState:
            self.saveToXML()
        self.ImgListIndex=self.ImgListIndex+1
        self.openCurrentImg()

    def openPrevImg(self):
        if len(self.mImgList)<=0:
            msg='No Image To Open'
            self.writeMsg(msg)
            return
        if self.isAutoSaving and self.saveState:
            self.saveToXML()

        self.ImgListIndex=self.ImgListIndex-1
        self.openCurrentImg()        

    def openCurrentImg(self):

        self.ClearBeforeOpenAnotherImg()

        self.setSaveState(False)

        if self.ImgListIndex>=len(self.mImgList):
            self.ImgListIndex=0
        elif self.ImgListIndex<0:
            self.ImgListIndex=len(self.mImgList)-1

        value=self.ImgListIndex/len(self.mImgList)*100
        self.slider.setValue(value)
        self.fileListLabel.setText('processing {}/{}'.format(self.ImgListIndex+1,len(self.mImgList)))

        ImgFilePath=self.mImgList[self.ImgListIndex]

        self.graphicView.loadImage(ImgFilePath)
        msg='load image from {}'.format(ImgFilePath)
        self.writeMsg(msg)

        fileWidgetItem = self.fileListWidget.item(self.ImgListIndex)
        fileWidgetItem.setSelected(True)
        self.fileListWidget.scrollToItem(fileWidgetItem)

        self.currentImgPath=ImgFilePath

        (imgFolder,imgName)=os.path.split(ImgFilePath)

        self.currentImageName=imgName

        xmlName=imgName[0:len(imgName)-4]+'.xml'
        self.setCentralWidget(self.graphicView)


        if self.annoFolderPath!='':
            xmlFilePath=os.path.join(self.annoFolderPath,xmlName)
            self.currentXMLName=xmlName
            if not os.path.exists(xmlFilePath):
                msg='not exist: {}'.format(xmlFilePath)
                self.writeMsg(msg)
                return

            boxList=loadBoxFromXML(xmlFilePath)
            
            msg='load annotations from {}'.format(xmlFilePath)
            self.writeMsg(msg)

            for boxItem in boxList:

                xmin=boxItem.bndbox['xmin']
                ymin=boxItem.bndbox['ymin']
                xmax=boxItem.bndbox['xmax']
                ymax=boxItem.bndbox['ymax']
                name=boxItem.name
                score=boxItem.score

                rectItem=MyRectItem(xmin,ymin,xmax-xmin,ymax-ymin,self.graphicView.graphicScene,self)
                rectItem.setName(name)
                rectItem.setScore(score)

                #self.rectItemList.append(rectItem)
                self.graphicView.addShape(rectItem,name)
                self.addRowToTable(name)

    def copyCurrentImgToDir(self):
        if os.path.exists(self.currentImgPath) and os.path.exists(self.copyingDir):
            shutil.copy(self.currentImgPath,self.copyingDir)
            msg='copying {} to {}'.format(self.currentImageName,self.copyingDir)
            self.writeMsg(msg)



    def openSelectedImg(self,item=None):
        if self.isAutoSaving and self.saveState:
            self.saveToXML()
            
        currentIndex=self.mImgList.index(item.text())
        self.ImgListIndex=currentIndex
        self.openCurrentImg()
    
    def setDrawing(self):
        self.graphicView.setDrawing(True)
    
    def setAutoSaving(self,autoSaving):
        self.isAutoSaving=autoSaving
        msg='set auto saving = {}'.format(self.isAutoSaving)
        self.writeMsg(msg)

    def addShape(self,className=None):
        txt=''
        if self.useDefaultLabelCheckbox.isChecked():
            txt=self.defaultLabelTextLine.text()
            self.addRowToTable(txt)

            self.setSaveState(True)
            return True,txt
        else:
            result,txt=ChooseNameForm(self.classNameList).exec()
            if result==1:
                self.addRowToTable(txt)
                self.setSaveState(True)
                return True,txt

        return False,txt

    def addRowToTable(self,txt):
        rowCount=self.tableList.rowCount()
        self.tableList.setRowCount(rowCount+1)
        item=QTableWidgetItem(txt)

        if self.tableList.columnCount()<2:
            self.tableList.setColumnCount(2)

        colorItem=QTableWidgetItem(' ')
        self.tableList.setItem(rowCount,0,item)
        self.tableList.setItem(rowCount,1,colorItem)



        self.tableList.setColumnWidth(0,self.tableList.sizeHintForColumn(0))
        self.tableList.setColumnWidth(1,self.tableList.rowHeight(0))
        if not txt in self.classNameList:
            self.classNameList.append(txt)
        
        color=MyColor.getColorByID(self.classNameList.index(txt))
        brush=QBrush(color)
        colorItem.setBackground(brush)
    
    def setSaveState(self,state):
        self.saveState=state

    def setBoxName(self,changedItem):
        columnIndex=changedItem.column() #we only care to column one,which stores our box name
        if columnIndex!=0:
            return

        rowIndex=changedItem.row()
        if rowIndex==-1 or rowIndex>=len(self.rectItemList):
            return

        boxItem=self.rectItemList[rowIndex]
        if self.tableList.currentItem() is None:
            return
        newName=self.tableList.currentItem().text()
        srcName=boxItem.name
        if srcName==newName:
            return

        if newName not in self.classNameList:
            self.classNameList.append(newName)
        
        colorID=self.classNameList.index(newName)
        newColor=MyColor.getColorByID(colorID)
        boxItem.setLineColor(newColor)

        boxItem.setName(newName)
        self.graphicView.graphicScene.update()
      
        self.tableList.clear()
        self.tableList.setRowCount(0)
        for rectItem in self.rectItemList:
            itemName=rectItem.name
            self.addRowToTable(itemName)
        self.graphicView.graphicScene.update()
        self.setSaveState(True)


    def setBoxLineColor(self):
        columnIndex=self.tableList.currentColumn()
        if columnIndex!=1:
            return

        rowIndex=self.tableList.currentRow()
        rectItem=self.rectItemList[rowIndex]
        name=rectItem.name
        colorIndex=self.classNameList.index(name)
        newColor = QColorDialog.getColor()
        MyColor.setColorByID(colorIndex,newColor)
        self.tableList.clear()
        self.tableList.setRowCount(0)

        for rectItem in self.rectItemList:
            itemName=rectItem.name
            index=self.classNameList.index(itemName)
            rectItem.setLineColor(MyColor.getColorByID(index))
            self.addRowToTable(itemName)
        self.graphicView.graphicScene.update()

        msg="set box line color"
        self.writeMsg(msg)

    def writeMsg(self,msg):
        time=QTime.currentTime().toString()
        msg=msg+' -- '+time+'\n'

        print(msg)
        self.logFileHandle.write(msg+'\n')

    def saveToXML(self):


        if self.annoFolderPath!='' and self.currentXMLName!='':
            
            imageSize=self.pixmap.size()

            image=self.pixmap.toImage()
            imageChannel=image.bitPlaneCount()/8

            boxList=[]
            for rectItem in self.rectItemList:
                boxItem=BoxItem()
                boxItem.setName(rectItem.name)
                boxItem.setScore(rectItem.score)
                rect=rectItem.rect()

                boxItem.setBox(rect.x(),rect.y(),rect.width()+rect.x(),rect.height()+rect.y())
                boxList.append(boxItem)
            xmlpath=os.path.join(self.annoFolderPath,self.currentXMLName)
            if boxList!=[]:
                writeBoxToXML(boxList,xmlpath,imageSize,imageChannel,self.imageFolderPath,self.currentImageName)
                msg='save to xml {}'.format(xmlpath)
                self.writeMsg(msg)
            else:
                if os.path.exists(xmlpath):
                    os.remove(xmlpath)

            
        pass

    def fitWindow(self):
        if self.pixmap==None:
            return

        self.graphicView.ScaleToOrigin()
        self.graphicView.ScaleToFit()
    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.fitWindow()

    def selectBox(self):
        for item in self.rectItemList:
            item.unselect()

        self.tableList
        rowIndex=self.tableList.currentRow()
        item=self.rectItemList[rowIndex]
        self.graphicView.selectItem(item)

    def zoomToPrevBox(self):
        if len(self.rectItemList)==0:
            return

        item=None
        if self.graphicView.selectedItem==None:
            item=self.rectItemList[0]
        else:
            index=self.currentBoxIndex
            index=index-1
            if index<0:
                index=len(self.rectItemList)-1
            
            self.currentBoxIndex=index
            item=self.rectItemList[index]
        
        self.zoomToBox(item)

    def zoomToNextBox(self):
        if len(self.rectItemList)==0:
            return

        item=None
        if self.graphicView.selectedItem==None:
            item=self.rectItemList[0]
        else:
            index=self.currentBoxIndex
            index=index+1
            if index>=len(self.rectItemList):
                index=0
            
            self.currentBoxIndex=index
            item=self.rectItemList[index]
        
        self.zoomToBox(item)

    def zoomToBox(self,boxItem):

        self.graphicView.selectItem(boxItem)
        rect=boxItem.rect()
        
        rectX,rectY,rectWidth,rectHeight=rect.x(),rect.y(),rect.width(),rect.height()

        imageWidth,imageHeight=self.pixmap.width(),self.pixmap.height()


        distance=5
        scaleWidth=imageWidth/(rectWidth+distance)
        scaleHeight=imageHeight/(rectHeight+distance)

        scale=scaleWidth if scaleWidth<scaleHeight else scaleHeight

        self.graphicView.ScaleToOrigin()
        self.graphicView.ScaleTo(scale)
        
        hbar=self.graphicView.horizontalScrollBar()
        vbar=self.graphicView.verticalScrollBar()

        hval=(rectX+rectWidth/2)/imageWidth*hbar.maximum()
        vval=(rectY+rectHeight/2)/imageHeight*vbar.maximum()      

        print('rectPos=({},{}) val=({},{})'.format(rectX,rectY,hval,vval))
        hbar.setValue(hval)
        vbar.setValue(vval)    
        print(hbar.value(),vbar.value())



    def copySelectedBox(self):

        msg='copy selected box'
        self.writeMsg(msg)

        if self.graphicView.selectedItem is not None:
            copyItem=self.graphicView.selectedItem.copy()
            txtName=self.graphicView.selectedItem.name
            self.graphicView.addShape(copyItem,txtName)
            self.addRowToTable(txtName)
            self.graphicView.selectItem(copyItem)

    def deleteBndBox(self,rectItem):
        pass
    
    def closeEvent(self,event):
        msg='close window'
        self.writeMsg(msg)
        
        if self.isAutoSaving and self.saveState:
            self.saveToXML()

        self.settings.writeSettings()
        self.logFileHandle.close()
        super().closeEvent(event)

class paintWidget(QWidget):
    def __init__(self,mainWindow=None):
        super().__init__()
        self.pixmap=QPixmap()
        self.mainWindow=mainWindow

    def paintEvent(self,event):
        qp=QPainter()
        qp.begin(self)
        qp.drawPixmap(0,0,self.pixmap)
        size=self.pixmap.size()
        w=size.width()
        h=size.height()

        qp.end()


    
def main(argv=[]):
    app=QApplication(sys.argv)
    mainWindow=MainWindow()
    sys.exit(app.exec_())


if __name__=='__main__':
    main()