# -*- coding: utf-8 -*-
"""
filename: ComunicacionCola

Un subproceso qeu se comunica con el proceso principal con una cola

Created on 12/02/2014
"""

__author__ = 'javier'

from multiprocessing import Process, Queue
import time


def cuenta(q):
    time.sleep(1)
    while q.empty():
        pass
    while not q.empty():
        print q.get(timeout=0.3)
        time.sleep(1)


if __name__ == '__main__':
    q = Queue()
    p = Process(target=cuenta, args=(q,))
    p.start()
    for i in range(10):
        q.put(i)
    p.join()
