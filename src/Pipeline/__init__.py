from os import environ
from pathlib import Path

base = environ["POI_LOCATION"]
LUOGHI_INTERESSE_SARDEGNA = base + "/input/LUOGHI_INTERESSE_SARDEGNA.csv"
LUOGHI_INTERESSE_SICILIA = base + "/input/LUOGHI_INTERESSE_SICILIA.csv"
CLEANED_SARDEGNA = base + "/data/CLEANED_SARDEGNA.csv"
CLEANED_SICILIA = base + "/data/CLEANED_SICILIA.csv"
POI_SARDEGNA_SICILIA = base + "/data/POI_SARDEGNA_SICILIA.csv"
POI_STATS = base + "/data/POI_STATS.csv"
POI_RDF_TURTLE = base + "/POI_RDF_TURTLE.ttl"

def files_are_present():
    files = [LUOGHI_INTERESSE_SICILIA, LUOGHI_INTERESSE_SARDEGNA, CLEANED_SARDEGNA, CLEANED_SICILIA, POI_SARDEGNA_SICILIA, POI_STATS, POI_RDF_TURTLE]
    if all([Path(file).is_file() for file in files]):
        return True
    else:
        return False
