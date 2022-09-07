import pandas as pd
import unidecode
import itertools
from decimal import Decimal
from urllib.error import HTTPError
from rdflib import Graph, RDF, RDFS, URIRef, Literal, XSD
from rdflib.namespace import Namespace
from . import POI_SARDEGNA_SICILIA, POI_STATS, POI_RDF_TURTLE

#Domain base URIs

ontology = "https://purl.archive.org/purl/net/poi_sardegna_sicilia/ontologia"
base_domain = "https://purl.archive.org/purl/net/poi_sardegna_sicilia/risorse"
dbpedia = "http://dbpedia.org/resource/"

#Namespaces
poi = Namespace(ontology)
owl = Namespace("http://www.w3.org/2002/07/owl")

def create_rdf_from_data():
    print("Creating RDF from data...")
    g = Graph()
    g.bind("poi", poi)
    g.bind("owl", owl)
    g = add_poi_data(POI_SARDEGNA_SICILIA, g)
    g = add_stats_data(POI_STATS, g)
    print("Saving RDF/Turtle file...")
    g.serialize(POI_RDF_TURTLE, format="turtle")


def add_poi_data(csv, graph):
    data_frame = pd.read_csv(csv, encoding="utf-8")
    #iterrows() provides a (index, Series) couple. We need the Series object only
    for _, row in data_frame.iterrows():
        if row["Regione"] == "Sardegna":
            region_uri = URIRef(base_domain + "/luoghi/Sardegna")
        else:
            region_uri = URIRef(base_domain + "/luoghi/Sicilia")
        city_uri = URIRef(base_domain + "/luoghi/" + urify_string(row["Comune"]))
        coordinates_uri = URIRef(base_domain + "/coordinates/" + urify_string(row["Indirizzo"]) + "-Coordinates")
        location_uri = URIRef(base_domain + "/indirizzi/" + urify_string(manage_address(row["Indirizzo"])))
        category_uri = URIRef(base_domain + "/categorie_poi/" + urify_string(row["Categoria"]))
        poi_uri = URIRef(base_domain + "/poi/" + urify_string(row["Denominazione"]))
        #Adding region
        if (region_uri, RDF.type, poi.Regione) not in graph:
            graph.add((region_uri, RDF.type, poi.Regione))
            graph.add((region_uri, RDFS.label, Literal(row["Regione"], datatype=XSD.string)))
        #Adding city
        if (city_uri, RDF.type, poi.Comune) not in graph:
            graph.add((city_uri, RDF.type, poi.Comune))
            graph.add((city_uri, RDFS.label, Literal(row["Comune"], datatype=XSD.string)))
        #Adding coordinates
        graph.add((coordinates_uri, RDF.type, poi.Coordinate))
        graph.add((coordinates_uri, poi.latitudine, Literal(row["Latitudine"], datatype=XSD.decimal)))
        graph.add((coordinates_uri, poi.longitudine, Literal(row["Longitudine"], datatype=XSD.decimal)))
        #Adding location
        if (location_uri, RDF.type, poi.Indirizzo) not in graph or (city_uri, RDF.type, poi.Comune) not in graph:
            graph.add((location_uri, RDF.type, poi.Indirizzo))
            graph.add((location_uri, RDFS.label, Literal(row["Indirizzo"], datatype=XSD.string)))
        #Adding category
        if (category_uri, RDF.type, poi.Categoria) not in graph:
            graph.add((category_uri, RDF.type, poi.Categoria))
            graph.add((category_uri, RDFS.label, Literal(row["Categoria"], datatype=XSD.string)))
        #Adding POI
        graph.add((poi_uri, RDF.type, poi.Punto_di_interesse))
        graph.add((poi_uri, RDFS.label, Literal(row["Denominazione"], datatype=XSD.string)))
        graph.add((poi_uri, poi.prezzo, Literal(row["Prezzo"], datatype=XSD.decimal)))
        #Adding Object Properties
        #Region
        graph.add((region_uri, poi.haComune, city_uri))
        graph.add((region_uri, owl.sameAs, URIRef(dbpedia + row["Regione"])))
        #City
        graph.add((city_uri, poi.haIndirizzo, location_uri))
        graph.add((city_uri, poi.inRegione, region_uri))
        graph.add((city_uri, owl.sameAs, URIRef(dbpedia + urify_string(row["Comune"]))))
        #Coordinates
        graph.add((coordinates_uri, poi.coordinateDi, location_uri))
        #Location
        graph.add((location_uri, poi.haCoordinate, coordinates_uri))
        graph.add((location_uri, poi.haPuntoDiInteresse, poi_uri))
        graph.add((location_uri, poi.inComune, city_uri))
        #Category
        graph.add((category_uri, poi.categoriaDi, poi_uri))
        #POI
        graph.add((poi_uri, poi.haCategoria, category_uri))
        graph.add((poi_uri, poi.inIndirizzo, location_uri))
        #graph.add((poi_uri, owl.sameAs, URIRef(dbpedia + urify_string(row["Denominazione"]))))
    return graph

def add_stats_data(csv, graph):
    dict_row = {
        "Museum" : 0,
        "Archaeological" : 1,
        "Monument" : 2
    }
    dict_col = {
        "Sar_tot" : 1,
        "Sar_mean" : 2,
        "Sic_tot" : 3,
        "Sic_mean" : 4
    }
    data_frame = pd.read_csv(csv, encoding="utf-8")
    stats_museum_uri = URIRef(base_domain + "/stats/museum")
    stats_archaeological_uri = URIRef(base_domain + "/stats/archaeological")
    stats_monument_uri = URIRef(base_domain + "/stats/monument")

    #Adding museums stats
    graph.add((stats_museum_uri, RDF.type, poi.Statistica_musei))
    graph.add((stats_museum_uri, RDFS.label, Literal("Statistica musei", datatype=XSD.string)))
    graph.add((stats_museum_uri, poi.tot_poi_sardegna, Literal(data_frame.loc[dict_row["Museum"]][dict_col["Sar_tot"]], datatype=XSD.integer)))
    graph.add((stats_museum_uri, poi.prezzo_medio_sardegna, Literal(data_frame.loc[dict_row["Museum"]][dict_col["Sar_mean"]], datatype=XSD.decimal)))
    graph.add((stats_museum_uri, poi.tot_poi_sicilia, Literal(data_frame.loc[dict_row["Museum"]][dict_col["Sic_tot"]], datatype=XSD.integer)))
    graph.add((stats_museum_uri, poi.prezzo_medio_sicilia, Literal(data_frame.loc[dict_row["Museum"]][dict_col["Sic_mean"]], datatype=XSD.decimal)))

    #Adding archaeological stats
    graph.add((stats_archaeological_uri, RDF.type, poi.Statistica_aree_archeologiche))
    graph.add((stats_archaeological_uri, RDFS.label, Literal("Statistica aree archeologiche", datatype=XSD.string)))
    graph.add((stats_archaeological_uri, poi.tot_poi_sardegna, Literal(data_frame.loc[dict_row["Archaeological"]][dict_col["Sar_tot"]], datatype=XSD.integer)))
    graph.add((stats_archaeological_uri, poi.prezzo_medio_sardegna, Literal(data_frame.loc[dict_row["Archaeological"]][dict_col["Sar_mean"]], datatype=XSD.decimal)))
    graph.add((stats_archaeological_uri, poi.tot_poi_sicilia, Literal(data_frame.loc[dict_row["Archaeological"]][dict_col["Sic_tot"]], datatype=XSD.integer)))
    graph.add((stats_archaeological_uri, poi.prezzo_medio_sicilia, Literal(data_frame.loc[dict_row["Archaeological"]][dict_col["Sic_mean"]], datatype=XSD.decimal)))

    #Adding monuments stats
    graph.add((stats_monument_uri, RDF.type, poi.Statistica_monumenti))
    graph.add((stats_monument_uri, RDFS.label, Literal("Statistica musei", datatype=XSD.string)))
    graph.add((stats_monument_uri, poi.tot_poi_sardegna, Literal(data_frame.loc[dict_row["Monument"]][dict_col["Sar_tot"]], datatype=XSD.integer)))
    graph.add((stats_monument_uri, poi.prezzo_medio_sardegna, Literal(data_frame.loc[dict_row["Monument"]][dict_col["Sar_mean"]], datatype=XSD.decimal)))
    graph.add((stats_monument_uri, poi.tot_poi_sicilia, Literal(data_frame.loc[dict_row["Monument"]][dict_col["Sic_tot"]], datatype=XSD.integer)))
    graph.add((stats_monument_uri, poi.prezzo_medio_sicilia, Literal(data_frame.loc[dict_row["Monument"]][dict_col["Sic_mean"]], datatype=XSD.decimal)))

    return graph

def urify_string(original_string):
    string = unidecode.unidecode(original_string.replace(' ', '_').replace(',', '_').replace('"', '_').replace("'", "_").replace('’', "_").replace('/', '_').replace('__', '_'))
    if string[0] == '_':
        string = string[1:]
    if string[len(string) - 1] == '_':
        string = string[0:len(string) - 1]
    return string

def manage_address(string):
    arr = string.split(",")
    if(len(arr) > 1):
        out = arr[0] + "," + arr[1]
    else:
        out = arr[0]
    return out