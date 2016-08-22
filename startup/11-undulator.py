from ophyd import (PVPositioner, Component as Cpt, EpicsSignal, EpicsSignalRO,
                   Signal)
from ophyd.utils import ReadOnlyError
import time as ttime




class UgapPositioner(PVPositioner):
    readback = Cpt(EpicsSignalRO, '-Ax:Gap}Mtr.RBV')
    setpoint = Cpt(EpicsSignal, '-Ax:Gap}Mtr')
    actuate = Cpt(EpicsSignal, '}Cmd:Start-Cmd')
    actuate_value = 1

    stop_signal = Cpt(EpicsSignal, '}Cmd:Stop-Cmd')
    stop_value = 1

    done = Cpt(EpicsSignalRO, '-Ax:Gap}Mtr.MOVN')
    done_val = 0

    
ugap = UgapPositioner(prefix='SR:C21-ID:G1A{EPU:1', settle_time=3., name='ugap')
ugap.read_attrs = ['setpoint', 'readback']

