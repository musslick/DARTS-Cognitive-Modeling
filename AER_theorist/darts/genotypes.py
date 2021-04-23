from collections import namedtuple

Genotype = namedtuple('Genotype', 'normal normal_concat')


PRIMITIVES = [  
    'none',
    'add',
    'subtract',
    'linear',
    'sigmoid',
    'mult',
    'exp',
    'relu',
]