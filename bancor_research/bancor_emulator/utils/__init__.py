import inspect

def library(globalVars, classHandle):
    for varName in vars(classHandle):
        if not varName.startswith('__'):
            setattr(classHandle, varName, globalVars[varName])

def using(libraryHandle, classHandle):
    for varName in vars(libraryHandle):
        if not varName.startswith('__'):
            setattr(classHandle, varName, getattr(libraryHandle, varName))

def parse(cast, var, attr):
    if hasattr(var, attr):
        return cast(getattr(var, attr))
    if type(var) is dict:
        return cast(var[attr])
    if var is not None:
        return cast(var)
    return cast(0)

class contract:
    def __init__(self):
        self._msg_sender = None

    def connect(self, _msg_sender):
        self._msg_sender = _msg_sender
        return self

    @property
    def msg_sender(self):
        f_locals = inspect.currentframe().f_back.f_back.f_locals
        return f_locals['self'] if 'self' in f_locals and isinstance(f_locals['self'], contract) else self._msg_sender
