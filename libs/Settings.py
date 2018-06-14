import os

class Settings:
    def __init__(self):

        self.dict={'annoFolderPath':'.','imageFolderPath':'.'}
        self.settingPath='./Caches/Settings.txt'
        self.readSettings()


    def setDict(self,key,value):
        self.dict[key]=value
    

    def writeSettings(self):
        with open(self.settingPath,'w') as f:
            for key,value in self.dict.items():
                f.write(str(key)+','+str(value)+'\n')
    

    def readSettings(self):
        if not os.path.exists(self.settingPath):
            with open(self.settingPath,'w') as f:
                pass

        with open(self.settingPath,'r') as f:
            lines=f.readlines()
            if len(lines)<=0:
                return
            for line in lines:
                key,value=line.strip('\n').split(',')
                self.dict[key]=value


