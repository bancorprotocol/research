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

from bancor_research.bancor_emulator.solidity.uint.float import Decimal

def assertAlmostEqual(expected, actual, maxAbsoluteError = 0, maxRelativeError = 0, relation = None):
    expected = Decimal(expected)
    actual = Decimal(actual)
    if actual != expected:
        absoluteError = abs(actual - expected)
        relativeError = absoluteError / expected
        maxAbsoluteError = Decimal(maxAbsoluteError)
        maxRelativeError = Decimal(maxRelativeError)
        assert not relation or relation(actual, expected)
        assert absoluteError <= maxAbsoluteError or relativeError <= maxRelativeError

LesserOrEqual = Decimal.__le__
GreaterOrEqual = Decimal.__ge__
