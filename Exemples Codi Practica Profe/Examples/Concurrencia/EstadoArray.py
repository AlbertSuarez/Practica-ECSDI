# -*- coding: utf-8 -*-
"""
filename: EstadoArray

Dis procesos que comparten un array de valores

Created on 12/02/2014

@author: javier
"""

__author__ = 'javier'

from multiprocessing import Process, Array
from ctypes import c_int


def proceso1(a):
    for i in range(0, 10, 2):
        a[i] = i * i


def proceso2(a):
    for i in range(1, 10, 2):
        a[i] = i * i


if __name__ == '__main__':
    arr = Array(c_int, 10)

    p1 = Process(target=proceso1, args=(arr,))
    p1.start()
    p2 = Process(target=proceso2, args=(arr,))
    p2.start()
    p1.join()
    p2.join()

    print arr[:]