__author__ = 'javier'

from SPARQLWrapper import SPARQLWrapper, JSON
from AgentUtil.SPARQLPoints import OPENLINK


sparql = SPARQLWrapper(OPENLINK)

# Museos en un radio de 20Km alrededor de Barcelona
sparql.setQuery("""
  Prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  Prefix ogc: <http://www.opengis.net/ont/geosparql#>
  Prefix geom: <http://geovocab.org/geometry#>
  Prefix lgdo: <http://linkedgeodata.org/ontology/>
  Prefix dbp: <http://dbpedia.org/ontology/>
  Prefix sch: <http://schema.org/>

SELECT DISTINCT ?label, ?location, ?sourcegeo   WHERE
  {
    <http://dbpedia.org/resource/Barcelona> geo:geometry ?sourcegeo .
    ?resource geo:geometry ?location ; rdfs:label ?label; rdf:type sch:Museum .
    FILTER ( bif:st_intersects ( ?location, ?sourcegeo, 40 ) ) .
    FILTER ( lang ( ?label ) = "es" )
  }
LIMIT 200  """)

sparql.setReturnFormat(JSON)
results = sparql.query()
results.print_results()


