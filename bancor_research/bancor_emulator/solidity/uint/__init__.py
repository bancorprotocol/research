from bancor_research.bancor_emulator import config

exec('from . {} import *'.format(config.mode))