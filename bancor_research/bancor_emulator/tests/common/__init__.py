from os.path import join, dirname
from json import loads, dumps
from bancor_research import Decimal

def read(fileName):
    file = open(_getPath(fileName), mode = 'r', newline = '\n')
    data = loads(file.read())
    file.close()
    return data

def write(fileName, data):
    file = open(_getPath(fileName), mode = 'w', newline = '\n')
    file.write(dumps(data, indent = 4))
    file.close()

def _getPath(fileName):
    return join(dirname(__file__), '..', '..', '..', '..', 'regression', 'data', fileName + '.json')

def assertAlmostEqual(expected, actual, maxAbsoluteError = 0, maxRelativeError = 0, relation = None):
    expected = Decimal(expected)
    actual = Decimal(actual)
    if actual.compare_total(expected):
        absoluteError = abs(actual - expected)
        relativeError = absoluteError / expected
        maxAbsoluteError = Decimal(maxAbsoluteError)
        maxRelativeError = Decimal(maxRelativeError)
        assert not relation or relation(actual, expected)
        assert absoluteError <= maxAbsoluteError or relativeError <= maxRelativeError

LesserOrEqual = Decimal.__le__
GreaterOrEqual = Decimal.__ge__
