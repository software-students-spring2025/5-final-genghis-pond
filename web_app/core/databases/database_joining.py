"""
Connect scientific names from the ML package with common names
"""

import pandas as pd

geofence_terms = pd.read_json('geofence_base.json')

print(geofence_terms)

terms = pd.DataFrame({
    'full_term': geofence_terms.columns,
    'allowed_countries': [geofence_terms[col] for col in geofence_terms.columns]
})
terms['allowed_country_list'] = terms['allowed_countries'].apply(lambda x: list(x.keys()))

terms['spaced_term'] = terms['full_term'].str.replace(';', ' ', regex=False)

split_terms = terms['full_term'].str.split(';', expand=True)

terms['genus'] = split_terms[3].str.lower()
terms['species'] = split_terms[4].str.lower()

terms['scientific_name'] = terms['genus'] + ' ' + terms['species']

ml_terms = terms

vern = pd.read_csv('VernacularName.tsv', delimiter = '\t')

vern = vern[vern['dcterms:language'] == 'eng']


taxon = pd.read_csv('Taxon.tsv', delimiter='\t', on_bad_lines='skip')

combine_terms = pd.merge(vern, taxon, on='dwc:taxonID', how='inner')

taxon_subset = combine_terms[['dwc:scientificName', 'dwc:scientificNameAuthorship']].copy()

taxon_subset = taxon_subset.dropna()


def clean_name(row):
    """
    Separate out the author from the scientific name
    """
    name = row['dwc:scientificName']
    author = row['dwc:scientificNameAuthorship']
    if name.endswith(' ' + author):
        return name[:-(len(author)+1)]  # remove space + author
    else:
        return name

combine_terms['scientificName_cleaned'] = taxon_subset.apply(clean_name, axis=1)

combine_terms['scientificName_cleaned'] = combine_terms['scientificName_cleaned'].str.encode('latin1', errors='ignore').str.decode('utf-8', errors='ignore')
combine_terms['scientificName_cleaned'] = combine_terms['scientificName_cleaned'].str.lower()
combine_terms.drop_duplicates(subset=['scientificName_cleaned'], inplace=True)

print("ML TERMS", ml_terms['scientific_name'].sort_values().head(30))
print("COMBINE TERMS", combine_terms['scientificName_cleaned'].sort_values().head(30))

print(taxon.columns)

full_data = pd.merge(ml_terms, combine_terms, left_on = 'scientific_name', right_on = 'scientificName_cleaned', how='outer')
print(len(full_data))

full_data['final_scientific_name'] = full_data['scientific_name'].fillna(full_data['scientificName_cleaned'])
full_data['common_name'] = full_data['dwc:vernacularName'].fillna(full_data['final_scientific_name'])
full_data['common_name'] = full_data['common_name'].str.lower()
print(full_data.columns)
print(full_data[['final_scientific_name', 'common_name']].head())
print(len(full_data))

full_data.to_csv('full_data.tsv', sep='\t', index=False)


