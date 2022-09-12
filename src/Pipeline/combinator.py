import pandas as pd
from . import CLEANED_SARDEGNA, CLEANED_SICILIA, POI_SARDEGNA_SICILIA, POI_STATS

def combine_data():
    sardegna = pd.read_csv(CLEANED_SARDEGNA, encoding="utf-8")
    sicilia = pd.read_csv(CLEANED_SICILIA, encoding="utf-8")
    #Adding region columns in data_frames
    sardegna.insert(0, 'Regione', "Sardegna")
    sicilia.insert(0, 'Regione', "Sicilia")
    #Concatenating data_frames
    combined = pd.concat([sardegna, sicilia])
    combined.to_csv(POI_SARDEGNA_SICILIA, index=False)
