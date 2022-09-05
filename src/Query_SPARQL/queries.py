from os import environ
from pathlib import Path
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace, RDF

base = environ["POI_LOCATION"]

def queries():
    query1()

def query1():
    g = rdflib.Graph()
    g.bind("poi", "https://purl.archive.org/purl/net/poi_sardegna_sicilia/ontologia")
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.bind("owl", "http://www.w3.org/2002/07/owl")
    g.parse(base + "/POI_RDF_TURTLE.ttl", format='turtle')

    results = g.query("""
        PREFIX poi: <https://purl.archive.org/purl/net/poi_sardegna_sicilia/ontologia>
        PREFIX owl: <http://www.w3.org/2002/07/owl>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
        SELECT ?denominazione ?prez
        WHERE {
            ?punto rdf:type poi:Punto_di_interesse .
            ?punto rdfs:label ?denominazione .
            ?punto poi:prezzo ?prez .
        }
    """)

    print('Results!')
    for row in results:
        print(row)

