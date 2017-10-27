import IPython
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import scipy.optimize as opt
import os
from bluesky.plans import scan, baseline_decorator, subs_decorator,abs_set,adaptive_scan,spiral_fermat,spiral,scan_nd,mv
from bluesky.callbacks import LiveTable,LivePlot, CallbackBase
from pyOlog.SimpleOlogClient import SimpleOlogClient
from esm import ss_csv
from cycler import cycler
from collections import ChainMap
import math
import re
from builtins import input as pyinput
from boltons.iterutils import chunked
import sys
ip=IPython.get_ipython()



def macro1():
    #This macro is used to run a series of undulator spectra a different photon energies.

    grating='600' # the grating to use in the scans
    EPU='105'
#    Photon_list=(20,50,100,150,200) # the list of photon energies to use in the scan
    Photon_list=(25,40,60,80,100) # the list of photon energies to use in the scan
    Erange=[0.75,6.5]   #the photon energy %range for the scans, in the form [x,y] where the start
                      #value is x*Eph and the end value is y*Eph or the limit of the grating range.

    yield from Beamline.move_to('Branch_A')
                      
    for Ephoton in Photon_list:
        yield from Eph.move_to(Ephoton,grating=grating,EPU=EPU,branch='A',shutter='open')
        yield from M3_pitch_alignment(Branch='A')
        yield from Eph.move_to(Erange[0]*Ephoton,grating=grating,EPU=None,branch='A',shutter='open')
        yield from mv(ExitSlitA.h_gap,300)
        uid = yield from scan_1D('qem07',PGM.Energy,Erange[0]*Ephoton,
                                 min(Erange[1]*Ephoton,Eph.Range[grating][1]),0.5)

        yield from mv(BTA2diag.trans,-87)
        qem07.em_range.put('12 pC')

        uid = yield from scan_1D('qem07@4',PGM.Energy,Erange[0]*Ephoton,
                                 min(Erange[1]*Ephoton,Eph.Range[grating][1]),0.5)

        yield from mv(BTA2diag.trans,-63)
        qem07.em_range.put('350 pC')


def macro2():

    uid = yield from scan_multi_1D('qem12@2', PGM.Focus_Const, 3.0, 3.3, 0.05, PGM.Energy,64.550 , 64.725, 0.0005)    
    #This macro is used to aquire the image of the beam upstream of M3, it involves moving the the YaG
    #screen and collecting several images that need to be summed together to get the entire image.

    yield from mv(PGM.Focus_Const,3.2)
    
    slit_list=(1,1.25,1.5,1.6,1.7,1.8,1.9,2) # the list of photon energies to use in the scan

    for slit in slit_list:
        yield from mv(FEslit.h_gap, slit, FEslit.v_gap, slit)
        uid = yield from M3_pitch_alignment('B')
        uid = yield from scan_1D('qem12@2', PGM.Energy,64.55 , 64.725, 0.0005)

    yield from mv(shutter_FE,'Close')


def macro3():

    grating='800'
    EPU='105'
    branch='A'
    
#    slit_list=(1,10) # the list of photon energies to use in the scan
#    slit_list=(10) # the list of photon energies to use in the scan
    
    photon_list=(30,40,60,80,100,200) # the list of photon energies to use in the scan
#    photon_list=(40,60,80,100,200) # the list of photon energies to use in the scan

#    pitch_list=(-0.712829,-0.711738,-0.710757,-0.710112,-0.70986,-0.70916)
#    yield from mv(BTA2diag.trans,-63)
#    yield from mv(ExitSlitA.h_gap,50 , ExitSlitA.v_gap,30) 
    
#    for i,photon in enumerate(photon_list):
#        yield from mv(FEslit.h_gap, slit_list[0], FEslit.v_gap, slit_list[0])       
#        yield from Eph.move_to(photon,grating=grating,EPU=EPU,branch=branch,shutter='open')
#        yield from mv(M3.Ry,pitch_list[i])
#        yield from M3_pitch_alignment(branch)
#        yield from mv(ExitSlitA.h_gap,50 , ExitSlitA.v_gap,30) 
#        EPUgap=Eph.Und_e2g(photon,EPU)
#        yield from scan_1D('qem07',EPU105.gap,EPUgap-4,EPUgap+4,0.1)
        
#        for slit in slit_list:        
#            yield from mv(FEslit.h_gap, slit, FEslit.v_gap, slit)

# yield from scan_1D('qem07',EPU105.gap,EPUgap-4,EPUgap+4,0.1)

    yield from Eph.move_to(100,grating=grating,EPU=EPU,branch=branch,shutter='open')
#     yield from mv(FEslit.h_gap, 10, FEslit.v_gap, 10)
 
    uid = yield from scan_1D('qem07',PGM.Energy,90,720,0.25)
    yield from mv(EPU105.phase,34.7)
    uid = yield from scan_1D('qem07',PGM.Energy,90,720,0.25)
    yield from mv(EPU105.phase,0)

    yield from Eph.move_to(60,grating=grating,EPU=EPU,branch=branch,shutter='open')
    yield from M3_pitch_alignment(branch)
    uid = yield from scan_1D('qem07',PGM.Energy,50,520,0.25)

    yield from Eph.move_to(30,grating=grating,EPU=EPU,branch=branch,shutter='open')
    yield from M3_pitch_alignment(branch)
    uid = yield from scan_1D('qem07',PGM.Energy,20,420,0.25)
     

    for photon in photon_list:
        yield from Eph.move_to(photon,grating=grating,EPU=EPU,branch=branch,shutter='open')
        yield from scan_1D('Mir3_Cam10_U_1',M3Udiag.trans,-20,20,0.1)

            
    yield from mv(shutter_FOE,'close')


def macro4():
    #This macro is to run series of 2D scans over 100 um x 100 um with 2 micron step size.

    for i in range(10):
        
        uid=yield from scan_2D('qem08@2',LT.Y,52.45,52.55,.002,LT.X,15.3,15.4,.002,scan_type='XAS')

 
        
