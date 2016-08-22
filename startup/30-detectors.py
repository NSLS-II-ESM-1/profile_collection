from ophyd.quadem import QuadEM

from ophyd import (EpicsSignalRO, EpicsSignal, Component as Cpt,
               DynamicDeviceComponent as DDCpt, Signal)

class ESMQuadEM(QuadEM):
    port_name = Cpt(Signal, value='EM180')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs.update([(self.acquire_mode, 'One-shot')  # single mode
                                ])

qem01 = ESMQuadEM('XF:21IDA-BI{EM:1}EM180:', name='qem01')
qem02 = ESMQuadEM('XF:21IDB-BI{EM:2}EM180:', name='qem02')
qem03 = ESMQuadEM('XF:21IDB-BI{EM:3}EM180:', name='qem03')
qem04 = ESMQuadEM('XF:21IDB-BI{EM:4}EM180:', name='qem04')
qem05 = ESMQuadEM('XF:21IDB-BI{EM:5}EM180:', name='qem05')

qem06 = ESMQuadEM('XF:21IDC-BI{EM:6}EM180:', name='qem06')
qem07 = ESMQuadEM('XF:21IDC-BI{EM:7}EM180:', name='qem07')
qem08 = ESMQuadEM('XF:21IDC-BI{EM:8}EM180:', name='qem08')
qem09 = ESMQuadEM('XF:21IDC-BI{EM:9}EM180:', name='qem09')
qem10 = ESMQuadEM('XF:21IDC-BI{EM:10}EM180:', name='qem10')

