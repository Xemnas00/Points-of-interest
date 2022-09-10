from os import environ
import rdflib
import pandas as pd

base = environ["POI_LOCATION"]

def queries():
    g = rdflib.Graph()
    g.bind("cis", "http://dati.beniculturali.it/cis/")
    g.bind("clvapit", "https://ontopia-lodview.agid.gov.it/onto/CLV/")
    g.bind("geo", "http://www.w3.org/2003/01/geo/wgs84_pos#")
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.parse(base + "/POI_RDF_TURTLE.ttl", format='turtle')
    create_stats(g)
    print("*" * 100)
    query3(g)
    print("*" * 100)
    query4(g)

def create_stats(g):
    # Retrieving stats data using queries
    cis_base = "http://dati.beniculturali.it/cis/"
    dict_row = {
        cis_base + "Museum": 0,
        cis_base + "ArchaeologicalArea": 1,
        cis_base + "MonumentalArea": 2
    }
    dict_col = {
        "Sar_tot": 1,
        "Sar_mean": 2,
        "Sic_tot": 3,
        "Sic_mean": 4
    }

    stats = [
        ["museo, galleria e/o raccolta", 0, 0, 0, 0],
        ["area o parco archeologico", 0, 0, 0, 0],
        ["monumento o complesso monumentale", 0, 0, 0, 0]
    ]

    stats_means = query1(g)
    for row in stats_means:
        if str(row.l) == "Sardegna":
            stats[dict_row[str(row.type)]][dict_col["Sar_mean"]] = float(row.average)
        else:
            stats[dict_row[str(row.type)]][dict_col["Sic_mean"]] = float(row.average)

    stats_tots = query2(g)
    for row in stats_tots:
        if str(row.l) == "Sardegna":
            stats[dict_row[str(row.type)]][dict_col["Sar_tot"]] = int(row.tot)
        else:
            stats[dict_row[str(row.type)]][dict_col["Sic_tot"]] = int(row.tot)

    data_frame = pd.DataFrame(stats, columns=['POI', 'Totali(Sardegna)', 'Prezzo medio in euro(Sardegna)', 'Totali(Sicilia)', 'Prezzo medio in euro(Sicilia)'])
    data_frame.to_csv(base + "/data/POI_STATS.csv", index=False)

def query1(graph):
    results = graph.query("""
        PREFIX cis: <http://dati.beniculturali.it/cis/>
        PREFIX clvapit: <https://ontopia-lodview.agid.gov.it/onto/CLV/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?l ?type (((ROUND(AVG(?p) * 100)) / 100) AS ?average)
        WHERE {
            ?o rdf:type cis:Offer ;
               cis:hasPriceSpecification ?p_spec;
               cis:includes ?t .
            ?p_spec cis:hasCurrencyValue ?p .  
            ?t cis:forAccessTo ?c .
            ?c cis:hasSite ?s ;
               cis:hasCISType ?type .
            ?s cis:hasAddress ?a .
            ?a clvapit:hasRegion ?r .
            ?r rdfs:label ?l       
        }GROUP BY ?r ?type
        ORDER BY ?l ?type
    """)

    return results

def query2(graph):
    results = graph.query("""
        PREFIX cis: <http://dati.beniculturali.it/cis/>
        PREFIX clvapit: <https://ontopia-lodview.agid.gov.it/onto/CLV/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?l ?type (COUNT(?c) AS ?tot)
        WHERE {
            ?c rdf:type cis:CulturalInstituteOrSite ;
               cis:hasSite ?s ;
               cis:hasCISType ?type .
            ?s cis:hasAddress ?a .
            ?a clvapit:hasRegion ?r .
            ?r rdfs:label ?l       
        }GROUP BY ?r ?type
        ORDER BY ?l ?type
    """)

    return results


def query3(graph):
    results = graph.query("""
            PREFIX cis: <http://dati.beniculturali.it/cis/>
            PREFIX clvapit: <https://ontopia-lodview.agid.gov.it/onto/CLV/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?n
            WHERE {
                ?i rdf:type cis:CulturalInstituteOrSite ;
                   cis:hasSite ?s ;
                   cis:institutionalName ?n .
                ?s cis:hasAddress ?a .
                ?a clvapit:hasCity ?c .
                ?c rdfs:label ?l .
                FILTER (?l = "Palermo") .
            }
        """)

    for row in results:
        print(row)

def query4(graph):
    results = graph.query("""
                PREFIX cis: <http://dati.beniculturali.it/cis/>
                PREFIX clvapit: <https://ontopia-lodview.agid.gov.it/onto/CLV/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?n
                WHERE {
                    ?i rdf:type cis:CulturalInstituteOrSite ;
                       cis:institutionalName ?n .
                    FILTER(REGEX(?n, "casa ", "i"))
                }
            """)

    for row in results:
        print(row)