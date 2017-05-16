from bluesky.plans import count
from bluesky.callbacks import LiveTable


assert BTA2_DiagA2_1.cam.connected
RE(count([BTA2_DiagA2_1]), LiveTable([BTA2_DiagA2_1]))
