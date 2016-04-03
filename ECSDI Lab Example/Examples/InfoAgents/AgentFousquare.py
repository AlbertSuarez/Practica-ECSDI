# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Agente que responde a peticiones

Demo que hace una consulta a FourSquare con unas coordenadas dentro de Barcelona
en un area de 4Km a la redonda buscando museos

Se ha de crear un fichero python APIKeys.py que contenga la información para el
acceso a FourSquare (FQCLIENT_ID, FQCLIENT_SECRET)

@author: javier
"""
__author__ = 'javier'

import foursquare

from AgentUtil.APIKeys import FQCLIENT_ID, FQCLIENT_SECRET


CLIENT_ID = FQCLIENT_ID
CLIENT_SECRET = FQCLIENT_SECRET

# Se conecta a FQ con la información de acceso
client = foursquare.Foursquare(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# Hace la consulta a FQ
v = client.venues.search(params={'ll': '41.4,2.14', 'intent': 'browse', 'radius': '4000', 'query': 'museo'})

# De la respuesta imprime lo que hay en la clave 'venues' del diccionario respuesta
print len(v['venues'])


# Imprime información de cada uno de los lugares encontrados
for vn in v['venues']:
    print vn['name'],
    if len(vn['categories']) != 0:
        print vn['categories'][0]['name']

