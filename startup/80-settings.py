from ophyd import EpicsSignal, EpicsSignalRO

#gs.DETS = []
#all_objs = globals()
#counters = [counter for counter in all_objs.values() if isinstance(counter, EpicsSignal)]

#gs.DETS = counters

"""
import logging

from ophyd.session import get_session_manager

sessionmgr = get_session_manager()
sessionmgr['olog_client'] = olog_client
print('These positioners are disconnected:')
print([k for k, v in sessionmgr.get_positioners().items() if not v.connected])

# metadata set at startup
gs.RE.md['owner'] = 'xf21id1'
gs.RE.md['group'] = 'esm'
gs.RE.md['beamline_id'] = 'ESM'
#gs.RE.md['custom'] = {}

def print_scanid(name, doc):
    if name == 'start':
        print('Scan ID:', doc['scan_id'])
        print('Unique ID:', doc['uid'])

def print_md(name, doc):
    if name == 'start':
        print('Metadata:\n', repr(doc))

#gs.RE.subscribe('start', print_scanid)
#from ophyd.commands import wh_pos, log_pos, mov, movr
"""

sd.baseline = [PGM, EPU1, EPU2, ExitSlitA, ExitSlitB,FEslit,M1,M3,M4A,M4B,LT,SP]


BlueskyMagics.positioners = [EPU1.phase,EPU2.phase,EPU1.gap,EPU2.gap,M1.X,M1.Ry,M1.Rz]
