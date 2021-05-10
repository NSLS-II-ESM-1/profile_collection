#esm_ui_config_file = "/home2/xf21id1/constructor/esm_usr1.ui"
sys.path.insert(0,'/home2/xf21id1/PEAK-notebooks-alpha13/PythonNotebooks/')
esm_ui_config_file = "/opt/bsstudio/bsstudio-xf/21id/esm_usr1.ui"

def update_gui():
    import os
    os.system("git -C /opt/bsstudio/bsstudio-xf pull")
    os.system("git -C /home2/xf21id1/git/bsstudio pull")
    #os.system("git -C /home2/xf21id1/git/bsstudio-xf pull")

def esm_gui1(filename=esm_ui_config_file, detached=False, verbose=False):
    # Note: install it in the developer mode with the following command before
    # it's packaged with conda
    #   $ cd /home2/xf21id1/git/bsstudio/
    #   $ pip install -e .
    import os
    os.environ["BSSTUDIO_LOG_FILE_NAME"] = "/var/log/bsstudio/bsstudio.log"
    import sys
    sys.path.append("/home2/xf21id1/git/bsstudio/")
    import bsstudio
    import warnings
    #warnings.simplefilter("ignore")
    bsstudio.load(filename, noexec=detached, verbose=verbose)

def esm_gui(filename=esm_ui_config_file, detached=False, verbose=False):
    #import cProfile
    #cProfile.run("esm_gui1('"+filename+"')", "profile_results")
    esm_gui1(filename, detached=detached, verbose=verbose)

def gui_designer():
    import os
    os.system("/opt/bsstudio/gui_designer.sh")

def bsstudio_profile_results():
    import pstats
    p = pstats.Stats('profile_results')
    p.sort_stats('cumulative').print_stats(10)
