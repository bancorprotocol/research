from bancor_research.bancor_emulator import config

if config.full_precision_mode:
    from . float import *
else:
    from . fixed import *
