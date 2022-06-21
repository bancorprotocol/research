def library(globalVars, classHandle):
    for varName in globalVars.keys():
        if not varName.startswith('__'):
            setattr(classHandle, varName, globalVars[varName])
