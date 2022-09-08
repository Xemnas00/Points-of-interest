from os import environ
import rdflib

base = environ["POI_LOCATION"]

def queries():
    g = rdflib.Graph()
    g.bind("poi", "https://purl.archive.org/purl/net/poi_sardegna_sicilia/ontologia")
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.parse(base + "/POI_RDF_TURTLE.ttl", format='turtle')
    print("*" * 100)
    query1(g)
    print("*" * 100)
    query2(g)
    print("*" * 100)
    query3(g)
    print("*" * 100)

#POIs ordered by price
def query1(graph):
    results = graph.query("""
        PREFIX poi: <https://purl.archive.org/purl/net/poi_sardegna_sicilia/ontologia>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
        SELECT ?denominazione ?prez
        WHERE {
            ?punto rdf:type poi:Punto_di_interesse .
            ?punto rdfs:label ?denominazione .
            ?punto poi:prezzo ?prez .
        } ORDER BY ?prez
    """)

    for row in results:
        print(row)

#POIs located in "Palermo"
def query2(graph):
    results = graph.query("""
        PREFIX poi: <https://purl.archive.org/purl/net/poi_sardegna_sicilia/ontologia>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?punto
        WHERE {
            ?punto rdf:type poi:Punto_di_interesse ;
                   rdfs:label ?denominazione ;
                   poi:inIndirizzo ?indirizzo .
            ?indirizzo poi:inComune ?comune .
            ?comune rdfs:label ?nome_comune .
            FILTER(?nome_comune="Palermo") .
        }
    """)

    for row in results:
        print(row)

#Regions and their POIs' average price
def query3(graph):
    results = graph.query("""
        PREFIX poi: <https://purl.archive.org/purl/net/poi_sardegna_sicilia/ontologia>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?regione (ROUND(AVG(?prez)*100)/100 AS ?average_price)
        WHERE {
            ?poi rdf:type poi:Punto_di_interesse ;
                 poi:inIndirizzo ?indirizzo .
            ?indirizzo poi:inComune ?comune .
            ?comune poi:inRegione ?regione .
            ?poi poi:prezzo ?prez .
        } 
        GROUP BY ?regione
        ORDER BY ?average_price
    """)

    for row in results:
        print(row)