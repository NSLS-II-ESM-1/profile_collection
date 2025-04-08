import os

import nslsii
from ophyd.signal import EpicsSignalBase


# Set timeout for all EpicsSignalBase objects
EpicsSignalBase.set_defaults(connection_timeout=8)

# Configure RE + other services
nslsii.configure_base(get_ipython().user_ns,
                      'arpes',
                      publish_documents_with_kafka=True,
                      redis_prefix="arpes-", # TODO: Verify this is correct
                      redis_url="info.esm.nsls2.bnl.gov") # TODO: Verify this is correct

# Set ipython startup dir variable (used in some modules):
PROFILE_STARTUP_PATH = os.path.abspath(get_ipython().profile_dir.startup_dir)
