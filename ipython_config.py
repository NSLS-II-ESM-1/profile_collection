c = get_config()
c.StoreMagics.autorestore = True
import os
if os.getenv("BS_ENABLE_OLOG_CALLBACK", 1) == 1:
    c.InteractiveShellApp.extensions = ['pyOlog.cli.ipy']
c.TerminalIPythonApp.log_datefmt = '%Y-%m-%d %H:%M:%S'
c.TerminalInteractiveShell.show_rewritten_input = True
# c.TerminalInteractiveShell.autocall = 2

#-----------------------------------------------------
#The following lines are in the startup file:
#from functools import partial
#from pyOlog import SimpleOlogClient
#from bluesky.callbacks.olog import logbook_cb_factory

## Set up the logbook. This configures bluesky's summaries of
## data acquisition (scan type, ID, etc.).

#LOGBOOKS = ['Data Acquisition']  # list of logbook names to publish to
#simple_olog_client = SimpleOlogClient()
#generic_logbook_func = simple_olog_client.log
#configured_logbook_func = partial(generic_logbook_func, logbooks=LOGBOOKS)

#cb = logbook_cb_factory(configured_logbook_func)
#RE.subscribe('start', cb)
#-------------------------------------------------------

