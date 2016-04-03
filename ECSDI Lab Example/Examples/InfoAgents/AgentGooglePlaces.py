# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Agente que responde a peticiones

Demo que hace una consulta a Google Places con las coordenadas que le asigna el
servicio de geolocalizacion a Barcelona en un area de 300m a la redonda buscando estaciones
de metro (categorizadas como 'bus_station')

Se ha de crear un fichero python APIKeys.py que contenga la información para el
acceso a las APIs de Google (GOOGLEAPI_KEY)

@author: javier
"""
__author__ = 'javier'

import pprint
from googleplaces import GooglePlaces
from AgentUtil.APIKeys import GOOGLEAPI_KEY


google_places = GooglePlaces(GOOGLEAPI_KEY)

query_result = google_places.nearby_search(
    location=u'Barcelona, España', keyword='metro',
    radius=300, types=['bus_station'])

# Imprimimos informacion de los resultados
print query_result
if query_result.has_attributions:
    print query_result.html_attributions

for place in query_result.places:
    # Returned places from a query are place summaries.
    print place.name
    print place.geo_location
    print place.reference

    # The following method has to make a further API call.
    place.get_details()
    # Referencing any of the attributes below, prior to making a call to
    # get_details() will raise a googleplaces.GooglePlacesAttributeError.
    pprint.pprint(place.details)  # A dict matching the JSON response from Google.
    print place.local_phone_number

