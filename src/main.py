from Pipeline import files_are_present, sardegna_cleaner
from Pipeline.sardegna_cleaner import create_cleaned_sardegna_data
from Pipeline.sicilia_cleaner import create_cleaned_sicilia_data
from Pipeline.combinator import combine_data
from Pipeline.RDF_triples_generator import create_rdf_from_data

if __name__ == '__main__':
    if files_are_present():
        print("Files already processed, skipping elaboration pipeline...")
    else:
        create_cleaned_sardegna_data()
        create_cleaned_sicilia_data()
        combine_data()
        create_rdf_from_data()