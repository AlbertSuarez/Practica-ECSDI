# -*- coding: utf-8 -*-
"""
File: AgentUtil

Created on 31/01/2014 9:31

Diferentes funciones comunes a los agentes implementados en ECSDI

@author: bejar

"""

__author__ = 'bejar'

from flask import request


def shutdown_server():
    """
    Funcion que para el servidor web

    :raise RuntimeError:
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


