from config import mode

exec('from . {} import *'.format(mode))