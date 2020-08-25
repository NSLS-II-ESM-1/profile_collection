from functools import partial
from ophyd.utils.epics_pvs import set_and_wait
set_and_wait = partial(set_and_wait, timeout=60)

import nslsii


nslsii.configure_base(get_ipython().user_ns, 'arpes')

