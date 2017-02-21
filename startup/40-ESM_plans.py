import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from databroker import DataBroker as db, get_table, get_images, get_events
from bluesky.plans import scan, baseline_decorator, subs_decorator,abs_set,adaptive_scan,spiral_fermat,spiral,scan_nd
from bluesky.spec_api import _figure_name
from bluesky.callbacks import LiveTable,LivePlot
from pyOlog.SimpleOlogClient import SimpleOlogClient
from esm import ss_csv
from cycler import cycler
import math
import re
#from tqdm import tqdm





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


def scan_time(DETS,num=1,delay=0,DET_channel=None,scan_type=None):
    '''scan_time(DETS,num=1,delay=0,DET_channel=None,scan_type=None):
       This scan provides a time measurement of a list of detectors, including live plotting and a live table. The detector to 
       'display' must be 1D and should be first in the list. 
         
       REQUIRED PARAMETERS
           DETS  --  A list of detectors to record at each step (first one must be 1D)
           
       OPTIONAL PARAMETERS
           num   --  Optional input of the number of points to take, default is 1 to capture until stopped using 'ctrl-C' set 'num = None'
           delay --  Optional delay time between succesive readings, default is 0.
           DET_channel  -- Optional channel number to plot for multi channel detectors (eg. for qem to plot 
                           'qem01_current1_mean_value' use 1). To use this option in the scan call you need
                                  to place ',DET_channel=x' after 'steps' in the scan call
           scan_type   -- Optional definition of the scan type to include in the metadata, correct use of this will allow
                           searching the database to be easier (for instance, if all XPS data is given the scan_type 'XPS'
                           then searching the database based on the keyword scan_type = 'XPS' will return all XPS scans).
     '''
    #This section determines the Y axis variable to plot for the scan, if the first detector in the list is a single channel
    #detector then it plots that detector value, if it has multiple single channels it plots the channel defined by the
    #optional input DET_channel (channel 1 is plotted if DET_channel is not specified.
    Y_axis = Get_Yaxis_name(DETS[0], DET_channel)

    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the metadata using the md={'keyword1'
    #:'value1','keyword2':'value2',..... } argument. For instance using md={'scan_type':'measurement type'} will define the scan_type as a particular
    #measurement type.
        
    #setup standard metadata
    _md = {'scan_name':'scan_time','plot_Xaxis':'sequence_no','plot_Yaxis':Y_axis,'scan_type':scan_type,'delay':delay}

        #Define the OLOG message to be generated.
           #This section is used to define what should be written to the OLOG. I want to include in here the text to be
           #written to the OLOG, some of the metadata as keywords for searching the OLOG as well as attach a text file
           #with a detalied list of all scan info and beamline motor positions and readouts for comparison later. 
        

    
    #Setup live table and live plot and tag modifier for the olog.
    #This section is used to define the live table and live plot functions for the scan.The '@subs_decorator'
    #call ensures that this is updated at each step of the scan           
    if num is not 1:
        table = LiveTable([])
        plot =  ESM_setup_Plot(Y_axis)  #LivePlot(Y_axis,scan_motor.name, ax=ax)
        add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)

        @subs_decorator(table)
        @subs_decorator(plot)
        @subs_decorator(add_tag)
        def inner():
            return( yield from count(DETS,num,delay,md=_md))
    else:
        def inner():
            return( yield from count(DETS,num,delay,md=_md))
      
    uid=yield from inner()
    ESM_save_csv(uid,Y_axis,time=True)


###    
###1D SCANS
###These scans are used to scan over 1 "motor" axis, the motor can be any variable that can be "set" via bluesky.


def scan_1D(DETS, scan_motor, start, end ,step_size,DET_channel=None,scan_type=None,adaptive=None):

    ''' This scan provides a 1D scan using a list of detectors, including a live plot and a live table. The detector to 
        "display" must be 1D and should be the first in the list of detectors.
        
        REQUIRED PARAMETERS   
            DETS  --  A list of detectors to record at each step (first one must be 1D)
            scan_motor  --  The "motor" to scan which has the form Device.motor (eg. M1D_slit.inboard)
            start, end, step_size      -- The start value, end value and step size for the motor (note the actual 
                                          end-value will be as close as possible to the given end_value).
        OPTIONAL PARAMETERS
            DET_channel  -- Optional channel number to plot for multi channel detectors (eg. for qem to plot 
                            'qem01_current1_mean_value' use 1). To use this option in the scan call you need to place 
                            ',DET_channel=x' after 'steps' in the scan call.
            scan_type   -- Optional definition of the scan type to include in the metadata, correct use of this will allow
                           searching the database to be easier (for instance, if all XPS data is given the scan_type 'XPS'
                           then searching the database based on the keyword scan_type = 'XPS' will return all XPS scans).    
        
        SCAN OPTIONS:
           Adaptive scan : This is a scan where the step size is adaptively set based on a target slope. For instance the 
                           step size starts off at steps_max, if the slope between the current point and the preceeding 
                           point is greater/smaller than a target slope then it decreases/increases the step size to achieve 
                           the desired slope. Addtionally 'backstep=True' can be used to allow for the scan to go back and 
                           add more points between preceding points.

                           To use this feature include ', adaptive = [steps2_min,steps2_max,target_slope,backstep,threshold]' 
                           after step_size in the call. 
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

    #This section determines the Y axis and X axis variable to plot for the scan, if the first detector in the list is a single channel
    #detector then it plots that detector value, if it has multiple single channels it plots the channel defined by the
    #optional input DET_channel (channel 1 is plotted if DET_channel is not specified), the X_axis is assumed to be the first motor in
    #the list 'motors'.
    Y_axis = Get_Yaxis_name(DETS[0], DET_channel)
    motors=[scan_motor]
    X_axis = first_key_heuristic(list(motors)[0])

    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the metadata using the md={'keyword1'
    #:'value1','keyword2':'value2',..... } argument. For instance using md={'scan_type':'measurement type'} will define the scan_type as a particular
    #measurement type.
        
    #setup standard metadata
    _md = {'scan_name':'scan_1D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'scan_type':scan_type,'delta':step_size}

    
    #Setup live table and live plot and tag modifier for the olog.
    #This section is used to define the live table and live plot and olog output  functions for the scan.The '@subs_decorator'
    #call ensures that this is updated at each step of the scan           

    #table = ESMLiveTable([scan_motor]+list(DETS),num_starts=1)
    table = LiveTable([scan_motor]+list(DETS))
    plot =  ESM_setup_Plot(Y_axis,motors)
    add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)

    @subs_decorator(table)
    @subs_decorator(plot)
    @subs_decorator(add_tag)
        
    #Define the scan
    def inner():
      if adaptive is None:
          return( yield from scan(DETS,scan_motor,start,stop,steps+1,md=_md))
      else:
          return( yield from adaptive_scan(DETS,Y_axis,scan_motor,start,stop,adaptive[0],adaptive[1],adaptive[2],adaptive[3],adaptive[4],md=md_))

    #run the scan  
    uid=yield from inner()
    # save the data to .csv
    ESM_save_csv(uid,Y_axis)

        #Add info to the OLOG message to be generated.
            #This section is used to add the metadata relating to if the scan was aborted, stopped or completed to the
            #OLOG. Also, if the scan was completed, it should attach a copy of the plot to the OLOG.

###
###2D SCANS
###These scans are used to scan over 2 "motor" axes, the motors can be any variable that can be "set" via bluesky.


def scan_multi_1D(DETS, scan_motor1, start1, end1, step_size1,scan_motor2, start2, end2, step_size2,
                  snake=False,DET_channel=None,plot_seperate=False,scan_type=None,adaptive=None):
    ''' run a 2D scan using a list of detectors, having each step as a new file,the detector to "display" must be 1D and
        must be the first detector in the list 'DETS'.
        
        REQUIRED PARAMETERS
            DETS  --  A list of 1D detectors to record at each step
            scan_motor1  --  The outer "motor" to scan (which is different for each file) which has the form Device.motor 
                             (eg. M1D_slit.inboard)
            scan_motor2  --  The inner "motor" to scan (x axis for each file) which has the form Device.motor 
                             (eg. M1D_slit.inboard)
            start1,start2,end1,end2,steps1,steps2      -- The start value, end value and number of steps for the outer motor 
                                                          (motor 1) and the inner motor (motor 2).
            
        OPTIONAL PARAMETERS
            Snake       -- Optional snake value (ie. have the scan move the scan_motor2 from start2 to end2 on even runs and 
                           from end2 to start2 on odd runs. To use this option in the scan you need to place ',snake=True' 
                           after steps in the scan call.                          
            DET_channel        -- Optional channel number to plot for multi channel detectors (eg. for qem to plot 
                                  'qem01_current1_mean_value' use 1). To use this option in the scan you need to place 
                                  ',DET_channel=x' after 'steps' in the scan call.
            plot_seperate      -- Optional indicator to plot each file on a seperate figure. To use this option in the 
                                  scan you need to place ',plot_seperate=True' after 'steps' in the scan call. The default is 
                                  to plot on any existing window with the same x and y axes, if one exists. If one doesn't 
                                  exists it will create a new plot.
            scan_type   -- Optional definition of the scan type to include in the metadata, correct use of this will allow
                           searching the database to be easier (for instance, if all XPS data is given the scan_type 'XPS'
                           then searching the database based on the keyword scan_type = 'XPS' will return all XPS scans).   
            

        OPTIONS:
           Adaptive scan : This is a scan where the step size is adaptively set based on a target slope. For instance the step 
                           size starts off at steps_max, if the slope between the current point and the preceeding point is 
                           greater/smaller than a target slope then it decreases/increases the step size to achieve the desired 
                           slope. Addtionally 'backstep=True' can be used to allow for the scan to go back and add more points 
                           between preceding points.

                           To use this feature include ', adaptive = [steps2_min,steps2_max,target_slope,backstep,threshold]' 
                           after step_size in the call. 
                               NOTE: In this case step_size is not used, but a value must be included.
                           
                           REQUIRED PARAMETERS FOR THIS OPTION
                               steps2_min, steps2_max  : Are the minimum and maximum step sizes to use in the adaptive scan.
                               target slope            : Is a target slope to aim for in the scan
                               backstep                : Is a boolean (either 'True' or 'False') which determines if the scan 
                                                         is allowed to back step to aquire more data in a region of large change.
                               threshold               : Is a threshold for going back and rescanning a region (default is 0.8).  
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

        
    #This section determines the Y axis variable to plot for the scan, if the first detector in the list is a single channel detector then it plots
    #that detector value, if it has multiple single channels it plots the channel defined by the optional input DET_channel (channel 1 is plotted if
    #DET_channel is not specified.
    Y_axis = Get_Yaxis_name(DETS[0], DET_channel)
    motors=[scan_motor2]
    X_axis = first_key_heuristic(list(motors)[0])

    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the metadata using the md={'keyword1'
    #:'value1','keyword2':'value2',..... } argument. For instance using md={'scan_name':'measurement type'} will define the scan_name as a particular
    #measurement type.
        
    #setup standard metadata
    _md = {'scan_name':'scan_multi_1D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'scan_type':scan_type,'delta':step_size2,
             'multi_axis':scan_motor1,'multi_start':start1,'multi_stop':stop1,'multi_num':steps1+1,'multi_delta':step_size1}
       

    #Setup live table and live plot and tag modifier for the olog.
    #This section is used to define the live table and live plot and olog readout functions for the scan.The '@subs_decorator'
    #call ensures that this is updated at each step of the scan
    
    #Set up the plotting, tables and metadata           
    table = LiveTable([scan_motor2]+list(DETS))
    if not plot_seperate :
       plot =  ESM_setup_Plot(Y_axis,motors)
        
    add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)



    for i,c_val in enumerate(np.linspace(start1, stop1, num=(steps1+1))):
    # Step through each of the outer motor values
       yield from abs_set(scan_motor1, c_val, wait=True )
       if plot_seperate:
           plot=   LivePlot(Y_axis,first_key_heuristic(list(motors)[0]),ax=None)

       #add the location of this scan in the multi scan
       _md.update ( {'multi_pos':i+1} )
           
       #set the motor1 position 
       @subs_decorator(table)
       @subs_decorator(plot)
       @subs_decorator(add_tag)
       # Define some decorators to perform at each step (table update, plot update etc.)
       def inner_forward():
           if adaptive is None:
               return(yield from scan(DETS,scan_motor2,start2,stop2,steps2+1,md=_md))
           else:
              return( yield from adaptive_scan(DETS,Y_axis,scan_motor2,start2,stop2,adaptive[0],adaptive[1],adaptive[2],adaptive[3],adaptive[4],md=_md))
           #defines what the scan at each motor 1 step should be
       @subs_decorator(table)
       @subs_decorator(plot)
       @subs_decorator(add_tag)
       def inner_backward():
           if adaptive is None:
               return (yield from scan(DETS,scan_motor2,stop2,start2,steps2+1,md=_md))
           else:
              return( yield from adaptive_scan(DETS,Y_axis,scan_motor2,stop2,start2,-1*adaptive[0],-1*adaptive[1],adaptive[2],adaptive[3],adaptive[4],md=_md))
           #defines what the scan at each motor 1 step should be

       # performs the next step in the scan
       if snake:
           if i%2==1:
               uid=yield from inner_backward()
           else:
               uid=yield from inner_forward()
       else:
          uid= yield from inner_forward()
       
       #Save the file as a csv file using the scan id as the name
       ESM_save_csv(uid,Y_axis)



       
def scan_2D(DETS, scan_motor1, start1, end1, step_size1,scan_motor2, start2, end2, step_size2,
                  snake=False,concurrent=False,normal_spiral=False,fermat_spiral=False,square_spiral=False,DET_channel=None,scan_type=None):
    ''' run a 2D scan using a list of detectors,the detector to "display" must be 1D and must be the first detector in the list 'DETS'.
        
        REQUIRED PARAMETERS
            DETS  --  A list of 1D detectors to record at each step
            scan_motor1  --  The outer "motor" to scan (which is different for each file) which has the form Device.motor 
                             (eg. M1D_slit.inboard)
            scan_motor2  --  The inner "motor" to scan (x axis for each file) which has the form Device.motor 
                             (eg. M1D_slit.inboard)
            start1,start2,end1,end2,steps1,steps2      -- The start value, end value and number of steps for the outer motor 
                                                          (motor 1) and the inner motor (motor 2).
            
        OPTIONAL PARAMETERS
            Snake       -- Optional snake value (ie. have the scan move the scan_motor2 from start2 to end2 on even runs and 
                           from end2 to start2 on odd runs. To use this option in the scan you need to place ',snake=True' 
                           after steps in the scan call.                          
            DET_channel        -- Optional channel number to plot for multi channel detectors (eg. for qem to plot 
                                  'qem01_current1_mean_value' use 1). To use this option in the scan you need to place 
                                  ',DET_channel=x' after 'steps' in the scan call.
            scan_type   -- Optional definition of the scan type to include in the metadata, correct use of this will allow
                           searching the database to be easier (for instance, if all XPS data is given the scan_type 'XPS'
                           then searching the database based on the keyword scan_type = 'XPS' will return all XPS scans).   
   

        OPTIONS:
           NOTE: The options are attempted in the order shown below and only the first option found will be implemented regardless
                 of the location in the call. Optional parameters above that are not relevant to these options will be ignored.

           Concurrent motion : This allows for the motion of the first and second motors to occur concurrently. This will map out 
                           a 1D line though 2D space, with even spaced steps for both axes.

                           To use this feature include 'concurrent=True ' after step_size2 in the call. 
                               NOTE: In this case step_size2 is not used, but a value must be included. the step size of the second 
                               motor will be deteremined fro mthe calucalted number of steps for motor one and the range of motor 2.
                           
                           REQUIRED PARAMETERS FOR THIS OPTION
                               no extra parameters are required.
           
            spiral        : Indicates that the scan should follow a spiral pattern, centered in the middle of the x and y ranges
                           defined.
  
                          To use this feature include ' normal_spiral = True' after step_size2 in the call
                               NOTE: The radius delta is determined from the first motor step size and the number of theta steps is 
                               determined from the radius delta and the motor 2 step size. The pattern for the spiral is a series of 
                               expanding "rings", according to the following relationships:
                                
                                 Parameters:
                                 1. range1 = end1-start1, range2 = end2-start2
                                 2. centre1 = start1+range1/2, centre2=start2+range2/2
                                 3. delta_radius = step_size2
                                 4. num_theta = round( (4*pi*delta_radius) / ( range2*atan(2*step_size1) )   ) 
                                         note: this equation ensures that the y axis step size for the largest circle is ~ step_size1
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


            fermat spiral  :Indicates that the scan should follow a fermat spiral pattern, centered in the middle of the x and y ranges,
                           defined.

                          To use this feature include ' fermat_spiral = True' after step_size2 in the call.
                               NOTE: The radius delta is determined from the first motor step size and the number of theta steps is 
                               determined from the radius delta and the motor2 step size. The pattern for the spiral maps out a fermat 
                               spiral, according to the following relationships:

                                 Parameters:
                                 1. range1 = end1-start1, range2 = end2-start2
                                 2. centre1 = start1+range1/2, centre2=start2+range2/2
                                 3. delta_radius = step_size2
                                 4. num_theta = round( (4*pi*delta_radius) / ( range2*atan(2*step_size1) )   ) 
                                         note: this equation ensures that the y axis step size for the largest circle is ~ stepsize1
                                 5. num_rings = int( ( 1.5* ((range1/2)**2+(range2/2)**2)**(1/2) * num_theta / (2*delta_radius)  )**2 )
                                 6. phi = 137.508 * pi/180
                                 7. n = the 'nth' ring in the spiral
 
                                 Path equations:
                                 1. radius = n**(1/2) * delta_radius * num_theta/2
                                 2. angle  = phi * n 
                                 3. x = centre2 + radius*cos(angle)                               
                                 4. y = centre1 + radius*sin(angle)

                           REQUIRED PARAMETERS FOR THIS OPTION
                               no extra parameters are required.



            square spiral : Indicates that the scan should follow a square spiral pattern, centered in the middle of the x and y ranges
                           defined.
  
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
    

        
    #This section determines the Z axis variable to plot for the scan, if the first detector in the list is a single channel detector then it plots
    #that detector value, if it has multiple single channels it plots the channel defined by the optional input DET_channel (channel 1 is plotted if
    #DET_channel is not specified.
    Z_axis = Get_Yaxis_name(DETS[0], DET_channel)
    Xmotors=[scan_motor2]
    X_axis = first_key_heuristic(list(Xmotors)[0])
    Ymotors=[scan_motor1]
    Y_axis = first_key_heuristic(list(Ymotors)[0])

    #Setup metadata
    #This section sets up the metadata that should be included in the experiment file. Users can add/or change the metadata using the md={'keyword1'
    #:'value1','keyword2':'value2',..... } argument. For instance using md={'scan_name':'measurement type'} will define the scan_name as a particular
    #measurement type.
        
    #setup standard metadata


    #Setup live table and live plot and tag modifier for the olog.
    #This section is used to define the live table and live plot and olog readout functions for the scan.The '@subs_decorator'
    #call ensures that this is updated at each step of the scan
    
    #Set up the plotting, tables and metadata           
    table = LiveTable([X_axis]+[Y_axis]+list(DETS))

    
    if concurrent is True:
        _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
             'X_axis':X_axis,'X_start':start2,'X_stop':stop2,'X_num':steps2+1,'X_delta':step_size2,
             'Y_axis':Y_axis,'Y_start':start1,'Y_stop':stop1,'Y_num':steps1+1,'Y_delta':step_size1}

        add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)

        
        plot =  ESM_setup_Plot(Z_axis,Ymotors)

        @subs_decorator(table)
        @subs_decorator(plot)
        @subs_decorator(add_tag)
        # Define some decorators to perform at each step (table update, plot update etc.)

        def inner_prod():
            return(yield from inner_product_scan(DETS,steps1+1,scan_motor1,start1,stop1,scan_motor2,start2,stop2,md=_md))

        uid= yield from inner_prod()
        
    elif normal_spiral is True:
         _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
               'X_axis':X_axis,'X_start':start2,'X_end':end2,'X_centre':centre2,'X_range':range2,'delta_radius':delta_radius,
               'Y_axis':Y_axis,'Y_start':start1,'Y_end':end1,'Y_centre':centre1,'Y_range':range1,'num_theta':num_theta}  

         add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)
         
         mesh = LiveMesh(X_axis,Y_axis,Z_axis, xlim=(start2-step_size2,end2+step_size2), ylim=(start1-step_size1,end1+step_size1) )
    
         @subs_decorator(table)
         @subs_decorator(mesh)
         @subs_decorator(add_tag)
         # Define some decorators to perform at each step (table update, plot update etc.)

         def spiral_scan():
             return(yield from spiral(DETS,scan_motor2,scan_motor1,centre2,centre1,range2,range1,delta_radius,num_theta,md=_md))

         uid= yield from spiral_scan()

         
    elif fermat_spiral is True:
        _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
               'X_axis':X_axis,'X_start':start2,'X_end':end2,'X_centre':centre2,'X_range':range2,'delta_radius':delta_radius,
               'Y_axis':Y_axis,'Y_start':start1,'Y_end':end1,'Y_centre':centre1,'Y_range':range1,'num_theta':num_theta}

        add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)
        
        mesh = LiveMesh(X_axis,Y_axis,Z_axis, xlim=(start2-step_size2,end2+step_size2), ylim=(start1-step_size1,end1+step_size1) )
        
        @subs_decorator(table)
        @subs_decorator(mesh)
        @subs_decorator(add_tag)
        # Define some decorators to perform at each step (table update, plot update etc.)

        def fermat_scan():
            return(yield from spiral_fermat(DETS,scan_motor2,scan_motor1,centre2,centre1,range2,range1,delta_radius,num_theta/2,md=_md))
    
        uid= yield from fermat_scan()

        
    elif square_spiral is True:
        _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
               'X_axis':X_axis,'X_start':start2,'X_end':end2,'X_centre':centre2,'X_range':range2,'x_num':steps2,
               'Y_axis':Y_axis,'Y_start':start1,'Y_end':end1,'Y_centre':centre1,'Y_range':range1,'y_num':steps1}

        add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)
        
        mesh = LiveMesh(X_axis,Y_axis,Z_axis, xlim=(start2-step_size2,end2+step_size2), ylim=(start1-step_size1,end1+step_size1) )
        
        @subs_decorator(table)
        @subs_decorator(mesh)
        @subs_decorator(add_tag)
        # Define some decorators to perform at each step (table update, plot update etc.)

        def square_scan():
            return(yield from spiral_square(DETS,scan_motor2,scan_motor1,centre2,centre1,range2,range1,steps2+1,steps1+1,md=_md))
    
        uid= yield from square_scan()


        
    else:
        _md = {'scan_name':'scan_2D','plot_Xaxis':X_axis,'plot_Yaxis':Y_axis,'plot_Zaxis':Z_axis,'scan_type':scan_type,
               'X_axis':X_axis,'X_start':start2,'X_stop':stop2,'X_num':steps2+1,'X_delta':step_size2,
             'Y_axis':Y_axis,'Y_start':start1,'Y_stop':stop1,'Y_num':steps1+1,'Y_delta':step_size1}

        add_tag = simple_olog_client.create_tag(_md['scan_name'],active=True)

        raster = LiveRaster( (steps1+1,steps2+1) , Z_axis , ylabel= Y_axis, xlabel= X_axis, extent=(start2-step_size2/2,stop2+step_size2/2,stop1+step_size1/2,start1-step_size1/2),
                            aspect=(abs( (stop2-start2+step_size2)/(stop1-start1+step_size1) ) ) ) 
        
        @subs_decorator(table)
        @subs_decorator(raster)
        @subs_decorator(add_tag)
        # Define some decorators to perform at each step (table update, plot update etc.)

        def outer_prod():
            return(yield from outer_product_scan(DETS,scan_motor1,start1,stop1,steps1+1,scan_motor2,start2,stop2,steps2+1,snake,md=_md))

        uid=yield from outer_prod()

        
    #Save the file as a csv file using the scan id as the name

       
###
###UTILITY FUNCTIONS
### These are functions that are used in the scan plans above, but are not independent scan plans themselves. 

def Get_Yaxis_name(det0, det0_channel):
    '''This Routine is used to determine the Y axis name to use for plotting or saving for a given detector and detector 
       channel. It assumes that if the given detector channel is none that the first channel is to be used.
       
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



def ESM_setup_Plot(Y_axis,motors=None):
    '''Setup a LivePlot by inspecting motors and Y_axis and plotting on an existing plot if it exists. If motors is empty, 
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
        fig_name = _figure_name('BlueSky: {} v sequence number'.format(y_key))
        #generate the figure name associated with the axes for sequence number instead of motor name, if it doesn't exist
        #create a new one.
        ax = plt.figure(fig_name).gca()
        #set the value of ax to the correct figure name
        return LivePlot(y_key, ax=ax)
        #return the LivePlot function with the correct figurte and axes names


        
def ESM_save_csv(uid,Y_axis,time=False):
    ''' Save a 1D scan to an X-Y .csv file, used with 1D detectors and 1D scans.
         
         REQUIRED PARAMETERS 
             uid  -- the unique id number for the scan to find it in the databroker
             Y_axis -- the name of the field to include in the "Y" wave 
         
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
            df =get_table(hdr,[Y_axis])
            #get the table if the X_axis is to be time.
        else:
            motor=hdr.start.motors[0]
            df =get_table(hdr,[motor,Y_axis])                
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

class ESMLiveTable(LiveTable):
    ''' This sub-class of LiveTable is to be used in order to add the progress bar and time to finish indicator to the scans. 

    '''
    def __init__(self, *args, num_starts, **kwargs):
        super().__init__(*args, **kwargs)
        self.tq = tqdm.tqdm(num_starts, ...)

    def start(self, doc):
        super().start(doc)
        self.tq.increment()
        self.by_run_tq = tqdm.tqdm(doc['num_steps'])

    def event(self, doc):
        super().event(doc)
        self.by_run_tq.increment()

        
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


#"" test""
#"test2"
def create_manual():
    '''This routine is designed to load up this file, extract out all of the help comments (between 
    the triple quotes), and export this as a pdf file to be used as a manual. 


    '''
    plan_file = open('/home/xf21id1/.ipython/profile_collection/startup/40-ESM_plans.py', 'r')
    contents= plan_file.read()
    quotes = re.findall(r"'''[^']*'''",contents,re.U)
    output = ''.join(quotes)
    print (output)
    plan_file.close()
