esm_ui_config_file = "/home2/xf21id1/constructor/esm_usr1.ui"


def esm_gui(filename=esm_ui_config_file):
    # Note: install it in the developer mode with the following command before
    # it's packaged with conda
    #   $ cd /home2/xf21id1/git/bsstudio/
    #   $ pip install -e .
    import bsstudio
    import warnings
    #warnings.simplefilter("ignore")
    bsstudio.load(filename)
