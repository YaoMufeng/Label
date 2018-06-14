class BoxItem:
    def __init__(self):
        self.name=''
        self.score=0
        self.bndbox={'xmin':0,'xmax':0,'ymin':0,'ymax':0}
    
    def setName(self,name):
        self.name=name
    
    def setScore(self,score):
        self.score=score
    
    def setBox(self,xmin,ymin,xmax,ymax):
        self.bndbox['xmin']=xmin
        self.bndbox['ymin']=ymin
        self.bndbox['xmax']=xmax
        self.bndbox['ymax']=ymax