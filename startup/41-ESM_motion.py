import IPython
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import scipy.optimize as opt
import os
from databroker import DataBroker as db, get_table, get_images, get_events
from bluesky.plans import scan, baseline_decorator, subs_decorator,abs_set,adaptive_scan,spiral_fermat,spiral,scan_nd,mv
from bluesky.spec_api import _figure_name, first_key_heuristic
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
###    The following set of code are used to move motors to pre-determined locations. For instance
###    moving the Low Temperature manipulator from the Low Temperature chamber to the Analysis chamber
###    and vice-versa. They can involve running through a series of steps to ensure that it is safe, and
###    then following a safe motion path to reach the desired location.

###    The Locations for the various locations and steps are to be stored in .csv files that are read by the program
###    prior to performing the move.


###    ESM motion device definitions

##    Definition of the motion device class located at ESM.

class ESM_motion_device:
    def __init__(self,definition_file_path):
        '''
        Move a series of motors to one of a series of predefined locations.
        This plan allows the user to move a series of motors to various locations as described in a .csv setup
        file. There are a number of attribute functions involved that allow the motors to be moved to
        the various locations from the current location. As described below, optionally the motion can occur via a
        transfer location
         
 
        Attribute Parameters and Functions
        ---------
        definition_file_path_str: str
            A string containing the filepath to the .csv file that defines the instance.

        data_dict: dict
            A dictionary that holds the information from the definition file with each sample position
            having it's own item callable by the position name keyword.

        read_location_position_data: function
            Extracts the data from the .csv definition file to data_dict

        axes: function
            Extracts the list of motion axes from data_dict.

        axes_dict: function
            Extracts the dictionary of motion axes an postions from data_dict for the inputted location.

        chambers: function
            Extracts the list of chambers.

        chambers_dict: function
            Extracts the dictionary of information about each chamber using the transfer locations defined
            by the suffix '_Tr' in the .csv file.
        
        current_chamber: function
            Determines which chamber the manipualtor is currently in.

        locations: function
            Extracts a list of loctations from data_dict.

        ask_user_continue: function
            provides a user prompt in the command line asking them to confirm the move.

        move_to: function
            moves the series of motors to the location defined by "location".

        DEFINITION FILE DESCRIPTION
        ---------------------------
        The definition file is a .csv file which has a column for each motor axis to be defined in the instance. The first 
        column should be labelled 'position_info'. Additional columns for each motion axis associated with this "device" 
        should be included and lablled with the 'Bluesky' axis name. For each defined "location" the name should be written 
        in the 'position_info' column and the position for each of the motor axes written in the corresponding column, if any 
        motor axis column is left blank then this axis is not moved for this location.
        
        If the optional parameters (see below) associated with a transfer axis are included then motion between the 2, or more 
        defined "sections" occurs by first moving to the defined 'transfer location' in the current section and then moving
        the transfer axis to the new section then finally moving inside the new section to the required position. 
        This is useful for manipulators when they should be "centered" before moving through a gate-valve, for example.
        When using this method, 1 transfer location for each section (or "chamber") should be defined, and given the 
        prefix '_Tr'. In addition to the motion axes these locations should also include the 'optional' columns: 
        
        chamber_info - To give a name to the chamber (all transfer locations should include a chamber).
        gate_valve_name_info - The name of the gate-valve that seperates the 2 chambers (can be "None").
        gate_valve_open_info - Should be "Yes", "No" or "Manual" to indicate if the gate valve should be opened, 
                               closed or if the gatevale should be opened manually prior to moving to this chamber
        transfer_axis_name -  should be the name of the motor axis that transfers the manipulator from one chamber to 
                              another
        transfer_axis_high_limit_info - should be the max value for the transfer axis while in this chamber.
        transfer_axis_low_limit_info - should be the min value for the transfer axis while in this chamber.        
                            
        For the non transfer locations all of these optional cloumns, with the exception of the chamber_info column, can
        be left blank. 

        '''

        
        #define the inputted values when defining an instance.
        self.definition_file_path=definition_file_path

        
        #define the information dictionaries for the instance.
        self.data_dict=self.read_location_position_data

        
    # Define the class properties here
    @property

    #Define the information functions here
    def read_location_position_data(self):
        ''' 
        Reads the definition csv file and record the info in data_dict. 
        
        This function reads the definition .csv file and writes the information to data_dict in order to 
        be used in the future motion.

        PARAMETERS
        ----------

        self.definition_file_path : str
            The path to the definiton .csv file for this instance.

        data_dict_temp : dict
            The output dictionary that contains the inforamtion form the .csv definition file.



        '''

        #define the dictionary to store the setup info.
        data_dict_temp = {}

        # extract the information formthe file and write it to the dictionary
        f=pd.read_csv(self.definition_file_path)
        f=f.set_index('position_info')

        for row_name in f.index:
            data_dict_temp[row_name]=dict(f.loc[row_name])

        return data_dict_temp


    def locations(self):
        ''' 
        Reads through data_dict file and generates a list of 'locations'. 
        
        This function sorts through data_dict and generates a list of location names. This is done assuming
        that the locations is the keyword list from data_dict.

        PARAMETERS
        ----------

        location_list : 
            The output list that contains the locations names.
 
        '''
        #define the locations list
        locations_list=list( self.data_dict.keys()  )

        return locations_list
        
        
    
    def axes(self):
        ''' 
        Reads through data_dict file and generates a list of 'axes names'. 
        
        This function sorts through data_dict and generates a list of axes names. This is done assuming
        that only the motion axes keywords in data_dict do not have the suffix '_info'.

        PARAMETERS
        ----------

        axes_list : 
            The output list that contains the axes names.
 
        '''

        #define the output list
        axes_list = list(key for key in list(self.data_dict[ list(self.data_dict.keys())[0]  ].keys()) if not
                         key.endswith('_info') )

        return axes_list

    def axes_dict(self, to_location ):
        ''' 
        Reads through data_dict file and generates a dictionary with the axes information. 
        
        This function sorts through data_dict and generates a dictionary, with the keywords being the
        possible locations and the entries being a dictionary of the axes information.

        PARAMETERS
        ----------

        axis_dict : dict
            The output dictionary that contains the chamber names and information.
 
        '''
        #define the input parameter
        self.to_location=to_location
        
        #define the output dictionary
        
        axis_dict={}
        
        #define the list of axes
        axis_list=self.axes()

        #define the dicionary of chamber info
        for axis in axis_list:
            axis_dict[axis]=self.data_dict[to_location][axis]
        
        return axis_dict
    

    def chambers(self):
        ''' 
        Reads through data_dict file and generates a list of chambers. 
        
        This function sorts through data_dict and generates a list of chambers using the 'chambers' column.

        PARAMETERS
        ----------

        chamber_list : list
            The list of chamber information.
 
        '''

        chamber_list=list(s for s in list(self.data_dict.keys()) if s.endswith('_Tr'))
        if len(chamber_list) <= 0:
            chamber_list=['No chamber']

        return chamber_list
        
    
    def chambers_dict(self):
        ''' 
        Reads through data_dict file and generates a dictionary with the chamber information. 
        
        This function sorts through data_dict and generates a dictionary, with the keywords being the
        possible chambers and the entries being a dictionary of the important information. This is done 
        assuming that only transfer postions for each chamber have the suffix '_Tr'.

        PARAMETERS
        ----------

        chamber_dict : dict
            The output dictionary that contains the chamber names and information.
 
        '''

        #define the output dictionary
        chamber_dict={}
        
        #define the list of chambers
        chamber_list=self.chambers()

        if chamber_list[0] == 'No chamber':
            chamber_dict['No chamber'] = chamber_list
        else:
            #define the dicionary of chamber info
            for pos in chamber_list:
                chamber_dict[self.data_dict[pos]['chamber_info']]=self.data_dict[pos]
        
        return chamber_dict


    
    def current_chamber(self):
        ''' 
        Determines what the current chamber is. 
        
        This function reads the position of the transfer axis and uses this to determine which chamber the 
        manipulator is currently located in. It retruns the name of the chamber as a string.

        PARAMETERS
        ----------
        
        chamber_name : str
            The output string which gives the name of the current chamber.
 
        '''

        # define the chamber information dictioanry
        chamber_dict=self.chambers_dict()



        chamber_name = 'error'

        if 'No chamber' in list(chamber_dict.keys()):
            chamber_name= 'No chamber'
        else:
            #define the motor record and axis attribute for the ttransfer axis
            obj,_,attr = chamber_dict[ list(chamber_dict.keys())[0] ] ['transfer_axis_name_info'].partition('_')
            #defien the transfer axis object
            transfer_axis=getattr(ip.user_ns[obj],attr)
            #determine the current trasnfer axis postion 
            axis_pos=transfer_axis.position
            #determine which chamber contains the axis position. 

            for chamber in list(chamber_dict.keys()):
                
                if float(chamber_dict[chamber]['transfer_axis_low_limit_info']) <= axis_pos <= float(chamber_dict[chamber]['transfer_axis_high_limit_info']):
                    chamber_name=chamber

        
                    
        return chamber_name


    def status(self, output='string'):
        ''' 
        Reads the status of every axis defined for the device and outputs the result as a dictioanry or a 
        formatted string. 
        
        Reads the position of every axis for the device and returns a dictionary, returns a formatted string
        or appends to a file.

        PARAMETERS
        ----------
        
        output : str, optional
            Indicates what to do with the output, default is to return a formatted string. Can take the values:
                - 'string', indicates the routine should return a formatted string.
                - 'string_and_file', indicates the routine should return a formatted string and append to a 
                   status file for the device.
                - 'dict', indicates the routine should return a dictionary of positions.

        f_string : str
            Possible output string for formatting.

        status_dict : dict
            Possible outputted dictionary, which has keywords for each motor in the axis list and contains 
            a dictionary of axes names and positions.
 
        '''

        #define the input parameter
        self.output=output

        #define the dictionary of motion axes for the current instance.
        axis_list=self.axes()
        axis_dict=self.axes_dict()

        temp_list=axis_list

        status_dict={}
     
        
        #continue looping over the list of remaining axes until none exist.
        while len(temp_list)>=0:
            temp_axes_dict={}
            device_name,_,axis = temp_list[0].partition('_')
            temp_axes_list = list(key for key in temp_list if key.startswith(device_name) )
            for axes in temp_axes_list:
                temp_axes_dict[axes]=axis_dict[axes]


                    
    
    def ask_user_continue(self,request_str):
        ''' 
        This function asks the user to confirm that the current process should be completed.
        
        This function asks the user, using the request_str to give specifics, if they should continue.

        PARAMETERS
        ----------
        
        request_str : str
            The output string given with the user prompt.
        '''

        valid={'yes':1,'no':0}
        prompt_str = ', continue (yes or no):'

        while True:
            sys.stdout.write(request_str + prompt_str)
            choice = input().lower()
            if choice in valid:
                return valid[choice]

        
    #Define the motion functions here

    def move_to(self, location):
        
        ''' 
        moves the manipulator to the position given by "location"
        
        This function moves the manipulator to the location defined by "location". it returns and error message
        indicating if the sample transfer was succesful, and if not what went wrong.

        PARAMETERS
        ----------

        location : str
            The position to move the manipulator to.
 
        '''

        #define the axes that need to be moved in the transfer.
        axis_dict=self.axes_dict(location)
        axis_list = list(axis for axis in list(axis_dict.keys()) if not np.isnan(axis_dict[axis]) )

        #check if the transfer goes between chambers
        if self.current_chamber() == 'No chamber':
            if self.ask_user_continue('This will move the manipulator, unless print_summary was used to call it') ==0:
                raise RuntimeError('user quit move')
            else:
                for axis in axis_list:
                    #define the motor record and axis attribute for the ttransfer axis
                    obj,_,attr = axis.partition('_')
                    #define the transfer axis object
                    move_axis=getattr(ip.user_ns[obj],attr)
                    #move the axis to the new location
                    yield from mv(move_axis, axis_dict[axis] )

        #if the transfer has multiple chambers.
        else:

            from_chamber=self.current_chamber()
            to_chamber=self.data_dict[location]['chamber_info']
            chamber_dict=self.chambers_dict()
        
            if from_chamber == 'error':
                raise RuntimeError('current manipulator position is outside all "chamber" ranges')

            elif from_chamber == to_chamber :
                if self.ask_user_continue('This will move the manipulator, unless print_summary was used to call it') ==0:
                    raise RuntimeError('user quit move')
                else:
                    #MOVE DIRECTLY TO THE NEW POSITION
                    for axis in axis_list:
                        #define the motor record and axis attribute for the ttransfer axis
                        obj,_,attr = axis.partition('_')
                        #define the transfer axis object
                        move_axis=getattr(ip.user_ns[obj],attr)
                        #move the axis to the new location
                        yield from mv(move_axis, axis_dict[axis] )
                
            elif chamber_dict[to_chamber]['gate_valve_open_info'] in ('Yes','Manual') :
                if self.ask_user_continue('This will move the manipulator and open a gate valve,'+
                                          ' unless print_summary was used to call it') ==0:
                    raise RuntimeError('user quit move')
                elif chamber_dict[to_chamber]['gate_valve_open_info'] == 'Manual' :
                    if self.ask_user_continue('gate valve must be opened manually. "IS GATE VALVE OPEN"') ==0:
                        raise RuntimeError('user quit move')
                else:
                    from_axes_list= list(key for key in chamber_dict[from_chamber].keys() if not key.endswith('_info') )
                    from_axis_list=list(axis for axis in from_axes_list if not np.isnan(chamber_dict[from_chamber][axis]) )
                    ####MOVE TO 'FROM CHAMBER' TRANSFER POSITION####
                    for axis in from_axis_list:
                        if not axis.endswith('_info'):
                            #define the motor record and axis attribute for the transfer axis
                            obj,_,attr = axis.partition('_')
                            #define the transfer axis object
                            move_axis=getattr(ip.user_ns[obj],attr)
                            #move the axis to the new location
                            yield from mv(move_axis, chamber_dict[from_chamber][axis] )

                    ####MOVE TO 'TO CHAMBER' TRANSFER POSITION ALONG 'TRANSFER AXIS'####
                    #define the motor record and axis attribute for the transfer axis
                    axis=chamber_dict[to_chamber]['transfer_axis_name_info']
                    obj,_,attr = axis.partition('_')
                    #define the transfer axis object
                    move_axis=getattr(ip.user_ns[obj],attr)
                    #move the axis to the new location
                    yield from mv(move_axis, chamber_dict[to_chamber][axis] )
                    
                    
                    ####MOVE TO POSITION IN 'TO CHAMBER'####
                    for axis in axis_list:
                        #define the motor record and axis attribute for the ttransfer axis
                        obj,_,attr = axis.partition('_')
                        #define the transfer axis object
                        transfer_axis=getattr(ip.user_ns[obj],attr)
                        #move the axis to the new location
                        yield from mv(transfer_axis, axis_dict[axis] )

                    
            else:
                if self.ask_user_continue('This will move the manipulator to the other chamber'+
                                          ', unless print_summary was used to call it') ==0:
                    raise RuntimeError('user quit move')
                else:

                    ####MOVE TO 'FROM CHAMBER' TRANSFER POSITION####
                    from_axes_list= list(key for key in chamber_dict[from_chamber].keys() if not key.endswith('_info') )
                    from_axis_list=list(axis for axis in from_axes_list if not np.isnan(chamber_dict[from_chamber][axis]) )
                    for axis in from_axis_list:
                        if not axis.endswith('_info'):
                            #define the motor record and axis attribute for the transfer axis
                            obj,_,attr = axis.partition('_')
                            #define the transfer axis object
                            move_axis=getattr(ip.user_ns[obj],attr)
                            #move the axis to the new location
                            yield from mv(move_axis, chamber_dict[from_chamber][axis] )

                    ####MOVE TO 'TO CHAMBER' TRANSFER POSITION ALONG 'TRANSFER AXIS'####
                    #define the motor record and axis attribute for the transfer axis
                    axis=chamber_dict[to_chamber]['transfer_axis_name_info']
                    obj,_,attr = axis.partition('_')
                    #define the transfer axis object
                    move_axis=getattr(ip.user_ns[obj],attr)
                    #move the axis to the new location
                    yield from mv(move_axis, chamber_dict[to_chamber][axis] )
                    
                    
                    ####MOVE TO POSITION IN 'TO CHAMBER'####
                    for axis in axis_list:
                        #define the motor record and axis attribute for the ttransfer axis
                        obj,_,attr = axis.partition('_')
                        #define the transfer axis object
                        transfer_axis=getattr(ip.user_ns[obj],attr)
                        #move the axis to the new location
                        yield from mv(transfer_axis, axis_dict[axis] )
                
        
    

## Define the instances of the ESM_device class

#The low temperature manipulator
LT_manip=ESM_motion_device('/home/xf21id1/.ipython/profile_collection/startup/motion_definition_files/LT_manip_definition.csv')    

#The beamline as a whole (swap branches, etc).
Beamline=ESM_motion_device('/home/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Beamline_definition.csv')  
