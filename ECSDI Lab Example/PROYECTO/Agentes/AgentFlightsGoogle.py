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

import json
import requests
import urllib2
import md5
import time
from geopy.geocoders import Nominatim
from AgentUtil.APIKeys import QPX_API_KEY

from flask import Flask, request
from rdflib import Graph, Namespace, Literal, URIRef
import datetime
from rdflib.plugins.stores import sparqlstore
CACHE_TIME_CONST = 1
# Nuestros namespaces que usaremos luego
myns = Namespace("http://my.namespace.org/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_rndtrp = Namespace("http://my.namespace.org/roundtrips/")
myns_vlo = Namespace("http://my.namespace.org/vuelos/")

# COMMON QUERY PARAMS
#QPX_END_POINT = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
QPX_END_POINT = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
headers = {'content-type': 'application/json'}

#Ejemplo de una respuesta. No se usa ahora, borrar después


# Formato Datetime
# defaultDepDate = datetime.strptime("2015-08-20", '%Y-%m-%d')
# defaultRetDate = datetime.strptime("2015-08-30", '%Y-%m-%d')

def buscar_vuelos(adultCount=1, childCount=0, origin="BCN", destination="ROM",
  departureDate="2015-08-20", returnDate="2015-08-30", solutions=50,
  maxPrice=500, earliestDepartureTime="06:00", latestDepartureTime="23:00",
  earliestReturnTime="06:00", latestReturnTime="23:00", cache = False):

  print "origin: " + origin
  print "destination: " + destination
  print "departureDate: " + departureDate
  print "returnDate: " + returnDate

  maxPriceStr = "EUR" + str(maxPrice)

  payload = {
    "request": {
      "slice": [
        {
          "origin": origin,
          "destination": destination,
          "date": departureDate,
          "permittedDepartureTime": {
            "earliestTime": earliestDepartureTime,
            "latestTime": latestDepartureTime
          }
        },
        {
          "origin": destination,
          "destination": origin,
          "date": returnDate,
          "permittedDepartureTime": {
            "earliestTime": earliestReturnTime,
            "latestTime": latestReturnTime
          }
        }
      ],
      "passengers": {
        "adultCount": adultCount,
        "infantInLapCount": 0,
        "infantInSeatCount": 0,
        "childCount": childCount,
        "seniorCount": 0
      },
      "solutions": solutions,
      "maxPrice": maxPriceStr,
      "refundable": False
    }
  }
  gresp = Graph()
  #print payload
  # tDelta = datetime.datetime.now() - requestTime
  # days, seconds = tDelta.days, tDelta.seconds
  # hours = days * 24 + seconds // 3600
  # minutes = (seconds % 3600) // 60
  # seconds = seconds % 60
  # b = (minutes < CACHE_TIME_CONST)
  b = cache
  if b == False:
    print "AgentFlightsGoogle => We make a new service request; cant rely on cache"
    r = requests.post(QPX_END_POINT, params={'key': QPX_API_KEY}, data=json.dumps(payload), headers=headers)
    #print r.text

    dic = r.json()
    out_file = open("test.json","w")

  # Save the dictionary into this file
  # (the 'indent=4' is optional, but makes it more readable)
    json.dump(dic,out_file, indent=4) 
    #print json.dumps(dic, indent=4, sort_keys=True)

    # Si quiero imprimir la respuesta pretty
    # for trip in dic['trips']['tripOption']:
    #     print "=========================> Total price: " + trip['saleTotal']
    #     sliceCount = 0
    #     for _slice in trip['slice']:
    #         print "## In slice => ", sliceCount
    #         print "Duration: ", _slice['duration']
    #         segmentCount = 0
    #         for segment in _slice['segment']:
    #             print "###### In segment => ", segmentCount
    #             print ("Flight number: " + segment['flight']['number'] +
    #                 ", flignt carrier: " + segment['flight']['carrier'])
    #             legCount = 0
    #             for leg in segment['leg']:
    #                 print "########## In leg => ", legCount
    #                 print ("From " + leg['origin'] + " to " + leg['destination'])
    #                 print ("Dep. time: " + leg['departureTime'] +
    #                     " from terminal " + leg['originTerminal'])
    #                 print ("Arr. time: " + leg['arrivalTime'] +
    #                     " to terminal " + leg['destinationTerminal'])
    #                 legCount += 1
    #             segmentCount += 1
    #         sliceCount += 1


    # Hago bind de las ontologias que usaremos en el grafo
    gresp.bind('myns_pet', myns_pet)
    gresp.bind('myns_atr', myns_atr)
    gresp.bind('myns_rndtrp', myns_rndtrp)
    gresp.bind('myns_vlo', myns_vlo)
    gresp.bind('myns', myns)

    i = 0
    print len(dic['trips']['tripOption'])
    # TODO: ANADIR TIPO DE ACTIVIDAD PARA RECORRER EL GRAFO
    for trip in dic['trips']['tripOption']:
        # Identificador unico para cada roundtrip
        i+= 1

        rndtrip_obj = myns_rndtrp[unicode(trip['id'])]
        # Precio del roundtrip
        gresp.add((rndtrip_obj, myns_atr.esUn, myns.viaje))
        gresp.add((rndtrip_obj, myns_atr.cuesta, Literal(trip['saleTotal'])))
        

        # DATOS IDA
        # Id unico para la ida del roundtrip
        idGo = trip['slice'][0]['segment'][0]['flight']['number'] +trip['slice'][0]['segment'][0]['flight']['carrier']
        vlo_obj_go = myns_vlo[idGo]
        # El roundtrip tiene esta ida
        gresp.add((rndtrip_obj, myns_atr.ida, vlo_obj_go))
        # La ida dura esto
        durationGo = trip['slice'][0]['duration']

        originid = trip['slice'][0]['segment'][0]['leg'][0]['origin']

        #este puede ser code
        Gonameid = [x['code'] for x in dic['trips']['data']['airport']].index(originid)
        Goairname = dic['trips']['data']['airport'][Gonameid]['name']

        destinationid = trip['slice'][0]['segment'][0]['leg'][0]['destination']
        
        #este puede ser code
        Gonameid = [x['code'] for x in dic['trips']['data']['airport']].index(destinationid)
        Goairllname = dic['trips']['data']['airport'][Gonameid]['name']


        gresp.add((vlo_obj_go, myns_atr.airportSalida, Literal(Goairname)))
        gresp.add((vlo_obj_go, myns_atr.airportLlegada, Literal(Goairllname)))
        

        gresp.add((vlo_obj_go, myns_atr.dura, Literal(durationGo)))
        # Fecha y hora de salida y aterrizaje de la ida
        horaGoSale = trip['slice'][0]['segment'][0]['leg'][0]['departureTime']
        horaGoLlega = trip['slice'][0]['segment'][0]['leg'][0]['arrivalTime']
        gresp.add((vlo_obj_go, myns_atr.hora_sale, Literal(horaGoSale)))
        gresp.add((vlo_obj_go, myns_atr.hora_llega, Literal(horaGoLlega)))
        # Terminal y ciudad de salida de la ida

        terminalGoSale = "unknown"
        if 'originTerminal' in trip['slice'][0]['segment'][0]['leg'][0]:
          terminalGoSale = trip['slice'][0]['segment'][0]['leg'][0]['originTerminal']

        terminalGoLlega = "unknown"
        if 'destinationTerminal' in trip['slice'][0]['segment'][0]['leg'][0]:
          terminalGoLlega = trip['slice'][0]['segment'][0]['leg'][0]['destinationTerminal']
        
        gresp.add((vlo_obj_go, myns_atr.terminal_sale, Literal(terminalGoSale)))
        gresp.add((vlo_obj_go, myns_atr.terminal_llega, Literal(terminalGoLlega)))
        # Direccion de la ida (redundante)
        ciudadGoSale = trip['slice'][0]['segment'][0]['leg'][0]['origin']
        ciudadGoLlega = trip['slice'][0]['segment'][0]['leg'][0]['destination']
        gresp.add((vlo_obj_go, myns_atr.ciudad_sale, Literal(ciudadGoSale)))
        gresp.add((vlo_obj_go, myns_atr.ciudad_llega, Literal(ciudadGoLlega)))

        # DATOS VUELTA
        # Id unico para la vuelta del roundtrip
        idBack = trip['slice'][1]['segment'][0]['flight']['number'] +trip['slice'][1]['segment'][0]['flight']['carrier']
        vlo_obj_back = myns_vlo[idBack]
        # El roundtrip tiene esta vuelta
        gresp.add((rndtrip_obj, myns_atr.vuelta, vlo_obj_back))

        originid = trip['slice'][1]['segment'][0]['leg'][0]['origin']
        #este puede ser code
        Gonameid = [x['code'] for x in dic['trips']['data']['airport']].index(originid)
        Goairname = dic['trips']['data']['airport'][Gonameid]['name']

        destinationid = trip['slice'][1]['segment'][0]['leg'][0]['destination']
        #este puede ser code
        Gonameid = [x['code'] for x in dic['trips']['data']['airport']].index(destinationid)
        Goairllname = dic['trips']['data']['airport'][Gonameid]['name']


        gresp.add((vlo_obj_back, myns_atr.airportSalida, Literal(Goairname)))
        gresp.add((vlo_obj_back, myns_atr.airportLlegada, Literal(Goairllname)))


        # Cuanto dura esta vuelta
        durationBack = trip['slice'][1]['duration']
        gresp.add((vlo_obj_back, myns_atr.dura, Literal(durationBack)))
        # Fecha y hora de salida y aterrizaje de la vuelta
        horaBackSale = trip['slice'][1]['segment'][0]['leg'][0]['departureTime']
        horaBackLlega = trip['slice'][1]['segment'][0]['leg'][0]['arrivalTime']
        gresp.add((vlo_obj_back, myns_atr.hora_sale, Literal(horaBackSale)))
        gresp.add((vlo_obj_back, myns_atr.hora_llega, Literal(horaBackLlega)))
        # Terminal y ciudad de salida de la vuelt
        terminalBackSale = "unknown"
        if 'originTerminal' in trip['slice'][1]['segment'][0]['leg'][0]:
          terminalBackSale = trip['slice'][1]['segment'][0]['leg'][0]['originTerminal']

        terminalBackLlega = "unknown"
        if 'destinationTerminal' in trip['slice'][1]['segment'][0]['leg'][0]:
          terminalBackLlega = trip['slice'][1]['segment'][0]['leg'][0]['destinationTerminal']

        gresp.add((vlo_obj_back, myns_atr.terminal_sale, Literal(terminalBackSale)))
        gresp.add((vlo_obj_back, myns_atr.terminal_llega, Literal(terminalBackLlega)))
        # Direccion de la vuelta (redundante)
        ciudadBackSale = trip['slice'][1]['segment'][0]['leg'][0]['origin']
        ciudadBackLlega = trip['slice'][1]['segment'][0]['leg'][0]['destination']
        gresp.add((vlo_obj_back, myns_atr.ciudad_sale, Literal(ciudadBackSale)))
        gresp.add((vlo_obj_back, myns_atr.ciudad_llega, Literal(ciudadBackLlega)))
    
    endpoint = 'http://localhost:5820/flight/query'
    store = sparqlstore.SPARQLUpdateStore()
    store.open((endpoint, endpoint))
    default_graph = URIRef('http://example.org/default-graph')
    ng = Graph(store, identifier=default_graph)
    ng = ng.update(u'INSERT DATA { %s }' % gresp.serialize(format='nt'))
    gresp.serialize('f.rdf')
  else:
    print "AgentFlightsGoogle => We read from cache"
  # print "GRAFO DE RESPUESTA"
  # for s, p, o in gresp:
  #   print 's: ' + s
  #   print 'p: ' + p
  #   print 'o: ' + o
  #   print '\n'
    endpoint = 'http://localhost:5820/flight/query'
    store = sparqlstore.SPARQLUpdateStore()
    store.open((endpoint, endpoint))
    default_graph = URIRef('http://example.org/default-graph')
    ng = Graph(store, identifier=default_graph)
    gresp = ng
    #gresp.parse('f.rdf' ,format='xml')

  print "repuesta"
  return gresp


