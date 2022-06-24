def library(globalVars, classHandle):
    for varName in vars(classHandle):
        if not varName.startswith('__'):
            setattr(classHandle, varName, globalVars[varName])
