import pandas as pd
from . import CLEANED_SARDEGNA, CLEANED_SICILIA, POI_SARDEGNA_SICILIA, POI_STATS

def combine_data():
    sardegna = pd.read_csv(CLEANED_SARDEGNA, encoding="utf-8")
    sicilia = pd.read_csv(CLEANED_SICILIA, encoding="utf-8")
    sardegna.insert(0, 'Regione', "Sardegna")
    sicilia.insert(0, 'Regione', "Sicilia")
    mean_price = sardegna["Prezzo"].mean()
    print(round(mean_price, 2))
    sardegna = sardegna.query('Prezzo <= @mean_price')
    mean_price = sicilia["Prezzo"].mean()
    print(round(mean_price, 2))
    sicilia = sicilia.query('Prezzo <= @mean_price')
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
    tot_naturalistic_park_sardegna = sardegna.loc[sardegna["Categoria"] == "parco naturalistico", "Categoria"].count()
    tot_naturalistic_park_sicilia = sicilia.loc[sicilia["Categoria"] == "parco naturalistico", "Categoria"].count()

    stats = [
    ["museo, galleria e/o raccolta", tot_museums_sardegna, str(evaluate_proportion(tot_museums_sardegna, tot_poi_sardegna)) + "%", tot_museums_sicilia, str(evaluate_proportion(tot_museums_sicilia, tot_poi_sicilia)) + "%", percentage_difference(tot_museums_sardegna, tot_museums_sicilia)],
    ["area o parco archeologico", tot_archaeological_areas_sardegna, str(evaluate_proportion(tot_archaeological_areas_sardegna, tot_poi_sardegna)) + "%", tot_archaeological_areas_sicilia, str(evaluate_proportion(tot_archaeological_areas_sicilia, tot_poi_sicilia)) + "%", percentage_difference(tot_archaeological_areas_sardegna, tot_archaeological_areas_sicilia)],
    ["monumento o complesso monumentale", tot_monuments_sardegna, str(evaluate_proportion(tot_monuments_sardegna, tot_poi_sardegna)) + "%", tot_monuments_sicilia, str(evaluate_proportion(tot_monuments_sicilia, tot_poi_sicilia)) + "%", percentage_difference(tot_monuments_sardegna, tot_monuments_sicilia)],
    ["parco naturalistico", tot_naturalistic_park_sardegna, str(evaluate_proportion(tot_naturalistic_park_sardegna, tot_poi_sardegna)) + "%", tot_naturalistic_park_sicilia, str(evaluate_proportion(tot_naturalistic_park_sicilia, tot_poi_sicilia)) + "%", percentage_difference(tot_naturalistic_park_sardegna, tot_naturalistic_park_sicilia)],
    ["Totali", tot_poi_sardegna, None, tot_poi_sicilia, None, percentage_difference(tot_poi_sardegna, tot_poi_sicilia)]
    ]
    data_frame = pd.DataFrame(stats, columns=['POI', 'Total(Sardegna)', 'Total_percentage(Sardegna)', 'Total(Sicilia)', 'Total_percentage(Sicilia)', 'Percentage difference_sardegna_sicilia'])
    data_frame.to_csv(POI_STATS, index=False)

def evaluate_proportion(num, total):
    return round((num * 100)/total, 2)

def percentage_difference(num1, num2):
    return str(round((num1 - num2)/num1, 2) * 100) + "%"
