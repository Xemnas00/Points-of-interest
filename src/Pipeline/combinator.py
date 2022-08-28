import pandas as pd
from . import CLEANED_SARDEGNA, CLEANED_SICILIA, POI_SARDEGNA_SICILIA, POI_STATS

def combine_data():
    sardegna = pd.read_csv(CLEANED_SARDEGNA, encoding="utf-8")
    sicilia = pd.read_csv(CLEANED_SICILIA, encoding="utf-8")
    sardegna.insert(0, 'Regione', "Sardegna")
    sicilia.insert(0, 'Regione', "Sicilia")
    combined = pd.concat([sardegna, sicilia])
    combined.to_csv(POI_SARDEGNA_SICILIA, index=False)

    tot_poi_sardegna = sardegna["Categoria"].count()
    tot_poi_sicilia = sicilia["Categoria"].count()
    tot_museums_sardegna = sardegna.loc[sardegna["Categoria"] == "museo, galleria e/o raccolta", "Categoria"].count()
    tot_museums_sicilia = sicilia.loc[sicilia["Categoria"] == "museo, galleria e/o raccolta", "Categoria"].count()
    tot_archaeological_areas_sardegna = sardegna.loc[sardegna["Categoria"] == "area o parco archeologico", "Categoria"].count()
    tot_archaeological_areas_sicilia = sicilia.loc[sicilia["Categoria"] == "area o parco archeologico", "Categoria"].count()
    tot_monuments_sardegna = sardegna.loc[sardegna["Categoria"] == "monumento o complesso monumentale", "Categoria"].count()
    tot_monuments_sicilia = sicilia.loc[sicilia["Categoria"] == "monumento o complesso monumentale", "Categoria"].count()
    mean_price_museums_sardegna = round(sardegna.loc[sardegna["Categoria"] == "museo, galleria e/o raccolta", "Prezzo"].mean(), 2)
    mean_price_museums_sicilia = round(sicilia.loc[sicilia["Categoria"] == "museo, galleria e/o raccolta", "Prezzo"].mean(), 2)
    mean_price_archaeological_areas_sardegna = round(sardegna.loc[sardegna["Categoria"] == "area o parco archeologico", "Prezzo"].mean(), 2)
    mean_price_archaeological_areas_sicilia = round(sicilia.loc[sicilia["Categoria"] == "area o parco archeologico", "Prezzo"].mean(), 2)
    mean_price_monuments_sardegna = round(sardegna.loc[sardegna["Categoria"] == "monumento o complesso monumentale", "Prezzo"].mean(), 2)
    mean_price_monuments_sicilia = round(sicilia.loc[sicilia["Categoria"] == "monumento o complesso monumentale", "Prezzo"].mean(), 2)

    stats = [
    ["museo, galleria e/o raccolta", tot_museums_sardegna, str(evaluate_proportion(tot_museums_sardegna, tot_poi_sardegna)) + "%", mean_price_museums_sardegna,  tot_museums_sicilia, str(evaluate_proportion(tot_museums_sicilia, tot_poi_sicilia)) + "%", mean_price_museums_sicilia],
    ["area o parco archeologico", tot_archaeological_areas_sardegna, str(evaluate_proportion(tot_archaeological_areas_sardegna, tot_poi_sardegna)) + "%", mean_price_archaeological_areas_sardegna, tot_archaeological_areas_sicilia, str(evaluate_proportion(tot_archaeological_areas_sicilia, tot_poi_sicilia)) + "%", mean_price_archaeological_areas_sicilia],
    ["monumento o complesso monumentale", tot_monuments_sardegna, str(evaluate_proportion(tot_monuments_sardegna, tot_poi_sardegna)) + "%", mean_price_monuments_sardegna, tot_monuments_sicilia, str(evaluate_proportion(tot_monuments_sicilia, tot_poi_sicilia)) + "%", mean_price_monuments_sicilia],
    ["Totali", tot_poi_sardegna, None, None, tot_poi_sicilia, None, None]
    ]
    data_frame = pd.DataFrame(stats, columns=['POI', 'Totali(Sardegna)', 'Percentuali(Sardegna)', 'Prezzo medio in euro(Sardegna)', 'Totali(Sicilia)', 'Percentuali(Sicilia)', 'Prezzo medio in euro(Sicilia)'])
    data_frame.to_csv(POI_STATS, index=False)

def evaluate_proportion(num, total):
    return round((num * 100)/total, 2)
