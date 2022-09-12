from urllib.error import HTTPError
import pandas as pd
import unidecode
from rdflib import Graph, RDF, RDFS, URIRef, Literal, XSD
from rdflib.namespace import Namespace
from . import POI_SARDEGNA_SICILIA, POI_RDF_TURTLE
from SPARQLWrapper import SPARQLWrapper, JSON

#Domain base URIs

cis_link = "http://dati.beniculturali.it/cis/"
clvapit_link = "https://ontopia-lodview.agid.gov.it/onto/CLV/"
geo_link = "http://www.w3.org/2003/01/geo/wgs84_pos#"
base_domain = "https://purl.archive.org/purl/net/poi_sardegna_sicilia/risorse"
dbpedia = "http://dbpedia.org/resource/"

#Namespaces
cis = Namespace(cis_link)
clvapit = Namespace(clvapit_link)
geo = Namespace(geo_link)
owl = Namespace("http://www.w3.org/2002/07/owl")

def create_rdf_from_data_cultural_on():
    print("Creating RDF from data...")
    g = Graph()
    g.bind("cis", cis)
    g.bind("owl", owl)
    g.bind("clvapit", clvapit)
    g = add_poi_data(POI_SARDEGNA_SICILIA, g)
    print("Saving RDF/Turtle file...")
    g.serialize(POI_RDF_TURTLE, format="turtle")

#Function that populates RDF Graph
def add_poi_data(csv, g):
    data_frame = pd.read_csv(csv, encoding="utf-8")
    institutes = retrieve_institutes()
    for _, row in data_frame.iterrows():
        region_uri = URIRef(base_domain + "/regioni/" + row["Regione"].lower())
        city_uri = URIRef(base_domain + "/comuni/" + our_urify_string(urify_string(row["Comune"])))
        address_uri = URIRef(base_domain + "/indirizzi/" + our_urify_string(urify_string(row["Indirizzo"])))
        site_uri = URIRef(base_domain + "/sedi/" + our_urify_string(urify_string(row["Denominazione"] + "_" + row["Contatti"] + "_" + row["Indirizzo"] + "_SITE")))
        cultural_institute_uri = URIRef(base_domain + "/poi/cultural_institute/" + our_urify_string(urify_string(row["Denominazione"] + "_" + row["Contatti"] + "_" + row["Indirizzo"]+ "_INSTITUTE")))
        contact_point_uri = URIRef(base_domain + "/punti_contattabili/" + our_urify_string(urify_string(row["Denominazione"] + "_" + row["Contatti"] + "_" + row["Indirizzo"] + "_CONTACTS")))
        price_specification_uri = URIRef(base_domain + "/specifiche_prezzo/" + our_urify_string(urify_string(row["Denominazione"] + "_" + row["Contatti"] + "_" +  row["Indirizzo"] + "_PRICESPEC")))
        offer_uri = URIRef(base_domain + "/offerte/" + our_urify_string(urify_string(row["Denominazione"] + row["Contatti"] + row["Indirizzo"] + "_OFFER")))
        ticket_uri = URIRef(base_domain + "/biglietti/" + our_urify_string(urify_string(row["Denominazione"] + row["Contatti"] + row["Indirizzo"] + "_TICKET")))

        g.add((region_uri, RDF.type, clvapit.Region))
        g.add((region_uri, RDFS.label, Literal(row["Regione"], datatype=XSD.string)))
        #Interlinking with DBPedia
        g.add((region_uri, owl.sameAs, URIRef(dbpedia + row["Regione"])))

        if ((city_uri, RDF.type, clvapit.City)) not in g:
            g.add((city_uri, RDF.type, clvapit.City))
            g.add((city_uri, RDFS.label, Literal(row["Comune"], datatype=XSD.string)))
            #Interlinking with DBPedia
            if is_city(urify_string(row["Comune"])) == True:
                g.add((city_uri, owl.sameAs, URIRef(dbpedia + urify_string(row["Comune"]))))
            elif row["Regione"] == "Sardegna" and is_city(urify_string(row["Comune"]) + ",_Sardinia") == True:
                g.add((city_uri, owl.sameAs, URIRef(dbpedia + urify_string(row["Comune"]) + ",_Sardinia")))
            elif row["Regione"] == "Sicilia" and is_city(urify_string(row["Comune"]) + ",_Sicily") == True:
                g.add((city_uri, owl.sameAs, URIRef(dbpedia + urify_string(row["Comune"]) + ",_Sicily")))

        g.add((address_uri, RDF.type, clvapit.Address))
        g.add((address_uri, clvapit.hasRegion, region_uri))
        g.add((address_uri, clvapit.hasCity, city_uri))

        g.add((contact_point_uri, RDF.type, cis.ContactPoint))
        g.add((contact_point_uri, RDFS.label, Literal("Contatti: " + row["Denominazione"], datatype=XSD.string)))
        if row["Contatti"] != "NON REGISTRATO":
            contatti = row["Contatti"].split("//")
            for contatto in contatti:
                g.add((contact_point_uri, cis.hasTelephone, URIRef(base_domain + "/contatti/" + contatto)))

        g.add((site_uri, RDF.type, cis.Site))
        g.add((site_uri, cis.isSiteOf, cultural_institute_uri))
        g.add((site_uri, cis.hasAddress, address_uri))
        g.add((site_uri, cis.hasContactPoint, contact_point_uri))


        g.add((cultural_institute_uri, RDF.type, cis.CulturalInstituteOrSite))
        g.add((cultural_institute_uri, RDFS.label, Literal("Istituto della cultura: " + row["Denominazione"], datatype=XSD.string)))
        g.add((cultural_institute_uri, cis.hasSite, site_uri))
        g.add((cultural_institute_uri, cis.institutionalName, Literal(row["Denominazione"], datatype=XSD.string)))
        g.add((cultural_institute_uri, cis.hasContactPoint, contact_point_uri))
        g.add((cultural_institute_uri, cis.hasTicket, ticket_uri))
        g.add((cultural_institute_uri, geo.lat, Literal(row["Latitudine"], datatype=XSD.float)))
        g.add((cultural_institute_uri, geo.long, Literal(row["Longitudine"], datatype=XSD.float)))
        if row["Categoria"] == "museo, galleria, raccolta":
            g.add((cultural_institute_uri, cis.hasCISType, cis.Museum))
        elif row["Categoria"] == "area o parco archeologico":
            g.add((cultural_institute_uri, cis.hasCISType, cis.ArchaeologicalArea))
        else:
            g.add((cultural_institute_uri, cis.hasCISType, cis.MonumentalArea))

        #Interlinking with MiC catalogue
        if institutes != False:
            for hit in institutes["results"]["bindings"]:
                if hit["l"]["value"] == row["Denominazione"]:
                    g.add((cultural_institute_uri, owl.sameAs, URIRef(hit["i"]["value"])))

        g.add((price_specification_uri, RDF.type, cis.PriceSpecification))
        g.add((price_specification_uri, cis.hasCurrency, cis.Euro))
        g.add((price_specification_uri, cis.hasCurrencyValue, Literal(row["Prezzo"], datatype=XSD.float)))

        g.add((ticket_uri, RDF.type, cis.Ticket))
        g.add((ticket_uri, RDFS.label, Literal("Biglietto intero per accedere a: " + row["Denominazione"], datatype=XSD.string)))
        g.add((ticket_uri, cis.forAccessTo, cultural_institute_uri))

        g.add((offer_uri, RDF.type, cis.Offer))
        g.add((offer_uri, cis.hasPriceSpecification, price_specification_uri))
        g.add((offer_uri, cis.includes, ticket_uri))
    #Interlinkng particular cities
    g.add((URIRef(base_domain + "/luoghi/" + urify_string("Siracusa")), owl.sameAs, URIRef(dbpedia + "Syracuse,_Sicily")))
    g.add((URIRef(base_domain + "/luoghi/" + urify_string("Campobello di Mazara")), owl.sameAs, URIRef(dbpedia + urify_string("Campobello di Mazara"))))

    return g

def urify_string(original_string):
    string = original_string.replace("\\", "_").replace(' ', '_').replace(',', '_').replace('"', '_').replace('’', "_").replace('/', '_').replace('__', '_')
    if string[0] == '_':
        string = string[1:]
    if string[len(string) - 1] == '_':
        string = string[0:len(string) - 1]
    return string

#This function performs an operation that should not be performed when we try to match URIs with DBPedia ones
def our_urify_string(string):
    return unidecode.unidecode(string.replace('\'', '_'))

def is_city(urificated_city):
    uri = URIRef('http://dbpedia.org/resource/' + urificated_city)
    pp = URIRef('http://dbpedia.org/ontology/PopulatedPlace')
    g_temp = Graph()
    g_temp.parse(uri)
    try:
        response = g_temp.query(
            "ASK {?uri a ?pp}",
            initBindings={'uri': uri, 'pp': pp}
        )
    except HTTPError:
        return False
    print(str(uri) + " is a PopulatedPlace? " + str(response.askAnswer))

    return response.askAnswer

def retrieve_institutes():
    sparql = SPARQLWrapper("https://dati.beniculturali.it/sparql") #Querying a remote SPARQL endpoint
    sparql.setQuery("""
        SELECT DISTINCT ?i ?l
        WHERE {
            ?i rdf:type cis:CulturalInstituteOrSite ;
               rdfs:label ?l ;
               cis:hasSite ?s .
            ?s cis:siteAddress ?a .
            ?a clvapit:hasRegion ?r .
            ?r rdfs:label ?region .
            FILTER(?region = "Sicilia" || ?region = "Sardegna")   
        }
    """)

    sparql.setReturnFormat(JSON)
    try:
        result = sparql.query().convert()
    except HTTPError:
        return False

    return result

