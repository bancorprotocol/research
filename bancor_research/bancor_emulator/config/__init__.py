from sys import modules

FIXED_POINT_MODE = 0
FLOAT_POINT_MODE = 1

mode = FIXED_POINT_MODE

def set_mode(new_mode):
    global mode
    if mode != new_mode:
        mode = new_mode
        for name in [name for name in modules if 'bancor_emulator' in name]:
            del modules[name]
