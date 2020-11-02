from ophyd import EpicsSignal,PVPositioner, EpicsSignalRO, EpicsMotor
from ophyd import Device, Component
from ophyd import DeviceStatus

class SES(Device):
    """
    Scienta SES control
    """

    center_en_sp = Component(EpicsSignal, ':center_en_SP')
    width_en_sp = Component(EpicsSignal, ':width_en_SP')
    set_start = Component(EpicsSignal, ':request')
    done = Component(EpicsSignalRO, ':done')
    iterations = Component(EpicsSignal, ':iterations_SP')
    excitation_en = Component(EpicsSignal, ':excitation_en_SP')
    steptime = Component(EpicsSignal, ':steptime_SP')
    acq_mode = Component(EpicsSignal, ':acq_mode_SP')
    pass_en = Component(EpicsSignal, ':pass_en_SP')
    lens_mode  = Component(EpicsSignal, ':lens_mode_SP')
    en_step = Component(EpicsSignal, ':en_step_SP')
    write_mode = Component(EpicsSignal, ':write_mode')


    def trigger(self):
        """
        Trigger the detector and return a Status object.
        """
        status = DeviceStatus(self)
        # Wire up a callback that will mark the status object as finished
        # when we see the state flip from "acquiring" to "not acquiring"---
        # that is, a negative edge.
        def callback(old_value, value, **kwargs):
            if old_value == 0 and value == 1:
                status._finished()
                self.done.clear_sub(callback)

        self.done.subscribe(callback, run=False)
        self.set_start.put(1)        
        # And return the Status object, which the caller can use to
        # tell when the action is complete.
        return status

    def read_params(self):
        """
        Read the existing parameters in SES into PVs
        """
        status = DeviceStatus(self)
        # Wire up a callback that will mark the status object as finished
        # when we see the state flip from "acquiring" to "not acquiring"---
        # that is, a negative edge.
        def callback(old_value, value, **kwargs):
            if old_value == 0 and value == 1:
                status._finished()
                self.done.clear_sub(callback)

        self.done.subscribe(callback, run=False)
        self.set_start.put(2)
        # And return the Status object, which the caller can use to
        # tell when the action is complete.
        return status

    
ses = SES('XF21ID1-ES-SES', name='ses')
