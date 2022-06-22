from tkinter import *
from tkinter import ttk
import epics
import time
import numpy as np
import datetime
import pylab
import matplotlib.pyplot as plt
# import tkMessageBox as tbox
import tkinter.messagebox as tbox
import os

Open = "7ida:rShtrA:Open"
Close = "7ida:rShtrA:Close"
Trig = "7idb:DG1:TriggerDelayBO"
TrigDone = "7idbSAZ:cam1:LiveMode.VAL"
MeanV = "7idbSAZ:Stats1:MeanValue_RBV"
Delaytime = "7idb:DG2:ADelayAO"
randomFrame = "7idbSAZ:cam1:RandomFrames"
focus="7idb:m7.VAL"
chamberX="7idb:m1.VAL"
chamberY="7idb:m2.VAL"
chamberYR="7idb:m2.RBV"
chamberXR="7idb:m1.RBV"
Delaytime="7idb:DG2:ADelayAO"
IDGAP="ID07us:GapSet.VAL"
IDDO="ID07us:Start.VAL"
TrigNum = "7idbSAZ:randomScan:num"
randomScan="7idbSAZ:randomScan:do"

SCU_CURRENT="ID07ds:MainCurrentRdbk.VAL"

def setPV(pvname, val, iswait = True):
    epics.caput(pvname, val, wait=iswait, timeout=1000000.0)

def popupmsg(msg):
    popup = Tk()
    popup.wm_title("ERROR!")
    label = ttk.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

def close_shutter(trys=5):
    for i in range(trys):
        setPV(Close, 1)
        time.sleep(3)
        if epics.caget("PB:07ID:STA_A_FES_CLSD_PL.VAL") == 1:
            # 1 = ON, shutter is closed
            # 0 = OFF, shutter is open
            if i > 0:
              print("---- retry succeeded! ----")
            return True
        else:
            print("Warnning: failed to close shutter, will retry (%d / %d)" % (i+1, trys))
            time.sleep(3)
    return False

def open_shutter(trys=5):
    #if epics.caget(SCU_CURRENT) >= 1 and \
            #epics.caget(IDGAP) <= 50:
        #msg = "Error! Do not use Undulator A and SCU at the same time!\n" + \
              #" ---- 1> set SCU current = 0 to use Undulator A, or \n" + \
              #" ---- 2> set Undulator A gap > 50 to use SCU"
        #popupmsg(msg)
        #close_shutter()
        #return False 

    for i in range(trys):
        setPV(Open,1)
        time.sleep(3)
        if epics.caget("PB:07ID:STA_A_FES_CLSD_PL.VAL") == 0:
            # 1 = ON, shutter is closed
            # 0 = OFF, shutter is open
            # wait until shutter is stable
	    # time.sleep(20)
            if i > 0:
              print("---- retry succeeded! ----")
            return True
        else:
            print("Warnning: failed to open shutter, will retry (%d / %d)" % (i+1, trys))
            time.sleep(3)


    timestr=datetime.datetime.now().strftime("%B-%d-%Y_%H:%M:%S")
    print("Error: cannot open shutter @ %s" % timestr)
    close_shutter()
    # clean up procedures, set shutter to close
    # setPV(Close,1)
    # time.sleep(3)
    return False


class Photron:

    def __init__(self, master):
        
        self.master = master

        master.title('Photron Scans')
        master.configure(bg = '#DFDCE3')
        
        self.tlabel = Label(master, text='Photron Scans', width=30, height=3, fg='#262228')

        # Scan Buttons
        self.dummyBut = Button(master, height=1, width=15, text='Dummy Scan', command=self.dummy)
        self.delayBut = Button(master, height=1, width=15, text='Delay Scan', command=self.delay)
        self.focusBut = Button(master, height=1, width=15, text='Focus Scan', command=self.focus)
        self.Scan2DBut = Button(master, height=1, width=15, text='2D Position Scan', command=self.Scan2D)

        self.ReshadingBut = Button(master, height=1, width=15, text='Re-Shading', command=self.MyShading)

        self.dummyBut.configure(bg='#4ABDAC')
        self.delayBut.configure(bg='#4ABDAC')
        self.focusBut.configure(bg='#4ABDAC')
        self.Scan2DBut.configure(bg='#4ABDAC')          
        self.ReshadingBut.configure(bg='#4ABDAC')               

        # Geometry
        self.tlabel.pack()
        self.dummyBut.pack(pady=10)
        self.delayBut.pack(pady=10)
        self.focusBut.pack(pady=10)
        self.Scan2DBut.pack(pady=10)
        self.ReshadingBut.pack(pady=10)

    def MyShading(self):
        self.ReshadingBut.configure(bg='#FC4A1A')
        pvname = "7idbSAZ:cam1:"
        print("AcquireMode --> Live")
        epics.caput(pvname + "AcquireMode", "Live", wait=True, timeout=100000.0)
        time.sleep(2)
        print("ShadingMode --> Off")
        epics.caput(pvname + "ShadingMode", "Off", wait=True, timeout=100000.0)
        time.sleep(2)
        print("ShadingMode --> On")
        epics.caput(pvname + "ShadingMode", "On", wait=True, timeout=100000.0)
        time.sleep(5)
        print("AcquireMode --> Record")
        epics.caput(pvname + "AcquireMode", "Record", wait=True, timeout=100000.0)
        print("Re-Shading Done.")
        self.ReshadingBut.configure(bg='#4ABDAC')               


    def dummy(self):
        def on_closing():
            self.dummyBut.configure(bg='#4ABDAC')
            dum.destroy()
        self.dummyBut.configure(bg='#FC4A1A')
        dum = Toplevel()
        gui = PhotronDummy(dum)
        dum.protocol("WM_DELETE_WINDOW", on_closing)
        dum.mainloop()

    def delay(self):
        def on_closing():
            self.delayBut.configure(bg='#4ABDAC')
            delay_root.destroy()
        self.delayBut.configure(bg='#FC4A1A')
        delay_root = Toplevel()
        gui = PhotronDelay(delay_root)
        delay_root.protocol("WM_DELETE_WINDOW", on_closing)
        delay_root.mainloop()

    def focus(self):
        def on_closing():
            self.focusBut.configure(bg='#4ABDAC')
            foc.destroy()
        self.focusBut.configure(bg='#FC4A1A')
        foc = Toplevel()
        gui = PhotronFocus(foc)
        foc.protocol("WM_DELETE_WINDOW", on_closing)
        foc.mainloop()
    def Scan2D(self):
        def on_closing():
            self.Scan2DBut.configure(bg='#4ABDAC')
            scan.destroy()
        self.Scan2DBut.configure(bg='#FC4A1A')
        scan = Toplevel()
        gui = PhotronScan2D(scan)
        scan.protocol("WM_DELETE_WINDOW", on_closing)
        scan.mainloop

class PhotronScan2D:
    
    locationid = 1

    def __init__(self, master):
        
        self.master = master
        master.title("7IDB-Camera Trig & Location Scan Control")
        
        self.cdv = StringVar()
        self.lcl = StringVar()
        self.itnum = StringVar()
        self.gotoev = StringVar()
        self.savepath = StringVar()
        self.ddltime = DoubleVar()
        self.didgap = DoubleVar()
        self.interv = DoubleVar()
        self.itnum2 = StringVar()
        self.ddltime2 = DoubleVar()
        self.didgap2 = DoubleVar()
        self.interv2 = DoubleVar()
        self.itnum3 = StringVar()
        self.ddltime3 = DoubleVar()
        self.didgap3 = DoubleVar()
        self.interv3 = DoubleVar()
        self.isidgap = IntVar()
        self.isdelay = IntVar() 
        self.Rframe = IntVar()  
        self.startp = IntVar()
        self.endp = IntVar()

        self.itnum.set("10")
        self.gotoev.set("1")
        self.didgap.set(25)
        self.ddltime.set(1.55)
        self.itnum2.set("10")
        self.didgap2.set(25)
        self.ddltime2.set(0.2)
        self.itnum3.set("10")
        self.didgap3.set(19)
        self.ddltime3.set(2.1)
        self.interv.set(1)
        self.interv2.set(1)
        self.interv3.set(1)
        self.cdv.set("Welcome!")
        self.isidgap.set(0)
        self.isdelay.set(0)
        self.savepath.set(epics.caget("7idbSAZ:TIFF1:FilePath",as_string=True))
        self.Rframe.set(250)
        self.startp.set(0)
        self.endp.set(0)

        self.EditPB = Button(master,text="Edit Points List", command=self.EPB, bg='#4ABDAC',font=("verdana",12))
        self.MEB = Button(master,text="Do DE", command=self.MEDOAll, bg='#4ABDAC',font=("verdana",12))
        self.SEB = Button(master,text="Do SE", command=self.SEDOAll, bg='#4ABDAC',font=("verdana",12))
        self.NMB = Button(master,text="Do NM", command=self.NMDOAll, bg='#4ABDAC',font=("verdana",12))
        self.PMEB = Button(master,text="DE Points", command=self.MEPoint, bg='#4ABDAC',font=("verdana",12))
        self.PSEB = Button(master,text="SE Points", command=self.SEPoint, bg='#4ABDAC',font=("verdana",12))
        self.PNMB = Button(master,text="NM Points", command=self.NMPoint, bg='#4ABDAC',font=("verdana",12))
        self.addB = Button(master,text="Next P", command=self.ADDDO, bg='#4ABDAC',font=("verdana",12))
        self.minusB = Button(master,text="Previous P", command=self.MINUSDO, bg='#4ABDAC',font=("verdana",12))
        self.gotoB = Button(master,text="Goto P", command=self.GOTODO, bg='#4ABDAC',font=("verdana",12))
        self.Contd = Label(master, text="Counting down", textvariable=self.cdv, fg='blue', font=("Helvetica",14))
        self.Locationfo=Label(master, text="Location", textvariable=self.lcl, fg='blue', font=("Helvetica",15))
        self.Ltnum = Label(master, text="Repeat",font=("verdana",8))
        self.Ldltime = Label(master, text="Delay Time / us",font=("verdana",8))
        self.Lidgap = Label(master, text="ID Gap / mm",font=("verdana",8))
        self.Linterv = Label(master, text="Record Delay / s",font=("verdana",8))
        self.e1 = Entry(master,textvariable=self.itnum, width=10,font=("verdana",12))
        self.e2 = Entry(master,textvariable=self.ddltime, width=10,font=("verdana",12))
        self.e3 = Entry(master,textvariable=self.didgap, width=10,font=("verdana",12))
        self.e4 = Entry(master,textvariable=self.itnum2, width=10,font=("verdana",12))
        self.e5 = Entry(master,textvariable=self.ddltime2, width=10,font=("verdana",12))
        self.e6 = Entry(master,textvariable=self.didgap2, width=10,font=("verdana",12))
        self.e7 = Entry(master,textvariable=self.itnum3, width=10,font=("verdana",12))
        self.e8 = Entry(master,textvariable=self.ddltime3, width=10,font=("verdana",12))
        self.e9 = Entry(master,textvariable=self.didgap3, width=10,font=("verdana",12))
        self.e10 = Entry(master,textvariable=self.interv, width=10,font=("verdana",12))
        self.e11 = Entry(master,textvariable=self.interv2, width=10,font=("verdana",12))
        self.e12 = Entry(master,textvariable=self.interv3, width=10,font=("verdana",12))
        self.gotoe = Entry(master,textvariable=self.gotoev, width=10,font=("verdana",12))
        self.isid = Checkbutton(master, text="Need Change Gap?", variable=self.isidgap)
        self.isdl = Checkbutton(master, text="Need Change Delay?", variable=self.isdelay)
        self.Lsavepath = Label(master, text="File Save Folder: ",font=("verdana",8))
        self.Esavepath = Entry(master,textvariable=self.savepath, width=40,font=("verdana",12))
        self.LRFrame = Label(master, text="Random Frame: ",font=("verdana",8))
        self.ERFrame = Entry(master,textvariable=self.Rframe, width=10,font=("verdana",12))
        self.Lstartp = Label(master, text="Test Points [start end]: ",font=("verdana",8))
        self.Estartp = Entry(master,textvariable=self.startp, width=10,font=("verdana",12))
        self.Eendp = Entry(master,textvariable=self.endp, width=10,font=("verdana",12))
        self.CMEB = Button(master,text="Do CurrentP DE", command=self.MEDOC, bg='#4ABDAC',font=("verdana",12))
        self.CSEB = Button(master,text="Do CurrentP SE", command=self.SEDOC, bg='#4ABDAC',font=("verdana",12))
        self.CNMB = Button(master,text="Do CurrentP NM", command=self.NMDOC, bg='#4ABDAC',font=("verdana",12))

        self.minusB.grid(row=0,column=0,padx=20,pady=5)
        self.addB.grid(row=0,column=1,padx=20,pady=5)
        self.gotoe.grid(row=0,column=2,padx=5,pady=10)
        self.gotoB.grid(row=0,column=3,padx=20,pady=5)
        self.Locationfo.grid(row=1,column=0, columnspan=6,padx=10,pady=10)
        self.Ltnum.grid(row=2,column=0,padx=(20,5),pady=(10,1))
        self.Ldltime.grid(row=2,column=1,padx=5,pady=(10,1))
        self.Lidgap.grid(row=2,column=2,padx=5,pady=(10,1))
        self.Linterv.grid(row=2,column=3,padx=5,pady=(10,1))
        self.e1.grid(row=3,padx=(20,5),pady=10)
        self.e2.grid(row=3,column=1,padx=5,pady=10)
        self.e3.grid(row=3,column=2,padx=5,pady=10)
        self.e4.grid(row=4,column=0,padx=(20,5),pady=5)
        self.e5.grid(row=4,column=1,padx=5,pady=5)
        self.e6.grid(row=4,column=2,padx=5,pady=5)
        self.e7.grid(row=5,column=0,padx=(20,5),pady=5)
        self.e8.grid(row=5,column=1,padx=5,pady=5)
        self.e9.grid(row=5,column=2,padx=5,pady=5)
        self.e10.grid(row=3,column=3,padx=5,pady=5)
        self.e11.grid(row=4,column=3,padx=5,pady=5)
        self.e12.grid(row=5,column=3,padx=5,pady=5)
        self.MEB.grid(row=3,column=4,padx=20,pady=10)
        self.SEB.grid(row=4,column=4,padx=20,pady=5)
        self.NMB.grid(row=5,column=4,padx=20,pady=5)
        self.PMEB.grid(row=3,column=6,padx=20,pady=10)
        self.PSEB.grid(row=4,column=6,padx=20,pady=5)
        self.PNMB.grid(row=5,column=6,padx=20,pady=5)
        self.isid.grid(row=6,column=2,padx=5,pady=(1,20))
        self.isdl.grid(row=6,column=1,padx=5,pady=(1,20))
        self.CMEB.grid(row=3,column=5,padx=20,pady=10)
        self.CSEB.grid(row=4,column=5,padx=20,pady=5)
        self.CNMB.grid(row=5,column=5,padx=20,pady=5)

        self.Lsavepath.grid(row=7,column=0, padx=5,pady=5)
        self.Esavepath.grid(row=7,column=1, padx=5,pady=5, columnspan=3)
        self.LRFrame.grid(row=7,column=4, padx=5,pady=5)
        self.ERFrame.grid(row=7,column=5, padx=5,pady=5)
        self.Lstartp.grid(row=0,column=4,padx=5,pady=10)
        self.Estartp.grid(row=0,column=5,padx=5,pady=10)
        self.Eendp.grid(row=0,column=6,padx=5,pady=10)

        self.Contd.grid(row=8,column=0, columnspan=6,padx=10,pady=10)
        #self.EditPB.grid(row=9,column=3,padx=20,pady=5)                

    def TrigCam(self,wi,opath,c=1):
        if wi == 1:
            tnum = int(self.e1.get())
            Detime=float(self.e2.get())/1000000
            IDgapmm=float(self.e3.get())
            interv = float(self.e10.get())
        elif wi == 2:
            tnum = int(self.e4.get())
            Detime=float(self.e5.get())/1000000
            IDgapmm=float(self.e6.get())
            interv = float(self.e11.get())
        elif wi == 3:
            tnum = int(self.e7.get())
            Detime=float(self.e8.get())/1000000
            IDgapmm=float(self.e9.get())
            interv = float(self.e12.get())

        if IDgapmm<11:
            tbox.showwarning("Error","ID gap can not smaller than 11!")
        else:
            isdela=int(self.isdelay.get())
            if isdela==1:
                self.cdv.set("Setting delay to %1.2fms"%(Detime*1000000))
                self.master.update_idletasks()
                setPV(Delaytime,Detime)
                time.sleep(0.5)
            self.isidg=int(self.isidgap.get())
            if self.isidg==1:
                self.cdv.set("Setting ID Gap to %1.2fmm"%(IDgapmm))
                self.master.update_idletasks()
                setPV(IDGAP,IDgapmm)
                time.sleep(0.5)
            
            setPV("7idbSAZ:randomScan:period",interv)
            setPV(IDDO,1)
            self.cdv.set("Shutter openning")
            self.master.update_idletasks()
            # setPV(Open,1)
            # time.sleep(3)  
            if open_shutter() == False:
                self.cdv.set("Failed to open shutter")
                return
            self.cdv.set("Collecting data...")
            self.master.update_idletasks()
            if c==1:
                llid = int(self.gotoe.get())
                cx=location[llid-1][0]
                cy=location[llid-1][1]
            else:
                cx = epics.caget(chamberXR)
                cy = epics.caget(chamberYR)
                llid = 0
        
            if wi == 1:
                namestr="DE_T%d-X=%.2f_Y=%.2f_"%(llid,cx,cy)
                pathstr="/DE_T%d-X=%.2f_Y=%.2f/"%(llid,cx,cy)
            elif wi == 2:
                namestr="SE_T%d-X=%.2f_Y=%.2f_"%(llid,cx,cy)
                pathstr="/SE_T%d-X=%.2f_Y=%.2f/"%(llid,cx,cy)
            elif wi == 3:
                namestr="NM_T%d-X=%.2f_Y=%.2f_"%(llid,cx,cy)
                pathstr="/NM_T%d-X=%.2f_Y=%.2f/"%(llid,cx,cy)

            newpath=opath+pathstr

            rframe = int(self.ERFrame.get())
            setPV(randomFrame,rframe)
            
            #CHECK IF ALL FREAMES COLLECTED
            allframes = tnum*epics.caget(randomFrame)
            allsaved = 1
            while allsaved == 1:
                setPV("7idbSAZ:TIFF1:FilePath",newpath)
                setPV("7idbSAZ:TIFF1:FileName",namestr)
                setPV("7idbSAZ:TIFF1:FileNumber",1)
                setPV(TrigNum,tnum)
                setPV("7idbSAZ:HDF1:NumCapture",allframes)
                setPV(randomScan,1)
                if epics.caget("7idbSAZ:TIFF1:FileNumber") == allframes+1:
                    allsaved = 0
                else:
                    self.cdv.set("Missed some data, re-collecting data...")
                    self.master.update_idletasks()
                    time.sleep(2)
                

    def MEPoint(self):
        self.EPB(1)
    def SEPoint(self):
        self.EPB(2)
    def NMPoint(self):
        self.EPB(3)

    def EPB(self,wi):
        if wi == 1:
            Pstr = "Edit DE Points List Now..."
            Ptxt = "DEScanList.txt"
            Tstr = "7IDB-DE Points Editor"
        elif wi == 2:
            Pstr = "Edit SE Points List Now..."
            Ptxt = "SEScanList.txt"
            Tstr = "7IDB-SE Points Editor"
        elif wi == 3:
            Pstr = "Edit NM Points List Now..."
            Ptxt = "NMScanList.txt"
            Tstr = "7IDB-NM Points Editor"

        self.cdv.set(Pstr)
        self.Contd.configure(fg='blue')
        self.master.update_idletasks()
        global location
        try:
            location_temp = np.genfromtxt(Ptxt)
            if len(np.shape(location_temp)) == 2 :
                location = list(location_temp)
            elif len(np.shape(location_temp)) == 1:
                location = [location_temp]
        except Exception:
            location = [[0,0]]
        sinx = StringVar()
        siny = StringVar()
        sinx.set("0")
        siny.set("0")
        subw = Tk()
        subw.title(Tstr)

        def Addtolist():
            global location
            xv=float(ex.get())
            yv=float(ey.get())
            pstr = "%d - [%1.2f %1.2f]"%(len(location)+1,xv,yv)
            Plist.insert(len(location),pstr)
            location.append([xv,yv])

        def Clearlist():
            global location
            Plist.delete(0,len(location)-1)
            location=[]

        def Exitsub():
            global location
            np.savetxt(Ptxt,location,fmt='%1.2f')
            subw.destroy()
            self.cdv.set("Points list saved...")
            self.Contd.configure(fg='blue')
            self.master.update_idletasks()
            # print(location)

        def Dellist():
            global location
            cs = Plist.curselection()
            csn = int(cs[0])
            location.pop(csn)
            print(location)
            Plist.delete(0,len(location))
            refreshlist()

        def refreshlist():
            global location
            for li in range(len(location)):
                xv=location[li][0]
                yv=location[li][1]
                pstr = "%d - [%1.2f %1.2f]"%(li+1,xv,yv)
                Plist.insert(li,pstr)

        delselB = Button(subw,text="Delete selected", command=Dellist, bg='red',font=("verdana",10),width=10)
        addtolistB = Button(subw,text="Add to list", command=Addtolist, bg='#4ABDAC',font=("verdana",10),width=20)
        clearlistB = Button(subw,text="Clear all points", command=Clearlist, bg='red',font=("verdana",10),width=20)
        exitsubB = Button(subw,text="Exit & Save", command=Exitsub, bg='#4ABDAC',font=("verdana",10))
        ex = Entry(subw,textvariable=sinx, width=10,font=("verdana",12))
        ey = Entry(subw,textvariable=siny, width=10,font=("verdana",12))
        sinx = Label(subw, text="X:",font=("verdana",12))
        siny = Label(subw, text="y:",font=("verdana",12))
        Plist = Listbox(subw,font=("verdana",12))
        refreshlist()

        ex.grid(row=0,column=2,padx=20,pady=10)
        ey.grid(row=1,column=2,padx=20,pady=10)
        sinx.grid(row=0,column=1,padx=20,pady=10)
        siny.grid(row=1,column=1,padx=20,pady=10)
        addtolistB.grid(row=2,column=1,padx=20,pady=10,columnspan=2)
        clearlistB.grid(row=3,column=1,padx=20,pady=10,columnspan=2)
        exitsubB.grid(row=4,column=2,padx=20,pady=10)
        Plist.grid(row=0,column=0,rowspan=4,padx=20,pady=10)
        delselB.grid(row=4,column=0,padx=20,pady=10)

        subw.mainloop()

    def DOAll(self,wi):
        opath=self.Esavepath.get()
        setPV("7idbSAZ:randomScan:doSeq.LNK1","7idb:DG1:TriggerDelayBO PP NMS")
        setPV("7idbSAZ:randomScan:doSeq.DLY2",1.5)
        setPV("7idbSAZ:TIFF1:FileTemplate","%s%s_%4.4d.tif")
        setPV("7idbSAZ:TIFF1:EnableCallbacks",1)
        setPV("7idbSAZ:HDF1:EnableCallbacks",1)
        if wi == 1:
            dostr = "Doing DE Now..."
            donestr = "DE is Done!"
            Ptxt = "DEScanList.txt"
        elif wi == 2:
            dostr = "Doing SE Now..."
            donestr = "SE is Done!"
            Ptxt = "SEScanList.txt"
        elif wi == 3:
            dostr = "Doing NM Now..."
            donestr = "NM is Done!"
            Ptxt = "NMScanList.txt"
    
        try:
            location_temp = np.genfromtxt(Ptxt)
            if len(np.shape(location_temp)) == 2 :
                location = list(location_temp)
            elif len(np.shape(location_temp)) == 1:
                location = [location_temp]
        except Exception:
            location = [[0,0]]
        startp = int(self.Estartp.get()) - 1
        endp = int(self.Eendp.get()) - 1
        for i in range(len(location)):
            if startp > 0:
                if i < startp:
                    continue
            if endp > 0:
                if i > endp:
                    continue
            self.movep(i+1)
            #self.MEB.configure(bg='#4ABDAC')
            #self.SEB.configure(bg='red')
            self.cdv.set(dostr)
            self.Contd.configure(fg='blue')
            self.master.update_idletasks()
            time.sleep(0.5)
            self.TrigCam(wi,opath)
            setPV(Close,1)
            self.cdv.set("Shutter  closed")
            self.master.update_idletasks()
            time.sleep(1)   

        self.Contd.configure(fg='red')
        self.cdv.set(donestr)
        self.movep(1,False,0)
        setPV("7idbSAZ:TIFF1:FilePath",opath)

    def MEDOAll(self):
        self.DOAll(1)

    def SEDOAll(self):
        self.DOAll(2)

    def NMDOAll(self):
        self.DOAll(3)

    def DOOne(self,wi):
        opath=self.Esavepath.get()
        setPV("7idbSAZ:randomScan:doSeq.LNK1","7idb:DG1:TriggerDelayBO PP NMS")
        setPV("7idbSAZ:randomScan:doSeq.DLY2",1)
        setPV("7idbSAZ:TIFF1:FileTemplate","%s%s_%4.4d.tif")
        setPV("7idbSAZ:TIFF1:EnableCallbacks",1)
        setPV("7idbSAZ:HDF1:EnableCallbacks",1)
        if wi == 1:
            dostr = "Doing Current DE Now..."
            donestr = "Current DE is Done!"
            Ptxt = "DEScanList.txt"
        elif wi == 2:
            dostr = "Doing Current SE Now..."
            donestr = "Current SE is Done!"
            Ptxt = "SEScanList.txt"
        elif wi == 3:
            dostr = "Doing Current NM Now..."
            donestr = "Current NM is Done!"
            Ptxt = "NMScanList.txt"
    
        try:
            location_temp = np.genfromtxt(Ptxt)
            if len(np.shape(location_temp)) == 2 :
                location = list(location_temp)
            elif len(np.shape(location_temp)) == 1:
                location = [location_temp]
        except Exception:
            location = [[0,0]]
        startp = int(self.Estartp.get()) - 1
        endp = int(self.Eendp.get()) - 1
        
        self.cdv.set(dostr)
        self.Contd.configure(fg='green')
        self.master.update_idletasks()
        time.sleep(0.5)
        self.TrigCam(wi,opath,2)
        setPV(Close,1)
        self.cdv.set("Shutter  closed")
        self.master.update_idletasks()
        time.sleep(1)   
        self.Contd.configure(fg='red')
        self.cdv.set(donestr)
        setPV("7idbSAZ:TIFF1:FilePath",opath)

    def MEDOC(self):
        self.DOOne(1)

    def SEDOC(self):
        self.DOOne(2)

    def NMDOC(self):
        self.DOOne(3)

    def movep(self,lid,iswait = True,isreal = 1):
        self.lcl.set("Moving to Point %d now..."%(lid))
        self.master.update_idletasks()
        cx=location[lid-1][0]
        cy=location[lid-1][1]
        setPV(chamberX,cx,iswait)
        setPV(chamberY,cy,iswait)
        ccx=epics.caget(chamberXR)
        ccy=epics.caget(chamberYR)
        if isreal == 1:
            showinfo="Now at Point %d [%1.2f, %1.2f]"%(lid,ccx,ccy)
        else:
            showinfo="Now at Point %d [%1.2f, %1.2f]"%(lid,cx,cy)
        self.lcl.set(showinfo)
        self.gotoev.set(lid)
        self.master.update_idletasks()
    

    def ADDDO(self):
        self.locationid = int(self.gotoe.get())
        if self.locationid==len(location):
            self.locationid=self.locationid
        else:
            self.locationid=self.locationid+1
        self.movep(self.locationid)

    def MINUSDO(self):
        self.locationid = int(self.gotoe.get())
        if self.locationid==1:
            self.locationid=self.locationid
        else:
            self.locationid=self.locationid-1
        self.movep(self.locationid)
    
    def GOTODO(self):
        gotonum = int(self.gotoe.get())
        if gotonum<1 or gotonum>len(location):
            self.lcl.set("Error")
        else:
            self.locationid=gotonum
        self.gotoev.set(self.locationid)
        self.master.update_idletasks()
        self.movep(self.locationid)

class PhotronDummy:

    def __init__(self, master):

        self.master = master
        master.title('Photron Dummy Scan')
        self.abort_val = BooleanVar()
        self.abort_val.set(False)

        # Title label
        self.tlabel = Label(master, text='Photron Dummy Scan', width=30)

        # Number of dummy steps
        self.NNframe = Frame(master)
        self.NNlabel = Label(self.NNframe, text='Total Step', height=2, width=10)
        self.NN = Entry(self.NNframe, width=10)
        self.NN.insert(0, 5000)
        self.NNlabel.grid(row=0, column=0, padx=5, pady=2)
        self.NN.grid(row=0, column=1, padx=5,pady=2)

        # Parameter setting steps
        self.PSframe = Frame(master)
        self.PSlabel = Label(self.PSframe, text='Random Frames', height=2, width=15)
        self.PSRF = Entry(self.PSframe, width=10)
        self.PSRF.insert(0, 1)
        self.PSlabel.grid(row=0, column=0, padx=5, pady=2)
        self.PSRF.grid(row=0, column=1, padx=5,pady=2)
        self.DTlabel = Label(self.PSframe, text='Delay Time', height=2, width=10)
        self.PSDT = Entry(self.PSframe, width=10)
        self.PSDT.insert(0, 1)
        self.DTlabel.grid(row=1, column=0, padx=5, pady=2)
        self.PSDT.grid(row=1, column=1, padx=5,pady=2)

        # Control Buttons
        self.Bframe = Frame(master)
        self.scanB = Button(self.Bframe, height=2, width=10, text='Scan', command=self.scan)
        self.abortB = Button(self.Bframe, height=2, width=10, text='Abort', command=self.abort)
        self.scanB.grid(row=2, column=0, padx=5)
        self.abortB.grid(row=2, column=1, padx=5)

        # Message
        self.msg_frame = Frame(master)
        self.msg_default = 'welcome'
        self.msg = StringVar()
        self.msg.set(self.msg_default)
        self.msg_label = Label(self.msg_frame, height=2, textvariable=self.msg)
        self.msg_label.pack()

        # Geometry
        self.tlabel.pack()
        #self.NNframe.pack()
        self.PSframe.pack()
        self.Bframe.pack(pady=2)
        self.msg_frame.pack()

    def scan(self):
        randomN = epics.caget(randomFrame)
        PSRF = int(self.PSRF.get())
        PSDT = int(self.PSDT.get())
        setPV(randomFrame,PSRF)
        setPV("7idbSAZ:TIFF1:EnableCallbacks",0)
        setPV("7idbSAZ:HDF1:EnableCallbacks",0)
        self.msg.set("Open shutter")
        self.master.update()
        # setPV(Open, 1)
        # time.sleep(3)
        if open_shutter() == False:
            self.msg.set("Failed to open shutter")
            self.master.update()
            time.sleep(1)
            self.msg.set("Ready")
            self.master.update()
            return
        #NN = int(self.NN.get())
        #print NN
        #for i in range(NN):
        #       if self.abort_val.get() == 0:
        #               setPV(Trig,1)
        #               time.sleep(0.5)
        #               setPV(TrigDone,1)
        #               time.sleep(0.5)
        #               self.msg.set("Now doing %d "%(i+1))
        #       else:
        #               self.abort_val.set(False)
        #               self.msg.set("Scan aborted")
        #               self.master.update()
        #               time.sleep(2)
        #               break
        #       self.master.update()            
        i = 0
        while self.abort_val.get() == 0:
            setPV(Trig,1)
            time.sleep(0.5)
            setPV(TrigDone,1)
            time.sleep(PSDT-0.5)
            i += 1
            self.msg.set("Now doing %d "%(i+1))
            self.master.update()
        setPV(Close, 1)
        self.msg.set("Close shutter")
        setPV(randomFrame,randomN)
        self.abort_val.set(False)

    def abort(self):
        self.abort_val.set(True)

class PhotronFocus:

    def __init__(self, master):

        self.master = master
        master.title('Photron Focus Scan')
        self.abort_val = BooleanVar()
        self.abort_val.set(False)

        # Title label
        self.tlabel = Label(master, text='Photron Focus Scan', width=30)

        # Scan setup
        self.scanframe = Frame(master)
        self.stlabel = Label(self.scanframe, text='Start df (mm)', height=2, width=10)
        self.st = Entry(self.scanframe, width=10)
        self.st.insert(0, -0.1)
        self.endlabel = Label(self.scanframe, text='End df (mm)', height=2, width=10)
        self.end = Entry(self.scanframe, width=10)
        self.end.insert(0, 0.1)
        self.NNlabel = Label(self.scanframe, text='Steps', height=2, width=10)
        self.NN = Entry(self.scanframe, width=10)
        self.NN.insert(0, 21)
        self.stlabel.grid(row=0, column=0, padx=5, pady=2)
        self.st.grid(row=0, column=1, padx=5,pady=2)
        self.endlabel.grid(row=1, column=0, padx=5, pady=2)
        self.end.grid(row=1, column=1, padx=5,pady=2)
        self.NNlabel.grid(row=2, column=0, padx=5, pady=2)
        self.NN.grid(row=2, column=1, padx=5,pady=2)

        # Control Buttons
        self.Bframe = Frame(master)
        self.scanB = Button(self.Bframe, height=2, width=10, text='Scan', command=self.scan)
        self.abortB = Button(self.Bframe, height=2, width=10, text='Abort', command=self.abort)
        self.scanB.grid(row=0, column=0, padx=5)
        self.abortB.grid(row=0, column=1, padx=5)

        # Message
        self.msg_frame = Frame(master)
        self.msg_default = 'apple pen'
        self.msg = StringVar()
        self.msg.set(self.msg_default)
        self.msg_label = Label(self.msg_frame, height=2, textvariable=self.msg)
        self.msg_label.pack()

        # Geometry
        self.tlabel.grid(row=0, column=0)
        self.scanframe.grid(row=1, column=0)
        self.Bframe.grid(row=2, column=0)
        self.msg_frame.grid(row=3, column=0)

    def scan(self):
        randomN = epics.caget(randomFrame)
        cur_f=epics.caget("7idb:m7.RBV")
        setPV(randomFrame,1)
        setPV("7idbSAZ:TIFF1:EnableCallbacks",1)
        setPV("7idbSAZ:HDF1:EnableCallbacks",0)
        setPV("7idbSAZ:TIFF1:FileName",'fs_')
        setPV("7idbSAZ:TIFF1:FileNumber",1)
        st = float(self.st.get())
        end = float(self.end.get())
        NN = int(self.NN.get())
        dt=np.linspace(st,end,NN)
        self.msg.set("Open shutter")
        self.master.update()
        # setPV(Open, 1)
        # time.sleep(3)
        if open_shutter() == False:
            self.msg.set("Failed to open shutter")
            return

        for i in range(NN):
            if self.abort_val.get() == 0:
                setPV(focus,cur_f+dt[i])
                setPV(Trig,1)
                time.sleep(0.5)
                setPV(TrigDone,1)
                time.sleep(0.5)
                print("Now doing %d - %1.5f"%(i+1,cur_f+dt[i]))
                self.msg.set("Now doing %d - %1.5f"%(i+1,cur_f+dt[i]))
            else:
                self.abort_val.set(False)
                self.msg.set("Scan aborted")
                self.master.update()
                time.sleep(2)
                break
            self.master.update()
        setPV(Close, 1)
        self.msg.set("Close shutter")
        setPV(randomFrame,randomN)
        setPV(focus,cur_f)
        print("done")

    def abort(self):
        self.abort_val.set(True)

class PhotronDelay:
    
    def __init__(self, master):

        self.master = master
        master.title('Photron Delay Scan')
        self.abort_val = BooleanVar()
        self.abort_val.set(False)

        # Title label
        self.tlabel = Label(master, text='Photron Delay Scan', width=30)

        # Scan setup
        self.scanframe = Frame(master)
        self.stlabel = Label(self.scanframe, text='Start delay (us)', height=2, width=12)
        self.st = Entry(self.scanframe, width=10)
        self.st.insert(0, 0)
        self.endlabel = Label(self.scanframe, text='End delay (us)', height=2, width=12)
        self.end = Entry(self.scanframe, width=10)
        self.end.insert(0, 4)
        self.NNlabel = Label(self.scanframe, text='Steps', height=2, width=10)
        self.NN = Entry(self.scanframe, width=10)
        self.NN.insert(0, 41)
        self.stlabel.grid(row=0, column=0, padx=5, pady=2)
        self.st.grid(row=0, column=1, padx=5,pady=2)
        self.endlabel.grid(row=1, column=0, padx=5, pady=2)
        self.end.grid(row=1, column=1, padx=5,pady=2)
        self.NNlabel.grid(row=2, column=0, padx=5, pady=2)
        self.NN.grid(row=2, column=1, padx=5,pady=2)

        # Control Buttons
        self.Bframe = Frame(master)
        self.scanB = Button(self.Bframe, height=2, width=10, text='Scan', command=self.scan)
        self.abortB = Button(self.Bframe, height=2, width=10, text='Abort', command=self.abort)
        self.scanB.grid(row=0, column=0, padx=5)
        self.abortB.grid(row=0, column=1, padx=5)

        # Message
        self.msg_frame = Frame(master)
        self.msg_default = 'pen apple apple pen'
        self.msg = StringVar()
        self.msg.set(self.msg_default)
        self.msg_label = Label(self.msg_frame, height=2, textvariable=self.msg)
        self.msg_label.pack()

        # Geometry
        self.tlabel.grid(row=0, column=0)
        self.scanframe.grid(row=1, column=0)
        self.Bframe.grid(row=2, column=0)
        self.msg_frame.grid(row=3, column=0)

    def scan(self):
        mv = []
        randomN = epics.caget(randomFrame)
        setPV(randomFrame,1)
        setPV("7idbSAZ:TIFF1:EnableCallbacks",0)
        setPV("7idbSAZ:HDF1:EnableCallbacks",0)
        setPV("7idbSAZ:Stats1:EnableCallbacks",1)
        st = float(self.st.get())
        end = float(self.end.get())
        NN = int(self.NN.get())
        dt=np.linspace(st,end*1e-6,NN)
        self.msg.set("Open shutter")
        self.master.update()
        # setPV(Open, 1)
        # time.sleep(3)
        if open_shutter() == False:
            self.msg.set("Failed to open shutter")
            return

        for i in range(NN):
            if self.abort_val.get() == 0:
                setPV(Delaytime,dt[i])
                setPV(Trig,1)
                time.sleep(0.5)
                setPV(TrigDone,1)
                time.sleep(0.5)
                mv.append(epics.caget(MeanV))
                print("Now doing %d - %1.2f : %1.2f"%(i+1,dt[i]*1e6,mv[i]))
                self.msg.set("Now doing %d - %1.2f : %1.2f"%(i+1,dt[i]*1e6,mv[i]))
            else:
                self.abort_val.set(False)
                self.msg.set("Scan aborted")
                dt = dt[:i]
                self.master.update()
                time.sleep(2)
                break
            self.master.update()
        setPV(Close, 1)
        self.msg.set("Close shutter")
        setPV(randomFrame,randomN)
        timestr=datetime.datetime.now().strftime("%B-%d-%Y_%H:%M:%S.txt")
        np.savetxt('../7idbSAZDelayScan/'+timestr,(dt*1e6,mv),fmt='%1.2f')
        plt.plot(dt*1e6,mv,'*r:')
        plt.xlabel('Delay (us)')
        plt.ylabel('Mean Intensity (ct)')
        plt.show()

    def abort(self):
        self.abort_val.set(True)


if __name__ == '__main__':
    root = Tk()
    gui = Photron(root)
    root.mainloop()