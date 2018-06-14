from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from libs.MyGraphicView import *
import os





class ChooseNameForm(QDialog):
    def __init__(self,classNameList):
        super().__init__()

        self.ReturnName=''
        self.classNameList=classNameList
        self.initUI()
        self.initVariables()



        
    def initVariables(self):
        self.classTextPath='./Caches/classes.txt'
        self.loadClassByCache()

    def initUI(self):
        self.setWindowTitle('Select Class')
        self.setWindowIcon(QIcon('./Icons/Class.png'))
        self.layout=QVBoxLayout()
        self.setLayout(self.layout)
        self.lineEdit=QLineEdit()
        self.layout.addWidget(self.lineEdit)

        self.HLayout=QHBoxLayout()

        self.okButton=QPushButton('OK')
        self.cancelButton=QPushButton('Cancel')

        self.okButton.clicked.connect(self.CheckNameNotNull)
        self.cancelButton.clicked.connect(self.reject)
        self.HLayout.addWidget(self.okButton)
        self.HLayout.addWidget(self.cancelButton)


        self.classList=QListWidget()
        self.classList.itemDoubleClicked.connect(self.ItemDoubleClicked)

        self.layout.addWidget(self.classList)
        self.layout.addLayout(self.HLayout)


    def ItemDoubleClicked(self):
        self.ReturnName=self.classList.selectedItems()[0].text()
        self.accept()

    def CheckNameNotNull(self):
        if self.lineEdit.text()!='':
            self.ReturnName=self.lineEdit.text()
            self.accept()

    def exec(self):
        return super().exec(),self.ReturnName


    def loadClassByCache(self):
        for className in self.classNameList:
            self.classList.addItem(className)
    
