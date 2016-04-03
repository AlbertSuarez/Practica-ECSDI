# -*- coding: utf-8 -*-
"""
filename: AgentBuscador

Agente que se registra como agente buscador de informacion

@author: javier
"""
__author__ = 'javier'

from multiprocessing import Process, Queue
import socket
import gzip
import argparse
import json

from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

from AgentUtil.OntoNamespaces import ACL, DSO, TIO, AMO
from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.Agent import Agent
from AgentUtil.Logging import config_logger
from AgentActividades import buscar_actividades
from AgentFlightsGoogle import buscar_vuelos
from AgentHotel import buscar_hoteles
from datetime import timedelta
import datetime
import logging

import pprint
from googleplaces import GooglePlaces, types, lang
from AgentUtil.APIKeys import GOOGLEAPI_KEY


#tiempo y listas que se usan para hacer control de cache
lastRequestFlightsTimestamp = datetime.datetime.fromtimestamp(0)
lastRequestHotelsTimestamp = datetime.datetime.fromtimestamp(0)
hotelconsult = {}
flightconsult= {}
activityconsult = []
# Definimos los parametros de la linea de comandos
parser = argparse.ArgumentParser()
parser.add_argument('--open', help="Define si el servidor esta abierto al exterior o no", action='store_true',
                    default=False)
parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
parser.add_argument('--dhost', default='localhost', help="Host del agente de directorio")
parser.add_argument('--dport', type=int, help="Puerto de comunicacion del agente de directorio")

# Logging
logger = config_logger(level=1)
#logging.basicConfig()

# parsing de los parametros de la linea de comandos
args = parser.parse_args()

# Configuration stuff
if args.port is None:
    port = 9003
else:
    port = args.port

plan_port = 9002


#hostname = socket.gethostname()
hostname = 'localhost'

if args.dport is None:
    dport = 9000
else:
    dport = args.dport

#dhostname = socket.gethostname()
dhostname = 'localhost'

# Flask stuff
app = Flask(__name__)

# Configuration constants and variables
agn = Namespace("http://www.agentes.org#")
nm = Namespace("http://www.agentes.org/actividades/")
myns = Namespace("http://my.namespace.org/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_act = Namespace("http://my.namespace.org/actividades/")
myns_lug = Namespace("http://my.namespace.org/lugares/")
myns_par = Namespace("http://my.namespace.org/parametros/")
# Contador de mensajes
mss_cnt = 0

# Datos del Agente
AgenteBuscador = Agent('AgentBuscador',
                  agn.AgentBuscador,
                  'http://%s:%d/comm' % (hostname, port),
                  'http://%s:%d/Stop' % (hostname, port))



# Datos del Agente
AgentePlanificador = Agent('AgentePlanificador',
                       agn.AgentePlanificador,
                       'http://%s:%d/comm' % (hostname, plan_port),
                       'http://%s:%d/Stop' % (hostname, plan_port))

# Global dsgraph triplestore
dsgraph = Graph()

# Cola de comunicacion entre procesos
cola1 = Queue()




@app.route("/iface", methods=['GET', 'POST'])
def browser_iface():
    """
    Permite la comunicacion con el agente via un navegador
    via un formulario
    """
    return 'Nothing to see here'


@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente

    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion del agente
    Simplementet retorna un objeto fijo que representa una
    respuesta a una busqueda de hotel

    Asumimos que se reciben siempre acciones que se refieren a lo que puede hacer
    el agente (buscar con ciertas restricciones, reservar)
    Las acciones se mandan siempre con un Request
    Prodriamos resolver las busquedas usando una performativa de Query-ref
    """
    global dsgraph
    global mss_cnt
    global hotelconsult
    global flightconsult
    global activityconsult
    global lastRequestHotelsTimestamp
    global lastRequestFlightsTimestamp
    #logger.info('Peticion de informacion recibida')
    print 'INFO AgentBuscador=> Peticion de informacion recibida\n'

    # Extraemos el mensaje y creamos un grafo con el
    message = request.args['content']
    print "INFO AgentBuscador => Mensaje extraído\n"
    # VERBOSE

    # Grafo en el que volcamos el contenido de la request
    gm = Graph()
    gm.parse(data=message)

    # Damos por supuesto que el sujeto es una peticion de actividad
    # En general habra que comprobar de que tipo es la peticion y hacer casos,
    # aunque creo que podemos poner todas las peticiones en un mosmo grafo
    # con diferentes sujetos (peticiones)

    # Propiedades del mensaje
    msgdic = get_message_properties(gm)
    # VERBOSE
    #print msgdic
    #print '\n\n'

    # Creo la lista de tipos con UN SOLO tipo
    # Habra que generalizar esto para mas de un tipo (o no)
    # Si lo hacemos, el planificador me tendra que pasar una list como parametro
    # VERBOSE
    #print "Lista append:"
    #print lista
    hotel = myns_pet.hotel
    busqueda = myns_pet.busqueda
    originCit = gm.value(subject= busqueda, predicate= myns_par.originCity)
    destinationCit = gm.value(subject= busqueda, predicate= myns_par.destinationCity)
    
    originVuelo="PRG"
    if str(originCit) == "Barcelona":
        originVuelo="BCN"
    elif str(originCit) == "Amsterdam":
        originVuelo="AMS"
    elif str(originCit) == "London":
        originVuelo="LON"
    elif str(originCit) == "Roma":
        originVuelo="ROM"
    elif str(originCit) == "Paris":
        originVuelo="PAR"

    destinationVuelo="BCN"
    destinationCountry="Spain"
    if str(destinationCit) == "Amsterdam":
        destinationVuelo="AMS"
        destinationCountry="Holland"
    elif str(destinationCit) == "London":
        destinationVuelo="LON"
        destinationCountry="United Kingdom"
    elif str(destinationCit) == "Roma":
        destinationVuelo="ROM"
        destinationCountry="Italy"
    elif str(destinationCit) == "Praha":
        destinationVuelo="PRG"
        destinationCountry="Czech Republic"
    elif str(destinationCit) == "Paris":
        destinationVuelo="PAR"
        destinationCountry="France"

    # Buscamos actividades en el metodo de AgentActividades
    print "INFO AgentBuscador => Looking for activities (in AgentActividades)..."
    requestTime=datetime.datetime.now()
    actividadesInt = gm.triples((None, myns_atr.tipo, None))
    gactividades = Graph()

    for s,p, o in actividadesInt:
        print o
        if o != None:
            ba = True
            if [destinationCountry,destinationCit, o] not in activityconsult:
                ba = False
                activityconsult.append([destinationCountry,destinationCit, o])
            gactividades += buscar_actividades(destinationCity=destinationCit, destinationCountry= destinationCountry, types= [o], cache = ba)

    print "INFO AgentBuscador => Activities found"
    #VERBOSE
    #Imprimimos el grafo de resultados para ver que pinta tiene
    #Realmente solo queremos devolverlo al planificador
    # for s, p, o in gactividades:
    #     print 's: ' + s
    #     print 'p: ' + p
    #     print 'o: ' + o
    #     print '\n'
    
    print "Buscamos hoteles"    


    departureDat=gm.value(subject= busqueda, predicate= myns_par.departureDate)

    returnDat=gm.value(subject= busqueda, predicate= myns_par.returnDate)

    propertyCategor=gm.value(subject= busqueda, predicate= myns_par.propertyCategory)

    b = True
    if lastRequestHotelsTimestamp == datetime.datetime.fromtimestamp(0) or requestTime - lastRequestHotelsTimestamp >= datetime.timedelta(minutes=15):
        b = False
    if (destinationCit, departureDat, returnDat, propertyCategor) != hotelconsult:
        b = False       
    if b == False :
        lastRequestHotelsTimestamp = requestTime
        hotelconsult = (destinationCit, departureDat, returnDat, propertyCategor)

    print "INFO AgentBuscador => Looking for hotels (in AgentHotel)..."


    ghoteles = buscar_hoteles(destinationCity = destinationCit,
                                destinationCountry = destinationCountry,
                               arrivalDate = departureDat,
                               departureDate = returnDat,
                               propertyCategory = propertyCategor,
                               cache = b)
    
    # Buscamos vuelos

    print "INFO AgentBuscador => Looking for flights (in AgentFlightsGoogle)..."
    maxPric=gm.value(subject= busqueda, predicate= myns_par.maxPrice)
    bf = True
    if lastRequestFlightsTimestamp == datetime.datetime.fromtimestamp(0) or requestTime - lastRequestFlightsTimestamp >= datetime.timedelta(minutes=5):
        bf = False
    if (originVuelo, destinationVuelo, departureDat, returnDat, maxPric) != flightconsult:
        bf = False
    if bf == False :
        lastRequestFlightsTimestamp = requestTime
        flightconsult = (originVuelo, destinationVuelo, departureDat, returnDat, maxPric)


    gvuelos = Graph()
    gvuelos = buscar_vuelos(origin=originVuelo, 
                            destination=destinationVuelo,
                            departureDate= departureDat, 
                            returnDate=returnDat,
                            maxPrice=maxPric, cache= bf)

    # Juntamos los tres grafos en una respuesta
    grespuesta = Graph()
    grespuesta = gvuelos + ghoteles + gactividades

    res_obj= agn['Buscador-responde']
    # Comprobamos que sea un mensaje FIPA ACL
    if msgdic is None:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = build_message(Graph(), ACL['not-understood'], sender=AgenteBuscador.uri, msgcnt=mss_cnt)
        print 'INFO AgentBuscador => El mensaje no era un FIPA ACL'
    else:
        # Obtenemos la performativa
        perf = msgdic['performative']

        if perf != ACL.request:
            # Si no es un request, respondemos que no hemos entendido el mensaje
            print "INFO AgentBuscador => No es una request FIPA ACL\n"
            gr = build_message(Graph(), ACL['not-understood'], sender=AgenteBuscador.uri, msgcnt=mss_cnt)
        else:
            # Extraemos el objeto del contenido que ha de ser una accion de la ontologia de acciones del agente
            # de registro

            # Averiguamos el tipo de la accion
            if 'content' in msgdic:
                content = msgdic['content']
                accion = gm.value(subject=content, predicate=RDF.type)

            # Aqui realizariamos lo que pide la accion
            # Retornamos un Inform-done con el grafo del resultado de la busqueda (grespuesta)
            gr = build_message(grespuesta,
                ACL['inform-done'],
                sender=AgenteBuscador.uri,
                msgcnt=mss_cnt,
                receiver=msgdic['sender'], 
                content=res_obj
                )

        mss_cnt += 1

    print 'INFO AgentBuscador => Respondemos a la peticion de busqueda'
    return gr.serialize(format='xml')


def tidyup():
    """
    Acciones previas a parar el agente

    """
    global cola1
    cola1.put(0)


def agentbehavior1(cola):
    """
    Un comportamiento del agente    port = 9001

    :return:
    """
    # Registramos el agente
    # gr = register_message()

    # Escuchando la cola hasta que llegue un 0
    fin = False
    while not fin:
        while cola.empty():
            pass
        v = cola.get()
        if v == 0:
            fin = True
        else:
            print v

            # Selfdestruct
            # requests.get(InfoAgent.stop)

#def buscar_vuelos():
def buscar_vuelos_ORIGINAL():

    g = Graph()

    # Carga el grafo RDF desde el fichero
    ontofile = gzip.open('../../FlightData/FlightRoutes.ttl.gz')
    g.parse(ontofile, format='turtle')

    # Consulta al grafo los aeropuertos dentro de la caja definida por las coordenadas
    qres = g.query(
        """
        prefix tio:<http://purl.org/tio/ns#>
        prefix geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
        prefix dbp:<http://dbpedia.org/ontology/>

        Select ?f
        where {
            ?f rdf:type dbp:Airport .
            ?f geo:lat ?lat .
            ?f geo:long ?lon .
            Filter ( ?lat < "41.7"^^xsd:float &&
                     ?lat > "41.0"^^xsd:float &&
                     ?lon < "2.3"^^xsd:float &&
                     ?lon > "2.0"^^xsd:float)
            }
        LIMIT 30
        """,
        initNs=dict(tio=TIO))

    # Recorre los resultados y se queda con el ultimo
    for r in qres:
        ap = r['f']

    print 'Aeropuerto:', ap
    print


    # Consulta todos los vuelos que conectan con ese aeropuerto
    airquery = """
        prefix tio:<http://purl.org/tio/ns#>
        Select *
        where {
            ?f rdf:type tio:Flight.
            ?f tio:to <%s>.
            ?f tio:from ?t.
            ?f tio:operatedBy ?o.
            }
        """ % ap

    qres = g.query(airquery, initNs=dict(tio=TIO))

    print 'Num Vuelos:', len(qres.result)
    print


    # Imprime los resultados
    for row in qres.result:
        print row

def buscar_transportes():
    g = Graph()

    # Carga el grafo RDF desde el fichero
    # Cambiar por RDF transportes
    # El fichero actual no esta en el mismo formato y no lo lee
    ontofile = gzip.open('../../TransportData/TransportRoutes.ttl.gz')
    g.parse(ontofile, format='turtle')

    # Consulta al grafo los aeropuertos dentro de la caja definida por las coordenadas
    qres = g.query(
        """
        prefix tio:<http://purl.org/tio/ns#>
        prefix geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
        prefix dbp:<http://dbpedia.org/ontology/>

        Select ?f
        where {
            ?f rdf:type dbp:Airport .
            ?f geo:lat ?lat .
            ?f geo:long ?lon .
            Filter ( ?lat < "41.7"^^xsd:float &&
                     ?lat > "41.0"^^xsd:float &&
                     ?lon < "2.3"^^xsd:float &&
                     ?lon > "2.0"^^xsd:float)
            }
        LIMIT 30
        """,
        initNs=dict(tio=TIO))

    # Recorre los resultados y se queda con el ultimo
    for r in qres:
        ap = r['f']

    print 'Aeropuerto:', ap
    print


    # Consulta todos los vuelos que conectan con ese aeropuerto
    airquery = """
        prefix tio:<http://purl.org/tio/ns#>
        Select *
        where {
            ?f rdf:type tio:Flight.
            ?f tio:to <%s>.
            ?f tio:from ?t.
            ?f tio:operatedBy ?o.
            }
        """ % ap

    qres = g.query(airquery, initNs=dict(tio=TIO))

    print 'Num Vuelos:', len(qres.result)
    print


    # Imprime los resultados
    for row in qres.result:
        print row    

if __name__ == '__main__':
    
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    #ab1.join()
    logger.info('The End')
