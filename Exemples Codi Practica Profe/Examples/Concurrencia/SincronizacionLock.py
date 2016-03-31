# -*- coding: utf-8 -*-
"""
filename: SincronizacionLock

Escritura exclusiva en un recurso compartido

Created on 12/02/2015

@author: javier
"""

__author__ = 'javier'

from multiprocessing import Process, Array, Lock
from ctypes import c_int


def proceso1(a, l):
    l.acquire()
    print a[:]
    for i in range(0, 10, 2):
        a[i] = i * i
    l.release()


def proceso2(a, l):
    l.acquire()
    print a[:]
    for i in range(1, 10, 2):
        a[i] = i * i
    l.release()


if __name__ == '__main__':
    arr = Array(c_int, 10)
    l = Lock()
    p1 = Process(target=proceso1, args=(arr, l,))
    p2 = Process(target=proceso2, args=(arr, l,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print arr[:]