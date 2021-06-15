import IPython
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import scipy.optimize as opt
import os
from bluesky.plans import count, scan, adaptive_scan, spiral_fermat, spiral,scan_nd
from bluesky.plan_stubs import abs_set, mv
from bluesky.preprocessors import baseline_decorator, subs_decorator
# from bluesky.callbacks import LiveTable,LivePlot, CallbackBase
#from pyOlog.SimpleOlogClient import SimpleOlogClient
from esm import ss_csv
from cycler import cycler
from collections import ChainMap
import math
import re
from boltons.iterutils import chunked
import sys
ip=IPython.get_ipython()

### READ IN DEFINITION DICTIONARY FROM CSV FILES IN: /home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Grt_Translation.csv', dtype='float') #you wanted float datatype
ESM_Grt_Translation = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Grt_Offset_A.csv',dtype='str') #you wanted float datatype
ESM_Grt_Offset_A = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Grt_Offset_B.csv', dtype='str') #float datatype
ESM_Grt_Offset_B = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/M2_Offset_A.csv', dtype='str') #string  datatype
ESM_M2_Offset_A = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/M2_Offset_B.csv', dtype='str') #string datatype
ESM_M2_Offset_B = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/c_value_A.csv', dtype='float') #float datatype
ESM_c_value_A = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/c_value_B.csv', dtype='float') #float datatype
ESM_c_value_B = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/c_value_B.csv', dtype='float') #float datatype
ESM_c_value_B = df.to_dict(orient='records')[0] #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU57_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_EPU57_theory = df.to_dict(orient='series') #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU57_LH_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_EPU57_LH_theory = df.to_dict(orient='series') #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU57_LV_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_EPU57_LV_theory = df.to_dict(orient='series') #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU105_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_EPU105_theory = df.to_dict(orient='series') #the[0] extract the dictionary

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU57.csv', dtype='float') #float datatype
ESM_Und_Energy_EPU57 = df.to_dict(orient='series')

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU105.csv', dtype='float') #float datatype
ESM_Und_Energy_EPU105 = df.to_dict(orient='series') 

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_LV_EPU105.csv', dtype='float') #float datatype
ESM_Und_Energy_LV_EPU105 = df.to_dict('series') 

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU105_Cgap_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_Cgap_EPU105_theory = df.to_dict('series') 

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU105_Cphase_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_Cphase_EPU105_theory = df.to_dict('series') 

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU57_Cgap_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_Cgap_EPU57_theory = df.to_dict('series') 

df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Und_Energy_EPU57_Cphase_theory.csv', dtype='float') #float datatype
ESM_Und_Energy_Cphase_EPU57_theory = df.to_dict('series') 





###MOVING MOTORS
###    The following set of code is used to create a class that provides a range of useful information
###    regarding the PGM and EPU.

###    ESM monochromator information

##    Definition of the monochromator device class located at ESM.

class ESM_monochromator_device:
    def __init__(self,name):
        '''
        Create a class that gives a range of values for moving the monochramotr and EPU's to different
        locations. it also provides information on the calculations that go into the mono and EPU
        calibration

        '''


        #define the inputted values when defining an instance.
        self.name=name
        #Define the information dictioanries here
        self.Grt_Translation = {}
        self.Grt_Offset = {}                                # grating offset information
        self.M2_Offset={}                                   # M2 offset information
        self.c_value={}                                     # c value information
        self.Range={}                        # the photon energy range for each grating and undulator
        self.Und_Energy={}                   # the undulator gap to photon energy data
        self.Und_Energy_LV={}                #undulator gap vs photon energy for LV
        self.Und_Energy_Cgap = {}
        self.Und_Energy_Cphase = {}
        self.M3_Angle_300={}                     # the M3 pitch angle vs photon energy for 300l/mm
        self.M3_Angle_600={}                     # the M3 pitch angle vs photon energy for 600l/mm
        self.M3_Angle_800={}                     # the M3 pitch angle vs photon energy for 800l/mm
        self.set_dicts                       # read the values to the device dictionaries

    # Define the class properties here
    @property
    def set_dicts(self):
        '''
        This routine is used to enter the values into the dictionaries

        '''
        self.Grt_Translation= ESM_Grt_Translation           # grating translation position
        self.Grt_Offset['A']= ESM_Grt_Offset_A
        self.Grt_Offset['B']= ESM_Grt_Offset_B
        self.M2_Offset['A']= ESM_M2_Offset_A
        self.M2_Offset['B']= ESM_M2_Offset_B
        self.c_value['A']= ESM_c_value_A
        self.c_value['B']= ESM_c_value_B


        self.Und_Energy['EPU57_theory'] = ESM_Und_Energy_EPU57_theory
#        self.Und_Energy['EPU57_LH_theory'] = ESM_Und_Energy_EPU57_LH_theory
#        self.Und_Energy['EPU57_LV_theory'] = ESM_Und_Energy_EPU57-LV_theory
        
        self.Und_Energy['EPU105_theory'] = ESM_Und_Energy_EPU105_theory
        self.Und_Energy['EPU57'] = ESM_Und_Energy_EPU57        
        self.Und_Energy['EPU105'] = ESM_Und_Energy_EPU105
        self.Und_Energy_LV['EPU105'] = ESM_Und_Energy_LV_EPU105
        self.Und_Energy_LV['EPU57'] = ESM_Und_Energy_EPU57_LV_theory 
        self.Und_Energy_Cgap['EPU105_theory'] = ESM_Und_Energy_Cgap_EPU105_theory
        self.Und_Energy_Cphase['EPU105_theory'] = ESM_Und_Energy_Cphase_EPU105_theory
        self.Und_Energy_Cgap['EPU57_theory'] = ESM_Und_Energy_Cgap_EPU57_theory
        self.Und_Energy_Cphase['EPU57_theory'] = ESM_Und_Energy_Cphase_EPU57_theory


        self.Range['1200']=[130,1500]
        self.Range['800']=[15,1500]
        self.Range['600']=[15,420]
        self.Range['300']=[15,1500]
        self.Range['EPU105']=[20,400]
        self.Range['EPU57']=[140,1390]


        self.M3_Angle_300['EPU105'] = {'Energy':  [20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 240, 280, 320, 360, 400],
                                    'ang' :  [-0.72, -0.7188, -0.7182, -0.7178,
                                               -0.7174, -0.7172, -0.7171, -0.7169,
                                               -0.7168, -0.7164, -0.7163, -0.7162,
                                               -0.7161, -0.7161, -0.7160, -0.7159,
                                               -0.7160, -0.7161, -0.7161] }

        self.M3_Angle_600['EPU105'] = {'Energy':  [30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 240, 280, 320, 360, 400],
                                    'ang' :  [-0.71490000000000009, -0.71420000000000006, -0.71360000000000001, -0.71320000000000006,
                                              -0.7128000000000001, -0.71260000000000001, -0.71240000000000003, -0.71220000000000006,
                                              -0.71190000000000009, -0.71170000000000011, -0.71150000000000002, -0.71140000000000003,
                                              -0.71130000000000004, -0.71110000000000007, -0.71090000000000009, -0.71090000000000009,
                                              -0.71090000000000009, -0.71060000000000001] }

        self.M3_Angle_800['EPU105'] = {'Energy':  [30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 240, 280, 320, 360, 400],
                                    'ang' :  [-0.71430000000000005, -0.71360000000000001, -0.71290000000000009, -0.71260000000000001,
                                              -0.71230000000000004, -0.71210000000000007, -0.7118000000000001, -0.71170000000000011,
                                              -0.71150000000000002, -0.71130000000000004, -0.71110000000000007, -0.71100000000000008,
                                              -0.71100000000000008, -0.7108000000000001, -0.71070000000000011, -0.71060000000000001,
                                              -0.71060000000000001, -0.71050000000000002] }




        return

    #Define the information functions here

    def Und_g2e(self,gap,EPU='57'):
        '''
        This function returns the photon energy value required for a given undulator gap and undulator.

        PARAMETERS
        ----------

        gap : float
            The undulator gap in mm.


        EPU : str
            The undulator to use, can be '57' (default, high energy) or '105'(low energy).

        photon_energy : float, output
            The photon energy value that is returned.

        '''

        # check that the gap value is within the range of the undulator
        if gap<min(self.Und_Energy['EPU'+EPU]['Gap']) or gap>max(self.Und_Energy['EPU'+EPU]['Gap']):
            raise RuntimeError('gap value out of range of undulator')
        else:
        #return the photon energy
            gtoe=interp1d(self.Und_Energy['EPU'+EPU]['Gap'],self.Und_Energy['EPU'+EPU]['Energy'])
            photon_energy=float(gtoe(gap))
            return photon_energy



    def Und_e2g(self,photon_energy,EPU='57'):
        '''
        This function returns the photon energy value required for a given undulator gap and undulator.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.

        EPU : str, optional
            The undulator to use, can be '57' (default, high energy) or '105'(low energy).
        gap : float, output
            The undulator gap in mm.



        '''

        # check that the gap value is within the range of the undulator
        if photon_energy<min(self.Und_Energy['EPU'+EPU]['Energy']) or photon_energy>max(self.Und_Energy['EPU'+EPU]['Energy']):
            raise RuntimeError('energy value out of range of undulator')
        else:
        #return the photon energy
            gtoe=interp1d(self.Und_Energy['EPU'+EPU]['Energy'],self.Und_Energy['EPU'+EPU]['Gap'])
            gap = float(gtoe(photon_energy))
            return gap





    def Und_e2g_LV(self,photon_energy,EPU='105'):
        '''
        This function returns the photon energy value required for a given undulator gap and undulator.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.

        EPU : str, optional
            The undulator to use, can be '57' (default, high energy) or '105'(low energy).
        gap : float, output
            The undulator gap in mm.



        '''

        # check that the gap value is within the range of the undulator
        if photon_energy<min(self.Und_Energy_LV['EPU'+EPU]['Energy']) or photon_energy>max(self.Und_Energy_LV['EPU'+EPU]['Energy']):
            raise RuntimeError('energy value out of range of undulator')
        else:
        #return the photon energy
            gtoe=interp1d(self.Und_Energy_LV['EPU'+EPU]['Energy'],self.Und_Energy_LV['EPU'+EPU]['Gap'])
            gap = float(gtoe(photon_energy))
            return gap

        
    def Und_e2g_Cgap(self,photon_energy,EPU='105'):
        '''
        This function returns the photon energy value required for a given undulator gap and undulator.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.

        EPU : str, optional
            The undulator to use, can be '57' (default, high energy) or '105'(low energy).
        gap : float, output
            The undulator gap in mm.



        '''

        # check that the gap value is within the range of the undulator
        if photon_energy<min(self.Und_Energy_Cgap['EPU'+EPU+'_theory']['Energy']) or photon_energy>max(self.Und_Energy_Cgap['EPU'+EPU+'_theory']['Energy']):
            raise RuntimeError('energy value out of range of undulator')
        else:
        #return the photon energy
            gtoe=interp1d(self.Und_Energy_Cgap['EPU'+EPU+'_theory']['Energy'],self.Und_Energy_Cgap['EPU'+EPU+'_theory']['Gap'])
            gap = float(gtoe(photon_energy))
            return gap




    def Und_e2g_Cphase(self,photon_energy,EPU='105'):
        '''
        This function returns the photon energy value required for a given undulator gap and undulator.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.

        EPU : str, optional
            The undulator to use, can be '57' (default, high energy) or '105'(low energy).
        gap : float, output
            The undulator gap in mm.



        '''

        # check that the gap value is within the range of the undulator
        if photon_energy<min(self.Und_Energy_Cphase['EPU'+EPU+'_theory']['Energy']) or photon_energy>max(self.Und_Energy_Cphase['EPU'+EPU+'_theory']['Energy']):
            raise RuntimeError('energy value out of range of undulator')
        else:
        #return the photon energy
            gtoe=interp1d(self.Und_Energy_Cphase['EPU'+EPU+'_theory']['Energy'],self.Und_Energy_Cphase['EPU'+EPU+'_theory']['Phase'])
            phase = float(gtoe(photon_energy))
            return phase


        
    def M3_e2a(self,photon_energy,grt='300',EPU='105'):
        '''
        This function returns the M3 angle given the photon energy (for now: only 300, epu105.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.

        grt : str, optional

        EPU : str, optional




        '''


        if grt == '300' and EPU == '105':

            if photon_energy<min(self.M3_Angle_300['EPU'+EPU]['Energy']) or photon_energy>max(self.M3_Angle_300['EPU'+EPU]['Energy']):
                                                      # check that the gap value is within the range of the undulator
                 raise RuntimeError('energy value out of range of undulator')
            else:
                                                       #return the photon energy
                etoa=interp1d(self.M3_Angle_300['EPU'+EPU]['Energy'],self.M3_Angle_300['EPU'+EPU]['ang'])
                angle = float(etoa(photon_energy))
                return angle

        elif grt == '600'and EPU == '105':

            if photon_energy<min(self.M3_Angle_600['EPU'+EPU]['Energy']) or photon_energy>max(self.M3_Angle_600['EPU'+EPU]['Energy']):
                                                      # check that the gap value is within the range of the undulator
                 raise RuntimeError('energy value out of range of undulator')
            else:
                                                       #return the photon energy
                etoa=interp1d(self.M3_Angle_600['EPU'+EPU]['Energy'],self.M3_Angle_600['EPU'+EPU]['ang'])
                angle = float(etoa(photon_energy))
                return angle

        elif grt == '800' and EPU == '105':

            if photon_energy<min(self.M3_Angle_800['EPU'+EPU]['Energy']) or photon_energy>max(self.M3_Angle_800['EPU'+EPU]['Energy']):
                                                      # check that the gap value is within the range of the undulator
                 raise RuntimeError('energy value out of range of undulator')
            else:
                                                       #return the photon energy
                etoa=interp1d(self.M3_Angle_800['EPU'+EPU]['Energy'],self.M3_Angle_800['EPU'+EPU]['ang'])
                angle = float(etoa(photon_energy))
                return angle


    def PGM_angles(self, photon_energy,grating,EPU='57',c=None):
        '''
        This function returns the mirror angles required for a given grating and photon energy.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.

        grating : str
            The lines per mm of the grating to use, can be '300', '600', '800' or '1200'.


        EPU : str
            The undulator to use, can be '57' (default, high energy) or '105'(low energy).

        c : float, optional
            The c value required, if it is omitted or set to 'None' then it is calculated from the
            grating equations.

        angles : dict, output
            A dictionary containing the calculated values under the key-words 'alpha', 'beta',
            'gamma' and 'c'. The angles are returned in degrees.



        '''
        # check that the energy is in the range of the grating and the undulator
        if (self.Range[grating][0]> photon_energy) or (self.Range[grating][1]< photon_energy):
            raise RuntimeError('photon energy out of range for grating,'+
                               'use Eph.Range to determine the correct grating and EPU')
        if not EPU == None:
            if (self.Range['EPU'+EPU][0]> photon_energy) or (self.Range['EPU'+EPU][1]< photon_energy):
                raise RuntimeError('photon energy out of range for undulator,'+
                                   'use Eph.Range to determine the correct grating and EPU')


        if EPU == '57':
            ra = 42302.0 #in mm  DISTANCE MONO TO EPU57
        elif EPU == '105':
            ra = 40000.0 #in mm  DISTANCE MONO TO EPU105
        elif EPU == None:
            ra = 40000.0 #in mm  DISTANCE MONO TO EPU105
        else:
             raise RuntimeError("EPU entry needs to be '57','105' or None ")


        rb = 15000.0 #in mm  DISTANCE MONO TO EXIT-SLITS
        r = rb/ra
        k = [300.0, 600.0, 800.0, 1200.0] #ln per mm
        a1 = [0.0582427, 0.0933142, 0.123453, 0.231924] # VLS first grating coeff
        rad2dg = 180/np.pi
        b2, X, L, A0, A2, C, alp, beta, gamma  = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        i = k.index(float(grating))
        b2 = -a1[i]/(2*k[i])
        X= photon_energy #energy range in eV
        L = (1.24/X)*0.001  # wavelenght in mm
        A0 = (k[i]*L)
        A2 = A0*rb*b2
        if c==None:
            C = np.sqrt((2*A2 + 4*(A2/A0)**2 + (4+2*A2-A0**2)*r -4*(A2/A0)*
                     np.sqrt((1+r)**2 + 2*A2*(1+r) -r*A0**2))/(-4 + A0**2 -4*A2 +4*(A2/A0)**2))
        else:
            C=c

        alp = np.arcsin(-A0/(C**2-1) + np.sqrt(1+(C*A0)**2/(C**2-1)**2))   #in radians
        beta = np.arccos(C*np.cos(alp))   # in radians
        gamma = ( alp + beta )/2

        angles={'alpha' : alp*rad2dg , 'beta' : beta*rad2dg , 'gamma' : gamma*rad2dg, 'c' : C  }
        return angles


    def change_offsets(self, grating, branch):
        '''
        This routine is used to change the grating and M2 mirror offsets using set.

        Given a set of grating offset,mirror offset and the number of line per mm used by the PGM software
        this routine updates the offset PV's but first setting the calibration PV to "set" then returning
        it to 'use' afterwards.

        PARAMETERS
        ----------

        grating : str
            The lines per mm of the grating to use, can be '300', '600', '800' or '1200'.

        branch : str
            The beamline branch which is to be used, can be 'A' (default) or 'B'.

        '''
        #3/17/21 Note - commented out changing USE/SET, which should not be needed and may cause loss of home pos
        #yield from mv(PGM.Mirror_Pitch_set, 1 , PGM.Grating_Pitch_set, 1)

        yield from mv(PGM.Mirror_Pitch_off, float(self.M2_Offset[branch][grating]) ,
                      PGM.Grating_Pitch_off, float(self.Grt_Offset[branch][grating]),
                      PGM.Grating_lines,float(grating) )

        #yield from mv(PGM.Mirror_Pitch_set, 0 , PGM.Grating_Pitch_set, 0)

        return


    def move_to(self,photon_energy,grating='800',branch='A',EPU='57',LP='LH', c='constant',shutter='close'):
        '''
        Sets the monochromator and undulator to the correct values for the given photon energy

        This function reads the definition .csv file and writes the information to data_dict in order to
        be used in the future motion.
        PARAMETERS
        ----------

        photon_energy : float
            The photon energy value to be set.

        grating : str
            The lines per mm of the grating to use, can be '300', '600', '800' or '1200'.

        branch : str
            The beamline branch which is to be used, can be 'A' (default) or 'B'.

        EPU : str
            The undulator to use, can be '57' (default, high energy) or '105'(low energy).

        c : str, optional
            This is an optional call to define if the c value should be calculated or if the pre-defined
            dictionary should be used.

        shutter : str, optional
            This string is used to to optionally have the shutter remain open during the move.

        '''

        # check that the requested value is within the range of both the EPU and the grating.
        if (self.Range[grating][0]> photon_energy) or (self.Range[grating][1]< photon_energy):
            raise RuntimeError('photon energy out of range for grating,'+
                               'use Eph.Range to determine the correct grating and EPU')
        elif not EPU==None:
            if (self.Range['EPU'+EPU][0]> photon_energy) or (self.Range['EPU'+EPU][1]< photon_energy):
                raise RuntimeError('photon energy out of range for EPU,'+
                                   'use Eph.Range to determine the correct grating and EPU')

        #shut the front end shutter prior to moving.
        # DAMA (mrakitin): commenting it out on 06/02/2018
        # since TwoButtonShutter does not behave well. Have to revisit it.
        # if shutter is 'close':
        #     yield from mv(shutter_FOE, 'Close')

        #Set the offsets and translations for the requested locations.
        yield from self.change_offsets(grating, branch)
        yield from mv(PGM.Grating_Trans, self.Grt_Translation[grating] )

        #Determine the number of steps and make the step arrays to use when moving the photon energy.
        n_steps=int(max(round( abs(self.PGM_angles(photon_energy,grating,EPU=EPU)['gamma']-
                               PGM.Mirror_Pitch.position)/1  ),
                    round( abs(self.PGM_angles(photon_energy,grating,EPU=EPU)['beta']-
                        PGM.Grating_Pitch.position)/2  )))
        if n_steps == 0: n_steps = 1 # if the number of steps is 0 set it to 1


        # divide the range of motion of M2 and the grating into 'n_steps' even steps

        if c=='calc':
            c_val = None
        else:
            c_val= self.c_value[branch][grating]


        if n_steps==1:
            M2_steps=[(self.PGM_angles(photon_energy,grating,EPU=EPU,
                                             c=c_val)['gamma'])]
            GRT_steps=[(self.PGM_angles(photon_energy,grating,EPU=EPU,
                                             c=c_val)['beta'])]
        else:
            M2_steps=np.linspace(PGM.Mirror_Pitch.position,
                             self.PGM_angles(photon_energy,grating,EPU=EPU,
                                             c=c_val)['gamma'], num=n_steps)
            GRT_steps=np.linspace(PGM.Grating_Pitch.position,
                              self.PGM_angles(photon_energy,grating,EPU=EPU,
                                              c=c_val)['beta'], num=n_steps)

        for i in range(n_steps):   # set position of M2 pitch and GRT pitch step by step.
            yield from mv(PGM.Mirror_Pitch, M2_steps[i],    PGM.Grating_Pitch, GRT_steps[i])

        yield from mv(PGM.Focus_Const, self.PGM_angles(photon_energy,grating,EPU=EPU, c=c_val)['c'],
                      PGM.Energy, photon_energy)

        if not EPU==None:
            if LP == 'LH':
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'phase'), 0.0 )
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'gap'), self.Und_e2g(photon_energy,EPU=EPU) )
            elif LP == 'LV':
#                yield from mv(getattr(ip.user_ns['EPU'+EPU],'gap'), 100.0 )                
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'phase'), float(EPU)/2 )
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'gap'), self.Und_e2g_LV(photon_energy,EPU=EPU) )
            elif LP == 'CL':
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'gap'), 100.0 )                
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'phase'), self.Und_e2g_Cphase(photon_energy,EPU=EPU) )
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'gap'), self.Und_e2g_Cgap(photon_energy,EPU=EPU) )
            elif LP == 'CR':
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'gap'), 100.0 )                
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'phase'),-self.Und_e2g_Cphase(photon_energy,EPU=EPU) )
                yield from mv(getattr(ip.user_ns['EPU'+EPU],'gap'), self.Und_e2g_Cgap(photon_energy,EPU=EPU) )
            
        # if shutter is 'close':
        #     yield from mv(shutter_FOE, 'Open')

#######################################
# commented temporarily next few lines
#######################################
#        if branch == 'A' and EPU == '105' and (grating == '300' or grating == '600' or grating =='800'):
#            yield from mv(M3.Ry,self.M3_e2a(photon_energy, grt=grating)-0.001)  #trick for minimizing backlash
#            for i in range(10):
#                yield from mv(M3.Ry,self.M3_e2a(photon_energy,grt=grating)+i*0.0001)

        return

## Define the instances of the ESM_device class

#The monochromator definition.
Eph=ESM_monochromator_device('Eph')

def scan_energy(detectors, energies, grating='800', branch='A', EPU='57', LP='LH', c='constant', shutter='close'):
    for energy in energies:
        yield from Eph.move_to(energy, grating=grating, branch=branch, EPU=EPU, LP=LP, c=c, shutter=shutter)
        yield from count(detectors)


