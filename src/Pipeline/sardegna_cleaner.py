import pandas as pd
from . import LUOGHI_INTERESSE_SARDEGNA, CLEANED_SARDEGNA

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

def create_cleaned_sardegna_data():
  # astype(str) turns all values of data frame into strings
    data = pd.read_csv(LUOGHI_INTERESSE_SARDEGNA, encoding="utf-8").astype(str)
    data = delete_incomplete_data_sardegna(data)
    data = filter_open_places_sardegna(data)
  # print(data.isin(['nan']).sum())  used to detect null values
    data = fix_columns_sardegna(data)
    data = cast_prices_sardegna(data)
  # print(data.isin(['nan']).sum())  used to detect null values
    data = fix_fax(data)
    data.to_csv(CLEANED_SARDEGNA, header=cols, index=False)

#Function that removes all rows with a null value in FRBI column(price)
def delete_incomplete_data_sardegna(data_frame):
        data_frame = data_frame.query('FRBI != "nan"')
        return data_frame

#Filters the rows based on the opening and closing of museums
def filter_open_places_sardegna(data_frame):
    data_frame = data_frame.query('FRF == "aperto"')
    data_frame = data_frame.drop("FRF", axis=1)
    return data_frame

#Drops useless columns, manages null values and sorts columns
def fix_columns_sardegna(data_frame):
    data_frame.drop(["NCE", "OGS", "CNL", "AQS", "LCP", "LCL", "FRM", "FRD", "FRBT", "FRBC", "FROP", "FROS", "FROG", "FROO", "FRI", "FRZS", "FRZI", "CNTE", "CNTW", "CNTS"], axis=1, inplace=True)
    #null values for tickets are the ones which were empty. They are free
    data_frame["CNTT"] = data_frame["CNTT"].replace(['nan'], 'NON REGISTRATO')
    data_frame["OGA"] = data_frame["OGA"].replace(['monumento naturale'], 'monumento o complesso monumentale')
    data_frame.loc[data_frame["OGN"] == "Museo Faunistico dell'Oasi di Assai", "OGA"] = "museo, galleria e/o raccolta"
    #fixing ticket prices strings to extract full prices only
    for i in range(data_frame["FRBI"].size):
        val = data_frame["FRBI"].values[i]
        val = val[val.find('e'):]
        val = ''.join([i for i in val if i.isdigit() or i == ',' or i == '/'])
        data_frame["FRBI"].values[i] = val[:val.find('/')]
    data_frame["OGA"] = data_frame["OGA"].replace(['museo, galleria e/o raccolta'], 'museo, galleria, raccolta')
    data_frame["LCC"] = data_frame["LCC"].replace(['Santa Teresa di Gallura'], 'Santa Teresa Gallura')
    #Sorting columns
    data_frame = data_frame[["OGN", "OGA", "LCC", "LCI", "LATITUDINE", "LONGITUDINE", "FRBI", "CNTT"]]
    return data_frame


#Function that converts prices to float values
def cast_prices_sardegna(data_frame):
    try:
        data_frame["FRBI"] = data_frame["FRBI"].str.replace(',', '.').astype(float)
    except ValueError:
        print(ValueError)
    return data_frame

#Remove Fax numbers and fixing telephones
def fix_fax(data_frame):
    data_frame["CNTT"] = data_frame["CNTT"].str.replace(' ', '')
    for i in range(data_frame["CNTT"].size):
        c = data_frame["CNTT"].values[i].split('//')
        contacts = ""
        for j in range(len(c)):
            if "FAX" not in c[j]:
                contacts += c[j] + "//"
        final_str = contacts[:len(contacts) - 2]
        data_frame["CNTT"].values[i] = final_str
    return data_frame