from bluesky.plans import relative_scan
from bluesky.callbacks import LiveTable


RE(relative_scan([BTA2_DiagA2_1], BTA2_diag.trans, -0.1, 0.1, 5),
   LiveTable([BTA2_diag.trans, BTA2_DiagA2_1]))
