# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Demo de consulta del servicio de hoteles ean.com

Para poder usarlo hay que registrarse y obtener una clave de desarrollador en  la direccion

https://devsecure.ean.com/member/register

Se ha de crear un fichero python APIKeys.py que contenga la información para el
acceso a EAN (EANCID, EANKEY)


@author: javier
"""

__author__ = 'javier'

import requests
from AgentUtil.APIKeys import EANCID, EANKEY


EAN_END_POINT = 'http://dev.api.ean.com/ean-services/rs/hotel/v3/list'

# Hacemos la peticion GET a la entrada del servicio REST
# Horteles en coordenadas de Barcelona en un radio de 2Km a la redonda
# 10 resultados con fecha de llegada 1 de febrero y salida 5 de febrero
# La fecha esta en formato ingles MM/DD/YYYY
# No se pueden hacer consultas con mas de un mes de antelacion
r = requests.get(EAN_END_POINT,
                 params={'apiKey': EANKEY, 'cid': EANCID, 'numberOfResults': 10,
                         'latitude': '041.40000', 'longitude': '002.16000',
                         'searchRadius': 2, 'searchRadiusUnit': 'KM',
                         'arrivalDate': '02/01/2015', 'departureDate': '02/05/2015'
                         })

# Generamos un diccionario python de la respuesta en JSON
dic = r.json()


# Imprimimos la informacion del nombre de los hores de los resultados
for hot in dic['HotelListResponse']['HotelList']['HotelSummary']:
    print hot['name']
