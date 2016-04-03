# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Esqueleto de agente usando los servicios web de Flask

/comm es la entrada para la recepcion de mensajes del agente
/Stop es la entrada que para el agente

Tiene una funcion AgentBehavior1 que se lanza como un thread concurrente

Asume que el agente de registro esta en el puerto 9000

@author: javier
"""

__author__ = 'javier'

from multiprocessing import Process, Queue
import socket

from rdflib import Graph, Namespace, Literal
from flask import Flask, request

from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.Agent import Agent
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.OntoNamespaces import ACL, DSO
from rdflib.namespace import FOAF
from AgentUtil.Logging import config_logger
from googleplaces import types
import json
import logging
from datetime import datetime, timedelta
# Configuration stuff
hostname = 'localhost' 
port = 9002
bus_port = 9003


agn = Namespace("http://www.agentes.org#")
myns = Namespace("http://my.namespace.org/")
myns_data = Namespace("http://my.namespace.org/fechas/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_par = Namespace("http://my.namespace.org/parametros/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_act = Namespace("http://my.namespace.org/actividades/")


# Contador de mensajes
mss_cnt = 0

# Datos del Agente
AgentePlanificador = Agent('AgentePlanificador',
                       agn.AgentePlanificador,
                       'http://%s:%d/comm' % (hostname, port),
                       'http://%s:%d/Stop' % (hostname, port))

# Datos del AgenteBuscador
AgenteBuscador = Agent('AgenteBuscador',
                       agn.AgenteBuscador,
                       'http://%s:%d/comm' % (hostname, bus_port),
                       'http://%s:%d/Stop' % (hostname, bus_port))

# Directory agent address
DirectoryAgent = Agent('DirectoryAgent',
                       agn.Directory,
                       'http://%s:9000/Register' % hostname,
                       'http://%s:9000/Stop' % hostname)


#logging.basicConfig()

# Global triplestore graph
dsgraph = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__)


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt

    print 'Peticion de informacion recibida\n'

    # Extraemos el mensaje y creamos un grafo con el
    message = request.args['content']
    print "Mensaje extraído\n"
    # VERBOSE
    print "\n\n"
    gm = Graph()
    gm.parse(data=message)
    print 'Grafo creado con el mensaje'

    msgdic = get_message_properties(gm)
    
    # Comprobamos que sea un mensaje FIPA ACL
    if msgdic is None:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = build_message(Graph(), ACL['not-understood'], sender=AgentePlanificador.uri, msgcnt=mss_cnt)
        print 'El mensaje no era un FIPA ACL'
    else:
        # Obtenemos la performativa
        perf = msgdic['performative']

        if perf != ACL.request:
            # Si no es un request, respondemos que no hemos entendido el mensaje
            gr = build_message(Graph(), ACL['not-understood'], sender=AgentePlanificador.uri, msgcnt=mss_cnt)
        else:
            # Extraemos el objeto del contenido que ha de ser una accion de la ontologia de acciones del agente
            # de registro
            # Averiguamos el tipo de la accion
            # if 'content' in msgdic:
            #     content = msgdic['content']
            #     accion = gm.value(subject=content, predicate=RDF.type)

            # Apartir de aqui tenemos que obtener parametro desde dialog y luego comunicar con buscador
            ########################################################### 
            # Parsear los parametros de Dialog
            print "Parsear los parametros de Dialog"
            #############################################################
            peticion = myns_pet["Dialogador-pide-paquete"]
            parametros = gm.triples((peticion, None, None))
            # VERBOSE
            
            actv = myns_pet.actividad

            ########################################################### 
            # Comunicar con buscador
            print "Los parametros recibidos"
            #############################################################
            # departureDate="2015-08-20"
            # returnDate="2015-08-30"
            # maxPrice=500
            # originCity="Amsterdam"
            # destinationCity="Barcelona"
            # propertyCategory=1


            originCity = gm.value(subject= peticion, predicate= myns_atr.originCity)
            #gmess.add((actv, myns_atr.lugar, origin))
            # VERBOSE
            print "originCity: "
            print originCity

            departureDate = gm.value(subject= peticion, predicate= myns_atr.departureDate)
            #gmess.add((actv, myns_atr.lugar, departureDate))
            # VERBOSE
            print "departureDate: "
            print departureDate

            returnDate = gm.value(subject= peticion, predicate= myns_atr.returnDate)
            #gmess.add((actv, myns_atr.lugar, returnDate))
            # VERBOSE
            print "returnDate: "
            print returnDate

            maxPrice = float(gm.value(subject= peticion, predicate= myns_atr.maxPrice))
            #gmess.add((actv, myns_atr.lugar, maxPrice))
            # VERBOSE
            print "maxPrice: "
            print maxPrice

            propertyCategory = gm.value(subject= peticion, predicate= myns_atr.propertyCategory)
            #gmess.add((actv, myns_atr.lugar, numberOfStars))
            # VERBOSE
            print "propertyCategory: "
            print propertyCategory
            
            actividades = []
            actividadesInt = gm.triples((None, myns_atr.tipo, None))

            for s,p, o in actividadesInt:
                if o != None:
                    actividades.append(o)

            activity= gm.value(subject= peticion, predicate= myns_atr.activities)
            print "activity: "
            print activity
            actividades.append(activity)
            


            destinationCity=gm.value(subject= peticion, predicate= myns_atr.destinationCity)
            print "destinationCity: "
            print destinationCity

            # Graph para buscador
            gmess = Graph()
            gmess.bind('myns_pet', myns_pet)
            gmess.bind('myns_atr', myns_atr)

            ########################################################### 
            # Comunicar con buscador
            # print "Los parametros hardcoreado"
            #############################################################

            
            # actividades= [types.TYPE_MOVIE_THEATER, types.TYPE_CASINO, types.TYPE_MUSEUM]


            # departureDate="2015-08-20"
            # returnDate="2015-08-30"
            # maxPrice=500
            # originCity="Amsterdam"
            # destinationCity="Barcelona"
            # propertyCategory=1

            print departureDate

            ########################################################### 
            # Mejorar preferencia de busqueda
            print "Mejorar preferencia de busqueda"
            #############################################################

            ########################################################### 
            # Comunicar con buscador
            print "Iniciar la comunicaion con buscador"
            #############################################################
            
            # Hago bind de las ontologias que voy a usar en el grafo
            # Estas ontologias estan definidas arriba (abajo de los imports)
            # Son las de peticiones y atributos (para los predicados de la tripleta)

            # Sujeto de la tripleta: http://my.namespace.org/peticiones/actividad
            # O sea, el mensaje sera una peticion de actividad
            # El buscador tendra que ver que tipo de peticion es
            ########################################################### 
            # Comunicar con buscador
            print "Añadir parametros de actividad"
            #############################################################
            # Paso los parametros de busqueda de actividad en el grafo
            busqueda = myns_pet.busqueda
            i = 0
            for a in actividades:
                if a != None:
                    i+= 1
                    actv = "actividad" + str(i)
                    gmess.add((busqueda, myns_par.actividad, myns_act.actv))
                    gmess.add((myns_act.actv, myns_atr.tipo, Literal(a)))
            
            i+= 1
            actv = "actividad" + str(i)
            gmess.add((busqueda, myns_par.actividad, myns_act.actv))
            gmess.add((myns_act.actv, myns_atr.tipo, Literal('restaurant')))
            
            ########################################################### 
            # Comunicar con buscador
            print "Añadir parametros de vuelo"
            #############################################################
            
            gmess.add((busqueda, myns_par.departureDate, Literal(departureDate)))
            gmess.add((busqueda, myns_par.returnDate, Literal(returnDate)))          
            gmess.add((busqueda, myns_par.maxPrice, Literal(maxPrice/3))) 

            ########################################################### 
            # Comunicar con buscador
            print "Añadir parametros de hotel"
            #############################################################
            hotel = myns_pet.hotel
            gmess.add((busqueda, myns_par.originCity, Literal(originCity)))
            gmess.add((busqueda, myns_par.destinationCity, Literal(destinationCity)))      
            gmess.add((busqueda, myns_par.propertyCategory, Literal(propertyCategory))) 

            # Uri asociada al mensaje sera: http://www.agentes.org#Planificador-pide-actividades
            res_obj= agn['Planificador-pide-datos']

            # Construyo el grafo y lo mando (ver los metodos send_message y build_message
            # en ACLMessages para entender mejor los parametros)
            print "INFO AgentePlanificador=> Sending request to AgenteBuscador\n"
            gr = send_message(build_message(gmess, 
                               perf=ACL.request, 
                               sender=AgentePlanificador.uri, 
                               receiver=AgenteBuscador.uri,
                               content=res_obj,
                               msgcnt=mss_cnt 
                               ),
                AgenteBuscador.address)
            print "Respuesta de busqueda recibida\n"
            
            # for s, p, o in grep:
            #     print 's: ' + s
            #     print 'p: ' + p
            #     print 'o: ' + o.encode('utf-8')
            #     print '\n'
            

            ########################################################### 
            # Calcular paquete
            print "Calcular paquete"
            #############################################################   

            grep = Graph()
            ########################################################### 
            # Calcular paquete
            print "Calcular Vuelos"
            #############################################################    
            gvuelo = Graph()
            for s,p,o in gr.triples((None, myns_atr.esUn, myns.viaje)):
                gvuelo += gr.triples((s, None, None) )

            gvueloid = gvuelo.query("""
                        PREFIX myns_atr: <http://my.namespace.org/atributos/>
                        SELECT DISTINCT ?a ?cuesta
                        WHERE{
                            ?a myns_atr:cuesta ?cuesta .
                            FILTER(str(?cuesta) != "")
                        }
                        ORDER BY (?cuesta)
                        LIMIT 1
                """)

            Aid = []
            cuestaVuelo = 0
            for s, c in gvueloid:
                print s
                Aid.append(s)
                cuestaVuelo = float(c[3:])

            maxPrice -= cuestaVuelo
            grep += gvuelo.triples((Aid[0], None, None))
            idgo = gr.value(subject= Aid[0], predicate= myns_atr.ida)
            idback = gr.value(subject= Aid[0], predicate= myns_atr.vuelta)

            grep += gr.triples((idgo,None, None))
            grep += gr.triples((idback, None, None))

            ########################################################### 
            # Calcular paquete
            print "Calcular Hotel"
            #############################################################    
            ghotel = Graph()
            for s,p,o in gr.triples((None, myns_atr.esUn, myns.hotel)):
                ghotel += gr.triples((s, None, None) )
            ghotelid = ghotel.query("""
                        PREFIX myns_atr: <http://my.namespace.org/atributos/>
                        SELECT DISTINCT ?a ?cuesta
                        WHERE{
                            ?a myns_atr:rating ?ratin .
                            ?a myns_atr:cuesta ?cuesta .
                            FILTER(str(?ratin) != "" && str(?cuesta) != "")
                            
                        }
                        ORDER BY DESC(?ratin) ?cuesta
                        LIMIT 1
                """)
            Aid = []
            cuestaHotel = 0
            for s, c in ghotelid:
                Aid.append(s)
                cuestaHotel = float(c)
            maxPrice -= cuestaHotel

            grep += ghotel.triples((Aid[0], None, None))


            #Actividades 
            ########################################################### 
            # Calcular paquete
            print "Calcular Actividades"
            #############################################################    
            gactividad = Graph()       
            for s,p,o in gr.triples((None, myns_atr.esUn, myns.actividad)):
                gactividad += gr.triples((s, None, None) )

            grestaurante = gactividad.query("""
                        PREFIX myns_atr: <http://my.namespace.org/atributos/>
                        SELECT DISTINCT ?a ?ratin ?tip
                        WHERE{
                            ?a myns_atr:rating ?ratin .
                            ?a myns_atr:tipo ?tip
                            FILTER(?tip = "restaurant")
                        }
                        ORDER BY DESC(?ratin)
                """)
            restaurant = []
            for g, r, t in grestaurante:
                restaurant.append(g)
            
            gnight = gactividad.query("""
                        PREFIX myns_atr: <http://my.namespace.org/atributos/>
                        SELECT DISTINCT ?a ?ratin ?tip
                        WHERE{
                            ?a myns_atr:rating ?ratin .
                            ?a myns_atr:tipo ?tip
                            FILTER
                                (?tip = "night_club" || 
                                 ?tip = "bar" ||
                                 ?tip = "casino"
                                 )
                        }
                        ORDER BY DESC(?ratin)
                """)
            
            night = []
            for g, r, t in gnight:
                night.append(g)
            print len(night)
            gday = gactividad.query("""
                        PREFIX myns_atr: <http://my.namespace.org/atributos/>
                        SELECT DISTINCT ?a ?ratin ?tip
                        WHERE{
                            ?a myns_atr:rating ?ratin .
                            ?a myns_atr:tipo ?tip
                            FILTER
                                (?tip != "night_club" && 
                                 ?tip != "bar" &&
                                 ?tip != "casino" &&
                                 ?tip != "restaurant"
                                 )
                        }
                        ORDER BY DESC(?ratin)
                """)
            daylist = []
            for g, r, t in gday:
                daylist.append(g)

            ########################################################### 
            # Escoger Actividades
            print "Escoger Actividades"
            #############################################################   
            day = datetime.strptime(departureDate, '%Y-%m-%d')
            print day
            cday = 0
            cnight = 0
            cres = 0
            rd = datetime.strptime(returnDate, '%Y-%m-%d')

            while day <= rd:
                auxd = day.strftime('%Y-%m-%d')
                print auxd
               # cada dia
                grfdata = myns_data[auxd]
                print grfdata
                grep.add((grfdata, myns_atr.esUn, myns.dia))
                grep.add((grfdata, myns_atr.formato, Literal(auxd)))
                if len(daylist) != 0:
                    # manana
                    grep.add((grfdata, myns_atr.manana, daylist[cday%len(daylist)]))
                    print "actividad anadido: " + gactividad.value(subject = daylist[cday%len(daylist)], predicate = myns_atr.nombre)

                    grep += gactividad.triples((daylist[cday%len(daylist)], None, None))
                    
                    cday += 1;


                    grep.add((grfdata, myns_atr.tarde, daylist[cday%len(daylist)]))

                    grep += gactividad.triples((daylist[cday%len(daylist)], None, None))
                    
                    cday += 1;

                # comida
                grep.add((grfdata, myns_atr.comida, restaurant[cres%len(restaurant)]))

                grep += gactividad.triples((restaurant[cres%len(restaurant)], None, None))
                
                cres += 1;       
                # cena

                grep.add((grfdata, myns_atr.cena, restaurant[cres%len(restaurant)]))

                grep += gactividad.triples((restaurant[cres%len(restaurant)], None, None))
                
                cres += 1;       
                # noche
                if len(night) != 0:
                    grep.add((grfdata, myns_atr.noche, night[cnight%len(night)]))

                    grep += gactividad.triples((night[cnight%len(night)], None, None))
                    
                    cnight += 1;

                day = day + timedelta(days=1)


    ########################################################### 
    # Construir mensage de repuesta
    print "Construir mensage de repuesta"
    #############################################################

    
    mss_cnt += 1

    print 'Respondemos a la peticion\n'
    ########################################################### 
    # Construir mensage de repuesta
    print "Retornar repuesta"
    #############################################################
    return grep.serialize(format='xml')


@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente

    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


def tidyup():
    """
    Acciones previas a parar el agente

    """
    pass


def agentbehavior1(cola):
    """
    Un comportamiento del agente

    :return:
    """
    pass

#def message_buscador():
#    """
#
#    """
#    gmess = Graph()
#
    # Construimos el mensaje de registro
#    gmess.bind('amo', AMO)
#    bus_obj = agn[AgentePlanificador.name + '-Request']
#    gmess.add((bus_obj, AMO.requestType, Literal('Actividad')))

    # Lo metemos en un envoltorio FIPA-ACL y lo enviamos
#    gr = send_message(
#        build_message(gmess, perf=ACL.request,
#                      sender=AgentePlanificador.uri,
#                      receiver=AgenteBuscador.uri,
#                      content=bus_obj,
#                      msgcnt=mss_cnt),
#        AgenteBuscador.address)

#    return gr

def comu():

    global mss_cnt 
    # Graph para buscador
    gmess = Graph()
    gmess.bind('myns_pet', myns_pet)
    gmess.bind('myns_atr', myns_atr)

    ########################################################### 
    # Comunicar con buscador
    print "Los parametros hardcoreado"
    #############################################################

    
    destination = "Madrid, Spain"
    actividades= [types.TYPE_MOVIE_THEATER, types.TYPE_CASINO, types.TYPE_MUSEUM]

    radius = 20000

    departureDate="2015-08-20"
    returnDate="2015-08-30"
    maxPrice=500

    originCity="Amsterdam"
    destinationCity="Barcelona"
    destinationCountry="Spain" 
    searchRadius=2 

    propertyCategory=1

    print departureDate

    ########################################################### 
    # Mejorar preferencia de busqueda
    print "Mejorar preferencia de busqueda"
    #############################################################

    ########################################################### 
    # Comunicar con buscador
    print "Iniciar la comunicaion con buscador"
    #############################################################
    
    # Hago bind de las ontologias que voy a usar en el grafo
    # Estas ontologias estan definidas arriba (abajo de los imports)
    # Son las de peticiones y atributos (para los predicados de la tripleta)

    # Sujeto de la tripleta: http://my.namespace.org/peticiones/actividad
    # O sea, el mensaje sera una peticion de actividad
    # El buscador tendra que ver que tipo de peticion es
    ########################################################### 
    # Comunicar con buscador
    print "Añadir parametros de actividad"
    #############################################################
    # Paso los parametros de busqueda de actividad en el grafo
    busqueda = myns_pet.busqueda
    i = 0
    for a in actividades:
        i+= 1
        actv = "actividad" + str(i)
        gmess.add((busqueda, myns_par.actividad, myns_act.actv))
        gmess.add((myns_act.actv, myns_atr.tipo, Literal(a)))
    
    i+= 1
    actv = "actividad" + str(i)
    gmess.add((busqueda, myns_par.actividad, myns_act.actv))
    gmess.add((myns_act.actv, myns_atr.tipo, Literal('restaurant')))
    
    ########################################################### 
    # Comunicar con buscador
    print "Añadir parametros de vuelo"
    #############################################################
    
    gmess.add((busqueda, myns_par.departureDate, Literal(departureDate)))
    gmess.add((busqueda, myns_par.returnDate, Literal(returnDate)))          
    gmess.add((busqueda, myns_par.maxPrice, Literal(maxPrice/3))) 

    ########################################################### 
    # Comunicar con buscador
    print "Añadir parametros de hotel"
    #############################################################
    hotel = myns_pet.hotel
    gmess.add((busqueda, myns_par.originCity, Literal(originCity)))
    gmess.add((busqueda, myns_par.destinationCity, Literal(destinationCity)))       
    gmess.add((busqueda, myns_par.propertyCategory, Literal(propertyCategory))) 

    # Uri asociada al mensaje sera: http://www.agentes.org#Planificador-pide-actividades
    res_obj= agn['Planificador-pide-datos']

    # Construyo el grafo y lo mando (ver los metodos send_message y build_message
    # en ACLMessages para entender mejor los parametros)
    print "INFO AgentePlanificador=> Sending request to AgenteBuscador\n"
    gr = send_message(build_message(gmess, 
                       perf=ACL.request, 
                       sender=AgentePlanificador.uri, 
                       receiver=AgenteBuscador.uri,
                       content=res_obj,
                       msgcnt=mss_cnt 
                       ),
        AgenteBuscador.address)
    print "Respuesta de busqueda recibida\n"
    
    # for s, p, o in grep:
    #     print 's: ' + s
    #     print 'p: ' + p
    #     print 'o: ' + o.encode('utf-8')
    #     print '\n'
    

    ########################################################### 
    # Calcular paquete
    print "Calcular paquete"
    #############################################################   

    grep = Graph()
    ########################################################### 
    # Calcular paquete
    print "Calcular Vuelos"
    #############################################################    
    gvuelo = Graph()
    for s,p,o in gr.triples((None, myns_atr.esUn, myns.viaje)):
        gvuelo += gr.triples((s, None, None) )

    gvueloid = gvuelo.query("""
                PREFIX myns_atr: <http://my.namespace.org/atributos/>
                SELECT DISTINCT ?a ?cuesta
                WHERE{
                    ?a myns_atr:cuesta ?cuesta .
                    FILTER(str(?cuesta) != "")
                }
                ORDER BY (?cuesta)
                LIMIT 1
        """)

    Aid = []
    cuestaVuelo = 0
    for s, c in gvueloid:
        print s
        Aid.append(s)
        cuestaVuelo = float(c[3:])

    maxPrice -= cuestaVuelo
    grep += gvuelo.triples((Aid[0], None, None))

    ########################################################### 
    # Calcular paquete
    print "Calcular Hotel"
    #############################################################    
    ghotel = Graph()
    for s,p,o in gr.triples((None, myns_atr.esUn, myns.hotel)):
        ghotel += gr.triples((s, None, None) )
    ghotelid = ghotel.query("""
                PREFIX myns_atr: <http://my.namespace.org/atributos/>
                SELECT DISTINCT ?a ?cuesta
                WHERE{
                    ?a myns_atr:rating ?ratin .
                    ?a myns_atr:cuesta ?cuesta .
                    FILTER(str(?ratin) != "" && str(?cuesta) != "")
                    
                }
                ORDER BY DESC(?ratin) ?cuesta
                LIMIT 1
        """)
    Aid = []
    cuestaHotel = 0
    for s, c in ghotelid:
        Aid.append(s)
        cuestaHotel = float(c)
    maxPrice -= cuestaHotel
    grep += ghotel.triples((Aid[0], None, None))


    #Actividades 
    ########################################################### 
    # Calcular paquete
    print "Calcular Actividades"
    #############################################################    
    gactividad = Graph()       
    for s,p,o in gr.triples((None, myns_atr.esUn, myns.actividad)):
        gactividad += gr.triples((s, None, None) )

    grestaurante = gactividad.query("""
                PREFIX myns_atr: <http://my.namespace.org/atributos/>
                SELECT DISTINCT ?a ?ratin ?tip
                WHERE{
                    ?a myns_atr:rating ?ratin .
                    ?a myns_atr:tipo ?tip
                    FILTER(?tip = "restaurant")
                }
                ORDER BY DESC(?ratin)
        """)
    restaurant = []
    for g, r, t in grestaurante:
        restaurant.append(g)
    
    gnight = gactividad.query("""
                PREFIX myns_atr: <http://my.namespace.org/atributos/>
                SELECT DISTINCT ?a ?ratin ?tip
                WHERE{
                    ?a myns_atr:rating ?ratin .
                    ?a myns_atr:tipo ?tip
                    FILTER
                        (?tip = "night_club" || 
                         ?tip = "bar" ||
                         ?tip = "casino"
                         )
                }
                ORDER BY DESC(?ratin)
        """)
    
    night = []
    for g, r, t in gnight:
        night.append(g)
    print len(night)
    gday = gactividad.query("""
                PREFIX myns_atr: <http://my.namespace.org/atributos/>
                SELECT DISTINCT ?a ?ratin ?tip
                WHERE{
                    ?a myns_atr:rating ?ratin .
                    ?a myns_atr:tipo ?tip
                }
                ORDER BY DESC(?ratin)
        """)
    daylist = []
    for g, r, t in gday:
        daylist.append(g)

    ########################################################### 
    # Escoger Actividades
    print "Escoger Actividades"
    #############################################################   
    day = datetime.strptime(departureDate, '%Y-%m-%d')
    cday = 0
    cnight = 0
    cres = 0
    rd = datetime.strptime(returnDate, '%Y-%m-%d')

    while day <= rd:
       # cada dia
        grfdata = myns_data.day
        
        # manana
        grep.add((grfdata, myns_data.manana, daylist[cday%len(daylist)]))


        grep += gactividad.triples((daylist[cday%len(daylist)], None, None))
        
        cday += 1;


        grep.add((grfdata, myns_data.tarde, daylist[cday%len(daylist)]))

        grep += gactividad.triples((daylist[cday%len(daylist)], None, None))
        
        cday += 1;

        # comida
        grep.add((grfdata, myns_data.comida, restaurant[cres%len(restaurant)]))

        grep += gactividad.triples((restaurant[cres%len(restaurant)], None, None))
        
        cres += 1;       
        # cena

        grep.add((grfdata, myns_data.cena, restaurant[cres%len(restaurant)]))

        grep += gactividad.triples((restaurant[cres%len(restaurant)], None, None))
        
        cres += 1;       
        # noche
        if len(night) != 0:
            grep.add((grfdata, myns_data.noche, night[cnight%len(night)]))

            grep += gactividad.triples((night[cnight%len(night)], None, None))
            
            cnight += 1;

        day = day + timedelta(days=1)


    ########################################################### 
    # Construir mensage de repuesta
    print "Construir mensage de repuesta"
    #############################################################
    # for s, p, o in grep:
    #     print 's: ' + s
    #     print 'p: ' + p
    #     print 'o: ' + o.encode('utf-8')
    #     print '\n'
    
    mss_cnt += 1

    return grep


if __name__ == '__main__':

    # Ponemos en marcha los behaviors
    ab1 = Process(target=agentbehavior1, args=(cola1,))
    ab1.start()
    #################1##################################
    # Inicio de peticion de ACTIVIDADES a AgentBuscador
    ###################################################

    # # Creo el grafo sobre el que mando los parametros de busqueda
    # gmess = Graph()
    # # Hago bind de las ontologias que voy a usar en el grafo
    # # Estas ontologias estan definidas arriba (abajo de los imports)
    # # Son las de peticiones y atributos (para los predicados de la tripleta)
    # gmess.bind('myns_pet', myns_pet)
    # gmess.bind('myns_atr', myns_atr)

    # # Parametros de la peticion de actividades
    # # Luego habra que sustituirlos por los que obtengo del planificador
    # location = 'Barcelona, Spain'
    # activity = 'movie'
    # radius = 20000
    # # De momento solo permitimos pasar un tipo. Ampliar a mas de uno luego quizas
    # tipo = types.TYPE_MOVIE_THEATER # Equivalente a: tipo = ['movie_theater']

    # # Sujeto de la tripleta: http://my.namespace.org/peticiones/actividad
    # # O sea, el mensaje sera una peticion de actividad
    # # El buscador tendra que ver que tipo de peticion es
    # actv = myns_pet.actividad

    # # Paso los parametros de busqueda de actividad en el grafo
    # gmess.add((actv, myns_atr.lugar, Literal(location)))
    # gmess.add((actv, myns_atr.actividad, Literal(activity)))
    # gmess.add((actv, myns_atr.radio, Literal(radius)))
    # gmess.add((actv, myns_atr.tipo, Literal(tipo)))

    # # Uri asociada al mensaje sera: http://www.agentes.org#Planificador-pide-actividades
    # res_obj= agn['Planificador-pide-actividades']

    # # Construyo el grafo y lo mando (ver los metodos send_message y build_message
    # # en ACLMessages para entender mejor los parametros)
    # print "INFO AgentePlanificador=> Sending request to AgenteBuscador\n"
    # gr = send_message(build_message(gmess, 
    #                    perf=ACL.request, 
    #                    sender=AgentePlanificador.uri, 
    #                    receiver=AgenteBuscador.uri,
    #                    content=res_obj,
    #                    msgcnt=mss_cnt 
    #                    ),
    #     AgenteBuscador.address)

    # # Ahora en gr tengo la respuesta de la busqueda con las actividades

    # # VERBOSE
    # # Con esto podemos coger todos los nombres de lasa actividades del grafo
    # # para poder coger los atributos de cada actividad
    # nombres = list()
    # for s, p, o in gr:
    #     if p == myns_atr.nombre:
    #         nombres.append(s)
    # print nombres

    # # VERBOSE
    # # Imprimo la respuesta por pantalla para ver lo que devuelve
    # # Luego en verdad esto se pasa al algoritmo del planificador
    # print "INFO AgentePlanificador => Response: \n"
    # for s, p, o in gr:
    #     print 's: ' + s
    #     print 'p: ' + p
    #     print 'o: ' + o
    #     print '\n'

    # VERBOSE
    # Descomentar para un print "pretty" del grafo de respuesta
    # print json.dumps(gr.json(), indent=4, sort_keys=True)
    #grep = comu()
    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    #   ab1.join()

    print 'INFO AgentePlanificador => The End'


