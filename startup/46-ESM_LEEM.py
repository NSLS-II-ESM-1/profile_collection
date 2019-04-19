import numpy as np
from ophyd.sim import NullStatus

from ophyd import Device
from ophyd import Device, EpicsSignal
from ophyd import Device, EpicsSignal, EpicsMotor, Component as Cpt


class LEEMDetector(Device):
    start_acq = Cpt(EpicsSignal, 'start_acq')
    fileinc = Cpt(EpicsSignal, 'fileinc')
    filepath = Cpt(EpicsSignal, 'filepath')
    filename = Cpt(EpicsSignal, 'filename')

    def __init__(self, *args, **kwargs):
        def check_if_done(value, old_value, **kwargs):
            st = self.st
            if st is not None:
                if value == 0 and old_value == 1:
                    st._finished()
                    self.st = None

        super().__init__(*args, **kwargs)
        # On a background thread, listen for the server's response.
        self.start_acq.subscribe(check_if_done)
        self.st = None

    def trigger(self):
        # Write to server.
        self.st = self.start_acq.set(1)
        return self.st


leem_det = LEEMDetector('XF:21ID2{LEEM}:', name='leem_det')
#leem_det.trigger()


def LEEM_plan(grating='600', EPU='105', E_start=100, E_stop=150, E_step=0.1):
    #Change energy and have LEEM take image

     # the grating to use in the scans

    energies = np.arange(E_start, E_stop+E_step, E_step)  # (100,105) # the list of photon energies to use in the scan
#    Erange=[0.75,6.5]   #the photon energy %range for the scans, in the form [x,y] where the start
                      #value is x*Eph and the end value is y*Eph or the limit of the grating range.

    #yield from Beamline.move_to('Branch_A')

    for energy in energies:
         yield from Eph.move_to(energy, grating=grating, EPU=EPU)
         yield from bp.count([leem_det], num=1)

