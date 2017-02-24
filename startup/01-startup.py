# Set up the logbook. This configures bluesky's summaries of
# data acquisition (scan type, ID, etc.).
# Make ophyd listen to pyepics.
from ophyd import setup_ophyd
setup_ophyd()

from metadatastore.mds import MDS
# from metadataclient.mds import MDS
from databroker import Broker
from databroker.core import register_builtin_handlers
from filestore.fs import FileStore

# pull from /etc/metadatastore/connection.yaml or
# /home/BLUSER/.config/metdatastore/connection.yml
mds = MDS({'host': 'xf21id1-ca1',
   'database': 'metadatastore',
   'port': 27017,
   'timezone': 'US/Eastern'}, auth=False)
# mds = MDS({'host': CA, 'port': 7770})

# pull configuration from /etc/filestore/connection.yaml or
# /home/BLUSER/.config/filestore/connection.yml
db = Broker(mds, FileStore({'host': 'xf21id1-ca1',
		    'port': 27017,
		    'database': 'filestore'}))
register_builtin_handlers(db.fs)

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
from bluesky.global_state import gs
gs.RE.subscribe('all', mds.insert)

# At the end of every run, verify that files were saved and
# print a confirmation message.
#from bluesky.callbacks.broker import verify_files_saved
#gs.RE.subscribe('stop', post_run(verify_files_saved))

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

# Optional: set any metadata that rarely changes.
# RE.md['beamline_id'] = 'YOUR_BEAMLINE_HERE'

# convenience imports
from ophyd.commands import *
from bluesky.callbacks import *
from bluesky.spec_api import *
from bluesky.global_state import gs, abort, stop, resume
from bluesky.plan_tools import print_summary
from bluesky.callbacks.broker import LiveImage
from time import sleep
import numpy as np

RE = gs.RE  # convenience alias

# Uncomment the following lines to turn on verbose messages for debugging.
# import logging
# ophyd.logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)

from functools import partial
from pyOlog import SimpleOlogClient
from bluesky.callbacks.olog import logbook_cb_factory


# backport upstream fix
import bluesky.callbacks.olog

bluesky.callbacks.olog.TEMPLATES['long'] = """
{{- start.plan_name }} ['{{ start.uid[:6] }}'] (scan num: {{ start.scan_id }})
Scan Plan
---------
{{ start.plan_name }}
{% if 'plan_args' in start %}
    {%- for k, v in start.plan_args | dictsort %}
        {{ k }}: {{ v }}
    {%-  endfor %}
{% endif %}
{% if 'signature' in start -%}
Call:
    {{ start.signature }}
{% endif %}
Metadata
--------
{% for k, v in start.items() -%}
{%- if k not in ['plan_name', 'plan_args'] -%}{{ k }} : {{ v }}
{% endif -%}
{%- endfor -%}"""

bluesky.callbacks.olog.TEMPLATES['desc'] = """
{{- start.plan_name }} ['{{ start.uid[:6] }}'] (scan num: {{ start.scan_id }})"""

bluesky.callbacks.olog.TEMPLATES['call'] = """RE({{ start.plan_name }}(
{%- for k, v in start.plan_args.items() %}{%- if not loop.first %}   {% endif %}{{ k }}={{ v }}
{%- if not loop.last %},
{% endif %}{% endfor %}))
"""

LOGBOOKS = ['Comissioning']  # list of logbook names to publish to
simple_olog_client = SimpleOlogClient()
generic_logbook_func = simple_olog_client.log
configured_logbook_func = partial(generic_logbook_func, logbooks=LOGBOOKS)

cb = logbook_cb_factory(configured_logbook_func, desc_dispatch=desc_templates)
RE.subscribe('start', cb)
logbook = simple_olog_client


import esm # general ESM routines: e2g(), g2e(), angles()
