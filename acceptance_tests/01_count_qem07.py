from bluesky.plans import count
from bluesky.callbacks import LiveTable


assert qem07.connected
RE(count([qem07]), LiveTable([qem07]))
