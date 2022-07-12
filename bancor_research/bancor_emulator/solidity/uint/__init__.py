from bancor_research.bancor_emulator.config import mode

exec('from . {} import *'.format(mode))