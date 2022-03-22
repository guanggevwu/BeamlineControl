import os
import time
import logging
# from highspeedcamera import PhotronDelay

import numpy as np
from epics import caget, caput

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO)


shutterA_open = "7ida:rShtrA:Open"
shutterA_close = "7ida:rShtrA:Close"
Trig = "7idb:DG1:TriggerDelayBO"
TrigDone = "7idbSAZ:cam1:LiveMode.VAL"
MeanV = "7idbSAZ:Stats1:MeanValue_RBV"
Delaytime = "7idb:DG2:ADelayAO"
randomFramepv = "7idbSAZ:cam1:RandomFrames"
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
CamMode=""


class beam():
    def __init__(self,timing) -> None:
        self.timing = timing   #timing is a list [SE,DE,NM]

# class DelayGenerator():
#     def __init__(self, name, trigger, A, B) -> None:
#         self.name = name
#         if name == 'DG1':
#             self.trigger = trigger
#             self.A = A
#             self.B = B

#     def set_channel_value(self, val):
#         caput(Apv)


#     def set_trigger_mode():
#         caput(dgtriggerpv)

class PhotronCam():
    def __init__(self,spprefix):
        self.pvprefix='7idbSAZ:cam1:'               #camera pv prefix
        self.spprefix=spprefix         #savepath prefix
    # def set_trigger_mode:

    def MyShading(self):
        logging.info("AcquireMode --> Live")
        caput(self.pvprefix + "AcquireMode", "Live", wait=True, timeout=100000.0)
        time.sleep(2)
        logging.info( "ShadingMode --> Off")
        caput(self.pvprefix + "ShadingMode", "Off", wait=True, timeout=100000.0)
        time.sleep(2)
        logging.info( "ShadingMode --> On")
        caput(self.pvprefix + "ShadingMode", "On", wait=True, timeout=100000.0)
        time.sleep(5)
        logging.info("AcquireMode --> Record")
        caput(self.pvprefix + "AcquireMode", "Record", wait=True, timeout=100000.0)
        logging.info( "Re-Shading Done.")


    def switch_mode(self, mode='random', sample_name='test', num_img=100,
                    exp_time=1.0, savepath=None, group_id=None):
        
        modelist=['random','random_reset','random_mid','random_start','continues']
        modepvlist=[1,2,3,4,5,6,7,8]
        modepv=modepvlist[modelist.index[mode]]
    
    def savefiles(self,spmain=None,tile='T0'):
        x=caget(chamberX)
        y=caget(chamberY)
        # logging.info([b for b in ['SE', 'DE', 'NM', ''] if os.path.sep+b in spmain])
        bunchmode=[b for b in ['SE', 'DE', 'NM', ''] if os.path.sep+b in spmain][0]
        if not bunchmode: bunchmode='SE'
        spposition=bunchmode+'_'+tile+f'-X={x:.2f}_Y={y:.2f}'
        caput('7idbSAZ:TIFF1:FilePath',os.path.join(self.spprefix,spmain,spposition))
        caput("7idbSAZ:TIFF1:EnableCallbacks",1)        
        caput('7idbSAZ:TIFF1:FileName',spposition)
        caput("7idbSAZ:TIFF1:FileNumber",1)
        # caput(TrigNum,tnum)###
        # caput("7idbSAZ:HDF1:NumCapture",allframes)###
        # caput(randomScan,1)###
        # if epics.caget("7idbSAZ:TIFF1:FileNumber") == allframes+1:
        #     allsaved = 0
        # else:
        #     self.cdv.set("Missed some data, re-collecting data...")
        #     self.master.update_idletasks()
        #     time.sleep(2)
        # caput("7idbSAZ:TIFF1:EnableCallbacks",0)



beam1=beam([0.0,1.0,2.0])
Photron=PhotronCam('E:\\CameraData4T\\2022.03\\Kefico')

def close_shutter():
    caput(shutterA_close, 1, wait=True)
    while caget("PB:07ID:STA_A_FES_CLSD_PL.VAL") != 1:
        time.sleep(0.1)
    logging.info('shutter is closed.')
    return True 

def open_shutter():
    caput("7ida:rShtrA:Open", 1, wait=True)
    while caget("PB:07ID:STA_A_FES_CLSD_PL.VAL") != 0:
        time.sleep(0.1)
    logging.info('shutter is open.')
    return True



def random_scan(spmain=None, triggermode='external', tile='T0', eachr=10, repeats=2, delay=1, 
    ST=0, timelength=12):
    """
    spmain format: "abc\\edf", not "\\abc\\edf" or "abc\\edf\\"
    """
    # Photron.switch_mode(mode='random')
    if spmain:
        Photron.savefiles(spmain,tile=tile)
    caput('7idbSAZ:cam1:AcquireMode',1)
    caput(randomFramepv,eachr)
    # caput("7idbSAZ:HDF1:EnableCallbacks",0)
    # open_shutter()
    if ST: open_shutter()
    if triggermode == 'manual':
        i=0
        while i < repeats:
            i+=1
            caput(Trig,1)
            time.sleep(delay)
            logging.info(f'done {i:} repeat')
            if i==199:
                logging.info('automatically stop after 200 repeats.')
        caput(TrigDone,1)

    # The external trigger can either be from 7idb:DG1 "internal" with a fixed rate, or an external signal sent to 7idb:DG1 with "Ext rising edge"
    elif triggermode == 'external':
        # caput('7idb:DG1:TriggerSourceMO',1)
        while caget('7idbSAZ:cam1:StatusName_RBV')!=4:
            time.sleep(0.1)
        logging.info('receiving triggering...')
        time.sleep(timelength)
        logging.info(f'{timelength} s window of receiving trigger finished')                
        caput(TrigDone,1)
        # input('press enter to continue...')  
        # caput('7idb:DG1:TriggerSourceMO',5)          
    if ST: close_shutter()

xlist1=[0,3.3,7.34,10.64]
ylist1=[0,0.05,0.05,0]
def position_scan(spmain=None, xlist=xlist1, ylist=ylist1, triggermode='external', eachr=10,
    repeats=2, delay=1, ST=0, timelength=12):
    if not xlist or not ylist:
        logging.info('no scan positions provided')
        return
    i=0
    for x,y  in zip(xlist,ylist):
        i+=1
        caput(chamberX,x,wait=True)
        caput(chamberY,y,wait=True)
        if i != 1:
            time.sleep(delay)
            logging.info(f'delay finished')
        logging.info(f'now at {i}th location: X = {x} mm and Y = {y} mm')
        random_scan(spmain=spmain,triggermode=triggermode,tile=f'T{i}',eachr=eachr,repeats=repeats,
        delay=1, ST=ST, timelength=timelength)
    caput(chamberX,xlist[0],wait=True)
    caput(chamberY,ylist[0],wait=True)    