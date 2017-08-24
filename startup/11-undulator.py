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
    
EPU1 = EPU('SR:C21-ID:G1A{EPU:1', name='EPU1')
EPU1.gap.read_attrs = ['setpoint', 'readback']
EPU1.gap.readback.name='EPU1_gap'
EPU1.phase.read_attrs = ['setpoint', 'readback']
EPU1.phase.readback.name='EPU1_phase'
EPU1.hints={'fields':[EPU1.gap.name,EPU1.phase.name]}

EPU2 = EPU('SR:C21-ID:G1B{EPU:2', name='EPU2')
EPU2.gap.read_attrs = ['setpoint', 'readback']
EPU2.gap.readback.name='EPU2_gap'
EPU2.phase.read_attrs = ['setpoint', 'readback']
EPU2.phase.readback.name='EPU2_phase'
EPU2.hints={'fields':[EPU2.gap.name,EPU2.phase.name]}
