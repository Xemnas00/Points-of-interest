import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from . import LUOGHI_INTERESSE_SICILIA, CLEANED_SICILIA

#Output columns
cols = [
    "Denominazione",
    "Categoria",
    "Comune",
    "Indirizzo",
    "Latitudine",
    "Longitudine",
    "Prezzo",
    "Contatti"
]

def create_cleaned_sicilia_data():
  # astype() turns all values of data frame into strings
    data = pd.read_csv(LUOGHI_INTERESSE_SICILIA, encoding="utf-8").astype(str)
    data = filter_open_places_sicilia(data)
    data = fix_columns_sicilia(data)
    data = delete_incomplete_data_sicilia(data)
    data = fix_prices_sicilia(data)
    data = fix_categories_sicilia(data)
    data = fix_addresses_sicilia(data)
    data = retrieve_lat_long_from_addresses_sicilia(data)
    data = fix_phone_numbers_sicilia(data)
    data.to_csv(CLEANED_SICILIA, header=cols, index=False)

def filter_open_places_sicilia(data_frame):
    data_frame["Orari"] = data_frame["Orari"].map(str.lower)
    pattern1 = re.compile(".*(((lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica).*chiuso)|(chiuso.*(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica)))")
    pattern2 = re.compile("(.*chiuso.*)|(.*non aperto.*)|(.*in atto chiuse al pubblico.*)")
    for i in range(data_frame["Orari"].size):
        if pattern1.match(data_frame["Orari"].values[i]) != None:
            data_frame["Orari"].values[i] = "APERTO"
        elif pattern2.match(data_frame["Orari"].values[i]) != None:
            data_frame["Orari"].values[i] = "CHIUSO"
    data_frame = data_frame.query('Orari != "CHIUSO"')
    return data_frame

def fix_columns_sicilia(data_frame):
    data_frame.drop(["Provincia", "Orari", "Biglietto ridotto", "Note", "scheda"], axis=1, inplace=True)
    data_frame["Latitudine"] = "nan"
    data_frame["Longitudine"] = "nan"
    data_frame.rename(columns={"Biglietto intero" : "Prezzo", "Telefono" : "Contatti"}, inplace=True)
    data_frame = data_frame[cols]
    return data_frame

#Function that removes all rows with a null value in "Prezzo"
def delete_incomplete_data_sicilia(data_frame):
        data_frame = data_frame.query('Prezzo != "nan"')
        return data_frame

def fix_prices_sicilia(data_frame):
    data_frame["Prezzo"] = data_frame["Prezzo"].replace(['Gratuito'], '0,00 €')
    data_frame["Prezzo"] = data_frame["Prezzo"].replace(['Ingresso libero'], '0,00 €')
    data_frame["Prezzo"] = data_frame["Prezzo"].replace(['Unico con Museo di Kamarina'], data_frame["Prezzo"].values[data_frame.index[data_frame["Denominazione"] == "Museo regionale di Kamarina"]])
    data_frame["Prezzo"] = data_frame["Prezzo"].str.replace(" ", "")
    data_frame["Prezzo"] = data_frame["Prezzo"].str.replace("€", "")
    data_frame["Prezzo"] = data_frame["Prezzo"].str.replace(",", ".")
    try:
        data_frame["Prezzo"] = data_frame["Prezzo"].astype(float)
    except ValueError:
        print(ValueError)
    return data_frame

def fix_categories_sicilia(data_frame):
    data_frame["Categoria"] = data_frame["Categoria"].map(str.lower)
    for i in range(data_frame["Categoria"].size):
        if "musei" in data_frame["Categoria"].values[i] or "antiquaria" in data_frame["Categoria"].values[i]:
            data_frame["Categoria"].values[i] = "museo, galleria, raccolta"
        elif "archeologiche" in data_frame["Categoria"].values[i]:
            data_frame["Categoria"].values[i] = "area o parco archeologico"
        elif "monumentale" in data_frame["Categoria"].values[i]:
            data_frame["Categoria"].values[i] = "monumento o complesso monumentale"
    data_frame = data_frame.query("Categoria != 'parco naturalistico'")
    return data_frame

def fix_addresses_sicilia(data_frame):
    data_frame["Indirizzo"] = data_frame["Indirizzo"].map(str.lower)
    pattern = re.compile("(via|viale|piazza|corso|piazzetta|lungomare)")
    pattern2 = re.compile("[a-z]+(,|\))*")
    for i in range(data_frame["Indirizzo"].size):
        vett = data_frame["Indirizzo"].values[i].split()
        result = ""
        for j in range(len(vett)):
            if pattern.match(vett[j]):
                result = vett[j]
                j += 1
                while j<len(vett) and pattern2.match(vett[j]) != None:
                    result += " " + vett[j]
                    j += 1
        result = result.replace(",", "")
        result = result.replace(")", "")
        if result != "":
            data_frame["Indirizzo"].values[i] = result + ", " + data_frame["Comune"].values[i] +", Italia"
        else:
            data_frame["Indirizzo"].values[i] = "nan"
    for i in range(data_frame["Indirizzo"].size):
        if data_frame["Indirizzo"].values[i] == 'nan':
            data_frame["Indirizzo"].values[i] = data_frame["Comune"].values[i] + ', Italia'
        else:
            data_frame["Indirizzo"].values[i] = data_frame["Indirizzo"].values[i].replace("snc", "")
    data_frame["Indirizzo"] = data_frame["Indirizzo"].replace(['via regina margherita, Palermo, Italia'], 'viale regina margherita, Palermo, Italia')
    data_frame["Indirizzo"] = data_frame["Indirizzo"].replace(['via patti, Palermo, Italia'], 'via crispi, Palermo, Italia')
    data_frame["Indirizzo"] = data_frame["Indirizzo"].replace(['corso vittorio emanuele n., Palermo, Italia'], 'corso vittorio emanuele, Palermo, Italia')
    data_frame["Indirizzo"] = data_frame["Indirizzo"].replace(['via cavagrande, Ispica, Italia'], 'Ispica, Italia')
    data_frame["Indirizzo"] = data_frame["Indirizzo"].replace(['via dante, Licata, Italia'], 'Licata, Italia')
    return data_frame

def retrieve_lat_long_from_addresses_sicilia(data_frame):
    geolocator = Nominatim(user_agent="sicilia_cleaner.py")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)
    df = pd.DataFrame({})
    df["Name"] = data_frame["Indirizzo"]
    df["Location"] = df["Name"].apply(geocode)
    df["Point"] = df["Location"].apply(lambda loc: tuple(loc.point) if loc else None)
    for i in range(df["Point"].size):
        if df["Point"].values[i] != None:
            data_frame["Latitudine"].values[i] = df["Point"].values[i][0]
            data_frame["Longitudine"].values[i] = df["Point"].values[i][1]
    #Fixing "Casa Museo Giovanni Verga" coordinates
    data_frame.loc[data_frame.Denominazione == "Casa Museo Giovanni Verga", ['Latitudine', 'Longitudine']] = '37.51166', '15.0867'
    #Fixing "Teatro Romano e Odeon di Catania" coordinates
    data_frame.loc[data_frame.Denominazione == "Teatro Romano e Odeon di Catania", ['Latitudine', 'Longitudine']] = '37.502935949999994', '15.082842766671142'
    #Fixing "Palazzo Ajutamicristo" coordinates
    data_frame.loc[data_frame.Denominazione == "Palazzo Ajutamicristo", ['Latitudine','Longitudine']] = '38.1135383', '13.367108349385965'
    #Fixing "Museo regionale badia" coordinates
    data_frame.loc[data_frame.Denominazione == "Museo archeologico regionale della Badia", ['Latitudine','Longitudine']] = '37.10329', '13.94061'
    #Fixing "Area archeologica della Neapolis, Orecchio di Dionisio e Teatro Greco" coordinates
    data_frame.loc[data_frame.Denominazione == "Area archeologica della Neapolis, Orecchio di Dionisio e Teatro Greco", ['Latitudine','Longitudine']] = '37.0856', '15.28407'
    #Fixing "Castello di Spadafora" coordinates
    data_frame.loc[data_frame.Denominazione == "Castello di Spadafora", ['Latitudine','Longitudine']] = '38.22294', '15.38009'
    #Fixing "Castello Grifeo" coordinates
    data_frame.loc[data_frame.Denominazione == "Castello Grifeo", ['Latitudine', 'Longitudine']] = '37.72788', '12.88747'
    #Fixing "Museo regionale di Adrano" coordinates
    data_frame.loc[data_frame.Denominazione == "Museo regionale di Adrano", ['Latitudine', 'Longitudine']] = '37.66048', '14.83759'
    # Fixing "Area archeologica Caucana" coordinates
    data_frame.loc[data_frame.Denominazione == "Area archeologica Caucana", ['Latitudine', 'Longitudine']] = '36.78818347420917', '14.506530958461992'
    # Fixing "Teatro Greco Romano di Taormina" coordinates
    data_frame.loc[data_frame.Denominazione == "Teatro Greco Romano di Taormina", ['Latitudine', 'Longitudine']] = '37.852929121406525', '15.290567555301687'
    # Fixing "Chiostro Santa Maria la Nuova (Duomo)" coordinates
    data_frame.loc[data_frame.Denominazione == "Chiostro Santa Maria la Nuova (Duomo)", ['Latitudine', 'Longitudine']] = '38.117076425936666', '13.344571841817114'
    # Fixing "Giardino di Villa Napoli e Piccola Cuba" coordinates
    data_frame.loc[data_frame.Denominazione == "Giardino di Villa Napoli e Piccola Cuba", ['Latitudine', 'Longitudine']] = '38.1061861890964', '13.33619745003384'
    # Fixing "Area archeologica Teatro antico e Antiquarium di Tindari" coordinates
    data_frame.loc[data_frame.Denominazione == "Area archeologica Teatro antico e Antiquarium di Tindari", ['Latitudine', 'Longitudine']] = '38.13854384872103', '14.96543751112948'
    # Fixing "Museo archeologico regionale di Marianopoli" coordinates
    data_frame.loc[data_frame.Denominazione == "Museo archeologico regionale di Marianopoli", ['Latitudine', 'Longitudine']] = '37.599103388483144', '13.913222539950656'
    # Fixing "Museo archeologico regionale Bernabo' Brea a Lipari" coordinates
    data_frame.loc[data_frame.Denominazione == "Museo archeologico regionale Bernabo' Brea a Lipari", ['Latitudine', 'Longitudine']] = '38.46720040958127', '14.956468718927361'
    # Fixing "Area archeologica e Antiquarium di Solunto" coordinates
    data_frame.loc[data_frame.Denominazione == "Area archeologica e Antiquarium di Solunto", ['Latitudine', 'Longitudine']] = '38.09191111161576', '13.532400566616872'
    # Fixing "Antiquarium di Milazzo" coordinates
    data_frame.loc[data_frame.Denominazione == "Antiquarium di Milazzo", ['Latitudine', 'Longitudine']] = '38.22606367442193', '15.2412067571643'
    # Fixing "Ipogeo Romano" coordinates
    data_frame.loc[data_frame.Denominazione == "Ipogeo Romano", ['Latitudine', 'Longitudine']] = '37.51366583510854', '15.08021203994833'
    # Fixing "Museo archeologico regionale di Lentini" coordinates
    data_frame.loc[data_frame.Denominazione == "Museo archeologico regionale di Lentini", ['Latitudine', 'Longitudine']] = '37.28850456039487', '15.001932180417898'
    # Fixing "Museo archeologico regionale di Centuripe" coordinates
    data_frame.loc[data_frame.Denominazione == "Museo archeologico regionale di Centuripe", ['Latitudine', 'Longitudine']] = '37.62224712517353', '14.741658426459338'
    # Fixing "Museo regionale Agostino Pepoli di Trapani - Museo interdisciplinare" coordinates
    data_frame.loc[data_frame.Denominazione == "Museo regionale Agostino Pepoli di Trapani - Museo interdisciplinare", ['Latitudine', 'Longitudine']] = '38.018939729546375', '12.54247101668273'
    return data_frame

def fix_phone_numbers_sicilia(data_frame):
    pattern = re.compile(".*[0-9]{5}.*")
    for i in range(data_frame["Contatti"].size):
        if pattern.match(data_frame["Contatti"].values[i]) == None:
            data_frame["Contatti"].values[i] = "NON REGISTRATO"
        data_frame["Contatti"].values[i] = data_frame["Contatti"].values[i].replace(";", " ")
    return data_frame