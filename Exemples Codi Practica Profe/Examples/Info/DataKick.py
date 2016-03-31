"""
.. module:: DataKick

DataKicke
*************

:Description: DataKick

    Ejemplo de consulta del servicio datakick.org

    Provee la informacion a traves de un servicio REST

    Se puede consultar la API en https://www.datakick.org/api
    pero lo mas simple es utilizar el metodo:

    https://www.datakick.org/api/items?query=

    Que permite buscar entre los productos con un texto libre


:Authors: bejar
    

:Version: 

:Created on: 25/02/2016 15:58 

"""

import requests
from requests.exceptions import ReadTimeout
__author__ = 'bejar'

DATAKICK_ENDPOINT = 'https://www.datakick.org/api/items'

r = requests.get(DATAKICK_ENDPOINT,
                 params={'query':'oil'
                         })

dic = r.json()

for prod in dic:
    for p in  prod.keys():
        print p, prod[p]
    print '-----------------------------'