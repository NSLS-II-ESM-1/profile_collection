import numpy as np
from scipy.interpolate import interp1d
from databroker import DataBroker as db, get_table, get_images, get_events

############ COLLECTING DATA ###############

def scan_1D_1Ddet(DETS, scan_motor, start, end, steps, Y_axis):

        ''' run a 1D scan using 1D detectors.
                DETS  --  A list of 1D detectors to record at each step
                scan_motor  --  The "motor" to scan which has the form Device.motor (eg. M1D_slit.inboard)
                start, end, steps      -- The start value, end value and number of steps for the motor
                Y_axis        -- The name of the detector value to plot on the live plot (eg. qem01_current1_mean_value )
   
        '''
        #Setup the scans detectors, live table and live plot using the global string  variable gs.
        gs.PLOT_Y=Y_axis
        gs.TABLE_COLS=DETS
        gs.DETS=DETS

        #Run the scan
        ascan(scan_motor,start,end,steps)

           
        
########### SAVING DATA ####################

def exp_1D_csv(f_nm, sc_num, motor, det):
        ''' save_scan_csv - usage: 

		   f_nm =string with extention '***.csv'.
                   sc_num = scan number
                   motor name
                   detector        
		   saves in csv format the last run'.
	'''								
	
        
        hdr = db[sc_num]
        df =get_table(hdr,[det, motor])
        del df['time']
        df.to_csv(f_nm,index=False)
