"""
.. module:: Example1

Example1
******

:Description: Example1

Ejemplos de RDFLIB

"""

__author__ = 'bejar'

from rdflib.namespace import RDF, RDFS, Namespace, FOAF, OWL
from rdflib import Graph, BNode, Literal
from pprint import pformat

g = Graph()

n = Namespace('http://ejemplo.org/')

p1 = n.persona1
v = Literal(22)

g.add((p1, FOAF.age, v))

# g.serialize('a.rdf')

for a, b, c in g:
    print a, b, c

for a, b in g[p1]:
    print a, b

t = g.triples((None, FOAF.age, Literal(22)))

for a in t:
    print a

