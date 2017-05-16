from bluesky.plans import count
from bluesky.callbacks import LiveTable


assert qem07.connected
RE.msg_hook = print
RE(count([qem07]), LiveTable([qem07]))
