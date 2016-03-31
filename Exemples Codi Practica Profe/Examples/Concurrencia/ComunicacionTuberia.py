# -*- coding: utf-8 -*-
"""
filename: CominicacionTuberia


Dos procesos que se comunican entre si a traves de una tuberia

Created on 12/02/2014

@author: javier
"""

__author__ = 'javier'

from multiprocessing import Process, Pipe


def proceso1(conn1, conn2):
    for i in range(100):
        conn1.send(i)
        print conn2.recv(), 'P1:'
    conn1.close()


def proceso2(conn1, conn2):
    for i in range(100):
        conn2.send(i)
        print conn1.recv(), 'P2:'
    conn1.close()


if __name__ == '__main__':
    conn1, conn2 = Pipe()
    p1 = Process(target=proceso1, args=(conn1, conn2,))
    p2 = Process(target=proceso2, args=(conn1, conn2,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
