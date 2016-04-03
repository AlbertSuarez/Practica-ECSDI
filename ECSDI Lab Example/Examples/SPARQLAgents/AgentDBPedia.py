# -*- coding: utf-8 -*-
"""
File: SPARQLQueries

Created on 01/02/2014 11:32

Programa python para enviar queries SPARQL


@author: bejar

"""
__author__ = 'javier'

from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF, N3
from rdflib import Graph, BNode, Literal

from AgentUtil.SPARQLPoints import DBPEDIA

# Configuramos el SPARQL de wikipedia
sparql = SPARQLWrapper(DBPEDIA)

# Obtenemos tods los tipos asignados a barcelona
# Si hacemos una query obtenemos un objeto de tipo answerset
# que contiene las vinculaciones de las variables de la query
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT  DISTINCT ?val
    WHERE { <http://dbpedia.org/resource/Barcelona> rdf:type  ?val.
          }
    LIMIT 1000
""")

# Los SELECT no siempre retornan un grafo RDF valido, por lo que es mas seguro obtener
# la informacion como JSON
sparql.setReturnFormat(JSON)

# Obtenemos los resultados y los imprimimos talcual
results = sparql.query()
results.print_results()

# Hacemos la llamada anterior pero convirtiendo el resultado en un diccionario python
resdic = sparql.query().convert()

# En el resultado ['head']['vars'] tiene las variables de la query y ['results'][bindings'] las vinculaciones
# Debemos comprobar que hay en los diferentes resultados
vars = resdic['head']['vars']
for res in resdic['results']['bindings']:
    for v in vars:
        print v, ':', res[v]

# Si queremos obtener el resultado como un grafo RDF que podamos manipular hemos de usar
# La consulta CONSTRUCT indicando como se construira el grafo a partir de los resultado
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    CONSTRUCT {<http://dbpedia.org/resource/Barcelona> rdf:type ?val}
    WHERE { <http://dbpedia.org/resource/Barcelona> rdf:type  ?val.
          }
    LIMIT 1000
""")

# Obtenemos los resultado en formato RDF que ya es un Graph() de RDFLib
sparql.setReturnFormat(RDF)
resgraph = sparql.query().convert()

# Resultado en N3
print resgraph.serialize(format='n3')

# Obtenemos todos los predicados
for _, _, p in resgraph:
    print p


    # Wikipedia Airlines
    # sparql.setQuery("""
    # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #     PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    #     PREFIX dbpedia2: <http://dbpedia.org/property/>
    #     SELECT  DISTINCT *
    #     WHERE { ?subject rdf:type <http://dbpedia.org/ontology/Airline>.
    #             ?subject <http://dbpedia.org/property/iata> ?IATA.
    #             ?subject <http://dbpedia.org/property/icao> ?ICAO.
    #             ?subject <http://dbpedia.org/property/airline> ?name.
    #             ?subject <http://dbpedia.org/property/callsign> ?cs
    #             FILTER (lang(?name) = "en" or lang(?name) = "" )
    #           }
    # """)

    # Wikipedia Airports
    # sparql.setQuery("""
    #     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #     PREFIX dbpedia2: <http://dbpedia.org/property/>
    #     SELECT  DISTINCT *
    #     WHERE { ?subject rdf:type <http://dbpedia.org/ontology/Airport>.
    #             ?subject <http://dbpedia.org/ontology/iataLocationIdentifier> ?IATA.
    #             ?subject <http://dbpedia.org/property/cityServed> ?city.
    #             ?subject <http://dbpedia.org/property/name> ?name.
    #             ?subject <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long.
    #             ?subject <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat.
    #             FILTER (lang(?name) = "en" or lang(?name) = "" )
    #           }
    # """)