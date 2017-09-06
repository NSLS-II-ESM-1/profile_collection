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
from boltons.iterutils import chunked
import sys
ip=IPython.get_ipython()


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
        self.set_dicts                       # read the values to the device dictionaries
        
    # Define the class properties here
    @property

    def set_dicts(self):
        '''
        This routine is used to enter the values into the dictionaries
        
        '''    
        self.Grt_Translation = {'1200':  -65.36,            # grating translation position
                                '800':  -205.429,
                                '600': -135.9223,
                                '300':  +5.4758}

        self.Grt_Offset['A']={'1200': '81.9522200000',
                              '800': '81.93502',
                              '600': '81.874220000',
                              '300': '81.90042'}
        self.Grt_Offset['B']={'1200': '81.96202',
                              '800': '81.93972',
                              '600': '81.92532',
                              '300': '81.89542'}
        
        self.M2_Offset['A']={'1200': '83.7681090000',
                             '800': '83.760909',
                             '600': '83.683109',
                             '300': '83.77470'}
        self.M2_Offset['B']={'1200': '83.773809',
                             '800': '83.7609090000',
                             '600': '83.776709',
                             '300': '83.7605'}

        self.c_value['A']={'1200': 2.05,
                           '800': 3.2,
                           '600': 3.0,
                           '300':2.0 }
        self.c_value['B']={'1200': 2.05,
                           '800': 3.1,
                           '600': 3.0,
                           '300':2.0 }

        self.Range['1200']=[130,1500]
        self.Range['800']=[15,1500]
        self.Range['600']=[15,420]
        self.Range['300']=[15,1500]
        self.Range['EPU105']=[20,400]
        self.Range['EPU57']=[140,1390]

        self.Und_Energy['EPU57_theory'] = {'Energy':[139.458530239435,141.444392791253,143.559979210818,
                                            145.804204119565,148.175977479049,150.674204590942,
                                            153.297786097036,156.045617979241,158.916591559587,
                                            161.90959350022,165.023505803409,168.257205811538,
                                            171.609566207111,175.079455012751, 178.665735591199,
                                            182.367266645316,186.18290221808,190.11149169259,
                                            194.151879792061,198.302906579829,202.563407459347,
                                            206.932213174189,211.408149808044,215.990038784724,
                                            220.676696868157,225.466936162391,230.359564111591,
                                            235.353383500043,240.447192452151,245.639784432436,
                                            250.92994824554,256.316468036223,261.798123289363,
                                            267.373688829957,273.041934823122,278.801626774092,
                                            284.65152552822,290.59038727098,296.616963527961,
                                            302.730001164874,308.928242387547,315.210424741927,
                                            321.575281114079,328.021539730189,334.547924156559,
                                            341.153153299612,347.835941405888, 354.594998062047,
                                            361.429028194866, 368.336732071244, 375.316805298195,
                                            382.367938822854, 389.488818932475, 396.678127254427,
                                            403.934540756203, 411.256731745412, 418.643367869782,
                                            426.093112117158, 433.604622815508, 441.176553632915,
                                            448.807553577581, 456.496266997829, 464.241333582098,
                                            472.041388358949, 479.895061697059, 487.800979305224,
                                            495.757762232359, 503.764026867499, 511.818384939796,
                                            519.919443518522,528.065805013067, 536.25606717294,
                                            544.488823087768, 552.762661187298, 561.076165241395,
                                            569.427914360043, 577.816482993344, 586.240440931519,
                                            594.69835330491, 603.188780583973, 611.710278579286,
                                            620.261398441547, 628.840686661569, 637.446685070287,
                                            646.077930838752, 654.732956478137, 663.41028983973,
                                            672.108454114939, 680.825967835294, 689.561344872439,
                                            698.313094438138, 707.079721084276, 715.859724702856,
                                            724.651600525996, 733.453839125938, 742.264926415039,
                                            751.083343645777, 759.907567410748, 768.736069642664,
                                            777.567317614362, 786.399773938792, 795.231896569024,
                                            804.062138798248, 812.888949259774, 821.710771927027,
                                            830.526046113552, 839.333206473016, 848.130682999199,
                                            856.916901026004, 865.690281227452, 874.449239617682,
                                            883.192187550953, 891.917531721639, 900.623674164238,
                                            909.309012253363, 917.971938703747, 926.610841570242,
                                            935.224104247818, 943.810105471564, 952.367219316688,
                                            960.893815198516, 969.388257872493, 977.848907434185,
                                            986.274119319273, 994.662244303559, 1003.01162850296,
                                            1011.32061337352, 1019.5875357114, 1027.81072765286,
                                            1035.98851667431, 1044.11922559226, 1052.20117256335,
                                            1060.23267108431, 1068.21202999203, 1076.13755346349,
                                            1084.0075410158, 1091.82028750619, 1099.574083132,
                                            1107.26721343069, 1114.89795927984, 1122.46459689717,
                                            1129.96539784048, 1137.39862900772, 1144.76255263694,
                                            1152.05542630632, 1159.27550293415, 1166.42103077885,
                                            1173.49025343895, 1180.4814098531, 1187.39273430006,
                                            1194.22245639874, 1200.96880110813, 1207.62998872736,
                                            1214.20423489568, 1220.68975059244, 1227.08474213714,
                                            1233.38741118937, 1239.59595474884, 1245.70856515541,
                                            1251.72343008902, 1257.63873256975, 1263.4526509578,
                                            1269.16335895348, 1274.76902559721, 1280.26781526956,
                                            1285.65788769119, 1290.93739792288, 1296.10449636555,
                                            1301.15732876022, 1306.09403618803, 1310.91275507025,
                                            1315.61161716826, 1320.18874958356, 1324.64227475776,
                                            1328.97031047262, 1333.17096984997, 1337.2423613518,
                                            1341.1825887802, 1344.98975127739, 1348.66194332569,
                                            1352.19725474756, 1355.59377070556, 1358.84957170238,
                                            1361.96273358083, 1364.93132752384, 1367.75342005444,
                                            1370.4270730358, 1372.9503436712, 1375.32128450404,
                                            1377.53794341784, 1379.59836363624, 1381.50058372299,
                                            1383.24263758197, 1384.82255445717, 1386.23835893271,
                                            1387.48807093281, 1388.56970572182, 1389.48127390421,
                                              1390.22078142458, 1390.78622956762],
                                    'Gap': [16.0, 16.2211055276, 16.4422110553, 16.6633165829,
                                           16.8844221106, 17.1055276382, 17.3266331658, 17.5477386935,
                                           17.7688442211, 17.9899497487, 18.2110552764, 18.432160804,
                                           18.6532663317, 18.8743718593, 19.0954773869, 19.3165829146,
                                           19.5376884422, 19.7587939698, 19.9798994975, 20.2010050251,
                                           20.4221105528, 20.6432160804, 20.864321608, 21.0854271357,
                                           21.3065326633, 21.527638191, 21.7487437186, 21.9698492462,
                                           22.1909547739, 22.4120603015, 22.6331658291, 22.8542713568,
                                           23.0753768844, 23.2964824121, 23.5175879397, 23.7386934673,
                                           23.959798995, 24.1809045226, 24.4020100503, 24.6231155779,
                                           24.8442211055, 25.0653266332, 25.2864321608, 25.5075376884,
                                           25.7286432161, 25.9497487437, 26.1708542714, 26.391959799,
                                           26.6130653266, 26.8341708543, 27.0552763819, 27.2763819095,
                                           27.4974874372, 27.7185929648, 27.9396984925, 28.1608040201,
                                           28.3819095477, 28.6030150754, 28.824120603, 29.0452261307,
                                           29.2663316583, 29.4874371859, 29.7085427136, 29.9296482412,
                                           30.1507537688, 30.3718592965, 30.5929648241, 30.8140703518,
                                           31.0351758794, 31.256281407, 31.4773869347, 31.6984924623,
                                           31.9195979899, 32.1407035176, 32.3618090452, 32.5829145729,
                                           32.8040201005, 33.0251256281, 33.2462311558, 33.4673366834,
                                           33.6884422111, 33.9095477387, 34.1306532663, 34.351758794,
                                           34.5728643216, 34.7939698492, 35.0150753769, 35.2361809045,
                                           35.4572864322, 35.6783919598, 35.8994974874, 36.1206030151,
                                           36.3417085427, 36.5628140704, 36.783919598, 37.0050251256,
                                           37.2261306533, 37.4472361809, 37.6683417085, 37.8894472362,
                                           38.1105527638, 38.3316582915, 38.5527638191, 38.7738693467,
                                           38.9949748744, 39.216080402, 39.4371859296, 39.6582914573,
                                           39.8793969849, 40.1005025126, 40.3216080402, 40.5427135678,
                                           40.7638190955, 40.9849246231, 41.2060301508, 41.4271356784,
                                           41.648241206, 41.8693467337, 42.0904522613, 42.3115577889,
                                           42.5326633166, 42.7537688442, 42.9748743719, 43.1959798995,
                                           43.4170854271, 43.6381909548, 43.8592964824, 44.0804020101,
                                           44.3015075377, 44.5226130653, 44.743718593, 44.9648241206,
                                           45.1859296482, 45.4070351759, 45.6281407035, 45.8492462312,
                                           46.0703517588, 46.2914572864, 46.5125628141, 46.7336683417,
                                           46.9547738693, 47.175879397, 47.3969849246, 47.6180904523,
                                           47.8391959799, 48.0603015075, 48.2814070352, 48.5025125628,
                                           48.7236180905, 48.9447236181, 49.1658291457, 49.3869346734,
                                           49.608040201, 49.8291457286, 50.0502512563, 50.2713567839,
                                           50.4924623116, 50.7135678392, 50.9346733668, 51.1557788945,
                                           51.3768844221, 51.5979899497, 51.8190954774, 52.040201005,
                                           52.2613065327, 52.4824120603, 52.7035175879, 52.9246231156,
                                           53.1457286432, 53.3668341709, 53.5879396985, 53.8090452261,
                                           54.0301507538, 54.2512562814, 54.472361809, 54.6934673367,
                                           54.9145728643, 55.135678392, 55.3567839196, 55.5778894472,
                                           55.7989949749, 56.0201005025, 56.2412060302, 56.4623115578,
                                           56.6834170854, 56.9045226131, 57.1256281407, 57.3467336683,
                                           57.567839196, 57.7889447236,58.0100502513, 58.2311557789,
                                           58.4522613065, 58.6733668342, 58.8944723618, 59.1155778894,
                                           59.3366834171, 59.5577889447, 59.7788944724, 60.0]}

        self.Und_Energy['EPU105_theory'] = {'Energy':[14.506, 15.854, 17.35, 19.605, 22.13, 25.022,
                                                      28.282, 31.959, 36.126, 40.82 , 48.979, 55.283,
                                                      62.321, 70.165, 78.954, 99.51,117.879, 138.889,
                                                      162.841, 189.785, 299.25,427.514],
                                     'Gap': [16, 17.5, 19, 21, 23, 25, 27, 29, 31, 33, 36, 38, 40, 42,
                                             44, 48, 51, 54, 57, 60, 70, 80]}

        self.Und_Energy['EPU57'] = { 'Energy':[130., 140., 150., 160., 170., 180., 190., 200., 210.,
                                               220., 230., 240., 250., 260., 270., 280., 290., 300.,
                                               250., 300., 350., 400., 450., 500., 550., 600., 650.,
                                               700., 750., 800., 850., 900., 950., 1000., 1000., 1050.,
                                               1100., 1150., 1200., 1250., 1300.,1350., 1400.],
                                       'Gap': [ 16.1, 16.2, 16.9, 17.6, 18.2, 18.8, 19.4, 19.9, 20.4,
                                                20.9, 21.4, 21.9, 22.3, 22.7, 23.1,23.5, 23.95, 24.3,
                                                22.3, 24.31, 26.1, 27.7, 29.2, 30.6, 31.9, 33.2, 34.5,
                                                35.7, 37., 38.2, 39.4, 40.6, 42.0, 43.2, 43.4, 44.7,
                                                46.2, 47.8, 49.8, 52., 54.3, 57.7, 61.5] }

        self.Und_Energy['EPU105'] = {'Energy':  [ 20., 25., 30., 35., 40., 45., 50., 55., 60., 65., 70.,
                                                  75., 80., 85., 90., 95., 100., 120., 140., 160., 180.,
                                                  200., 220., 240., 260., 280., 300., 320., 340., 360.,
                                                  380., 400.],
                                     'Gap' :  [ 21.5, 25.1, 28.05, 30.6, 32.8, 34.7, 36.44, 38., 39.5,
                                                40.84, 42.1, 43.24, 44.39, 45.4, 46.39, 47.3, 48.2,
                                                51.5, 54.3, 56.8, 59.1, 61.3, 63.2, 65.1, 66.9, 68.6,
                                                70.3, 71.9, 73.5, 75.1, 76.7, 78.2] }
                                     



        
        return
    
    #Define the information functions here
    
    def Und_g2e(self,gap,EPU='EPU57'):
        '''
        This function returns the photon energy value required for a given undulator gap and undulator.

        PARAMETERS
        ----------
   
        gap : float
            The undulator gap in mm.
   

        EPU : str
            The undulator to use, can be EPU57 (default, high energy) or EPU105(low energy).

        photon_energy : float, output
            The photon energy value that is returned.

        '''

        # check that the gap value is within the range of the undulator
        if gap<min(self.Und_Energy[EPU]['Gap']) or gap>max(self.Und_Energy[EPU]['Gap']):
            raise RuntimeError('gap value out of range of undulator')    
        else:
        #return the photon energy
            gtoe=interp1d(self.Und_Energy[EPU]['Gap'],self.Und_Energy[EPU]['Energy'])
            photon_energy=float(gtoe(gap))
            return photon_energy


        
    def Und_e2g(self,photon_energy,EPU='EPU57'):
        '''
        This function returns the photon energy value required for a given undulator gap and undulator.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.
   
        EPU : str, optional
            The undulator to use, can be EPU57 (default, high energy) or EPU105(low energy).
        gap : float, output
            The undulator gap in mm.



        '''

        # check that the gap value is within the range of the undulator
        if photon_energy<min(self.Und_Energy[EPU]['Energy']) or photon_energy>max(self.Und_Energy[EPU]['Energy']):
            raise RuntimeError('energy value out of range of undulator')    
        else:
        #return the photon energy
            gtoe=interp1d(self.Und_Energy[EPU]['Energy'],self.Und_Energy[EPU]['Gap'])
            gap = float(gtoe(photon_energy))
            return gap
        

    def PGM_angles(self, photon_energy,grating,EPU='EPU57',c=None):
        '''
        This function returns the mirror angles required for a given grating and photon energy.

        PARAMETERS
        ----------
        photon_energy : float
            The photon energy value in eV.
   
        grating : str
            The lines per mm of the grating to use, can be '300', '600', '800' or '1200'.


        EPU : str
            The undulator to use, can be EPU57 (default, high energy) or EPU105(low energy).

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

        if (self.Range[EPU][0]> photon_energy) or (self.Range[EPU][1]< photon_energy):
            raise RuntimeError('photon energy out of range for undulator,'+
                               'use Eph.Range to determine the correct grating and EPU')
        
        
        if EPU == 'EPU57':
            ra = 42302.0 #in mm  DISTANCE MONO TO EPU57
        elif EPU == 'EPU105':
            ra = 40000.0 #in mm  DISTANCE MONO TO EPU105
        else:
             raise RuntimeError("EPU entry needs to be 'EPU57' or 'EPU105' ") 


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

        yield from mv(PGM.Mirror_Pitch_set, 1 , PGM.Grating_Pitch_set, 1)

        yield from mv(PGM.Mirror_Pitch_off, float(self.M2_Offset[branch][grating]) ,
                      PGM.Grating_Pitch_off, float(self.Grt_Offset[branch][grating]))
#                      PGM.Grating_lines,grating )
        os.system('caput XF:21IDB-OP{Mono:1}:LINES:SET ' + grating)  # tells to the PGM software which grating 
        yield from mv(PGM.Mirror_Pitch_set, 0 , PGM.Grating_Pitch_set, 0)

        return

                
    def move_to(self,photon_energy,grating='800',branch='A',EPU='EPU57',c='constant'):
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
            The undulator to use, can be EPU57 (default, high energy) or EPU105(low energy).

        c : str, optional
            This is an optional call to define if the c value should be calculated or if the pre-defined
            dictionary should be used.

        '''

        # check that the requested value is within the range of both the EPU and the grating.
        if (self.Range[grating][0]> photon_energy) or (self.Range[grating][1]< photon_energy):
            raise RuntimeError('photon energy out of range for grating,'+
                               'use Eph.Range to determine the correct grating and EPU')
        elif(self.Range[EPU][0]> photon_energy) or (self.Range[EPU][1]< photon_energy):       
            raise RuntimeError('photon energy out of range for EPU,'+
                               'use Eph.Range to determine the correct grating and EPU')

        #shut the front end shutter prior to moving.
        yield from mv(shutter_FOE, 'Close')

        #Set the offsets and translations for the requested locations.
        yield from self.change_offsets(grating, branch)
        yield from mv(PGM.Grating_Trans, self.Grt_Translation[grating] )

        #Determine the number of steps and make the step arrays to use when moving the photon energy.
        n_steps=int(max(round( abs(self.PGM_angles(photon_energy,grating,EPU=EPU)['gamma']-
                               PGM.Mirror_Pitch.position)/1  ),
                    round( abs(self.PGM_angles(photon_energy,grating,EPU=EPU)['beta']-
                        PGM.Grating_Pitch.position)/2  )))
        if n_steps == 0: n_steps = 1
        # divide the range of motion of M2 and the grating into 'n_steps' even steps

        if c=='calc':
            c_val = None
        else:
            c_val= self.c_value[branch][grating]

        M2_steps=np.linspace(PGM.Mirror_Pitch.position,
                             self.PGM_angles(photon_energy,grating,EPU=EPU,
                                             c=c_val)['gamma'], num=n_steps)  
        GRT_steps=np.linspace(PGM.Grating_Pitch.position,
                              self.PGM_angles(photon_energy,grating,EPU=EPU,
                                              c=c_val)['beta'], num=n_steps) 
        for i in range(n_steps):   # set position of M2 pitch and GRT pitch step by step.
            yield from mv(PGM.Mirror_Pitch, M2_steps[i],    PGM.Grating_Pitch, GRT_steps[i])              
        
        yield from mv(PGM.Focus_Const, self.PGM_angles(photon_energy,grating,EPU=EPU,
                                                       c=c_val)['c']
                      , PGM.Energy, photon_energy,
                      getattr(ip.user_ns[EPU],'gap'),self.Und_e2g(photon_energy,EPU=EPU) )
            
        yield from mv(shutter_FOE, 'Open')
        return 
        
## Define the instances of the ESM_device class

#The monochromator definition.
Eph=ESM_monochromator_device('Eph')    
  
