from sys import modules

full_precision_mode = False

def enable_full_precision_mode(state):
    global full_precision_mode
    if full_precision_mode != state:
        full_precision_mode = state
        par_name = '.'.join(__name__.split('.')[:-1])
        for name in [name for name in modules if name.startswith(par_name) and name != __name__]:
            del modules[name]
