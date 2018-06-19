import sys


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from libs.gdalIO import *
from libs.ChooseNameForm import *

import math


class MyGraphicView(QGraphicsView):

    def __init__(self,graphicScene,mainWindow):
        super().__init__(graphicScene,mainWindow)
        self.graphicScene=graphicScene
        self.mainWindow=mainWindow

        self.initializeVariables()
        self.initPen()
        self.initBackGround()


    def initializeVariables(self):
        self.ctrl_pressed=False
        self.mousepressed=False
        self.KEY_CTRL=16777249
        self.KEY_DELETE=16777223
        self.lastPointPos=None
        self.pressedPointPos=None
        self.releasedPointPos=None
        self.gdalDataSet=None
        self.currentScale=1

        self.drawing=False
        self.tempItem=None
        self.tempMoveItem=None


        self.pixItem=None
        self.selectedItem=None
        self.choosedName=None

        self.nodeRadius=3


    def initBackGround(self):
        self.palette=QPalette()
        self.palette.setColor(self.backgroundRole(),QColor(230,230,230))
        self.setPalette(self.palette)


    def initPen(self):
        self.pen=QPen(QColor(255,0,0,255))
        self.pen.setWidth(2)
        self.brush=QBrush(QColor(255,255,255,0))
        self.selectedBrush=QBrush(QColor(0,128,255,128))

    def initAction(self):
        self.delLabelAct=QAction('delete label')
        self.delLabelAct.triggered.connect(self.deleteItem)
        self.delLabelAct.setShortcut('delete')

    def keyPressEvent(self,event):
        if event.key()==self.KEY_CTRL:
            self.ctrl_pressed=True
        elif event.key()==self.KEY_DELETE:
            self.deleteItem()

    def keyReleaseEvent(self,event):
        if event.key()==self.KEY_CTRL:
            self.ctrl_pressed=False


    def wheelEvent(self,event):

        delta=event.angleDelta().y()/1200
        scale_ratio=1-delta

        if self.ctrl_pressed:
            self.currentScale=self.currentScale*scale_ratio
            self.scale(scale_ratio,scale_ratio)

        super().wheelEvent(event)

    def mousePressEvent(self,event):
        self.mousepressed=True
        pos=event.pos()
        self.lastPointPos=pos

        newPos=self.mapToScene(event.pos().x(),event.pos().y())

        x,y=pos.x(),pos.y()
        newPos=self.mapToScene(x,y)
        newX=newPos.x()
        newY=newPos.y()
    
        item=self.graphicScene.itemAt(newX,newY,QTransform())

        tmpItem=None


        for Item in self.mainWindow.rectItemList:
            Item.unselect()



        if item is not None:
            
            if isinstance(item,MyRectItem):
                tmpItem=item
                index=self.mainWindow.rectItemList.index(item)
                self.mainWindow.tableList.selectRow(index)
                self.selectedItem=item
                item.select()
            elif isinstance(item,MyNodeItem):
                tmpItem=item


        if self.drawing:
            self.pressedPointPos=self.lastPointPos
        else:
            self.tempMoveItem=tmpItem

        super().mousePressEvent(event)
        
        
    def mouseReleaseEvent(self,event):
        self.mousepressed=False
        self.lastPointPos=event.pos()

        if self.drawing:
            self.handleDrawing(self.lastPointPos,False)

        
        
        self.tempMoveItem=None
        super().mouseReleaseEvent(event)
        self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self,event):

        pos=event.pos()
        x=pos.x()
        y=pos.y()

        if self.mousepressed:
            if self.drawing:
                self.handleDrawing(pos,True)
            else:

                x,y=pos.x(),pos.y()
                newPos=self.mapToScene(x,y)
                newX=newPos.x()
                newY=newPos.y()

                #item=self.graphicScene.itemAt(newX,newY,QTransform())

                if self.tempMoveItem is not None:
                    if isinstance(self.tempMoveItem,MyRectItem):
                        self.handleDragItem(self.tempMoveItem,pos)
                    elif isinstance(self.tempMoveItem,MyNodeItem):
                        self.handleResizeItem(self.tempMoveItem,pos)
                else:
                    self.handleDrag(pos)

    def handleResizeItem(self,tempMoveItem,pos):

        if self.lastPointPos==None:
            pass
        else:
            
            dPos=pos-self.lastPointPos

            dx=dPos.x()/self.currentScale
            dy=dPos.y()/self.currentScale

            parentItem=tempMoveItem.rectItem

            geo=parentItem.rect()
            x,y,w,h=geo.x(),geo.y(),geo.width(),geo.height()

            if tempMoveItem==parentItem.subItemTopLeft:
                parentItem.setRect(x+dx,y+dy,w-dx,h-dy)
            elif tempMoveItem==parentItem.subItemTopRight:
                parentItem.setRect(x,y+dy,w+dx,h-dy)
            elif tempMoveItem==parentItem.subItemBottomLeft:
                parentItem.setRect(x+dx,y,w-dx,h+dy)
            elif tempMoveItem==parentItem.subItemBottomRight:
                parentItem.setRect(x,y,w+dx,h+dy)

            rect=parentItem.rect()
            newX,newY,newW,newH=rect.x(),rect.y(),rect.width(),rect.height()

            self.setCursor(Qt.ClosedHandCursor)

        self.lastPointPos=pos


    def handleDrawing(self,pos,isTemp=True):
        self.lastPointPos=pos
        self.setCursor(Qt.CrossCursor)

        x1=self.pressedPointPos.x()
        y1=self.pressedPointPos.y()

        x2=pos.x()
        y2=pos.y()

        sceneWidth,sceneHeight=self.graphicScene.width(),self.graphicScene.height()

        newPoint1=self.mapToScene(x1,y1)
        newPoint2=self.mapToScene(x2,y2)

        x1,y1=newPoint1.x(),newPoint1.y()
        x2,y2=newPoint2.x(),newPoint2.y()

        xTop=x1 if x1<x2 else x2
        yTop=y1 if y1<y2 else y2
        xBottom=x2 if x1<x2 else x1
        yBottom=y2 if y1<y2 else y1

        xTop=0 if xTop<0 else xTop
        yTop=0 if yTop<0 else yTop

        xBottom=sceneWidth if xBottom>sceneWidth else xBottom
        yBottom=sceneHeight if yBottom>sceneHeight else yBottom

        width=math.fabs(xTop-xBottom)/self.currentScale
        height=math.fabs(yTop-yBottom)/self.currentScale
 
        if isTemp:
            if self.tempItem==None:

                self.tempItem=MyRectItem(xTop,yTop,width,height,self.graphicScene,self.mainWindow)
                self.tempItem.setBrush(self.brush)
                self.graphicScene.addItem(self.tempItem)  
            else:
                self.tempItem.setRect(xTop,yTop,width,height)
        else:

            self.releasedPointPos=self.lastPointPos
            self.graphicScene.removeItem(self.tempItem)
            self.tempItem.removeNodeItem()

            del self.tempItem
            self.tempItem=None

            graphicItem=MyRectItem(xTop,yTop,width,height,self.graphicScene,self.mainWindow)
            graphicItem.setBrush(self.brush)



            result,txt=self.mainWindow.addShape()
            
            if result==True:
                self.addShape(graphicItem,txt)
            else:
                graphicItem.removeNodeItem()
            self.drawing=False
    
    def addShape(self,item,name):
        self.graphicScene.addItem(item)
        item.setName(name)
        self.mainWindow.rectItemList.append(item)

    def handleDrag(self,pos):
        if self.lastPointPos==None:
            pass
        else:
            
            dPos=pos-self.lastPointPos
            dx,dy=dPos.x(),dPos.y()

            hbar=self.horizontalScrollBar()
            vbar=self.verticalScrollBar()

            h_val=hbar.value()
            v_val=vbar.value()

            self.setCursor(Qt.ClosedHandCursor)
            hbar.setValue(h_val-dx)
            vbar.setValue(v_val-dy)


        self.lastPointPos=pos

    def handleDragItem(self,item,pos):

        dPos=pos-self.lastPointPos
        dx=dPos.x()
        dy=dPos.y()

        dx=dx/self.currentScale
        dy=dy/self.currentScale

        self.lastPointPos=pos

        rect=item.rect()
        x,y,w,h=rect.x(),rect.y(),rect.width(),rect.height()

        if not self.RectIsInScene(x+dx,y+dy,w,h):
            return
        item.setRect(x+dx,y+dy,w,h)
    
    def RectIsInScene(self,x,y,w,h):
        if x<0 or y<0 or x>self.graphicScene.width()-w or y>self.graphicScene.height()-h:
            return False
        return True
    def PosIsInScene(self,x,y):
        if x<0 or y<0 or x>self.graphicScene.width()or y>self.graphicScene.height():
            return False
        return True

    def setDrawing(self,drawing=False):
        self.drawing=drawing
        self.setCursor(Qt.CrossCursor)

    def deleteItem(self):
        if self.selectedItem==None:
            return
        
        index=self.mainWindow.rectItemList.index(self.selectedItem)
        del self.mainWindow.rectItemList[index]

        self.mainWindow.tableList.removeRow(index)

        self.graphicScene.removeItem(self.selectedItem)
        self.selectedItem.removeNodeItem()

        self.selectedItem=None

    def loadImage(self,ImagePath):
        try:
            pixmap=QPixmap(ImagePath)
        except:
            print('load image error')
            return

        qimage=QImage()
        if pixmap.isNull():
            try:
                self.gdalDataSet=gdal.Open(ImagePath,gdal.GA_ReadOnly)
                qimage=readGDALFromFile(self.gdalDataSet)
                pixmap.fromImage(qimage)
            except:
                print('unable to load')
                return

            if pixmap.isNull():
                print('load gdal image error')
                return
        
        imageSize=pixmap.size()
        width,height=imageSize.width(),imageSize.height()

        frameWidth=self.geometry().width()

        scale_ratio=width/frameWidth

        self.graphicScene.clear()
        self.pixItem=self.graphicScene.addPixmap(pixmap)
        self.graphicScene.setSceneRect(0,0,pixmap.width(),pixmap.height())
        
        self.currentScale=1/self.currentScale
        self.scale(self.currentScale,self.currentScale)
        self.currentScale=1



class MyRectItem(QGraphicsRectItem):
    def __init__(self,x,y,w,h,scene,mainWindow):
        super().__init__(x,y,w,h)
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.scene=scene
        self.mainWindow=mainWindow
        
        

        self.initDesigner()
        self.initVariables()
        self.initPen()

        self.initNode()

    def initNode(self):

        self.subItemTopLeft=MyNodeItem(self.x,self.y,self.nodeRadius*2,self.nodeRadius*2,self)
        self.subItemTopRight=MyNodeItem(self.x+self.w,self.y,self.nodeRadius*2,self.nodeRadius*2,self)
        self.subItemBottomLeft=MyNodeItem(self.x,self.y+self.h,self.nodeRadius*2,self.nodeRadius*2,self)
        self.subItemBottomRight=MyNodeItem(self.x+self.w,self.y+self.h,self.nodeRadius*2,self.nodeRadius*2,self)


        self.subItemTopLeft.setSpanAngle(360*12)
        self.subItemTopRight.setSpanAngle(360*12)
        self.subItemTopRight.setStartAngle(360*12)

        self.subItemBottomLeft.setSpanAngle(360*12)
        self.subItemBottomLeft.setStartAngle(360*4)

        self.subItemBottomRight.setSpanAngle(360*12)
        self.subItemBottomRight.setStartAngle(360*8)


        self.scene.addItem(self.subItemTopLeft)
        self.scene.addItem(self.subItemTopRight)
        self.scene.addItem(self.subItemBottomLeft)
        self.scene.addItem(self.subItemBottomRight)


    def removeNodeItem(self):
        self.scene.removeItem(self.subItemTopLeft)
        self.scene.removeItem(self.subItemTopRight)
        self.scene.removeItem(self.subItemBottomLeft)
        self.scene.removeItem(self.subItemBottomRight)         


    def initVariables(self):

        self.subItemTopLeft=None
        self.subItemTopRight=None
        self.subItemBottomLeft=None
        self.subItemBottomRight=None

        self.points=[]
        self.score=0
        self.name=''
        self.widthBase=2
        self.nodeRadius=4
    
    def initPen(self):
        self.pen=QPen(QColor(255,0,0,255))
        self.pen.setWidth(2)
        self.setPen(self.pen)

    def setScore(self,score):
        self.score=score
    
    def setName(self,name):
        self.name=name


    def initDesigner(self):
        self.setToolTip('press to drag me!')

        self.pressed=False
        self.lastPointPos=None
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setEnabled(True)
        #self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.brush=QBrush(QColor(255,255,255,0))
        self.selectedBrush=QBrush(QColor(0,128,255,128))

    def select(self):
        self.setBrush(self.selectedBrush)
        
    
    def unselect(self):
        self.setBrush(self.brush)
    



    def paint(self,painter,styleOptionGraphicsItem,param4):
        


        self.pen.setWidth(self.widthBase*self.mainWindow.graphicView.currentScale*0.5)
        self.setPen(self.pen)
        super().paint(painter,styleOptionGraphicsItem,param4)


    def moveBy(self,dx,dy):
        #self.subItemTopLeft.moveBy(dx,dy)
        #self.subItemTopRight.moveBy(dx,dy)
        #self.subItemBottomLeft.moveBy(dx,dy)
        #self.subItemBottomRight.moveBy(dx,dy)
        super().moveBy(dx,dy)

    def setRect(self,x,y,w,h):
        rect=self.subItemTopLeft.rect()
        w0,h0=rect.width(),rect.height()

        self.subItemTopLeft.setRect(x-w0/2,y-h0/2,w0,h0)
        self.subItemTopRight.setRect(x-w0/2+w,y-h0/2,w0,h0)
        self.subItemBottomLeft.setRect(x-w0/2,y-h0/2+h,w0,h0)
        self.subItemBottomRight.setRect(x-w0/2+w,y-h0/2+h,w0,h0)
        super().setRect(x,y,w,h)


class MyNodeItem(QGraphicsEllipseItem):


    def __init__(self,x,y,w,h,rectItem):
        self.rectItem=rectItem
        super().__init__(x-w/2,y-h/2,w,h)
        self.initVariables()
        self.initPen()

    def initVariables(self):
        self.baseWidth=1


    def initPen(self):
        self.pen=QPen(QColor(255,0,0,255))
        self.pen.setWidth(self.baseWidth)
        self.brush=QBrush(QColor(255,255,0,255))
        self.selectedBrush=QBrush(QColor(0,128,255,128))

        self.setBrush(self.brush)
        self.setPen(self.pen)
        