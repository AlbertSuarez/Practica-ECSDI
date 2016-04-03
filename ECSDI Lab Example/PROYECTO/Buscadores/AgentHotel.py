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
from AgentUtil.APIKeys import EAN_DEV_CID, EAN_KEY, EAN_SECRET

from AgentUtil.Agent import Agent
import socket
from rdflib import Graph, Namespace, Literal
import datetime

# Nuestros namespaces que usaremos luego
agn = Namespace("http://www.agentes.org#")
myns = Namespace("http://my.namespace.org/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_hot = Namespace("http://my.namespace.org/hoteles/")

# Configuration stuff
port = 9004
hostname = socket.gethostname()

CACHE_TIME_CONST = 1
LOG_TAG = "DEBUG AgentHotel => "
# Datos del Agente
AgenteHotel = Agent('AgentHotel',
                  agn.AgentHotel,
                  'http://%s:%d/comm' % (hostname, port),
                  'http://%s:%d/Stop' % (hostname, port))

# COMMON QUERY PARAMS
service = 'http://api.ean.com/ean-services/rs/hotel/'
version = 'v3/'
method = 'list'
EAN_END_POINT = service + version + method
minorRev = 29

# GENERATE SECRET FOR QUERY
hash = md5.new()
# seconds since GMT Epoch
timestamp = str(int(time.time()))
# print timestamp
sig = md5.new(EAN_KEY + EAN_SECRET + timestamp).hexdigest()
# print "Sig has ", sig.__len__(), " charachters"

# Formato Datetime
# defaultArrDate = datetime.strptime("08/20/2015", '%m/%d/%Y')
# defaultDepDate = datetime.strptime("08/30/2015", '%m/%d/%Y')

def buscar_hoteles(destinationCity="Barcelona", destinationCountry="Spain", 
  searchRadius=5, arrivalDate="2015-8-20", departureDate="2015-8-30", 
  numberOfAdults=1, numberOfChildren=0, propertyCategory=1, requestTime=datetime.datetime.fromtimestamp(0)):
  #Values: 1: hotel 2: suite 3: resort 4: vacation rental/condo 5: bed & breakfast 6: all-inclusive
  print destinationCity
  print destinationCountry
  print arrivalDate
  print departureDate
  print LOG_TAG+"looking for hotels"
  arrivaldepD = datetime.datetime.strptime(arrivalDate, '%Y-%m-%d')
  arrivaldepDStr = arrivaldepD.strftime("%m/%d/%Y")

  departuredepD = datetime.datetime.strptime(departureDate, '%Y-%m-%d')
  departuredepDStr = departuredepD.strftime("%m/%d/%Y")

  gresp = Graph()
  # COORDINATES OF THE DESTINATION

  print LOG_TAG+"checking cache"
  tDelta = datetime.datetime.now() - requestTime
  days, seconds = tDelta.days, tDelta.seconds
  hours = days * 24 + seconds // 3600
  minutes = (seconds % 3600) // 60
  seconds = seconds % 60
  print LOG_TAG+"resolving timestamp"
  b = (minutes < CACHE_TIME_CONST)
  b = True
  if b == False:
    print "AgentHotel => We make a new service request; cant rely on cache"
    geolocator = Nominatim()
    location = geolocator.geocode(destinationCity + ", " + destinationCountry)
    print ((location.latitude, location.longitude))
    print
  
    r = requests.get(EAN_END_POINT,
                     params={'cid': EAN_DEV_CID,
                     		'minorRev': minorRev,
                     		'apiKey': EAN_KEY,
                     		'sig': sig,
                     		'locale': 'es_ES',
                     		'currencyCode': 'EUR',
                     		'numberOfResults': 10,
                     		'latitude': location.latitude,
                     		'longitude': location.longitude,
                            'searchRadius': searchRadius,
                            'searchRadiusUnit': "KM",
                            'arrivalDate': arrivaldepDStr,
                            'departureDate': departuredepDStr,
                            'numberOfAdults': numberOfAdults,
                            'numberOfChildren': numberOfChildren,
                            'propertyCategory': propertyCategory  
                        	})

    #print r.text
    dic = r.json()
    out_file = open("h.json","w")

# Save the dictionary into this file
# (the 'indent=4' is optional, but makes it more readable)
    json.dump(dic,out_file, indent=4) 
    #print json.dumps(dic, indent=4, sort_keys=True)

    # Hago bind de las ontologias que usaremos en el grafo
    gresp.bind('myns_pet', myns_pet)
    gresp.bind('myns_atr', myns_atr)
    gresp.bind('myns_hot', myns_hot)

    if 'EanWsError' in dic['HotelListResponse']:
    	print ('Error de tipo ' + dic['HotelListResponse']['EanWsError']['category'], 
        ' => ' + dic['HotelListResponse']['EanWsError']['verboseMessage'])
      #gresp = build_message(Graph(), ACL['not-understood'], sender=AgentHotel.uri)
    else:
      for hot in dic['HotelListResponse']['HotelList']['HotelSummary']:
    	 # print ("Hotel " + hot['name'],
    	 # 	", distancia del centro: " + '{:.2f}'.format(hot['proximityDistance']),
    	 # 	' ' + hot['proximityUnit'] + ', precio total: ',
    	 # 	hot['RoomRateDetailsList']['RoomRateDetails']['RateInfos']['RateInfo']['ChargeableRateInfo']['@total'],
    	 # 	', rating: ' + '{:.1f}'.format(hot['hotelRating']),
    	 # 	', tripAdvisorRating: ' + '{:.1f}'.format(hot['tripAdvisorRating']),
    	 # 	' tripAdvisorReviewCount: ' + '{:.0f}'.format(hot['tripAdvisorReviewCount'])
    	 # 	)
        hot_obj = myns_hot[hot['hotelId']]
        gresp.add((hot_obj, myns_atr.esUn, myns.hotel))
        gresp.add((hot_obj, myns_atr.codigoPostal, Literal(hot['postalCode'])))
        gresp.add((hot_obj, myns_atr.descripcionDeHabitacion, Literal(hot['RoomRateDetailsList']['RoomRateDetails']['roomDescription'])))
        gresp.add((hot_obj, myns_atr.adresa, Literal(hot['address1'])))
        gresp.add((hot_obj, myns_atr.nombre, Literal(hot['name'])))
        gresp.add((hot_obj, myns_atr.descriptionCorta, Literal(hot['shortDescription'])))
        gresp.add((hot_obj, myns_atr.distanciaRepectoAlCentro, Literal(hot['proximityDistance'])))
        gresp.add((hot_obj, myns_atr.distanciaRepectoAlCentro_unidad, Literal(hot['proximityUnit'])))
        gresp.add((hot_obj, myns_atr.cuesta, Literal(hot['RoomRateDetailsList']['RoomRateDetails']['RateInfos']['RateInfo']['ChargeableRateInfo']['@total'])))
        gresp.add((hot_obj, myns_atr.rating, Literal(hot['hotelRating'])))
        gresp.add((hot_obj, myns_atr.tripAdvisorRating, Literal(hot['tripAdvisorRating'])))
        gresp.add((hot_obj, myns_atr.tripAdvisorReviewCount, Literal(hot['tripAdvisorReviewCount'])))
        gresp.serialize('h.rdf')
  else: 
    print "AgentHotel => We read from cache"
    gresp.parse('h.rdf' ,format='xml')
  print "retornar repuesta"
  return gresp




