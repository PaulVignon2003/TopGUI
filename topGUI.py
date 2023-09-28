#GUI by Paul Vignon for Topology Optimization solvers based on the Topology99 matlab program by Ole Sigmund

from tkinter import *
from tkinter import ttk, messagebox, filedialog
import os, math, subprocess
from subprocess import PIPE

class elemBox:
    def __init__(self,elem,ID_number,*args):
        self.ID_number=ID_number
        self.elem=elem
        self.checkCol=math.floor((ID_number-1+nely)/nely)-1
        self.checkRow=(ID_number-1+nely)%nely
        self.Nodes=['',nodeListMat[ID_number+self.checkCol],nodeListMat[ID_number+self.checkCol+1],nodeListMat[ID_number+nely+self.checkCol+1],nodeListMat[ID_number+nely+self.checkCol+2]]
        self.DOFs=[dofListMat[2*(ID_number+self.checkCol)-1][0],dofListMat[2*(ID_number+self.checkCol)][0],dofListMat[2*(ID_number+self.checkCol+1)-1][0],dofListMat[2*(ID_number+self.checkCol+1)][0],dofListMat[2*(ID_number+nely+self.checkCol+1)-1][0],dofListMat[2*(ID_number+nely+self.checkCol+1)][0],dofListMat[2*(ID_number+nely+self.checkCol+2)-1][0],dofListMat[2*(ID_number+nely+self.checkCol+2)][0]]

    def updateNodes(self,*args):
        try:
            selected=nodeCanvas.find('withtag','nodeSelected')
            for j in selected:
                j=j-1
                for i in range(1,len(dofActiveList)):
                    dofActiveList[i][2*j-1][1]=True
                    dofActiveList[i][2*j][1]=True
        except:
            pass
        
    def selectElem(self,event,*args):
        global dofActiveList
        dofActiveList=['']
        #WIP (add ttk.label below meshCanvas to show errors and updates)
        print(f'You selected elem #{self.ID_number}')
        print(f'It is made of nodes #{self.Nodes[1]}, #{self.Nodes[2]}, #{self.Nodes[3]}, #{self.Nodes[4]}')
        print(f'It interacts with DOFs #{self.DOFs[0]}, #{self.DOFs[1]}, #{self.DOFs[2]}, #{self.DOFs[3]}, #{self.DOFs[4]}, #{self.DOFs[5]}, #{self.DOFs[6]}, #{self.DOFs[7]}')
        try:
            meshCanvas.itemconfigure('elemSelected',fill='grey75')
            meshCanvas.dtag('all','elemSelected')
        except:
            pass
        meshCanvas.addtag('elemSelected','withtag','current')
        meshCanvas.itemconfigure('elemSelected',fill='white')
        dofTemp=['']
        for i in range(8):
            dofTemp.append([self.DOFs[i],False,''])
        dofActiveList.append(dofTemp)

    def deselectElem(self,event,*args):
        global dofActiveList
        dofActiveList=['']
        try:
            meshCanvas.itemconfigure('current',fill='grey75')
            meshCanvas.dtag('current','elemSelected')
        except:
            pass
        selected=meshCanvas.find('withtag','elemSelected')
        for j in selected:
            dofTemp=['']
            for i in range(8):
                dofTemp.append([elemList[j].DOFs[i],False,''])
            dofActiveList.append(dofTemp)
        self.updateNodes()
        updateDOFs()
        updateNodeViz()
        
        
    def selectElemAdd(self,event,*args):
        global dofActiveList
        dofActiveList=['']
        #WIP (add ttk.label below meshCanvas to show errors and updates)
        print(f'You added elem #{self.ID_number} to the selection')
        print(f'It is made of nodes #{self.Nodes[1]}, #{self.Nodes[2]}, #{self.Nodes[3]}, #{self.Nodes[4]}')
        print(f'It interacts with DOFs #{self.DOFs[0]}, #{self.DOFs[1]}, #{self.DOFs[2]}, #{self.DOFs[3]}, #{self.DOFs[4]}, #{self.DOFs[5]}, #{self.DOFs[6]}, #{self.DOFs[7]}')
        meshCanvas.itemconfigure('elemSelected',fill='grey75')
        meshCanvas.addtag('elemSelected','withtag','current')
        meshCanvas.itemconfigure('elemSelected',fill='white')
        selected=meshCanvas.find('withtag','elemSelected')
        for j in selected:
            dofTemp=['']
            for i in range(8):
                dofTemp.append([elemList[j].DOFs[i],False,''])
            dofActiveList.append(dofTemp)
        self.updateNodes()
        updateDOFs()
        updateNodeViz()

    def selectElemLine(self,event,*args):
        global dofActiveList
        dofActiveList=['']
        selected=meshCanvas.find('withtag','elemSelected')
        checkSign=int(self.ID_number-selected[0])
        if checkSign > 0:
            start=selected[0]
            end=self.ID_number+1
        elif checkSign < 0:
            start=self.ID_number
            end=selected[0]+1
        else:
            return
        if len(selected)==1:
            if self.checkCol == elemList[selected[0]].checkCol:
                print ('yepCol')
                for i in range(start,end):
                    meshCanvas.addtag('elemSelected','withtag','elem%s'%i)
                meshCanvas.itemconfigure('elemSelected',fill='white')
            elif self.checkRow == elemList[selected[0]].checkRow:
                print ('yepRow')
                for i in range(start,end,nely):
                    meshCanvas.addtag('elemSelected','withtag','elem%s'%i)
                meshCanvas.itemconfigure('elemSelected',fill='white')
            else:
                setError('Can only select a horizontal or vertical line')
                return
        else:
            setError('Cannot start a line from more than one element')
            return
        selected=meshCanvas.find('withtag','elemSelected')
        for j in selected:
            dofTemp=['']
            for i in range(8):
                dofTemp.append([elemList[j].DOFs[i],False,''])
            dofActiveList.append(dofTemp)
        self.updateNodes()
        updateDOFs()
        updateNodeViz()
        print(f'You selected a line from elem #{start} to elem #{end-1}')

    

class nodeBox:
    def __init__(self,node,ID_number,*args):
        self.ID_number=ID_number
        self.node=node

    def selectNode(self,event,*args):
        global dofActiveList
        global selectedNodeVizList
        #WIP (add ttk.label below meshCanvas to show errors and updates)
        print(f'You selected node #{self.ID_number}')
        nodeCanvas.itemconfigure('nodeSelected',fill='grey50')
        nodeCanvas.addtag('nodeSelected','withtag','current')
        nodeCanvas.itemconfigure('nodeSelected',fill='grey80')
        selected=nodeCanvas.find('withtag','nodeSelected')
        selectedNodeVizList=['']
        try:
            for j in selected:
                j=j-1
                selectedNodeVizList.append(j)
                for i in range(1,len(dofActiveList)):
                    dofActiveList[i][2*j-1][1]=True
                    dofActiveList[i][2*j][1]=True
        except:
            pass
        updateDOFs()
        updateNodeViz()
        

    def deselectNode(self,event,*args):
        global dofActiveList
        dofActiveList=['']
        global selectedNodeVizList
        selectedNodeVizList=['']
        try:
            nodeCanvas.itemconfigure('current',fill='grey50')
            nodeCanvas.dtag('current','nodeSelected')
        except:
            pass
        selected=meshCanvas.find('withtag','elemSelected')
        for j in selected:
            dofTemp=['']
            for i in range(8):
                dofTemp.append([elemList[j].DOFs[i],False,''])
            dofActiveList.append(dofTemp)
        selected=nodeCanvas.find('withtag','nodeSelected')
        try:
            for j in selected:
                j=j-1
                selectedNodeVizList.append(j)
                for i in range(1,len(dofActiveList)):
                    dofActiveList[i][2*j-1][1]=True
                    dofActiveList[i][2*j][1]=True
        except:
            pass
        updateDOFs()
        updateNodeViz()
        
def apply(*args):
    try:
        valx.set(int(nelxVar.get()))
        nelyEntry.focus()
        gridSettingsText.set("The program will use a " +valx.get()+ " by [nely] grid mesh")
        valy.set(int(nelyVar.get()))
        applyButton.focus()
        gridSettingsText.set("The program will use a " +valx.get()+ " by " +valy.get()+ " grid mesh")
        drawMesh()
    except ValueError:
        pass

def setError(errorText):
    print(errorText)
    messagebox.showerror(title='Error',message=errorText)

def prepMesh(*args):
    global nelx
    global nely
    try:
        nelx=int(nelxVar.get())
        nely=int(nelyVar.get())
    except:
        pass
    if nelx*nely>22500:
        gridSettingsText.set("The program cannot use more than 22500 elements")
        meshInfoLabel.configure(foreground='red')
        return(22500)
    global meshFrame
    global mFs
    mFs=ttk.Style()
    mFs.configure('meshFrame.TFrame', borderwidth=2, relief='sunken')
    meshFrame=ttk.Frame(mainframe, style='meshFrame.TFrame', padding=1, width=0.850*screenW, height=0.750*screenH)
    #fix the formatting issue
    meshFrame.grid(column=1, row=3, columnspan=4, rowspan=3)
    global meshCanvas
    meshCanvas=Canvas(meshFrame, width=0.850*screenW, height=0.750*screenH)
    meshCanvas.grid(column=0,row=0,sticky=(N,W,E,S))
    global origX
    origX=meshCanvas.xview()[0]
    global origY
    origY=meshCanvas.yview()[0]
    global zoomHist
    zoomHist=1
    meshCanvas.bind("<MouseWheel>", doZoom)
    meshCanvas.bind('<ButtonPress-2>', lambda event: meshCanvas.scan_mark(event.x, event.y))
    meshCanvas.bind("<B2-Motion>", lambda event: meshCanvas.scan_dragto(event.x, event.y, gain=1))
    return(0)
    
def drawMesh(*args):
    global elemList
    global nodeListMat
    global dofListMat
    global dofActiveList
    global nodeColor
    global updateNodeVizTemp
    try:
        clearMesh()
    except:
        pass
    checkTemp=prepMesh()
    if checkTemp==0:
        meshInfoLabel.configure(foreground='black')
    else:
        setError('Cannot have more than 22500 elements')
        return
    resetViewButton.configure(state='enabled')
    elemNumber=1
    elemList=['']
    nodeListMat=['']
    dofListMat=['']
    dofActiveList=['']
    for i in range(1,(nelx+1)*(nely+1)+1):
        nodeListMat.append(i)
    for i in range(1,2*(nelx+1)*(nely+1)+1):
        dofListMat.append([i,''])
    scaleFactor=math.floor(min((0.85*screenW)/nelx,(0.75*screenH)/nely))
    if scaleFactor>10:
        scaleFactor-=1
    else:
        pass
    centeringX=math.ceil(((0.85*screenW)-(scaleFactor*nelx))/2)+1
    centeringY=math.ceil(((0.75*screenH)-(scaleFactor*nely))/2)+1
    for i in range(centeringX,centeringX+scaleFactor*nelx,scaleFactor):
        for j in range(centeringY,centeringY+scaleFactor*nely,scaleFactor):
               elem=meshCanvas.create_rectangle(i,j,i+scaleFactor,j+scaleFactor,fill="gray75",outline='black',tags=('elem%s'% elemNumber))
               id=elem
               elemList.append(elemBox(elem, elemNumber))
               meshCanvas.tag_bind(id,'<ButtonRelease-1>',elemList[elemNumber].selectElemAdd)
               #meshCanvas.tag_bind(id,'<Control-ButtonRelease-1>',elemList[elemNumber].selectElemAdd)
               meshCanvas.tag_bind(id,'<Shift-ButtonRelease-1>',elemList[elemNumber].selectElemLine)
               meshCanvas.tag_bind(id,'<ButtonRelease-3>',elemList[elemNumber].deselectElem)
               elemNumber+=1
    radius=math.ceil(0.15*scaleFactor)
    nodeNumber=1
    for i in range(nelx+1):
        for j in range(nely+1):
            Xviz=i*scaleFactor+centeringX
            Yviz=j*scaleFactor+centeringY
            SPCviz=meshCanvas.create_oval(Xviz-radius,Yviz-radius,Xviz+radius,Yviz+radius,fill="grey50",outline='grey50',tags=('node%s'% nodeNumber))
            nodeNumber+=1
    nodeColor='grey80'
    updateNodeVizTemp=[1]
    
def updateNodeViz(*args):
    global nodeColor
    global updateNodeVizTemp
    try:
        for i in updateNodeVizTemp:
            meshCanvas.itemconfigure('node%d'%i,fill='grey50',outline='grey50')
        elemSelected=meshCanvas.find('withtag','elemSelected')
        updateNodeVizTemp=[]
        for i in range(1,len(selectedNodeVizList)):
            for j in elemSelected:
                updateNodeVizTemp.append(elemList[j].Nodes[selectedNodeVizList[i]])
        updateNodeVizTemp=list(dict.fromkeys(updateNodeVizTemp))
        for i in updateNodeVizTemp:
            meshCanvas.itemconfigure('node%d'%i,fill=nodeColor,outline=nodeColor)
            meshCanvas.dtag('node%d'%i,'grey80')
            meshCanvas.dtag('node%d'%i,'HotPink')
            meshCanvas.dtag('node%d'%i,'aqua')
            meshCanvas.addtag(nodeColor,'withtag','node%d'%i)
        nodeColor='grey80'
    except:
        pass
    
def doZoom(event):
    global zoomHist
    factor = 1.001 ** event.delta
    meshCanvas.scale(ALL, (0.425*screenW), (0.375*screenH), factor, factor)
    zoomHist*=factor


#Creating Tk instance

root = Tk()
root.title("Topology99 Input GUI")
screenW=root.winfo_screenwidth()
screenH=root.winfo_screenheight()
root.state('zoomed')

#Styles

frames=ttk.Style()
frames.configure('frame.TFrame', background='grey90')

entrys=ttk.Style()
entrys.configure('entry.TEntry', background='grey90')

buttons=ttk.Style()
buttons.configure('button.TButton', background='grey90')

labels=ttk.Style()
labels.configure('label.TLabel', background='grey90')

#Initializing the main frame

mainframe=ttk.Frame(root, padding="3 3 12 12",style='frame.TFrame')
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
root.columnconfigure(0,weight=1)
root.rowconfigure(0,weight=1)

#User input for size of the mesh

ttk.Label(mainframe, text="Number of elements on x : ",style='label.TLabel').grid(column=1,row=1,sticky=E)

nelx=0
nelxVar=StringVar()
nelxEntry=ttk.Entry(mainframe, width=7, textvariable=nelxVar,style='entry.TEntry')
nelxEntry.grid(column=2,row=1,sticky=(W,E))

ttk.Label(mainframe, text="Number of elements on y : ",style='label.TLabel').grid(column=3,row=1,sticky=E)

nely=0
nelyVar=StringVar()
nelyEntry=ttk.Entry(mainframe, width=7, textvariable=nelyVar,style='entry.TEntry')
nelyEntry.grid(column=4,row=1,sticky=(W,E))

valx=StringVar()
valy=StringVar()
applyButton=ttk.Button(mainframe, text="Apply", command=apply,style='button.TButton')
applyButton.grid(column=5,row=1,sticky=W)

gridSettingsText=StringVar()
gridSettingsText.set("The program will use a [nelx] by [nely] grid mesh")
meshInfoLabel=ttk.Label(mainframe,textvariable=gridSettingsText,style='label.TLabel')
meshInfoLabel.grid(column=1,row=2,columnspan=4)

prepMesh()

#------------------------------------------------------------------------------------------------------------|Node and DOF Selection|----------------------------------------------------------------------------------------------------
nodeFrame=ttk.Frame(mainframe, width=0.12*screenW, height=0.215*screenW,style='meshFrame.TFrame',padding=5)
nodeFrame.grid(column=5,row=3)
nodeFrame.columnconfigure(2)
nodeFrame.grid_propagate(False)

ttk.Label(nodeFrame,text='Loads and Constraints').grid(column=1,row=1,columnspan=2,sticky='')

nodeCanvas=Canvas(nodeFrame,width=(0.12*screenW-10),height=(0.12*screenW-10))
nodeCanvas.grid(column=1,row=2,columnspan=2,sticky='')

def setupNodeCanvas(*args):
    global nodeList
    start=0.02*screenW
    end=0.1*screenW-10
    radius=0.015*screenW
    nodeCanvas.create_rectangle(start,start,end,end,fill='white',outline='black')
    nodeNumber=1
    nodeList=['']
    for i in [start,end]:
        for j in [start,end]:
            node=nodeCanvas.create_oval(i-radius,j-radius,i+radius,j+radius,fill='grey50',outline='black',tags='node%s'% nodeNumber)
            id=node
            nodeList.append(nodeBox(node,nodeNumber))
            nodeCanvas.tag_bind(id,'<ButtonRelease-1>',nodeList[nodeNumber].selectNode)
            nodeCanvas.tag_bind(id,'<ButtonRelease-3>',nodeList[nodeNumber].deselectNode)
            nodeNumber+=1
    
setupNodeCanvas()

axisXVar=BooleanVar()
axisXVar.set(False)
axisYVar=BooleanVar()
axisYVar.set(False)

def findDOFs(*args):
    selected=['']
    for i in range(1,len(dofActiveList)):
        for j in range(1,9):
            if dofActiveList[i][j][1]==True:
                 selected.append(dofActiveList[i][j])
            else:
                pass
    return selected

def removeDuplicates(*args):
    temp=['']
    out=['']
    selected=findDOFs()
    for i in range(1,len(selected)):
        temp.append(selected[i][0])
    temp=list(dict.fromkeys(temp))
    for i in range(1,len(temp)):
        out.append([temp[i],'',''])
    for i in range(1,len(out)):
        for j in range(1,len(selected)):
            if out[i][0]==selected[j][0]:
                out[i][1]=selected[j][1]
                out[i][2]=selected[j][2]
            else:
                pass
    return out

def getAxis(*args):
    axisX=axisXVar.get()
    axisY=axisYVar.get()
    axis=[axisX,axisY]
    return axis

def updateDOFs(*args):
    try:
        global selectedDOFs
        global LCUIButtonCounter
        selectedDOFs=removeDuplicates()
        axis=getAxis()
        for i in range(1,len(selectedDOFs)):
            if i%2==1:
                selectedDOFs[i][1]=axis[0]
            else:
                selectedDOFs[i][1]=axis[1]
        if LCUIButtonCounter==0:
            LCUIButtonCounter+=1
        else:
            if selectLC==0:
                root.unbind("<Return>")
                root.bind("<Return>",applySPC)
            else:
                root.unbind("<Return>")
                root.bind("<Return>",applyButtonState[loadBox.current()])
    except:
        pass

buttonFrame=ttk.Frame(nodeFrame,padding=15)
buttonFrame.grid(column=1,columnspan=2,row=4,rowspan=2)
buttonFrame.columnconfigure(5)

ttk.Label(buttonFrame,text="       ").grid(column=3,row=1,rowspan=2)

axisXcb=ttk.Checkbutton(buttonFrame,text='X axis', variable=axisXVar,onvalue=True,offvalue=False,command=updateDOFs)
axisXcb.grid(column=4,row=1,sticky=E)
axisYcb=ttk.Checkbutton(buttonFrame,text='Y axis', variable=axisYVar,onvalue=True,offvalue=False,command=updateDOFs)
axisYcb.grid(column=4,row=2,sticky=E)

ttk.Separator(nodeFrame,orient=HORIZONTAL).grid(row=3,column=1,columnspan=2,sticky=(W,E),padx=25)
ttk.Separator(nodeFrame,orient=HORIZONTAL).grid(row=6,column=1,columnspan=2,sticky=(W,E),padx=25)

#------------------------------------------------------------------------------------------------------------|Loads and Constraints|----------------------------------------------------------------------------------------------------

selectLCVar=IntVar()
selectLCVar.set(0)

def drawConstraintUI(*args):
    try:
        loadFrame.destroy()
    except:
        pass
    
    global SPCFrame
    SPCFrame=ttk.Frame(nodeFrame,padding=30)
    SPCFrame.grid(column=1,columnspan=2,row=7)
    
    global applySPC
    
    def applySPC(*args):
        global nodeColor
        try:
            for i in range(1,len(selectedDOFs)):
                if selectedDOFs[i][1]==True:
                    selectedDOFs[i][2]=0
                else:
                    pass
            for i in range(1,len(dofListMat)):
                for j in range(1,len(selectedDOFs)):
                    if selectedDOFs[j][0]==dofListMat[i][0] and selectedDOFs[j][2]==0:
                        dofListMat[i][1]=0
                    else:
                        pass
            nodeColor='HotPink'
            updateNodeViz()
            clearSelected()
        except:
            pass
        return
    
    SPCButton=ttk.Button(SPCFrame,text="Apply Constraints",command=applySPC)
    SPCButton.grid(column=1,row=1)
    if LCUIButtonCounter>0:
        root.unbind("<Return>")
        root.bind("<Return>",applySPC)
    else:
        pass
                                                                                                
def drawLoadsUI(*args):
    try:
        SPCFrame.destroy()
    except:
        pass
    
    global loadFrame
    loadFrame=ttk.Frame(nodeFrame,padding=10)
    loadFrame.grid(column=1,columnspan=2,row=7)

    loadEntryVar=StringVar()
    loadEntry=ttk.Entry(loadFrame,textvariable=loadEntryVar,width=7)
    loadEntry.grid(column=2,row=1)
    
    global applyLoadNodal
    global applyLoadDistrib
    
    def applyLoadNodal(*args):
        global nodeColor
        try:
            load=float(loadEntryVar.get())
            if load-int(load)==0.0:
                load=int(load)
            else:
                pass
            if load == (0 or 0.0):
                setError('Loads can not be equal to 0')
                return
            else:
                pass
            for i in range(1,len(selectedDOFs)):
                if selectedDOFs[i][1]==True:
                    selectedDOFs[i][2]=load
                else:
                    pass
            print(selectedDOFs)
            for i in range(1,len(dofListMat)):
                for j in range(1,len(selectedDOFs)):
                    if selectedDOFs[j][0]==dofListMat[i][0] and selectedDOFs[j][2]==load:
                        dofListMat[i][1]=load
                        print(dofListMat[i])
                    else:
                        pass
            nodeColor='aqua'
            updateNodeViz()
            clearSelected()
        except:
            pass
        return

    def applyLoadDistrib(*args):
        global nodeColor
        try:
            length=len(selectedDOFs)
            loadedNodes=0
            for i in range(1,length):
                loadedNodes+=0.5
            load=((int(loadEntryVar.get()))/loadedNodes)
            if load == 0.0:
                setError('Loads can not be equal to 0')
                return
            else:
                pass
            for j in range(1,int((length+1)/2)):
                if selectedDOFs[2*j-1][1]==True and selectedDOFs[2*j][1]==False:
                    selectedDOFs[2*j-1][2]=load
                elif selectedDOFs[2*j-1][1]==False and selectedDOFs[2*j][1]==True:
                    selectedDOFs[2*j][2]=load
                else:
                    setError('Cannot apply a distributed load to two axes at once')
                    return                
            print(selectedDOFs)            
            for i in range(1,len(dofListMat)):
                for j in range(1,length):
                    if selectedDOFs[j][0]==dofListMat[i][0] and selectedDOFs[j][2]==load:
                        dofListMat[i][1]=load
                        print(dofListMat[i])
                    else:
                        pass
            nodeColor='aqua'
            updateNodeViz()
            clearSelected()
        except:
            print('error')
            pass
        return
    
    applyButton=ttk.Button(loadFrame,text="Apply Load",command=applyLoadNodal)
    applyButton.grid(column=1,columnspan=2,row=2,sticky='')
    global applyButtonState
    applyButtonState=[applyLoadNodal,applyLoadDistrib]
    
    def updateApplyButton(*args):
        loadEntry.focus()
        i=loadBox.current()
        applyButton.configure(command=applyButtonState[i])
        if LCUIButtonCounter>0:
            root.unbind("<Return>")
            root.bind("<Return>",applyButtonState[i])
        else:
            pass
        return
    
    global loadBoxStr
    global loadBox
    loadBoxStr=StringVar()
    loadBox=ttk.Combobox(loadFrame,textvariable=loadBoxStr,values=('Nodal','Distributed'),state='readonly',width=12)
    loadBox.current(0)
    loadBox.grid(column=1,row=1)
    loadBox.bind('<<ComboboxSelected>>',updateApplyButton)

    for child in loadFrame.winfo_children():
        child.grid_configure(padx=10,pady=5)
    
def drawLCUI(*args):
    global selectLC
    selectLC=selectLCVar.get()
    if selectLC==0:
        drawConstraintUI()
    else:
        drawLoadsUI()
    global LCUIButtonCounter
    if LCUIButtonCounter==0:
        LCUIButtonCounter+=1
    else:
        if selectLC==0:
            root.unbind("<Return>")
            root.bind("<Return>",applySPC)
        else:
            root.unbind("<Return>")
            root.bind("<Return>",applyButtonState[loadBox.current()])

LCUIButtonCounter=0

selectSPC=ttk.Radiobutton(buttonFrame,text='Constraints',variable=selectLCVar,value=0,command=drawLCUI)
selectSPC.grid(column=2,row=1,sticky=W)
selectLoad=ttk.Radiobutton(buttonFrame,text='Loads',variable=selectLCVar,value=1,command=drawLCUI)
selectLoad.grid(column=2,row=2,sticky=W)

drawLCUI()


#---------------------------------------------------------------------------------------------------------------|Reset Function|---------------------------------------------------------------------------------------------------------

def resetView(*args):
    global zoomHist
    try:
        meshCanvas.xview_moveto(origX)
        meshCanvas.yview_moveto(origY)
        meshCanvas.scale(ALL,(0.425*screenW), (0.375*screenH),1/zoomHist,1/zoomHist)
        zoomHist=1
    except:
        pass

#Reset GUI

resetViewButton=ttk.Button(mainframe, text="Reset view", command=resetView, style='button.TButton', state='disabled')
resetViewButton.grid(column=5,row=4)

#---------------------------------------------------------------------------------------------------------------|Clear Functions|--------------------------------------------------------------------------------------------------------

def clearNone(*args):
    return

def clearSelected(*args):
    global updateNodeVizTemp
    global selectedNodeVizList
    global dofActiveList
    try:
        meshCanvas.itemconfigure('elemSelected',fill='grey75')
        meshCanvas.dtag('all','elemSelected')
        updateNodeVizTemp=[]
        selectedNodeVizList=['']
        dofActiveList=['']
        nodeCanvas.itemconfigure('nodeSelected',fill='grey50')
        nodeCanvas.dtag('all','nodeSelected')
        meshCanvas.itemconfigure('grey80',fill='grey50',outline='grey50')
        meshCanvas.dtag('grey80')
    except:
        pass
    
        
def clearMesh(*args):
    global dofActiveList
    global elemList
    global nodeListMat
    global dofListMat
    elemList=['']
    nodeListMat=['']
    dofListMat=['']
    dofActiveList=['']
    meshCanvas.delete('all')
    resetViewButton.configure(state='disabled')
    
def clearLoads(*args):
    for i in range(1,len(dofListMat)):
        if type(dofListMat[i][1])==int and dofListMat[i][1]!=0:
            dofListMat[i][1]=''
            print(dofListMat[i])
        elif type(dofListMat[i][1])==float and dofListMat[i][1]!=0.0:
            dofListMat[i][1]=''
            print(dofListMat[i])
        else:
            pass
    meshCanvas.itemconfigure('aqua',fill='grey50',outline='grey50')
    meshCanvas.dtag('aqua')
    return

def clearSPC(*args):
    for i in range(1,len(dofListMat)):
        if type(dofListMat[i][1])==int and dofListMat[i][1]==0:
            dofListMat[i][1]=''
            print(dofListMat[i])
        else:
            pass
    meshCanvas.itemconfigure('HotPink',fill='grey50',outline='grey50')
    meshCanvas.dtag('HotPink')
    return

#Clear GUI

clearFrame=ttk.Frame(mainframe, style='frame.TFrame')
clearFrame.grid(column=5, row=5)

clearBoxStr=StringVar()
clearBox=ttk.Combobox(clearFrame,textvariable=clearBoxStr,values=('None','Selected','Constraints','Loads','Mesh'),state='readonly')
clearBox.current(0)
clearBox.grid(column=1,row=1)

clearButtonState=[('disabled',clearNone),('enabled',clearSelected),('enabled',clearSPC),('enabled',clearLoads),('enabled',clearMesh)]
clearButton=ttk.Button(clearFrame, text="Clear",state='disabled', command=clearNone,style='button.TButton')
clearButton.grid(column=1,row=2)

def updateClearButton(*args):
    i=clearBox.current()
    clearButton.configure(state=clearButtonState[i][0],command=clearButtonState[i][1])
clearBox.bind('<<ComboboxSelected>>',updateClearButton)

for child in clearFrame.winfo_children():
    child.grid_configure(padx=5,pady=5)

#----------------------------------------------------------------------------------------------------------------|Output block|----------------------------------------------------------------------------------------------------------

outputFrame=ttk.Frame(mainframe,relief='sunken',borderwidth=2, width=0.75*screenW, height=0.08*screenH)
outputFrame.grid(column=2,columnspan=4,row=6,sticky=E)

penalVar=StringVar()
penalVar.set(3)
volfrVar=StringVar()
volfrVar.set(0.5)
rminVar=StringVar()
rminVar.set(2)
solverVar=StringVar()

dirNameVar=StringVar()
dirNameVar.set(os.getcwd().replace('\\','/'))
dirName=dirNameVar.get()
def getDir(*args):
    global dirName
    dirName=filedialog.askdirectory()
    dirName.replace('\\','/')
    dirNameVar.set(dirName)
    print(dirName)
    return

def writeOutput(*args):
    global dirName
    if dirNameVar.get()=='':
        setError('Please choose a folder')
        return
    try:
        os.remove(f"{dirNameVar.get()}/pyout.txt")
    except:
        pass
    f=open(f"{dirNameVar.get()}/pyout.txt","x")
    
    output=[f"{nelx}"]
    output.append('\n')
    outputstr=''.join(map(str,output))
    #---------------------------------------
    output=[f"{nely}"]
    output.append('\n')
    outputstr=outputstr+''.join(map(str,output))
    #---------------------------------------
    output=[f"{volfrVar.get()}"]
    output.append('\n')
    outputstr=outputstr+''.join(map(str,output))
    #---------------------------------------
    output=[f"{math.floor(float(penalVar.get()))}"]
    output.append('\n')
    outputstr=outputstr+''.join(map(str,output))
    #---------------------------------------
    output=[f"{math.floor(float(rminVar.get()))}"]
    output.append('\n')
    outputstr=outputstr+''.join(map(str,output))
    #---------------------------------------
    output=["["]
    for i in range(1,len(dofListMat)):
        if type(dofListMat[i][1])==int and dofListMat[i][1]==0:
            output.append(str(dofListMat[i][0]))
            output.append(', ')
    if output == ["["]:
        setError('No boundary conditions have been set')
        f.close()
        return
    else:
        output.pop()
    output.append(']\n')
    outputstr=outputstr+''.join(map(str,output))
    #---------------------------------------
    output=["["]
    nbloads=0
    for i in range(1,len(dofListMat)):
        if (type(dofListMat[i][1])==int and dofListMat[i][1]!=0) or (type(dofListMat[i][1])==float and dofListMat[i][1]!=0.0):
            output.append(str(dofListMat[i]))
            output.append(', ')
            nbloads+=1
    if output == ["["]:
        setError('No loads have been set')
        f.close()
        return
    else:
        output.pop()
    output.append(']\n')
    outputstr=outputstr+''.join(map(str,output))+str(nbloads)+'\n'+dirName
    #---------------------------------------
    f.write(outputstr)
    f.close()
    octaveExePath = octExeVar.get()
    try:
        # Execute the MATLAB script using subprocess
        dirName=dirNameVar.get()
        solver=solverVar.get()
        pyDir=os.getcwd().replace('\\','/')
        try:
            dirName.replace('\\','/')
        except:
            pass
        octaveProc=subprocess.Popen(f'{octaveExePath}',stdin=PIPE,text=True)
        if dirName != pyDir:
            try:
                os.remove('pyout.txt')
            except:
                pass
            
            octaveProc.communicate(f'addpath("{pyDir}"); addpath("{dirName}"); topGUI_{solver}')
        else:
            octaveProc.communicate(f'addpath("{dirName}"); topGUI_{solver}')
        os.remove(dirName+'/pyout.txt')
        print("MATLAB script executed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing MATLAB script: {e}")
    return

dirNameEntry=ttk.Entry(outputFrame,textvariable=dirNameVar,state='readonly',width=125)
dirNameEntry.grid(column=4,row=1,sticky=E)

getDirButton=ttk.Button(outputFrame,text='Choose folder',command=getDir)
getDirButton.grid(column=5,row=1)

startButton=ttk.Button(outputFrame,text='Export and run',command=writeOutput)
startButton.grid(column=5,row=2)

outputEntryFrame=ttk.Frame(outputFrame)
outputEntryFrame.grid(column=4,row=2,sticky=E)

def volfrBoundsCheck(*args):
    if float(volfrVar.get())>0.99:
        volfrVar.set(0.99)
    elif float(volfrVar.get())<0.01:
        volfrVar.set(0.01)
    else:
        pass

def penalBoundsCheck(*args):
    if float(penalVar.get())>15.0:
        penalVar.set(15)
    elif float(penalVar.get())<1.0:
        penalVar.set(1)
    else:
        pass

def rminBoundsCheck(*args):
    if float(rminVar.get())>15.0:
        rminVar.set(15)
    elif float(rminVar.get())<1.0:
        rminVar.set(1)
    else:
        pass

ttk.Label(outputEntryFrame,text='Volume Fraction = ',padding=(20,0,0,0)).grid(column=1,row=1,sticky=E)
volfrSb=ttk.Spinbox(outputEntryFrame,from_=0.01,to=0.99,increment=0.05,textvariable=volfrVar,width=7)
volfrSb.grid(column=2,row=1,sticky=W)
volfrSb.bind('<FocusOut>',volfrBoundsCheck)

ttk.Label(outputEntryFrame,text='Penalization = ',padding=(20,0,0,0)).grid(column=3,row=1,sticky=E)
penalSb=ttk.Spinbox(outputEntryFrame,from_=1.0,to=15.0,increment=1.0,textvariable=penalVar,width=7)
penalSb.grid(column=4,row=1,sticky=W)
penalSb.bind('<FocusOut>',penalBoundsCheck)

ttk.Label(outputEntryFrame,text='Minimum dimension = ',padding=(20,0,0,0)).grid(column=5,row=1,sticky=E)
rminSb=ttk.Spinbox(outputEntryFrame,from_=1.0,to=15.0,increment=1.0,textvariable=rminVar,width=7)
rminSb.grid(column=6,row=1,sticky=W)
rminSb.bind('<FocusOut>',rminBoundsCheck)

ttk.Label(outputEntryFrame,text='Select solver = ',padding=(20,0,0,0)).grid(column=7,row=1,sticky=E)
solverBox=ttk.Combobox(outputEntryFrame,textvariable=solverVar,values=('SIMP','softbeso','levelset_octave'),state='readonly',width=10)
solverBox.current(0)
solverBox.grid(column=8,row=1,sticky=W)

#------------------------------------------------------------------------------------------------------------------|Settings|------------------------------------------------------------------------------------------------------------

octExeVar=StringVar()
try:
    fSettings=open('settings.txt','r')
    octExeVar.set(fSettings.read())
except:
    pass

def getOctExe(*args):
    octExe=filedialog.askopenfilename()
    octExe.replace('\\','/')
    octExeVar.set(octExe)
    f=open("settings.txt","w")
    f.write(octExe)
    f.close()
    

octExeEntry=ttk.Entry(outputFrame,textvariable=octExeVar,state='readonly',width=115)
octExeEntry.grid(column=1,row=1)

octExeGetButton=ttk.Button(outputFrame,text='Set Octave Path',command=getOctExe)
octExeGetButton.grid(column=2,row=1)

ttk.Label(outputFrame,text=r'Example: "C:/Program Files/GNU Octave/Octave-8.2.0/mingw64/bin/octave-gui.exe"    octave-gui.exe is recommended over octave-cli.exe').grid(column=1,columnspan=2,row=2,sticky=W)

ttk.Separator(outputFrame,orient=VERTICAL).grid(row=1,column=3,rowspan=2,sticky=(N,S),padx=10)
#---------------------------------------------------------------------------------------------------------------|mainloop + init|--------------------------------------------------------------------------------------------------------
for child in outputFrame.winfo_children():
    child.grid_configure(padx=5,pady=5)
    
for child in mainframe.winfo_children():
    child.grid_configure(padx=5,pady=5)

nelxEntry.focus()
root.bind("<Return>",apply)

root.mainloop()
