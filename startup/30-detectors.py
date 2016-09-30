from ophyd.quadem import QuadEM

from ophyd import (EpicsSignalRO, EpicsSignal, Component as Cpt,
               DynamicDeviceComponent as DDCpt, Signal)
from ophyd import AreaDetector, SingleTrigger, HDF5Plugin, TIFFPlugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.filestore_mixins import FileStoreTIFFIterativeWrite


class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass
    # AD v2.2.0 (at least) does not have this. It is present in v1.9.1.
    # file_number_sync = None


class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    pass


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


class MyDetector(SingleTrigger, AreaDetector):
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix='TIFF1:',
               write_path_template='/image_data/',  # trailing slash!
               read_path_template='/xf21id-ioc2/cam01/')
          
    #hdf5 = Cpt(HDF5PluginWithFileStore,
    #           suffix='HDF1:',
    #           write_path_template='/home/xf21id1/Images/cam01/',  # trailing slash!
    #           read_path_template='/xf21id-ioc2/home/xf21id1/Images/cam01/')
    
Diag1_Horiz = MyDetector('XF:21IDA-BI{Diag:1-Cam:H}', name='Diag1_Horiz')
Diag1_Horiz.tiff.write_path_template = '/image_data/cam01/'
Diag1_Horiz.read_attrs = ['tiff']
Diag1_Horiz.tiff.read_attrs = []


Diag1_Vert = MyDetector('XF:21IDA-BI{Diag:1-Cam:V}', name='Diag1_Vert')
Diag1_Vert.tiff.write_path_template = '/image_data/cam02/'
Diag1_Vert.read_attrs = ['tiff']
Diag1_Vert.tiff.read_attrs = []
