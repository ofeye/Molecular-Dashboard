import numpy as np
import math


def my_floor(a, precision=0):
    return np.true_divide(np.floor(a * 10**precision), 10**precision)

def my_ceil(a, precision=0):
    return np.round(a + 0.5 * 10**(-precision), precision)

def my_ceil_2(a):
    return math.log10(my_ceil(a,int(my_ceil(abs(math.log10(a))))))

def my_floor_2(a):
    return math.log10(my_floor(a,int(my_ceil(abs(math.log10(a))))))