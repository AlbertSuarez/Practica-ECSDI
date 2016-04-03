# -*- coding: utf-8 -*-
"""
filename: EstadoManager

Procesos que comparten datos con el Namespace de un manager

Created on 12/02/2014

@author: javier
"""

__author__ = 'javier'

from multiprocessing import Process, Manager, Lock


def proceso1(nsp, l):
    l.acquire()
    data = nsp.data
    a = ['a', 'b', 'c']
    for i, v in enumerate(a):
        data[v] = i
    nsp.data = data
    print nsp.data
    l.release()


def proceso2(nsp, l):
    l.acquire()
    data = nsp.data
    a = ['e', 'f', 'g']
    for i, v in enumerate(a):
        data[v] = i
    nsp.data = data
    print nsp.data
    l.release()


if __name__ == '__main__':
    shnsp = Manager().Namespace()
    l = Lock()

    shnsp.data = {}

    p1 = Process(target=proceso1, args=(shnsp, l,))
    p2 = Process(target=proceso2, args=(shnsp, l,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print shnsp.data

