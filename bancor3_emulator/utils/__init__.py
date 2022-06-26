from inspect import currentframe

def library(globalVars, classHandle):
    for varName in vars(classHandle):
        if not varName.startswith('__'):
            setattr(classHandle, varName, globalVars[varName])

class account:
    def __init__(self):
        self._msg_sender = None

    def connect(self, _msg_sender):
        self._msg_sender = _msg_sender
        return self

    def msg_sender(self):
        f_locals = currentframe().f_back.f_back.f_locals
        return f_locals['self'] if 'self' in f_locals else self._msg_sender
