from sys import modules

full_precision_mode = False

def enable_full_precision_mode(state):
    global full_precision_mode
    if full_precision_mode != state:
        full_precision_mode = state
        for name in [name for name in modules if 'bancor_emulator' in name and 'config' not in name]:
            del modules[name]
