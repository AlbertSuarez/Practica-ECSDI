# -*- coding: utf-8 -*-
"""
File: AgentFlights

Created on 07/02/2014 9:00

Hace consultas al fichero FlightRoutes.ttl.gz

@author: bejar

"""

__author__ = 'bejar'

import gzip

from rdflib import Graph

from AgentUtil.OntoNamespaces import TIO


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
