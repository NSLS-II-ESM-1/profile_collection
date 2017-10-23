from ophyd import (PVPositioner, Component as Cpt, EpicsSignal, EpicsSignalRO,
                   Device)
from ophyd.utils import ReadOnlyError
import time as ttime




class UgapPositioner(PVPositioner):
    readback = Cpt(EpicsSignalRO, '-Ax:Gap}Mtr.RBV')
    setpoint = Cpt(EpicsSignal, '-Ax:Gap}Mtr')
    actuate = Cpt(EpicsSignal, '}Cmd:Start-Cmd', string=True)
    actuate_value = 'On'

    stop_signal = Cpt(EpicsSignal, '}Cmd:Stop-Cmd')
    stop_value = 1

    done = Cpt(EpicsSignal, '}Cmd:Start-Cmd')
    done_value = 0

    kill_switch_pressed = Cpt(EpicsSignalRO, '}Sts:Kill-Sts')
    safety_device_fail = Cpt(EpicsSignalRO, '}Sts:Safety-Sts', string=True)
    emergency_open_gap = Cpt(EpicsSignalRO, '}Sts:OpenGapCmd-Sts', string=True)
    # TODO subscribe kill switch pressed and stop motion

class UphasePositioner(PVPositioner):
    readback = Cpt(EpicsSignalRO, '-Ax:Phase}Mtr.RBV')
    setpoint = Cpt(EpicsSignal, '-Ax:Phase}Mtr')
    actuate = Cpt(EpicsSignal, '}Cmd:Start-Cmd', string=True)
    actuate_value = 'On'

    stop_signal = Cpt(EpicsSignal, '}Cmd:Stop-Cmd')
    stop_value = 1

    done = Cpt(EpicsSignal, '}Cmd:Start-Cmd')
    done_value = 0

    kill_switch_pressed = Cpt(EpicsSignalRO, '}Sts:Kill-Sts')
    safety_device_fail = Cpt(EpicsSignalRO, '}Sts:Safety-Sts', string=True)
    emergency_open_gap = Cpt(EpicsSignalRO, '}Sts:OpenGapCmd-Sts', string=True)
    # TODO subscribe kill switch pressed and stop motion

class EPU(Device):
    gap = Cpt(UgapPositioner, '', settle_time=0)
    phase = Cpt(UphasePositioner, '', settle_time=0)
    
EPU57 = EPU('SR:C21-ID:G1A{EPU:1', name='EPU57')
EPU57.gap.read_attrs = ['setpoint', 'readback']
EPU57.gap.readback.name='EPU57_gap'
EPU57.phase.read_attrs = ['setpoint', 'readback']
EPU57.phase.readback.name='EPU57_phase'
EPU57.hints={'fields':[EPU57.gap.name,EPU57.phase.name]}

EPU105 = EPU('SR:C21-ID:G1B{EPU:2', name='EPU105')
EPU105.gap.read_attrs = ['setpoint', 'readback']
EPU105.gap.readback.name='EPU105_gap'
EPU105.phase.read_attrs = ['setpoint', 'readback']
EPU105.phase.readback.name='EPU105_phase'
EPU105.hints={'fields':[EPU105.gap.name,EPU105.phase.name]}



class Source(Device):
    #This is a class to be used to define the readback values of the beam source front the
    #front end.

        #define the channels in the readback device.
        Current=Comp(EpicsSignalRO,'OPS-BI{DCCT:1}I:Real-I')
        Xoffset=Comp(EpicsSignalRO,'C31-{AI}Aie21:Offset-x-Cal')
        Xangle=Comp(EpicsSignalRO,'C31-{AI}Aie21:Angle-x-Cal')
        Yoffset=Comp(EpicsSignalRO,'C31-{AI}Aie21:Offset-y-Cal')
        Yangle=Comp(EpicsSignalRO,'C31-{AI}Aie21:Angle-y-Cal')


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
            #Define the list of EPICS signal status values.
            det_status_dict={}
            det_status_dict[self.name]={self.name+'_Current':self.Current.value,
                                        self.name+'_Xoffset':self.Xoffset.value,
                                        self.name+'_Xangle':self.Xangle.value,
                                        self.name+'_Yoffset':self.Yoffset.value,
                                        self.name+'_Yangle':self.Yangle.value}

            #Define the list of EPICS motor status values.
            status_dict={}
            status_dict['EPU_105']={'EPU105_gap':EPU105.gap.position,
                                    'EPU105_phase':EPU105.phase.position}

            status_dict['EPU57']={'EPU57_gap':EPU57.gap.position,
                                  'EPU57_phase':EPU57.phase.position}

            status_dict['FEslit']={'FEslit_h_center':FEslit.h_center.position,
                                 'FEslit_h_gap':FEslit.h_gap.position,
                                 'FEslit_v_center':FEslit.v_center.position,
                                 'FEslit_v_gap':FEslit.v_gap.position}
            
            
        
            f_string='************************************************************\n'
            f_string+=self.name+' STATUS:  '+time.strftime("%c") + '\n'
            f_string+='************************************************************\n\n'

            
            #step through the detectors and read the values.
            f_string+='EPICS SIGNAL COMPONENTS\n'
            f_string+='-----------------------\n'
            for key in list(det_status_dict.keys()):
                f_string+='    '+key+':\n'
                key_dict = det_status_dict[key]
                for det in key_dict:
                    obj,_,attr = det.partition('_')
                    f_string+='\t '+det+' -->  %f\n' % getattr(ip.user_ns[obj],attr).value
                f_string+='\n'           
            
            # step through the motors and read the values
            f_string+='EPICS MOTOR COMPONENTS\n'
            f_string+='-----------------------\n'
            for key in list(status_dict.keys()):
                f_string+='    '+key+':\n'
                key_dict = status_dict[key]
                for axis in key_dict:
                    obj,_,attr = axis.partition('_')
                    f_string+='\t '+axis+' -->  %f\n' % getattr(ip.user_ns[obj],attr).position
                    f_string+='\n'
        
            if output.startswith('string'):
                print (f_string)

            if output.endswith('file'):
                fl="/direct/XF21ID1/status_files/"
                fl+=self.name+'_status'
                f = open(fl, "a")
                f.write(f_string)
                f.close()

            if output == 'dict':
                return status_dict              

BeamSource = Source('SR:',name='BeamSource')
BeamSource.hints = {'fields': ['BeamSource_Current','BeamSource_Xoffset','BeamSource_Xangle',
                                 'BeamSource_Yoffset','BeamSource_Yangle' ] }
