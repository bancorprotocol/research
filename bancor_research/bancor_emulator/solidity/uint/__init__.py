from bancor_research.bancor_emulator import config

match config.mode:
    case config.FIXED_POINT_MODE: from . fixed import *
    case config.FLOAT_POINT_MODE: from . float import *
