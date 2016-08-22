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

