import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from . import LUOGHI_INTERESSE_SICILIA, CLEANED_SICILIA

#Output columns
cols = [
    "Denominazione",
    "Categoria",
    "Sottocategoria",
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
    data_frame["Sottocategoria"] = "nan"
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
    else:
        mean_price = data_frame["Prezzo"].mean()
        print(round(mean_price, 2))
        data_frame = data_frame.query('Prezzo <= @mean_price')
    return data_frame


def extract_subcategory_from_category_sicilia(data_frame):
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
            data_frame["Indirizzo"].values[i] = result + ", " + data_frame["Comune"].values[i] + ", Italia"
        else:
            data_frame["Indirizzo"].values[i] = "nan"
    for i in range(data_frame["Indirizzo"].size):
        if data_frame["Indirizzo"].values[i] == 'nan':
            data_frame["Indirizzo"].values[i] = data_frame["Comune"].values[i] + ', Italia'
        else:
            data_frame["Indirizzo"].values[i] = data_frame["Indirizzo"].values[i].replace("snc", "")
    return data_frame

def retrieve_lat_long_from_addresses_sicilia(data_frame):
    geolocator = Nominatim(user_agent="sicilia_cleaner.py")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)
    df = pd.DataFrame({})
    df["Name"] = data_frame["Indirizzo"]
    df["Location"] = df["Name"].apply(geocode)
    df["Point"] = df["Location"].apply(lambda loc: tuple(loc.point) if loc else None)
    df2 = pd.DataFrame({'Name': ['Sicilia, Italia']})
    df2["Location"] = df2["Name"].apply(geocode)
    df2["Point"] = df2["Location"].apply(lambda loc: tuple(loc.point) if loc else None)
    for i in range(df["Point"].size):
        if df["Point"].values[i] != None:
            data_frame["Latitudine"].values[i] = df["Point"].values[i][0]
            data_frame["Longitudine"].values[i] = df["Point"].values[i][1]
        else:
            data_frame["Latitudine"].values[i] = df2["Point"].values[0][0]
            data_frame["Longitudine"].values[i] = df2["Point"].values[0][1]
    return data_frame

def fix_phone_numbers_sicilia(data_frame):
    pattern = re.compile(".*[0-9]{5}.*")
    for i in range(data_frame["Contatti"].size):
        if pattern.match(data_frame["Contatti"].values[i]) == None:
            data_frame["Contatti"].values[i] = "NON REGISTRATO"
        data_frame["Contatti"].values[i] = data_frame["Contatti"].values[i].replace(";", " ")

    return data_frame



