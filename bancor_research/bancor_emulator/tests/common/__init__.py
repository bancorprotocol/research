from os.path import join, dirname
from json import loads, dumps

def read(fileName):
    file = open(_getPath(fileName), 'r')
    data = loads(file.read())
    file.close()
    return data

def write(fileName, data):
    file = open(_getPath(fileName), 'w')
    file.write(dumps(data, indent = 2))
    file.close()

def _getPath(fileName):
    return join(dirname(__file__), '..', 'project', 'tests', 'data', fileName + '.json')
