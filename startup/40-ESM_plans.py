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





###COLLECTING DATA
###   The following set of "plans" is used to run different types of scans at 21-ID. Using these plans instead of the 
###   in-built bluesky scans simply allows for customization of the OLOG entries, the metadata and for easier inclusion
###   of the plotting routines. The system for naming scans(which is used to create an easy to follow process) is:
###   
###          'detector'_('non standard scan identifier'_)'scan dimension'
###             
###          With the components:
###              'detector_' : This is just used at the start to define a 1D(scan) or 2D(image) detector as the live
###                            display detector. The live display detector should always be the 1st detector in the list.
###
###              'non standard scan identifier' : This is an optional inclusion to define non-standard scan, the list of
###                            options include:
###
###                  'multi_' : To define a plan that executes a series of scans, each saved as seperate files.
###
###
###              'scan dimension' : This defines the number of scan axes that the scan should step through, options include:
###
###                   'time' : for time axis scans.
###                   '1D'   : for 1 dimensional motor scans
###                   '2D'   : for 2 dimensional motor scans
###                   'ND'   : for N dimensional motor scans        
###
###Important Definitions:
###        motor: Any variable that can be "set" by bluesky including:
###                   motors, temperatures (if controlled by a temperature controller), pressures (if controlled by a leak
###                      valve), voltages, photon energy, etc 
###
###    detectors: Any device in bluesky that provides readback including:
###                   Analyzers, cameras, pico-ammeters, currents, pressures, temperatures, etc.



###        
###TIME SCANS
###These scans are used to scan over time.


def scan_time(detectors,num=1,delay=0,DET_channel=None,DET_channel_value=None,scan_type=None):
    '''
    scan over time
    This scan provides a time measurement of a list of detectors, including live plotting and a live table. The detector to 
    'display' must be 1D, or have statistics set up so that a 1D attribute exists (such as intengrated 'total' intensity)  
    and should be first in the list. 
         
    PARAMETERS
    ----------
    detectors : list
        A list of detectors to record at each step.
    num : number, optional
        Optional input of the number of points to take, default is 1. To capture until stopped using 'ctrl-C' set 'num = None'
    delay : number, optional  
        Optional delay time between succesive readings, default is 0.
    DET_channel : list, optional  
        Optional channel number, for each detector, to plot for multi channel detectors 
        (eg. for qem to plot 'qem01_current1_mean_value' use 1). 
            To use this option in the scan call you need to place ',

            DET_channel=[[det1_x1,det1_x2...],[det2_x1...],...]' after 'steps' in the scan call

    DET_channel_value : list, optional 
        Optional channel value, for each detector and channel defined abvoe, to plot for multi channel detectors 
        (eg. for a camera to plot 'stats1_max_value' use "max"). 
            To use this option in the scan call you need to place ',DET_channel=x' after 'steps'  and 
            DET_channel=[[det1_x1_val,det1_x2_val...],[det2_x1_val...],...] where "*_val" is 'total', 'max', or 'min'.


    scan_type : string, optional 
        Optional definition of the scan type to include in the metadata, correct use of this will allow searching the 
        database to be easier (for instance, if all XPS data is given the scan_type 'XPS' then searching the database 
        based on the keyword scan_type = 'XPS' will return all XPS scans).
     '''
    #This section determines the Y axis variable to plot for the scan, if the first detector in the list is a single channel
    #detector then it plots that detector value, if it has multiple single channels it plots the channel defined by the
    #optional input DET_channel (channel 1 is plotted if DET_channel is not specified.
#    Y_axis = Get_Yaxis_name(detectors[0], DET_channel)

    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file.
    #Users can add/or change the metadata using the md={'keyword1'
    #:'value1','keyword2':'value2',..... } argument. For instance using md={'scan_type':'measurement type'}
    #will define the scan_type as a particular
    #measurement type.
        
    #setup standard metadata
    # _md = {'scan_name':'scan_time','plot_Xaxis':'sequence_no','plot_Yaxis':Y_axis,'scan_type':scan_type,'delay':delay}

    #change the "hints" on the detectors so that only the relevant info is included
    ESM_setup_hints(detectors,DET_channel,DET_channel_value)

    if num is not 1:

        def inner():
            return( yield from count(detectors,num,delay))
    else:
        def inner():
            return( yield from count(detectors,num,delay))
      
    uid=yield from inner()
    motors=[]
#    ESM_save_csv(uid,Y_axis,motors,time=True)

    return uid
    

###    
###1D SCANS
###These scans are used to scan over 1 "motor" axis, the motor can be any variable that can be "set" via bluesky.


def scan_1D(detectors, scan_motor, start, end ,step_size,DET_channel=None,DET_channel_value=None,scan_type=None,adaptive=None):

    ''' 
    scan over a single axis taking a list of detectors at each point.
    This scan provides a 1D scan using a list of detectors, including a live plot and a live table. The detector to 
    "display" must be 1D and should be the first in the list of detectors, or have statistics set up so that a 1D 
    attribute exists (such as integrated 'total' intensity) and should be first in the list.
        
    PARAMETERS
    ----------   
    detectors : list  
        A list of detectors to record at each step.
    scan_motor : motor  
        The "motor" to scan which has the form Device.motor (eg. M1D_slit.inboard)
    start : number
        The start value for the scan axis
    end : number 
        The end value for the scan axis, the actual end value will be determined from the start and step size.    
    step_size : number
        The step size for the scan axis

    DET_channel : list, optional  
        Optional channel number, for each detector, to plot for multi channel detectors 
        (eg. for qem to plot 'qem01_current1_mean_value' use 1). 
            To use this option in the scan call you need to place ',

            DET_channel=[[det1_x1,det1_x2...],[det2_x1...],...]' after 'steps' in the scan call

    DET_channel_value : list, optional 
        Optional channel value, for each detector and channel defined abvoe, to plot for multi channel detectors 
        (eg. for a camera to plot 'stats1_max_value' use "max"). 
            To use this option in the scan call you need to place ',DET_channel=x' after 'steps'  and 
            DET_channel=[[det1_x1_val,det1_x2_val...],[det2_x1_val...],...] where "*_val" is 'total', 'max', or 'min'.


    scan_type : string, optional
        Optional definition of the scan type to include in the metadata, correct use of this will allow searching the 
        database to be easier (for instance, if all XPS data is given the scan_type 'XPS' then searching the database 
        based on the keyword scan_type = 'XPS' will return all XPS scans).    

    Adaptive scan : list, optional 
        This is a scan where the step size is adaptively set based on a target slope. For instance the 
        step size starts off at steps_max, if the slope between the current point and the preceeding 
        point is greater/smaller than a target slope then it decreases/increases the step size to achieve 
        the desired slope. Addtionally 'backstep=True' can be used to allow for the scan to go back and 
        add more points between preceding points.

        To use this feature include ', adaptive = [steps2_min,steps2_max,target_slope,backstep,threshold] after 
        step_size in the call. 
        
            NOTE: In this case step_size is not used, but a value must be included.
                           
                 REQUIRED PARAMETERS FOR THIS OPTION 
                     steps2_min, steps2_max  : Are the minimum and maximum step sizes to use in the adaptive scan.
                     target slope            : Is a target slope to aim for in the scan
                     backstep                : Is a boolean (either 'True' or 'False') which determines if the scan 
                                               is allowed to back step to aquire more data in a region of large change.
                     threshold               : Is a threshold for going back and rescanning a region (default is 0.8).  
                           
     '''
    # This section determines the no of steps to include in order to get as close as possible to the endpoint specified.

    if(  ( start<end and step_size<0 ) or ( start>end and step_size>0 )   ):
        step_size*=-1
    
    steps=abs(round((end-start)/step_size))
    stop=start+step_size*steps

    #This section determines the Y axis and X axis variable to plot for the scan, if the first detector in the list is a
    #single channel detector then it plots that detector value, if it has multiple single channels it plots the channel
    #defined by the optional input DET_channel (channel 1 is plotted if DET_channel is not specified), the X_axis is
    #assumed to be the first motor in the list 'motors'.
#    Y_axis = Get_Yaxis_name(detectors[0], DET_channel)
#    motors=[scan_motor]
#    X_axis = first_key_heuristic(list(motors)[0])
#    motors_list=[X_axis]
    
    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the
    #metadata using the md={'keyword1':'value1','keyword2':'value2',..... } argument. For instance using
    #md={'scan_type':'measurement type'} will define the scan_type as a particular measurement type.
        
    #setup standard metadata
#    _md = {'scan_name':'scan_1D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'scan_type':scan_type,'delta':step_size}

    

        
    #Define the scan
    def inner():
      if adaptive is None:
          return( yield from scan(detectors,scan_motor,start,stop,steps+1,md=_md))
      else:
          return( yield from adaptive_scan(detectors,Y_axis,scan_motor,start,stop,adaptive[0],adaptive[1],adaptive[2],
                                           adaptive[3],adaptive[4],md=md_))

    #run the scan  
    uid=yield from inner()
    # save the data to .csv
    ESM_save_csv(uid,Y_axis,motors_list)

    return uid

    

###
###2D SCANS
###These scans are used to scan over 2 "motor" axes, the motors can be any variable that can be "set" via bluesky.


def scan_multi_1D(detectors, scan_motor1, start1, end1, step_size1,scan_motor2, start2, end2, step_size2,
                  snake=False,DET_channel=None,DET_channel_value=None,scan_type=None,adaptive=None):
    ''' 
    run a series of 1D scans over a second motor (each line saved seperately). 
    Run a 2D scan using a list of detectors, having each step as a new file,the detector to "display" must be 1D, or 
    have statistics set up so that a 1D attribute exists (such as intengrated 'total' intensity) and should be first 
    in the list. It must be the first detector in the list 'DETS'.
        
    PARAMETERS
    ----------
    detectors : list 
        A list of detectors to record at each step
    scan_motor1 : motor
        The outer "motor" to scan (which is different for each file) which has the form Device.motor (eg. 
        M1D_slit.inboard)
    scan_motor2 : motor 
        The inner "motor" to scan (x axis for each file) which has the form Device.motor (eg. M1D_slit.inboard)
    start1,start2 : numbers
        The start values for axis 1 and axis 2 respectively
    end1,end2 : numbers
        The end values axis 1 and axis 2 respectively (this is a suggested value only, real value will be deteremined 
        using start and step_size.
    steps1,steps2 : numbers
        The number of steps for axis 1 and axis 2 respectively.

    snake : boolean, optional
        Optional snake value (ie. have the scan move the scan_motor2 from start2 to end2 on even runs and from end2 
            to start2 on odd runs. 
                To use this option in the scan you need to place ',snake=True' after steps in the scan call.                          
    DET_channel : list, optional  
        Optional channel number, for each detector, to plot for multi channel detectors 
        (eg. for qem to plot 'qem01_current1_mean_value' use 1). 
            To use this option in the scan call you need to place ',

            DET_channel=[[det1_x1,det1_x2...],[det2_x1...],...]' after 'steps' in the scan call

    DET_channel_value : list, optional 
        Optional channel value, for each detector and channel defined abvoe, to plot for multi channel detectors 
        (eg. for a camera to plot 'stats1_max_value' use "max"). 
            To use this option in the scan call you need to place ',DET_channel=x' after 'steps'  and 
            DET_channel=[[det1_x1_val,det1_x2_val...],[det2_x1_val...],...] where "*_val" is 'total', 'max', or 'min'.


    scan_type : string, optional
        Optional definition of the scan type to include in the metadata, correct use of this will allow searching the 
        database to be easier (for instance, if all XPS data is given the scan_type 'XPS' then searching the database 
        based on the keyword scan_type = 'XPS' will return all XPS scans).   
   
 
    Adaptive scan : boolean, True
       This is a scan where the step size is adaptively set based on a target slope. For instance the step 
       size starts off at steps_max, if the slope between the current point and the preceeding point is 
       greater/smaller than a target slope then it decreases/increases the step size to achieve the desired 
       slope. Addtionally 'backstep=True' can be used to allow for the scan to go back and add more points 
       between preceding points.

       To use this feature include ', adaptive = [steps2_min,steps2_max,target_slope,backstep,threshold] after 
       step_size in the call. 
                           NOTE: In this case step_size is not used, but a value must be included.
                           
                           REQUIRED PARAMETERS FOR THIS OPTION
                               steps2_min, steps2_max  : Are the minimum and maximum step sizes to use in the 
                                                         adaptive scan.
                               target slope            : Is a target slope to aim for in the scan
                               backstep                : Is a boolean (either 'True' or 'False') which determines 
                                                         if the scan 
                                                         is allowed to back step to aquire more data in a region of 
                                                         large change.
                               threshold               : Is a threshold for going back and rescanning a region 
                                                         (default is 0.8).  
        '''


        


    # This section determines the no of steps to include in order to get as close as possible to the endpoint specified.
    if(  ( start1<end1 and step_size1<0 ) or ( start1>end1 and step_size1>0 )   ):
        step_size1*=-1
    
    steps1=abs(round((end1-start1)/step_size1))
    stop1=start1+step_size1*steps1

    if(  ( start2<end2 and step_size2<0 ) or ( start2>end2 and step_size2>0 )   ):
        step_size2*=-1
    
    if adaptive is None:
        steps2=abs(round((end2-start2)/step_size2))
        stop2=start2+step_size2*steps2
    else:
        steps2=adaptive[1]
        stop2=end2

    initial_uid = 'current uid'
    #This value holds the intial uid for the scan.
    
    #This section determines the Y axis variable to plot for the scan, if the first detector in the list is a single
    #channel detector then it plots that detector value, if it has multiple single channels it plots the channel
    #defined by the optional input DET_channel (channel 1 is plotted if DET_channel is not specified.)
#    Y_axis = Get_Yaxis_name(detectors[0], DET_channel)
#    motors=[scan_motor2]
#    X_axis = first_key_heuristic(list(motors)[0])
#    motors_list=[X_axis]
    
    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the
    #metadata using the md={'keyword1':'value1','keyword2':'value2',..... } argument. For instance using md={'scan_name'
    #:'measurement type'} will define the scan_name as a particular measurement type.
        
    #setup standard metadata
#    _md = {'scan_name':'scan_multi_1D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'scan_type':scan_type,'delta':step_size2,
#'multi_axis':scan_motor1.name,'multi_start':start1,'multi_stop':stop1,'multi_num':steps1+1,
#              'multi_delta':step_size1}

         


    for i,c_val in enumerate(np.linspace(start1, stop1, num=(steps1+1))):
    # Step through each of the outer motor values
       yield from abs_set(scan_motor1, c_val, wait=True )
         
       #add the location of this scan in the multi scan, and the intial uid.
       
       _md.update ( {'multi_pos':i+1 , 'initial_uid': initial_uid } )
       
           

       def inner_forward():
           if adaptive is None:
               return(yield from scan(detectors,scan_motor2,start2,stop2,steps2+1,md=_md))
           else:
              return( yield from adaptive_scan(detectors,Y_axis,scan_motor2.name,start2,stop2,adaptive[0],adaptive[1],
                                               adaptive[2],adaptive[3],adaptive[4],md=_md))
           #defines what the scan at each motor 1 step should be

       def inner_backward():
           if adaptive is None:
               return (yield from scan(detectors,scan_motor2,stop2,start2,steps2+1,md=_md))
           else:
              return( yield from adaptive_scan(detectors,Y_axis,scan_motor2,stop2,start2,-1*adaptive[0],-1*adaptive[1],
                                               adaptive[2],adaptive[3],adaptive[4],md=_md))
           #defines what the scan at each motor 1 step should be

       # performs the next step in the scan
       if snake:
           if i%2==1:
               uid=yield from inner_backward()
           else:
               uid=yield from inner_forward()
       else:
          uid= yield from inner_forward()
       
       if initial_uid is 'current uid':
           initial_uid = uid
       
       #Save the file as a csv file using the scan id as the name
       ESM_save_csv(uid,Y_axis,motors_list)
       
    return initial_uid

       
def scan_2D(detectors, scan_motor1, start1, end1, step_size1,scan_motor2, start2, end2, step_size2,
                  snake=False,concurrent=False,normal_spiral=False,fermat_spiral=False,square_spiral=False,
                  DET_channel=None,DET_channel_value=None,scan_type=None):
    '''
    Run a 2D scan using a list of detectors.
        
    PARAMETERS
    ----------
    detectors : list 
        A list of detectors to record at each step
    scan_motor1 : motor
        The outer "motor" to scan (which is different for each file) which has the form Device.motor 
        (eg. M1D_slit.inboard)
    scan_motor2 : motor 
        The inner "motor" to scan (x axis for each file) which has the form Device.motor 
        (eg. M1D_slit.inboard)
    start1,start2 : numbers
        The start values for axis 1 and axis 2 respectively
    end1,end2 : numbers
        The end values axis 1 and axis 2 respectively (this is a suggested value only, real value will 
        be deteremind using start and step_size.
    steps1,steps2 : numbers
        The number of steps for axis 1 and axis 2 respectively.

    snake : boolean, optional
        Optional snake value (ie. have the scan move the scan_motor2 from start2 to end2 on even runs 
        and from end2 to start2 on odd runs. 
            To use this option in the scan you need to place ',snake=True' after steps in the scan call.                          
    DET_channel : list, optional  
        Optional channel number, for each detector, to plot for multi channel detectors 
        (eg. for qem to plot 'qem01_current1_mean_value' use 1). 
            To use this option in the scan call you need to place ',

            DET_channel=[[det1_x1,det1_x2...],[det2_x1...],...]' after 'steps' in the scan call

    DET_channel_value : list, optional 
        Optional channel value, for each detector and channel defined abvoe, to plot for multi channel detectors 
        (eg. for a camera to plot 'stats1_max_value' use "max"). 
            To use this option in the scan call you need to place ',DET_channel=x' after 'steps'  and 
            DET_channel=[[det1_x1_val,det1_x2_val...],[det2_x1_val...],...] where "*_val" is 'total', 'max', or 'min'.



    scan_type : string, optional
        Optional definition of the scan type to include in the metadata, correct use of this will allow 
        searching the database to be easier (for instance, if all XPS data is given the scan_type 'XPS' then 
        searching the database based on the keyword scan_type = 'XPS' will return all XPS scans).   
   

    Concurrent motion : boolean, optional
        This allows for the motion of the first and second motors to occur concurrently. This will map out a
        1D line though 2D space, with even spaced steps for both axes.
            To use this feature include 'concurrent=True ' after step_size2 in the call. 
                           
            NOTE: In this case step_size2 is not used, but a value must be included. the step size of the second 
            motor will be determined fro mthe calucalted number of steps for motor one and the range of motor 2.
                           
           
    spiral : boolean, optional 
        Optional indicator that the scan should follow a spiral pattern, centered in the middle of the x and y 
        ranges defined.
  
            To use this feature include ' normal_spiral = True' after step_size2 in the call
                               
                NOTE: The radius delta is determined from the first motor step size and the number of theta steps is 
                determined from the radius delta and the motor 2 step size. The pattern for the spiral is a series of 
                expanding "rings", according to the following relationships:
                                
                                 Parameters:

                                 1. range1 = end1-start1, range2 = end2-start2

                                 2. centre1 = start1+range1/2, centre2=start2+range2/2

                                 3. delta_radius = step_size2

                                 4. num_theta = round( (4*pi*delta_radius) / ( range2*atan(2*step_size1) )   ) 

                                 note: this equation ensures that the y axis step size for the largest circle is ~ 
                                 step_size1

                                 5. num_rings = 1+int( ( ((range1/2)**2+(range2/2)**2)**(1/2) / (delta_radius)  )**2 )

                                 6. n = the 'nth' ring in the spiral, i = the 'ith' angle for the 'nth'ring
 
                                 Path equations:
 
                                 1. radius = n**(1/2) * delta_radius * num_theta/2

                                 2. delta_angle = 2*pi/( n*num_theta )

                                 3. angle  = i * delta_angle 

                                 4. x = centre2 + radius*cos(angle)                               

                                 5. y = centre1 + radius*sin(angle)
             
                          REQUIRED PARAMETERS FOR THIS OPTION
                               no extra parameters are required.


    fermat spiral : boolean, optional
        Optional indicator that the scan should follow a fermat spiral pattern, centered in the middle of the x and 
        y ranges, defined.

            To use this feature include ' fermat_spiral = True' after step_size2 in the call.
                               
                NOTE: The radius delta is determined from the first motor step size and the number of theta steps is 
                determined from the radius delta and the motor2 step size. The pattern for the spiral maps out a fermat 
                spiral, according to the following relationships:

                                 Parameters:

                                 1. range1 = end1-start1, range2 = end2-start2

                                 2. centre1 = start1+range1/2, centre2=start2+range2/2

                                 3. delta_radius = step_size2

                                 4. num_theta = round( (4*pi*delta_radius) / ( range2*atan(2*step_size1) )   ) 
                                         note: this equation ensures that the y axis step size for the largest circle is 
                                         ~ stepsize1

                                 5. num_rings = int((1.5*((range1/2)**2+(range2/2)**2)**(1/2) * num_theta/(2*delta_radius))**2)
                                 
                                 6. phi = 137.508 * pi/180

                                 7. n = the 'nth' ring in the spiral
 
                                 Path equations:

                                 1. radius = n**(1/2) * delta_radius * num_theta/2

                                 2. angle  = phi * n 

                                 3. x = centre2 + radius*cos(angle)                               

                                 4. y = centre1 + radius*sin(angle)

                           REQUIRED PARAMETERS FOR THIS OPTION
                               no extra parameters are required.



    square spiral : boolean, optional
        Optional indicator that the scan should follow a square spiral pattern, centered in the middle of the x and y 
            ranges defined.
  
            To use this feature include ' square_spiral = True' after step_size2 in the call

                NOTE:  The pattern for the square spiral is a series of expanding square "rings", the number of points in
                both the x and y ranges needs to be both even or both odd, this will be set in the plan if it is not already
                true.

 
        '''


        
 

    # This section determines the no of steps to include in order to get as close as possible to the endpoint specified.
    if(  ( start1<end1 and step_size1<0 ) or ( start1>end1 and step_size1>0 )   ):
        step_size1*=-1

    if(  ( start2<end2 and step_size2<0 ) or ( start2>end2 and step_size2>0 )   ):
        step_size2*=-1

    if concurrent is True:
        steps1=abs(round((end1-start1)/step_size1))
        stop1=start1+step_size1*steps1
        
        steps2=steps1
        stop2=end2
        step_size2=(stop2-start2)/steps2

    elif normal_spiral is True or fermat_spiral is True:
        range2=end2-start2
        centre2=start2+(range2)/2
        
        range1=end1-start1
        centre1=start1+(range1)/2

        delta_radius=step_size2
        num_theta=round( (4*math.pi*delta_radius)/( math.atan(2*step_size1)*range2) )

    elif square_spiral is True:
        range2=end2-start2
        centre2=start2+(range2)/2
        
        range1=end1-start1
        centre1=start1+(range1)/2
        #print ( 'end2: '+ str(end2) + ' start2: ' + str(start2) + ' step_size2: ' + str(step_size2)   )  

        steps2=round((end2-start2)/step_size2)
        steps1=round((end1-start1)/step_size1)
        #print ( 'steps2: '+ str(steps2) + ' steps1: ' + str(steps1)   )  
        
        
        if ( (steps2%2==1) and (steps1%2!=1) ) or ( (steps2%2!=1) and (steps1%2==1) ) :
            steps1+=1
            
        #print ( 'steps2: '+ str(steps2) + ' steps1: ' + str(steps1)   )  
        
    else:    
        steps1=abs(round((end1-start1)/step_size1))
        stop1=start1+step_size1*steps1

        steps2=abs(round((end2-start2)/step_size2))
        stop2=start2+step_size2*steps2
    

        
    #This section determines the Z axis variable to plot for the scan, if the first detector in the list is a single channel
    #detector then it plots that detector value, if it has multiple single channels it plots the channel defined by the
    #optional input DET_channel (channel 1 is plotted if DET_channel is not specified).
#    Z_axis = Get_Yaxis_name(detectors[0], DET_channel)
#    Xmotors=[scan_motor2]
#    X_axis = first_key_heuristic(list(Xmotors)[0])
#    Ymotors=[scan_motor1]
#    Y_axis = first_key_heuristic(list(Ymotors)[0])

    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the metadata
    #using the md={'keyword1':'value1','keyword2':'value2',..... } argument. For instance using md={'scan_name':
    #'measurement type'} will define the scan_name as a particular measurement type.
        
    #setup standard metadata

    
    if concurrent is True:
 #       _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_typ#e,
#             'X_axis':X_axis,'X_start':start2,'X_stop':stop2,'X_num':steps2+1,'X_delta':step_size2,
#             'Y_axis':Y_axis,'Y_start':start1,'Y_stop':stop1,'Y_num':steps1+1,'Y_delta':step_size1}

        # Define some decorators to perform at each step (table update, plot update etc.)

        def inner_prod():
            return(yield from inner_product_scan(detectors,steps1+1,scan_motor1,start1,stop1,scan_motor2,start2,stop2,))#md=_md))

        uid= yield from inner_prod()
        
    elif normal_spiral is True:
#         _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
#               'X_axis':X_axis,'X_start':start2,'X_end':end2,'X_centre':centre2,'X_range':range2,'delta_radius':delta#_radius,
#               'Y_axis':Y_axis,'Y_start':start1,'Y_end':end1,'Y_centre':centre1,'Y_range':range1,'num_theta':num_theta}  


         # Define some decorators to perform at each step (table update, plot update etc.)
         mesh = LiveMesh(X_axis,Y_axis,Z_axis, xlim=(start2-step_size2,end2+step_size2), ylim=(start1-step_size1,
                                                                                             end1+step_size1) )

         @subs_decorator(mesh)


         
         def spiral_scan():
             return(yield from spiral(detectors,scan_motor2,scan_motor1,centre2,centre1,range2,range1,delta_radius,
                                      num_theta))#,md=_md))

         uid= yield from spiral_scan()

         
    elif fermat_spiral is True:
#        _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
#               'X_axis':X_axis,'X_start':start2,'X_end':end2,'X_centre':centre2,'X_range':range2,'delta_radius':delta_radius,
#               'Y_axis':Y_axis,'Y_start':start1,'Y_end':end1,'Y_centre':centre1,'Y_range':range1,'num_theta':num_theta}


        
        mesh = LiveMesh(X_axis,Y_axis,Z_axis, xlim=(start2-step_size2,end2+step_size2), ylim=(start1-step_size1,
                                                                                             end1+step_size1) )

        @subs_decorator(mesh)


        def fermat_scan():
            return(yield from spiral_fermat(detectors,scan_motor2,scan_motor1,centre2,centre1,range2,range1,delta_radius,
                                            num_theta/2))#,md=_md))
    
        uid= yield from fermat_scan()

        
    elif square_spiral is True:
 #       _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
#               'X_axis':X_axis,'X_start':start2,'X_end':end2,'X_centre':centre2,'X_range':range2,'x_num':steps2,
#               'Y_axis':Y_axis,'Y_start':start1,'Y_end':end1,'Y_centre':centre1,'Y_range':range1,'y_num':steps1}

        
        mesh = LiveMesh(X_axis,Y_axis,Z_axis, xlim=(start2-step_size2,end2+step_size2), ylim=(start1-step_size1,
                                                                                              end1+step_size1) )

        @subs_decorator(mesh)


        def square_scan():
            return(yield from spiral_square(detectors,scan_motor2,scan_motor1,centre2,centre1,range2,range1,
                                            steps2+1,steps1+1,md=_md))
    
        uid= yield from square_scan()


        
    else:
 #       _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
#               'X_axis':X_axis,'X_start':start2,'X_stop':stop2,'X_num':steps2+1,'X_delta':step_size2,
#             'Y_axis':Y_axis,'Y_start':start1,'Y_stop':stop1,'Y_num':steps1+1,'Y_delta':step_size1}

        grid = LiveGrid( (steps1+1,steps2+1) , Z_axis , ylabel= Y_axis, xlabel= X_axis, extent=(start2-step_size2/2,                                                                                                stop2+step_size2/2,start1-step_size1/2,stop1+step_size1/2),
                         aspect=(abs( (stop2-start2)/(stop1-start1) ) ) ) 
        
        @subs_decorator(grid)
        # Define some decorators to perform at each step (table update, plot update etc.)

        def outer_prod():
            return(yield from outer_product_scan(detectors,scan_motor1,start1,stop1,steps1+1,scan_motor2,start2,stop2,
                                                 steps2+1,snake))#,md=_md))

        uid=yield from outer_prod()

    return uid


        
def scan_ND(DETS, *args,concurrent=False,DET_channel=None,DET_channel_value=None,scan_type=None):
    ''' run a 2D scan using a list of detectors,the detector to "display" must be 1D, or have statistics set up so that 
        a 1D attribute exists (such as intengrated 'total' intensity) and should be first in the list. It must be the 
        first detector in the list 'DETS'.
        
        PARAMETERS
        ----------

        detectors : list  
            A list of detectors to record at each step.
        *args : - 
           This is a patterned like;
                      ( ''scan_motor1, start1,end1,step_size1,  scan_motor2, start2,end2,step_size2,snake2    ....... 
                                scan_motorN, startN,endN,step_sizeN,snake3)   
                scan_motorX  --  The Xth "motor" to scan which has the form Device.motor (eg. M1D_slit.inboard), the 
                      first motor is the outer most (slowest) motor and the last is the inner (fastest) motor.
                startX,endX,step_sizeX  -- The start value, end value and number of steps for the Xth motor, the end 
                      value will actually be >= to endX, to ensure that the step_size is correct.
                snakeX  -- For all motors but the first motor there is this 'snake' argument that defines if a winding 
                      trajectory (min -> max, max -> min, ....) or a left-right trajectory (min -> max, min -> max, ....) 
                      is to be used. This is 'True' for a winding trajectory and 'False' for a left-right trajectory.
                                      
    DET_channel : list, optional  
        Optional channel number, for each detector, to plot for multi channel detectors 
        (eg. for qem to plot 'qem01_current1_mean_value' use 1). 
            To use this option in the scan call you need to place ',

            DET_channel=[[det1_x1,det1_x2...],[det2_x1...],...]' after 'steps' in the scan call

    DET_channel_value : list, optional 
        Optional channel value, for each detector and channel defined abvoe, to plot for multi channel detectors 
        (eg. for a camera to plot 'stats1_max_value' use "max"). 
            To use this option in the scan call you need to place ',DET_channel=x' after 'steps'  and 
            DET_channel=[[det1_x1_val,det1_x2_val...],[det2_x1_val...],...] where "*_val" is 'total', 'max', or 'min'.

        
        scan_type : string optional.
            Optional definition of the scan type to include in the metadata, correct use of this will allow searching the 
            database to be easier (for instance, if all XPS data is given the scan_type 'XPS' then searching the database 
            based on the keyword scan_type = 'XPS' will return all XPS scans).   

        Concurrent motion : Boolean, optional
                Optional boolean that allows for the motion of the first and second motors to occur concurrently. This will map 
                out a 1D line though ND space, with even spaced steps for all axes.

                           To use this feature include 'concurrent=True ' after step_size2 in the call. 
                               NOTE: In this case step_size2 is not used, but a value must be included. the step size of the second 
                               motor will be determined fro mthe calucalted number of steps for motor one and the range of motor 2.
                           
                           REQUIRED PARAMETERS FOR THIS OPTION
                               no extra parameters are required.
        '''

    args = list(args)
    #turn the *args entry itno a list
    args.insert(4,False)
    #insert "False" as the snake value for the first argument to make it easy to seperate the axes.
    if len(args) %5 !=0:
        raise ValueError("wrong number of positional arguments")

    chunk_args= chunked(args,5)
        
 
    Dim = len(chunk_args)
    #define the number of motor axes in the scan
    new_args = []
    #define the new args list to be sent to the scan plan.
    motors_list = []
    
    # This section determines the no of steps to include in order to get as close as possible to the endpoint specified.

 #   _md = {'scan_name':'scan_ND','scan_type':scan_type}
    
    # for each motor axis in the scan.
    for i,motor_list in enumerate(chunk_args):

        motor=[motor_list[0]]
        motors_list.append(first_key_heuristic(list(motor)[0]))
        
        if (  (motor_list[1]<motor_list[2] and motor_list[3]<0) or ( motor_list[1]>motor_list[2] and motor_list[3]>0 )   ):
            motor_list[3]*=-1
            # ensure that the direction defined by the step_size matches that defined by start and stop.

        
            
        if concurrent is True:
        #if the scan is an inner product scan.
            Y_axis = Get_Yaxis_name(detectors[0], DET_channel)
            new_args.append(motor_list[0])
            new_args.append(motor_list[1])
            if i == 0:   
                steps=abs(round((motor_list[2]-motor_list[1])/motor_list[3]))+1
                stop=motor_list[1]+motor_list[3]*(steps-1)
                new_args.append(stop)
                _md.update({'steps':steps,'axis'+str(Dim-i): motor_list[0].name,'start'+str(Dim-i): motor_list[1],
                            'stop'+str(Dim-i):motor_list[2],'delta'+str(Dim-i):motor_list[3]})
                X_motors = [motor_list[0]]
            else:
                step_size=(motor_list[2]-motor_list[1])/(steps-1)
                new_args.append(motor_list[2])
                _md.update({'axis'+str(Dim-i): motor_list[0].name,'start'+str(Dim-i): motor_list[1],
                            'stop'+str(Dim-i):motor_list[2],'delta'+str(Dim-i):step_size}) 
                 
                
        else:
        # if the scan is a normal outer product scan
            #define the number of steps and the new stop value based on the step_size.
            steps=abs(round((motor_list[2]-motor_list[1])/motor_list[3]))
            stop=motor_list[1]+motor_list[3]*steps

            #add the new values to the new_args list
            new_args.append(motor_list[0])
            new_args.append(motor_list[1])
            new_args.append(stop)
            new_args.append(steps+1)

            if i != 0:
                new_args.append(motor_list[4])

 #           _md.update({'axis'+str(Dim-i): motor_list[0].name,'start'+str(Dim-i): motor_list[1],'stop'+str(Dim-i):motor_list[2],
#                    'num'+str(Dim-i):steps,'delta'+str(Dim-i):motor_list[3]})
      
    

        
    #This section determines the Z axis variable to plot for a 2D axis scan, if the first detector in the list is a single
    #channel detector then it plots that detector value, if it has multiple single channels it plots the channel defined by
    #the optional input DET_channel (channel 1 is plotted if DET_channel is not specified).


    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the metadata using
    #the md={'keyword1':'value1','keyword2':'value2',..... } argument. For instance using md={'scan_name':'measurement type'} will
    #define the scan_name as a particular measurement type.
        
    #setup standard metadata



    #This section sets up the rest of the info and performs the correct scan.
    if concurrent is True:
    #if the scan is an inner product scan.

        #setup the table, plotting and the metadata.

        def inner_prod():
            return(yield from inner_product_scan(detectors,steps,*new_args,md=_md))

        uid= yield from inner_prod()
        
    else:
    # if the scan is a normal outer product scan
        
            
        #re-cast the new_args list to a tuple
        new_args = tuple(new_args)

        # Define some decorators to perform at each step (table update, plot update etc.)

            
        def outer_prod():
            return(yield from outer_product_scan(detectors,*new_args))#,md=_md))


        uid=yield from outer_prod()

    return uid





###
###Alignment scans
###These are scans specifically written for beamline alignment. 

def M3_pitch_alignment(Branch="A"):
    ''' 
    Runs a scan of the M3 mirror pitch to the exit slit to find the maximum and then sets the pitch to this value. 
        
    This scan is used to find the optimal location of either the M3 mirror pitch. It runs a 1D scan over a
    pre-determined range for the M3 Pitch and then determines the intensity maxima position. The range of the scan is 
    different if the scan is for the B branch or the A branch.

    PARAMETERS
    ----------

    Branch : string, optional
        This allows for the selection of the Branch line for the scan to use. 
                    Allowed values are: A - use the "A" branch.
                                        B - use the "B" branch.
                                       
    '''

    x_axis = M3.Ry                 # The x axis of the scan

    FE_hgap_axis = FEslit.h_gap     # The front end horizontal gap motor
    FE_hgap_pos  = 0.6               # The front end horizontal gap value
    FE_vgap_axis = FEslit.v_gap     # The front end vertical gap motor
    FE_vgap_pos  = 0.6               # The front end vertical gap value

    scan_type_str='M3_pitch_alignment_'+Branch
    
    if Branch is "A":
        x_start = -0.69              # The x_axis start value of the scan
        x_end   = -0.73              # The x_axis end value of the scan
        x_stepsize = -0.00002          # The x_axis step size of the scan

        detector = qem07      # The detector to use for the scan.
        det_range = '350 pC'     # The range to use for the scan
        det_vals_reading = 5  # The values per reading to use.
        det_avg_time = 0.1    # The averaging time to use.
        det_int_time = 0.0004 # The integration time to use.

        Exit_Slit_hgap_motor = ExitSlitA.h_gap # The motor required to move the horizontal exit slit
        Exit_Slit_hgap_pos = 5                # The horizontal gap opening to use
        Exit_Slit_vgap_motor = ExitSlitA.v_gap # THe motor required to move the vertical exit slit
        Exit_Slit_vgap_pos = 5                # The vertical gap opening to use


        Diode_motor = BTA2diag.trans    #The motor to move the diode into position.
        Diode_pos = -63                  #The position of the diode motor to be used during the scan


    elif Branch is "B":
        x_start = -0.69              # The x_axis start value of the scan
        x_end   = -0.730              # The x_axis end value of the scan
        x_stepsize = -0.00002         # The x_axis step size of the scan

        detector = qem12      # The detector to use for the scan.
        det_range = '350 pC'     # The range to use for the scan
        det_vals_reading = 5  # The values per reading to use.
        det_avg_time = 0.1    # The averaging time to use.
        det_int_time = 0.0004 # The integration time to use.

        Exit_Slit_hgap_motor = ExitSlitB.h_gap # The motor required to move the horizontal exit slit
        Exit_Slit_hgap_pos = 5                 # The horizontal gap opening to use
        Exit_Slit_vgap_motor = ExitSlitB.v_gap # The motor required to move the vertical exit slit
        Exit_Slit_vgap_pos = 5                  # The vertical gap opening to use
        
        Diode_motor = BTB2diag.trans    #The motor to move the diode into position.
        Diode_pos = -63                  #The position of the diode motor to be used during the scan


    # Read the intial values for each motor that is to be moved.
    initial_x_pos  =x_axis.position

    initial_FE_hgap_pos = FE_hgap_axis.position
    initial_FE_vgap_pos = FE_vgap_axis.position

    initial_det_range = detector.em_range.value                # The initial detector range
    initial_det_vals_reading = detector.values_per_read.value  # The initial values per reading.
    initial_det_avg_time = detector.averaging_time.value       # The initial averaging time.
    initial_det_int_time = detector.integration_time.value     # The initial integration time.

    initial_Exit_Slit_hgap_pos = Exit_Slit_hgap_motor.position # The initial horizontal gap opening
    initial_Exit_Slit_vgap_pos = Exit_Slit_vgap_motor.position # The initial vertical gap opening

    initial_diode_pos = Diode_motor.position                   # The initial location of the diode motor.

    #Move the values to the starting positions for the scan.
    
    yield from mv( x_axis,x_start, FE_hgap_axis,FE_hgap_pos, FE_vgap_axis,FE_vgap_pos,
                   Diode_motor,Diode_pos, Exit_Slit_hgap_motor,Exit_Slit_hgap_pos,
                   Exit_Slit_vgap_motor,Exit_Slit_vgap_pos)

    detector.em_range.put(det_range)                    # The range to use for the scan
    detector.values_per_read.put(det_vals_reading)      # The values per reading to use.
    detector.averaging_time.put(det_avg_time)           # The averaging time to use.
    detector.integration_time.put(det_int_time)         # The integration time to use.

    #Run the scan
    uid=yield from (scan_1D([detector],x_axis,x_start,x_end,x_stepsize,scan_type=scan_type_str)) 

    #move everything to the initial positions
    yield from mv(FE_hgap_axis,initial_FE_hgap_pos, FE_vgap_axis,initial_FE_vgap_pos,
                   Diode_motor,initial_diode_pos, Exit_Slit_hgap_motor,initial_Exit_Slit_hgap_pos,
                   Exit_Slit_vgap_motor,initial_Exit_Slit_vgap_pos)

    detector.em_range.put(initial_det_range)                    # The range to use for the scan
    detector.values_per_read.put(initial_det_vals_reading)      # The values per reading to use.
    detector.averaging_time.put(initial_det_avg_time)           # The averaging time to use.
    detector.integration_time.put(initial_det_int_time)         # The integration time to use

    #Determine the location of the maximum intensity.
    if uid is not None:
        hdr=db[uid]
        output=max_in_1D(uid)

        max_y=output[1]
        max_x=output[0]

        #set the scan axis to the new value.
    else:
        max_x=initial_x_pos
        
    yield from mv( x_axis,max_x )
    

def FE_slits_alignment(detector_location="Diagon",mv_center=False,return_all=False):
    ''' 
    Take an image of the beam relative to the Bremstrahlung collimator using the diagon or using either branches 
    gas cell diode.
        
    This scan is used to check the location of the X-ray's relative to the Bremstrahlung collimator, 
    which is the first apperture downstream of the ratchet wall. The centre value is then compared to 
    an expected value which indicates if the 'bumps' need to be corrected. 

    PARAMETERS
    ----------
    detector_location : string, optional
        This allows for the selection of the Diagon (default selection) or the gas cell qem as the detector
        that is used to take the scan. Allowed values are: Diagon - use the Diagon.
                                                           Gas_cellA - use the A branch gas cell qem.
                                                           Gas_cellB - use the B branch gas cell qem.
                                       
    mv_center : Boolean, optional
        This allows for the routine to move the exit slits to the "fitted" beam center.


    return_all : Boolean, optional
        This allows for the routine to return all motors moved during the scan to their original locations.
        To use this set return_all = True.

    '''
    # Define some parameters that are to be used in the scan, these are designed to be 'preset' and hence are not
    #'inputted' into the scan.
    Und = EPU1.gap
    Und_gap = 35.5  #The gap to use for the undulator, together with the photon energy they ensure that the 'image' is of
               # a 2D 'peak' to allow for ease of calculations in the routine.
    
    x_axis = FEslit.h_center # The x axis of the scan
    x_start = -5              # The x_axis start value of the scan
    x_end   = 5               # The x_axis end value of the scan
    x_stepsize = .5          # The x_axis step size of the scan

    y_axis = FEslit.v_center # The y axis of the scan
    y_start = -5              # The y_axis start value of the scan
    y_end   = 5              # The y_axis end value of the scan
    y_stepsize = .5         # The y_axis step size of the scan


    FE_hgap_axis = FEslit.h_gap     # The front end horizontal gap motor
    FE_hgap_pos  = 0.75              # The front end horizontal gap value
    FE_vgap_axis = FEslit.v_gap     # The front end vertical gap motor
    FE_vgap_pos  = 0.75              # The front end vertical gap value

    accuracy_level = 0.2    #Used to compare the old and new "center" positions, if the difference is larger
                            #than this it sends out a warning and does not update
        
    
    if detector_location is 'Diagon':
        detector = Diag1_CamH # The detector to use for the scan.
        det_exp_time = 0.5    # The exposure time to use for the scan.
        det_aqu_period = 0.5  # The aquire period for the detector.
        det_num_images = 1    # The number of images to aquire at each step.
        det_exp_image = 1     # The number of exposures per image to aquire at each step.

        det_Mir_motor = Diagon.H_mirror # The motor axis associated with the mirror for the diagon detector
        det_Mir_pos = -55               # The value the Mirror motor should be at during the measurement
        det_Yag_motor = Diagon.H_Yag    # The motor axis associated with the Yag for the diagon detector
        det_Yag_pos = 0                 # The value the Yag motor should be during the measurement

        det_Mir2nd_motor = Diagon.V_mirror # The motor axis associated with the mirror for the diagon detector
        det_Mir2nd_pos = 0                 # The value the Mirror motor should be at during the measurement
                                           # (indicating that it is retracted).

        det_ROI1_Xstart = 300 # The starting point for ROI1.
        det_ROI1_Xsize  = 780 # The size, in points, for ROI1.    
        det_ROI1_Ystart = 85  # The starting point for ROI1.
        det_ROI1_Ysize  = 780 # The size, in points, for ROI1.

        scan_type_str='FE_slit_alignment_Diagon'
        
    elif detector_location is 'Gas_cellA':
        detector = qem07      # The detector to use for the scan.
        det_range = '50 pC'     # The range to use for the scan
        det_vals_reading = 5  # The values per reading to use.
        det_avg_time = 0.1    # The averaging time to use.
        det_int_time = 0.0004 # The integration time to use.

        Exit_Slit_hgap_motor = ExitSlitA.h_gap # THe motor required to move the horizontal exit slit
        Exit_Slit_hgap_pos = 500                # The horizontal gap opening to use
        Exit_Slit_vgap_motor = ExitSlitA.v_gap # THe motor required to move the vertical exit slit
        Exit_Slit_vgap_pos = 500                # The vertical gap opening to use

        PGM_Energy_motor = PGM.Energy    #The motor required to move the PGM energy.
        PGM_Energy_pos = 662             #THe energy at which to perform the scan.


        Diode_motor = BTA2diag.trans    #The motor to move the diode into position.
        Diode_pos = -63                  #The position of the diode motor to be used during the scan

        scan_type_str='FE_slit_alignment_Gas_cellA'
        
        
    elif detector_location is 'Gas_cellB':
        detector = qem12      # The detector to use for the scan.
        det_range = '50 pC'     # The range to use for the scan
        det_vals_reading = 5  # The values per reading to use.
        det_avg_time = 0.1    # The averaging time to use.
        det_int_time = 0.0004 # The integration time to use.

        Exit_Slit_hgap_motor = ExitSlitB.h_gap # The motor required to move the horizontal exit slit
        Exit_Slit_hgap_pos = 500                # The horizontal gap opening to use
        Exit_Slit_vgap_motor = ExitSlitB.v_gap # The motor required to move the vertical exit slit
        Exit_Slit_vgap_pos = 500                # The vertical gap opening to use

        PGM_Energy_motor = PGM.Energy    #The motor required to move the PGM energy.
        PGM_Energy_pos = 662             #THe energy at which to perform the scan.

        
        Diode_motor = BTB2diag.trans    #The motor to move the diode into position.
        Diode_pos = -63                  #The position of the diode motor to be used during the scan

        scan_type_str='FE_slit_alignment_Gas_cellB'


    else:
        return None

    # Read the intial values for each motor that is to be moved.
    initial_Und_gap =Und.position
    initial_x_axis  =x_axis.position
    initial_y_axis  =y_axis.position

    initial_FE_hgap_pos = FE_hgap_axis.position
    initial_FE_vgap_pos = FE_vgap_axis.position
    
    if detector_location is 'Diagon':
    
        initial_det_exp_time = detector.cam.acquire_time.value
        initial_det_aqu_period = detector.cam.acquire_period.value
        initial_det_num_images = detector.cam.num_images.value
        initial_det_exp_image = detector.cam.num_exposures.value

        initial_det_ROI_Xstart = detector.roi1.min_xyz.min_x.value
        initial_det_ROI_Xsize = detector.roi1.size.x.value
        initial_det_ROI_Ystart = detector.roi1.min_xyz.min_y.value
        initial_det_ROI_Ysize = detector.roi1.size.y.value

        initial_det_Mir_pos = det_Mir_motor.position
        initial_det_Yag_pos = det_Yag_motor.position

    elif 'Gas_cell' in detector_location:

        initial_det_range = detector.em_range.value                # The initial detector range
        initial_det_vals_reading = detector.values_per_read.value  # The initial values per reading.
        initial_det_avg_time = detector.averaging_time.value       # The initial averaging time.
        initial_det_int_time = detector.integration_time.value     # The initial integration time.

        initial_Exit_Slit_hgap_pos = Exit_Slit_hgap_motor.position # The initial horizontal gap opening
        initial_Exit_Slit_vgap_pos = Exit_Slit_vgap_motor.position # The initial vertical gap opening

        initial_PGM_Energy_pos = PGM_Energy_motor.position         #The initial photon energy.
        initial_diode_pos = diode_motor.position                   # The initial location of the diode motor.

    #ADD A CLOSE SHUTTER CALL HERE




    #Move the values to the starting positions for the scan.
    
    yield from mv( Und,Und_gap,  x_axis,x_start,  y_axis, y_start,
                  FE_hgap_axis,FE_hgap_pos,  FE_vgap_axis,FE_vgap_pos)

    if detector_location is 'Diagon':
        yield from mv (det_Mir_motor,det_Mir_pos,  det_Yag_motor,det_Yag_pos)

        detector.cam.acquire_time.put(det_exp_time)
        detector.cam.acquire_period.put(det_aqu_period)
        detector.cam.num_images.put(det_num_images)
        detector.cam.num_exposures.put(det_exp_image)

        detector.roi1.min_xyz.min_x.put(det_ROI1_Xstart)
        detector.roi1.size.x.put(det_ROI1_Xsize)
        detector.roi1.min_xyz.min_y.put(det_ROI1_Ystart)
        detector.roi1.size.y.put(det_ROI1_Ysize)
    elif 'Gas_cell' in detector_location:
        yield from mv(Exit_Slit_hgap_motor,Exit_Slit_hgap_pos,  Exit_Slit_vgap_motor,Exit_Slit_vgap_pos,
                      PGM_Energy_motor,PGM_Energy_pos,   diode_motor,Diode_pos)

        detector.em_range.put(det_range)                    # The range to use for the scan
        detector.values_per_read.put(det_vals_reading)      # The values per reading to use.
        detector.averaging_time.put(det_avg_time)           # The averaging time to use.
        detector.integration_time.put(det_int_time)         # The integration time to use.

        
        
    #ADD AN OPEN SHUTTER CALL HERE
    
    uid=yield from (scan_2D([detector],y_axis,y_start,y_end,y_stepsize,x_axis,x_start,x_end,x_stepsize,snake=True,
                                scan_type=scan_type_str))  


    if uid is not None:
        hdr=db[uid]
        output=max_in_2D(uid)

        max_y=output[1]
        max_x=output[2]

        if (abs(max_x/initial_x_axis-1) <= accuracy_level) and (abs(max_y/initial_y_axis-1) <= accuracy_level):
            print ("The fitted FE slit position at the ",str(detector_location),
                   " detector is: FE_slit_h_center = ",max_x," FE_slit_v_center = ", max_y)
        else:
            mv_center=False
            print ("WARNING:: THE NEW FITTED POSITION IS DIFFERENT FROM THE NEW POSITION BY ",
                   max(abs(max_x-initial_x_axis),abs(max_y-initial_y_axis) ),
                   " (The fitted FE slit position at the ",detector_location,
                   " detector is: FE_slit_h_center = ",max_x," FE_slit_v_center = ", max_y,
                   ", the new position has not been set)")

    else:
        max_x=None
        max_y=None
    

    # Reset the values to the original position if 'return_all = True'
    #ADD A CLOSE PHOTON SHUTTER LINE HERE.
    if return_all is True:


        yield from mv( Und,initial_Und_gap,  x_axis,initial_x_axis,  y_axis, initial_y_axis)

        if detector_location is 'Diagon':
            yield from mv(det_Mir_motor,initial_det_Mir_pos,  det_Yag_motor,initial_det_Yag_pos)

            detector.cam.acquire_time.put(initial_det_exp_time)
            detector.cam.acquire_period.put(initial_det_aqu_period)
            detector.cam.num_images.put(initial_det_num_images)
            detector.cam.num_exposures.put(initial_det_exp_image)

            detector.roi1.min_xyz.min_x.put(initial_det_ROI_Xstart)
            detector.roi1.size.x.put(initial_det_ROI_Xsize)
            detector.roi1.min_xyz.min_y.put(initial_det_ROI_Ystart)
            detector.roi1.size.y.put(initial_det_ROI_Ysize)

        elif 'Gas_cell' in detector_location:
            yield from mv(Exit_Slit_hgap_motor,initial_Exit_Slit_hgap_pos,
                          Exit_Slit_vgap_motor,initial_Exit_Slit_vgap_pos,
                          PGM_Energy_motor,initial_PGM_Energy_pos,
                          diode_motor,initial_diode_pos)

            detector.em_range.put(initial_det_range)                    # The range to use for the scan
            detector.values_per_read.put(initial_det_vals_reading)      # The values per reading to use.
            detector.averaging_time.put(initial_det_avg_time)           # The averaging time to use.
            detector.integration_time.put(initial_det_int_time)         # The integration time to use.
        

        
    if mv_center is True:
        yield from mv(FE_hgap_axis,max_x,  FE_vgap_axis,max_y)
    elif return_all is True:
        yield from mv (FE_hgap_axis,initial_FE_hgap_pos,  FE_vgap_axis,initial_FE_vgap_pos)


    #ADD AN OPEN SHUTTER CALL HERE

    return [max_x,max_y]


def Mirror_alignment(axes='M1_Ry_M3_Ry',Branch='A',mv_optimum=False,return_all=False):
    ''' 
    Aligns the M1 and/or M3 mirrors to the exit slit but looking at the intensity and/or linewidth after
    the exit slit. 
        
    This scan is used to find the optimal location of either the M1 or M3 mirror axes. It runs a 2D scan over a
    pre-determined range for the 2 axes and then determines the intensity maxima position.

    PARAMETERS
    ----------
    axes : string, optional
        This allows for the selection of the 2 axes to be used in the scan. 
                    Allowed values are: M1_Ry_M3_Ry - scan over the pitch of both mirrors.
                                        M3_X_M3_Ry  - scan the M3 mirror in-out and pitch.                                        
                                        M3_Z_M3_Ry  - scan the M3 mirror along the beam and pitch.
                                        M3_Rz_M3_Ry  - scan the M3 mirror along the beam and pitch.
                                        OTHERS TO BE ADDED.

    Branch : string, optional
        This allows for the selection of the Branch line for the scan to use. 
                    Allowed values are: A - use the "A" branch.
                                        B - use the "B" branch.
                                       
    mv_optimal : Boolean, optional
        This allows for the routine to move the mirror axes to the "fitted" position at the end of the scan.


    return_all : Boolean, optional
        This allows for the routine to return all motors moved during the scan to their original locations.
        To use this set return_all = True.

    '''
    # Define some parameters that are to be used in the scan, these are designed to be 'preset' and hence are not
    #'inputted' into the scan.
    Und = EPU1.gap
    Und_gap = 35.5  #The gap to use for the undulator, together with the photon energy they ensure that the 'correct' detector
                    #settings are used

    FE_hgap_axis = FEslit.h_gap     # The front end horizontal gap motor
    FE_hgap_pos  = 0.75              # The front end horizontal gap value
    FE_vgap_axis = FEslit.v_gap     # The front end vertical gap motor
    FE_vgap_pos  = 0.75              # The front end vertical gap value
                    
    PGM_Energy_motor = PGM.Energy    #The motor required to move the PGM energy.
    PGM_Energy_pos = 662             #The photon energy at which to perform the scan.
    

    det_range = '350 pC'     # The range to use for the scan
    det_vals_reading = 5  # The values per reading to use.
    det_avg_time = 0.1    # The averaging time to use.
    det_int_time = 0.0004 # The integration time to use.

    accuracy_level = 0.1    #Used to compare the old and new "center" positions, if the difference is larger
                            #than this it sends out a warning and does not update
    
    if Branch is "A":
        Exit_Slit_hgap_motor = ExitSlitA.h_gap # The motor required to move the horizontal exit slit
        Exit_Slit_hgap_pos = 0                  # The horizontal gap opening to use
        Exit_Slit_vgap_motor = ExitSlitA.v_gap # The motor required to move the vertical exit slit
        Exit_Slit_vgap_pos = 5                  # The vertical gap opening to use

        Diode_motor = BTA2diag.trans    #The motor to move the diode into position.
        Diode_pos = -63                  #The position of the diode motor to be used during the scan
        
        detector = qem07      # The detector to use for the scan.

        
    elif Branch is "B":
        Exit_Slit_hgap_motor = ExitSlitB.h_gap # The motor required to move the horizontal exit slit
        Exit_Slit_hgap_pos = 10                 # The horizontal gap opening to use
        Exit_Slit_vgap_motor = ExitSlitB.v_gap # The motor required to move the vertical exit slit
        Exit_Slit_vgap_pos = 10                 # The vertical gap opening to use

        Diode_motor = BTB2diag.trans    #The motor to move the diode into position.
        Diode_pos = -63                  #The position of the diode motor to be used during the scan

        detector = qem12      # The detector to use for the scan.

    else:
        return None
        
    
    if axes is "M1_Ry_M3_Ry":
        if Branch is "A":
            x_axis = M3.Ry                 # The x axis of the scan
            x_start = -0.7085              # The x_axis start value of the scan
            x_end   = -0.7035              # The x_axis end value of the scan
            x_stepsize = -0.00002          # The x_axis step size of the scan

            y_axis = M1.Ry               # The y axis of the scan
            y_start = -3660              # The y_axis start value of the scan
            y_end   = -3620              # The y_axis end value of the scan
            y_stepsize =  2              # The y_axis step size of the scan

        elif Branch is "B":
            x_axis = M3.Ry                # The x axis of the scan
            x_start = -0.719              # The x_axis start value of the scan
            x_end   = -0.714              # The x_axis end value of the scan
            x_stepsize = -0.00002         # The x_axis step size of the scan

            y_axis = M1.Ry               # The y axis of the scan
            y_start = -3640              # The y_axis start value of the scan
            y_end   = -3600              # The y_axis end value of the scan
            y_stepsize =  2              # The y_axis step size of the scan

            
        scan_type_str='Mirror_alignment_M1_RY_M3_RY_Branch_'+Branch

        
    elif axes is "M3_X_M3_Ry":
        if Branch is "A":
            x_axis = M3.Ry # The x axis of the scan
            x_start = -0.71              # The x_axis start value of the scan
            x_end   = -0.695              # The x_axis end value of the scan
            x_stepsize = -0.00002           # The x_axis step size of the scan

            y_axis = M3.X # The y axis of the scan
            y_start = -0.3              # The y_axis start value of the scan
            y_end   = 1.5               # The y_axis end value of the scan
            y_stepsize = 0.1            # The y_axis step size of the scan

        elif Branch is "B":
            x_axis = M3.Ry # The x axis of the scan
            x_start = -0.726               # The x_axis start value of the scan
            x_end   = -0.71                # The x_axis end value of the scan
            x_stepsize = -0.0001           # The x_axis step size of the scan

            y_axis = M3.X # The y axis of the scan
            y_start = 1.1                # The y_axis start value of the scan
            y_end   = 3                  # The y_axis end value of the scan
            y_stepsize = 0.05            # The y_axis step size of the scan
            
        scan_type_str='Mirror_alignment_M3_X_M3_RY_Branch_'+Branch

    elif axes is "M3_Z_M3_Ry":
        if Branch is "A":
            x_axis = M3.Ry # The x axis of the scan
            x_start = -0.7085              # The x_axis start value of the scan
            x_end   = -0.7035             # The x_axis end value of the scan
            x_stepsize = -0.00002           # The x_axis step size of the scan

            y_axis = M3.Z # The y axis of the scan
            y_start = -2.5              # The y_axis start value of the scan
            y_end   = 2.5               # The y_axis end value of the scan
            y_stepsize = 0.25            # The y_axis step size of the scan

        elif Branch is "B":
            x_axis = M3.Ry # The x axis of the scan
            x_start = -0.7085              # The x_axis start value of the scan
            x_end   = -0.7035             # The x_axis end value of the scan
            x_stepsize = -0.00002           # The x_axis step size of the scan

            y_axis = M3.Z # The y axis of the scan
            y_start = -2.5              # The y_axis start value of the scan
            y_end   = 2.5               # The y_axis end value of the scan
            y_stepsize = 0.25            # The y_axis step size of the scan
            
        scan_type_str='Mirror_alignment_M3_Z_M3_RY_Branch_'+Branch


    elif axes is "M3_Rz_M3_Ry":
        if Branch is "A":
            x_axis = M3.Ry # The x axis of the scan
            x_start = -0.7085              # The x_axis start value of the scan
            x_end   = -0.7035              # The x_axis end value of the scan
            x_stepsize = -0.00002           # The x_axis step size of the scan

            y_axis = M3.Rz               # The y axis of the scan
            y_start = -1.5              # The y_axis start value of the scan
            y_end   = 0.75               # The y_axis end value of the scan
            y_stepsize = 0.25            # The y_axis step size of the scan

        elif Branch is "B":
            x_axis = M3.Ry # The x axis of the scan
            x_start = -0.735              # The x_axis start value of the scan
            x_end   = -0.70              # The x_axis end value of the scan
            x_stepsize = -0.0005           # The x_axis step size of the scan

            y_axis = M3.Rz               # The y axis of the scan
            y_start = -1.5              # The y_axis start value of the scan
            y_end   = 1.5               # The y_axis end value of the scan
            y_stepsize = 0.25            # The y_axis step size of the scan
            
        scan_type_str='Mirror_alignment_M3_Rz_M3_Ry_Branch_'+Branch

        
    else:
        return None


    #Save the initial values of all moved motors so that they can be reset.
    initial_Und_gap = Und.position                             # The initial Undulator position.
    initial_PGM_Energy_pos = PGM_Energy_motor.position         # The initial PGM energy.
    initial_det_range = detector.em_range.value                # The initial detector range.
    initial_det_vals_reading = detector.values_per_read.value  # The initial values per reading.
    initial_det_avg_time = detector.averaging_time.value       # The initial averaging time.
    initial_det_int_time = detector.integration_time.value     # The initial integration time.
    initial_x_axis_pos = x_axis.position                       # The initial x_axis position.
    initial_y_axis_pos = y_axis.position                       # The initial y_axis position.
    initial_Exit_Slit_vgap_pos = Exit_Slit_vgap_motor.position # The initial vertical gap for the exit slit.
    initial_Exit_Slit_hgap_pos = Exit_Slit_hgap_motor.position # The initial horizontal gap for the exit slit.
    initial_FE_hgap_pos  = FE_hgap_axis.position              # The initial front end horizontal gap value.
    initial_FE_vgap_pos  = FE_vgap_axis.position              # The initial front end vertical gap value.
    initial_Diode_pos = Diode_motor.position                   # The initial location of the diode motor.

    #Set the values to the correct initial states here.
    
    #ADD A CLOSE SHUTTER CALL HERE.
    yield from mv( Und,Und_gap,  x_axis,x_start,  y_axis, y_start, Exit_Slit_vgap_motor,Exit_Slit_vgap_pos,
                   Exit_Slit_hgap_motor,Exit_Slit_hgap_pos,  PGM_Energy_motor,PGM_Energy_pos,
                   FE_hgap_axis,FE_hgap_pos,    FE_vgap_axis,FE_vgap_pos,   Diode_motor,Diode_pos)

    detector.em_range.put(det_range)                    # The range to use for the scan
    detector.values_per_read.put(det_vals_reading)      # The values per reading to use.
    detector.averaging_time.put(det_avg_time)           # The averaging time to use.
    detector.integration_time.put(det_int_time)         # The integration time to use.
    
    #ADD AN OPEN SHUTTER CALL HERE.

    # Run the scan
    uid=yield from (scan_2D([detector],y_axis,y_start,y_end,y_stepsize,x_axis,x_start,x_end,x_stepsize,snake=False,
                                scan_type=scan_type_str))  


    if uid is not None: 
        hdr=db[uid]
        output=max_in_2D(uid)

        max_y=db.get_table(hdr,[hdr.start.plot_Yaxis])[x_num*popt_amp[1]]
        max_x=position[popt_amp[1]]


        if abs(max_x/initial_x_axis_pos-1) <= accuracy_level and abs(max_y/initial_y_axis_pos-1) <= accuracy_level:
            print ("The fitted x axis positions at the ",Branch," ",x_axis_motor.name, " motor are: ",max_x,
                   ". The fitted y axis positions at the ",Branch," ",y_axis_motor.name, " motor are: ",max_y)
            output=[max_x,max_y]
        else:
            mv_center=False
            print ("WARNING:: THE NEW FITTED POSITION IS DIFFERENT FROM THE OLD POSITION BY ",max(abs(max_x-initial_x_axis_pos),
                    abs(max_y-initial_y_axis_pos) ),"(The fitted x axis positions at the ",Branch," ",x_axis_motor.name, " motor are: ",max_x,
                   ". The fitted y axis positions at the ",Branch," ",y_axis_motor.name, " motor are: ",max_y,". The new position has not been set")

    else:
       output=None
       max_x=None
       max_y=None
       
   

    # Reset the values to the original position if 'return_all = True'
    #ADD A CLOSE PHOTON SHUTTER LINE HERE.
    if return_all is True:
        yield from mv( Und,initial_Und_gap,   Exit_Slit_vgap_motor,initial_Exit_Slit_vgap_pos,
                       Exit_Slit_hgap_motor,initial_Exit_Slit_hgap_pos,  PGM_Energy_motor,initial_PGM_Energy_pos,
                       FE_hgap_axis,initial_FE_hgap_pos,    FE_vgap_axis,initial_FE_vgap_pos,   Diode_motor,initial_Diode_pos   )

        detector.em_range.put(initial_det_range)                    # The range to use for the scan
        detector.values_per_read.put(initial_det_vals_reading)      # The values per reading to use.
        detector.averaging_time.put(initial_det_avg_time)           # The averaging time to use.
        detector.integration_time.put(initial_det_int_time)         # The integration time to use.
        

        
    if mv_optimum is True:
        yield from mv( x_axis,max_x,  y_axis, max_y)
    elif return_all is True:
        yield from mv ( x_axis,initial_x_axis_pos,  y_axis, initial_y_axis_pos)


    #ADD AN OPEN SHUTTER CALL HERE
    
    return output



def M1_M3_alignment(Branch='A',mv_optimum=False,return_all=True):
    ''' 
    Aligns the M1 and M3 mirrorsby stepping through the combinations possible with Mirror_alignment.
        
    This scan is used to find the optimal location of bpth M1 and M3, it runs a series of Mirror_Alignment scans over
    all combinations of axes that regisater a difference in the intensity for the branch specfied by the Branch variable.
     Branch : string, optional
        This allows for the selection of the Branch line for the scan to use. 
                    Allowed values are: A - use the "A" branch.
                                        B - use the "B" branch.
                                       
    mv_optimal : Boolean, optional
        This allows for the routine to move the mirror axes to the "fitted" position at the end of the scan.


    return_all : Boolean, optional
        This allows for the routine to return all motors moved during the scan to their original locations.
        To use this set return_all = True.

    '''  
    
    output_M1_Ry=yield from Mirror_alignment(axes='M1_Ry_M3_Ry',Branch=Branch,mv_optimum=mv_optimum,return_all=return_all)
    output_M3_X=yield from Mirror_alignment(axes='M3_X_M3_Ry',Branch=Branch,mv_optimum=mv_optimum,return_all=return_all)
    output_M3_Z=yield from Mirror_alignment(axes='M3_Z_M3_Ry',Branch=Branch,mv_optimum=mv_optimum,return_all=return_all)
    output_M3_Rz=yield from Mirror_alignment(axes='M3_Rz_M3_Ry',Branch=Branch,mv_optimum=mv_optimum,return_all=return_all)

    print("M1_Ry, M3_Ry results are: ",output_M1_Ry," ([[amp pos M3_Ry,amp pos M1_Ry],[LW pos M3_Ry,LW pos M1_Ry])")
    print("M3_X, M3_Ry results are: ",output_M3_X," ([[amp pos M3_Ry,amp pos M3_X],[LW pos M3_Ry,LW pos M3_X])")
    print("M3_Z, M3_Ry results are: ",output_M3_Z," ([[amp pos M3_Ry,amp pos M3_Z],[LW pos M3_Ry,LW pos M3_Z])")
    print("M3_Rz, M3_Ry results are: ",output_M3_Rz," ([[amp pos M3_Ry,amp pos M3_Rz],[LW pos M3_Ry,LW pos M3_Rz])")
    
###
###UTILITY FUNCTIONS
### These are functions that are used in the scan plans above, but are not independent scan plans themselves. 

def Get_Yaxis_name(det0, det0_channel):
    '''This Routine is used to determine the Y axis name to use for plotting or saving for a given detector and detector 
       channel, if the detector is an 2D detector it will plot the integrated total intensity, if it is set up to do so.
       In this case DET_Channel indicates which stats channel to plot.  
       It assumes that if the given detector channel is none that the first channel is to be used.
       
       REQUIRED PARAMETERS
           det0  --  This is the detector that is to be used
           DET_channel  -- This is the detector channel to be used
   
    '''
    if det0_channel is not None:
    # if DET_channel is a number
        try:
            read_chan, *_ = [r for r in det0.read_attrs if str(det0_channel) in r]
            # attempt to find the detector with the number 'DET_channel' in the name. if found save the position to read_chan  
        except ValueError:
            # if the channel number is not found set plot_target to det0
            plot_target = det0
        else:
            # if the exception is not found read the attribute name from the channel name attributes list
            plot_target = getattr(det0, read_chan)
        finally:
            pass
    else:
        #if DET_channel is None then set the plot target to det0
        plot_target = det0
        
    # finally return the name of the channel associated with plot_target.  
    return first_key_heuristic(plot_target)

def ESM_setup_hints(detectors,DET_channel,DET_channel_value):
    '''
    This function is used to set the hints to a sub-set of the total value of possible attributes. 

    This function uses the 'set_primary' attribute of our detectors in order to change the list of attributes in the
    .hints attribute.

    PARAMETERS:
    -----------
    detectors : list
        A list of detectors

    DET_channel : list
        Channel numbers to plot for each detectors (eg. for qem to plot 'qem01_current1_mean_value' 
        use DET_channel=[1]). 

    DET_channel_value : list 
        A list of Channel values to plot for each detectors and channel (eg. for a camera to plot 'stats1_max_value' 
        use DET_channel_value=[["max"]]). Can take the values 'total', 'max' or 'min'.
            
    '''

    for i,DET in enumerate(detectors):
        DET.set_primary(DET_channel[i],DET_channel_value[i])
    


def ESM_setup_Plot(Y_axis,motors=None):
    '''
    Setup a Liveplot by inspecting motors and Y_axis and plotting on an existing plot if it exists. If motors is empty,
    use sequence number.The function returns LivePlot with the correct axis, and figure definition. 
    
    REQUIRED PARAMETERS
        Y_axis -- the name of the Y_axis for the plot (can be found using Get_Yaxis_name) 

    OPTIONAL PARAMETERS
        motors -- a list containing the motor for the scan x axis 

    '''
    y_key = Y_axis
    #set the y_key to the Y-axis
    
    if motors:
    # if motors is not empty
        x_key = first_key_heuristic(list(motors)[0])
        #find the "axis name" associated with the given motor
        fig_name = _figure_name('BlueSky: {} v {}'.format(y_key, x_key))
        #generate the figure name based on x and y axis names, if it doesn't exist create a new one.
        ax = plt.figure(fig_name).gca()
        #set the value of ax to the correct figure name
        return LivePlot(y_key, x_key, ax=ax)
        #return the LivePlot function with the correct figure and axes names.
    else:
    #if motors is empty
        fig_name = _figure_name('BlueSky: {} v time'.format(y_key))
        #generate the figure name associated with the axes for sequence number instead of motor name, if it doesn't exist
        #create a new one.
        ax = plt.figure(fig_name).gca()
        #set the value of ax to the correct figure name
        return LivePlot(y_key, ax=ax)
        #return the LivePlot function with the correct figurte and axes names


        
def ESM_save_csv(uid,Y_axis,motors_list,time=False):
    ''' Save a 1D scan to an X-Y .csv file, used with 1D detectors and 1D scans.
         
         REQUIRED PARAMETERS 
             uid  -- the unique id number for the scan to find it in the databroker
             Y_axis -- the name of the field to include in the "Y" wave 
             motors -- a list of motor readback values that need to be included in the table.         

         OPTIONAL PARAMETERS    
             time -- optional, indicates if the X axis to save should be time, default is to use the scan motor from the uid.
    '''
    if uid is not None:
    #If the uid has a value then perform the save, otherwise do nothing. This is required to ensure that it does not attempt
    #to execute when using the "print_summary" call to the plan.
        hdr=db[uid]
        #load the header file for the given uid
        f_nm=str(hdr.start.scan_id)+'.csv'
        # Define the filen name from the scan id number and the  '.csv' suffix
        if time:
            df = hdr.table(fields=[Y_axis])
            #get the table if the X_axis is to be time.
        else:
            motor=motors_list[0]
            df = hdr.table(fields=motors_list+[Y_axis])                
            del df['time']
            #if the X axis is not to be time then find the scan motor name from the uid get the table then delete the time
            #column
            cols=df.columns.tolist()
            m=cols.index(motor)
            cols.pop(m)
            cols=[motor]+cols
            df=df[cols]
            #move the 'motor' column to the first column in the table.

        f_path="/direct/XF21ID1/csv_files/"+f_nm
        #Define the path to where the file should be saved.
        
        df.to_csv(f_path,index=False)
        #save the table to the .csv file.


class ESMLivePlot(CallbackBase):
    """
    Build a function that updates a plot from a stream of Events.
    Note: If your figure blocks the main thread when you are trying to
    scan with this callback, call `plt.ion()` in your IPython session.
    Parameters
    ----------
    y : str
        the name of a data field in an Event
    x : str, optional
        the name of a data field in an Event
        If None, use the Event's sequence number.
    legend_keys : list, optional
        The list of keys to extract from the RunStart document and format
        in the legend of the plot. The legend will always show the
        scan_id followed by a colon ("1: ").  Each
    xlim : tuple, optional
        passed to Axes.set_xlim
    ylim : tuple, optional
        passed to Axes.set_ylim
    ax : Axes, optional
        matplotib Axes; if none specified, new figure and axes are made.
    fig : Figure
        deprecated: use ax instead
    All additional keyword arguments are passed through to ``Axes.plot``.
    Examples
    --------
    >>> my_plotter = LivePlot('det', 'motor', legend_keys=['sample'])
    >>> RE(my_scan, my_plotter)
    """
    def __init__(self, y, x=None, *, legend_keys=None, xlim=None, ylim=None,
                 ax=None, fig=None, **kwargs):
        super().__init__()
        if fig is not None:
            if ax is not None:
                raise ValueError("Values were given for both `fig` and `ax`. "
                                 "Only one can be used; prefer ax.")
            warnings.warn("The `fig` keyword arugment of LivePlot is "
                          "deprecated and will be removed in the future. "
                          "Instead, use the new keyword argument `ax` to "
                          "provide specific Axes to plot on.")
            ax = fig.gca()
        if ax is None:
            fig, ax = plt.subplots()
        self.ax = ax

        if legend_keys is None:
            legend_keys = []
        self.legend_keys = ['scan_id'] + legend_keys
        if x is not None:
            self.x, *others = _get_obj_fields([x])
        else:
            self.x = None
        self.y, *others = _get_obj_fields([y])
        self.ax.set_ylabel(y)
        self.ax.set_xlabel(x or 'time (seconds)')
        if xlim is not None:
            self.ax.set_xlim(*xlim)
        if ylim is not None:
            self.ax.set_ylim(*ylim)
        self.ax.margins(.1)
        self.kwargs = kwargs
        self.lines = []
        self.legend = None
        self.legend_title = " :: ".join([name for name in self.legend_keys])

    def start(self, doc):
        # The doc is not used; we just use the singal that a new run began.
        self.x_data, self.y_data = [], []
        self.initial_time = None
        label = " :: ".join(
            [str(doc.get(name, name)) for name in self.legend_keys])
        kwargs = ChainMap(self.kwargs, {'label': label})
        self.current_line, = self.ax.plot([], [], **kwargs)
        self.lines.append(self.current_line)
        self.legend = self.ax.legend(
            loc=0, title=self.legend_title).draggable()
        super().start(doc)

    def event(self, doc):
        "Unpack data from the event and call self.update()."
        try:
            if self.x is not None:
                # this try/except block is needed because multiple event
                # streams will be emitted by the RunEngine and not all event
                # streams will have the keys we want
                new_x = doc['data'][self.x]
            else:
                new_x = doc['time']
                if self.initial_time is None:
                    self.initial_time = new_x

                new_x = new_x - self.initial_time
                
                ###DIFFERENCE FROM LIVEPLOT: AT THIS POINT I CHANGED 'seq_num' TO 'time'###
                ### I also added the lines here to make the time start from the first point.
            new_y = doc['data'][self.y]
        except KeyError:
            # wrong event stream, skip it
            return
        self.update_caches(new_x, new_y)
        self.update_plot()
        super().event(doc)

    def update_caches(self, x, y):
        self.y_data.append(y)
        self.x_data.append(x)

    def update_plot(self):
        self.current_line.set_data(self.x_data, self.y_data)
        # Rescale and redraw.
        self.ax.relim(visible_only=True)
        self.ax.autoscale_view(tight=True)
        self.ax.figure.canvas.draw_idle()

    def stop(self, doc):
        if not self.x_data:
            print('LivePlot did not get any data that corresponds to the '
                  'x axis. {}'.format(self.x))
        if not self.y_data:
            print('LivePlot did not get any data that corresponds to the '
                  'y axis. {}'.format(self.y))
        if len(self.y_data) != len(self.x_data):
            print('LivePlot has a different number of elements for x ({}) and'
                  'y ({})'.format(len(self.x_data), len(self.y_data)))
        super().stop(doc)

def _get_obj_fields(fields):
    """
    If fields includes any objects, get their field names using obj.describe()
    ['det1', det_obj] -> ['det1, 'det_obj_field1, 'det_obj_field2']"
    """
    string_fields = []
    for field in fields:
        if isinstance(field, str):
            string_fields.append(field)
        else:
            try:
                field_list = sorted(field.describe().keys())
            except AttributeError:
                raise ValueError("Fields must be strings or objects with a "
                                 "'describe' method that return a dict.")
            string_fields.extend(field_list)
    return string_fields



        
def spiral_square_pattern(x_motor, y_motor, x_centre, y_centre, x_range, y_range, x_num,y_num):
    '''Square spiral scan, centered around (x_start, y_start)
    Parameters
    ----------
    x_motor : object, optional
        any 'setable' object (motor, temp controller, etc.)
    y_motor : object, optional
        any 'setable' object (motor, temp controller, etc.)
    x_centre : float
        x center
    y_centre : float
        y center
    x_range : float
        x width of spiral
    y_range : float
        y width of spiral
    x_num : float
        number of x axis points
    y_num : float (must be even if x_num is even and must be odd if x_num is odd, if not it is increased by 1 to ensure this)
        number of y axis points 
    Returns
    -------
    cyc : cycler
    '''


    x_points, y_points = [], []

    if x_num%2==0:
        num_st= 2
        if y_num%2==1:
           y_num+=1

        offset=0.5
        
    else:
        num_st=1
        if y_num%2==0:
            y_num+=1

        offset=0
        
        x_points.append(x_centre)
        y_points.append(y_centre)
        
    #print( 'x_range = '+str(x_range)+', x_num = '+str(x_num)  )
    #print( 'y_range = '+str(y_range)+', y_num = '+str(y_num)  )
     
    delta_x = x_range/(x_num-1)
    delta_y = y_range/(y_num-1)


    
    num_ring = max(x_num,y_num)

    x_max=x_centre + delta_x * (x_num-1)/2
    x_min=x_centre - delta_x * (x_num-1)/2

    y_max=y_centre + delta_y * (y_num-1)/2
    y_min=y_centre - delta_y * (y_num-1)/2
    


    
    #print ( 'num_ring = '+str(num_ring)  )
    for n,i_ring in enumerate(range(num_st, num_ring+1,2)):
        #print ('x_centre: '+str(x_centre)+', delta_x: '+str(delta_x))
        #print ('y_centre: '+str(y_centre)+', delta_y: '+str(delta_y))
        x_ring_max=x_centre + delta_x * (n+offset)
        y_ring_max=y_centre + delta_y * (n+offset)
        x_ring_min=x_centre - delta_x * (n+offset)
        y_ring_min=y_centre - delta_y * (n+offset)
        #print('i_ring = '+str(i_ring)+', x_ring_min= '+str(x_ring_min)+', y_ring_min= '+str(y_ring_min)  ) 

        for n in range(1, i_ring):
            x = x_ring_min+delta_x*(n-1)
            y = y_ring_min

            if ( (x <= x_max) and (x>= x_min) and (y<=y_max) and (y>=y_min)     ):
                x_points.append(x)
                y_points.append(y)
            
        for n in range(1, i_ring):
            y = y_ring_min+delta_y*(n-1)
            x = x_ring_max

            if ( (x <= x_max) and (x>= x_min) and (y<=y_max) and (y>=y_min)     ):
                x_points.append(x)
                y_points.append(y)

            
        for n in range(1, i_ring):
            x = x_ring_max-delta_x*(n-1)
            y = y_ring_max

            if ( (x <= x_max) and (x>= x_min) and (y<=y_max) and (y>=y_min)     ):
                x_points.append(x)
                y_points.append(y)

        for n in range(1, i_ring):
            y = y_ring_max-delta_y*(n-1)
            x = x_ring_min

            if ( (x <= x_max) and (x>= x_min) and (y<=y_max) and (y>=y_min)     ):
                x_points.append(x)
                y_points.append(y)



    cyc = cycler(x_motor, x_points)
    cyc += cycler(y_motor, y_points)
    return cyc

def spiral_square(detectors, x_motor, y_motor, x_centre, y_centre, x_range,
                  y_range, x_num, y_num, *, per_step=None, md=None):
    '''Absolute square spiral scan, centered around (x_centre, y_centre)
    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    x_motor : object
        any 'setable' object (motor, temp controller, etc.)
    y_motor : object
        any 'setable' object (motor, temp controller, etc.)
    x_centre : float
        x center
    y_centre : float
        y center
    x_range : float
        x width of spiral
    y_range : float
        y width of spiral
    x_num : float
        number of x axis points
    y_num : float (must be even if x_num is even and must be odd if x_num is odd, if not it is increased by 1 to ensure this)
        number of y axis points 
    per_step : callable, optional
        hook for cutomizing action of inner loop (messages per step)
        See docstring of bluesky.plans.one_nd_step (the default) for
        details.
    md : dict, optional
        metadata
    See Also
    --------
    :func:`bluesky.plans.spiral`
    :func:`bluesky.plans.relative_spiral`
    :func:`bluesky.plans.spiral_fermat`
    :func:`bluesky.plans.relative_spiral_fermat`
    '''
    pattern_args = dict(x_motor=x_motor, y_motor=y_motor, x_centre=x_centre,
                        y_centre=y_centre, x_range=x_range, y_range=y_range,
                        x_num = x_num, y_num = y_num)
    cyc = spiral_square_pattern(**pattern_args)

    # Before including pattern_args in metadata, replace objects with reprs.
    pattern_args['x_motor'] = repr(x_motor)
    pattern_args['y_motor'] = repr(y_motor)
    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'x_motor': repr(x_motor), 'y_motor': repr(y_motor),
                         'x_centre': x_centre, 'y_centre': y_centre,
                         'x_range': x_range, 'y_range': y_range,
                         'x_num': x_num, 'y_num': y_num,
                         'per_step': repr(per_step)},
           'plan_name': 'spiral_square',
           'plan_pattern': 'spiral_square',
          }
    _md.update(md or {})

    return (yield from scan_nd(detectors, cyc, per_step=per_step, md=_md))


def gaussian_1D(x,params):
    '''This function defines a 2D gaussian that is used for fitting.
    Parameters
    ----------
    x : variable
        the axis variable for the 1D gaussian.
    params : variables
        the list of "fitting" variables for the 2D gaussian
            Parameters:

            1. amp  =  the amplitude of the 1D guassian
            2. cen =  the centre of the first axis gaussian
            4. std = the width of the first axis gaussian
            6. bkg  = height of the constant background for the gaussian
    '''
    amp,cen,std,bkg = params
    return amp*np.exp(-(x-cen)**2/2/std**2)+bkg

def gaussian_1D_error(params,y,x):
    '''This function defines the difference between a fitted gaussian and the raw data.
    Parameters
    ----------
    params : variables
        the list of "fitting" variables for the 2D gaussian
            Parameters:

            1. amp  =  the amplitude of the 1D guassian
            2. cen =  the centre of the first axis gaussian
            4. std = the width of the first axis gaussian
            6. bkg  = height of the constant background for the gaussian

    y  : variable 
        the value of the raw data at (x)
    x : variable
        the axis variable for the 1D gaussian.
    '''

    return gaussian_1D(x, params)-y
                      
    
def gaussian_2D(x1,x2,params):
    '''This function defines a 2D gaussian that is used for fitting.
    Parameters
    ----------
    x1 : variable
        the first axis variable for the 2D gaussian.
    x2 : variable
        the second axis variable for the 2D gaussian.
    params : variables
        the list of "fitting" variables for the 2D gaussian
            Parameters:

            1. amp  =  the amplitude of the 2D guassian
            2. cen1 =  the centre of the first axis gaussian
            3. cen2 = the centre of the 2nd axis guassian 
            4. std1 = the width of the first axis gaussian
            5. std2 = the width of the second axis gaussian
            6. bkg  = height of the constant background for the gaussian
    '''
    amp,cen1,cen2,std1,std2,bkg = params
    return amp*np.exp(-(x1-cen1)**2/2/std1**2-(x2-cen2)**2/2/std2**2)+bkg

def gaussian_2D_error(params,y,x1,x2):
    '''This function defines the difference between a fitted gaussian and the raw data.
    Parameters
    ----------
    params : variables
        the list of "fitting" variables for the 2D gaussian
            Parameters:

            1. amp  =  the amplitude of the 2D guassian
            2. cen1 =  the centre of the first axis gaussian
            3. cen2 = the centre of the 2nd axis guassian 
            4. std1 = the width of the first axis gaussian
            5. std2 = the width of the second axis gaussian
            6. bkg  = height of the constant background for the gaussian
    y  : variable 
        the value of the raw data at (x1, y1)
    x1 : variable
        the first axis variable for the 2D gaussian.
    x2 : variable
        the second axis variable for the 2D gaussian.
    '''

    return gaussian_2D(x1, x2, params)-y


def fit_Gauss_1Dseries(uid,initial_guess):
    ''' 
    This scan fits 1D Gaussian curves o each line in a 2D dataset giben by uid.
        
    This scan is used to fit to a 1D Gaussian to each line in a 2D dataset, the output is then a set of 1D data corresponding to the
    amplitude, position and linewidth as a fucntion of the Y axis of the dataset. The function returns a list with 4 items, the items 
    being the data for amplitude,position, linewidth, background offset and y_sequence number.                   

    Parameters
    ----------
    uid : number
        This is the uid used to extract the data from the databroker.
                                       
    initial_guess : list
        This is the initial guess for the amplitude, centre, width and background offset, in a list in this order.

    '''  

    #reference the data
    hdr=db[uid]
    
    #find out the shape of the data
    x_num = hdr.start.X_num
    y_num = hdr.start.Y_num
        
    #Load the data from the databroker.
   
    amplitude=[]
    linewidth=[]
    position=[]
    background=[]
    y_seq=[]
        
    #step through each "row" and fit a gaussian.
    for y_step in range(0,y_num):
        x = db.get_table(hdr,[hdr.start.plot_Xaxis])[x_num*y_step:x_num*(y_step+1)-1] 
        y_seq.append(y_step)
        data = db.get_table(hdr,[hdr.start.plot_Zaxis])[x_num*y_step:x_num*(y_step+1)-1]

        popt_row, pcov_row = opt.leastsq(gaussian_1D_error,x0=initial_guess,args=(data[hdr.start.plot_Zaxis],x[hdr.start.plot_Xaxis]))
        amplitude.append(popt_row[0])
        position.append(popt_row[1])
        linewidth.append(popt_row[2])
        background.append(popt_row[3])

        initial_guess[0]=popt_row[0]
        initial_guess[1]=popt_row[1]
        initial_guess[2]=popt_row[2]
        initial_guess[3]=popt_row[3]

        
    return [amplitude,linewidth,position,background,y_seq]
    

def max_in_1D(uid):
    ''' 
    This scan is used to find the maximum value in a 1D data set and return the max value, and the x co-ordinate.
        
    This scan is used to find the maximum value in a 1D dataset and return the max value, and the x co-ordinate.
    It returns a list containing the x and y values for the maximum y value in the dataset.                   

    Parameters
    ----------
    uid : number
        This is the uid used to extract the data from the databroker.

    '''
    
    scan = db[scan_id]
    if scan.start.plot_Xaxis.startswith('FE'):
        Xname = scan.start.plot_Xaxis.replace('_readback', '_setpoint')
    else:
        Xname = scan.start.plot_Xaxis+'_user_setpoint'
        
    data2D = db.get_table(scan,[Xname, scan.start.plot_Yaxis])
    del data2D['time']

    max_idx = np.argmax(data3D[scan.start.plot_Yaxis], axis=None)

    return [data2D[Xname][max_idx],data2D[scan.start.plot_Yaxis][max_idx]]


def max_in_2D(uid):
    ''' 
    This scan is used to find the maximum value in a 2D data set and return the max value, and the x and y co-ordinates.
        
    This scan is used to find the maximum value in a 2D dataset and return the max value, and the x and y co-ordinates.
    It returns a list containg the x, y and z values for the maximum z value in the dataset.                   

    Parameters
    ----------
    uid : number
        This is the uid used to extract the data from the databroker.

    '''
    
    scan = db[scan_id]
    if scan.start.plot_Xaxis.startswith('FE'):
        Xname = scan.start.plot_Xaxis.replace('_readback', '_setpoint')
        Yname = scan.start.plot_Yaxis.replace('_readback', '_setpoint')
    else:
        Xname = scan.start.plot_Xaxis+'_user_setpoint'
        Yname = scan.start.plot_Yaxis+'_user_setpoint'
        
    data3D = db.get_table(scan,[Xname, Yname, scan.start.plot_Zaxis])
    del data3D['time']

    max_idx = np.argmax(data3D[scan.start.plot_Zaxis], axis=None)

    return [data3D[Xname][max_idx],data3D[Yname][max_idx],data3D[scan.start.plot_Zaxis][max_idx]]
