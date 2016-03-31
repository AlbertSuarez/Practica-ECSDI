"""
.. module:: OpenProductData

OpenProductData
*************

:Description: OpenProductData

   Base de datos de productos OpenProductData


   La documentacion de la API REST esta en:

   http://pod.opendatasoft.com/api/v1/documentation

   Se pueden hacer busquedas usando la entrada de la API

   http://pod.opendatasoft.com/api/records/1.0/search/

   La base de datos que contiene productos es 'pod_gtin' (el campo 'dataset')
   Se puede hacer consutas con texto libre usando el campo 'q' y obtener mas
   o menos respuestas con el campo 'rows'

   Se pueden hacer consultas interactivas para ver los campos que se pueden usar y otras opciones en la direccion:

    http://pod.opendatasoft.com/explore/dataset/pod_gtin/

:Authors: bejar

:Version: 

:Created on: 29/03/2016 14:30 

"""

__author__ = 'bejar'


import requests



OPD_ENDPOINT = 'http://pod.opendatasoft.com/api/records/1.0/search/'

# Cosas con 'fruit' en algun campo
r = requests.get(OPD_ENDPOINT,
                 params={'dataset':'pod_gtin', 'q': 'fruit', 'rows': 20
                        })
# Extraemos la respuesta json como un diccionario python
dic = r.json()

# La respuesta esta en el campo records
res = dic['records']

print len(res)

# La respuesta es una lista de objetos donde los datos de los productos estan en el campo 'fields'
for prod in res:
    pr = prod['fields']
    for p in  pr.keys():
        print p, pr[p]
    print '-----------------------------'


# Productos que tengan el texto 'Timberland' en algun campo dentro de la categoria 'Footwear'
r = requests.get(OPD_ENDPOINT,
                 params={'dataset':'pod_gtin', 'rows': 20, 'q': 'Timberland',
                         'refine.gpc_s_nm': 'Footwear'
                        })

dic = r.json()
res = dic['records']

print len(res)

for prod in res:
    pr = prod['fields']
    for p in pr.keys():
        print p, pr[p]
    print '-----------------------------'
