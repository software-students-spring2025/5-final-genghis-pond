import pandas as pd

iucn_dist = pd.read_csv('distribution.txt', delimiter = '\t', header=None)

iucn_dist.columns = ['ID', 'notsure', 'scope', 'presence', 'authors', 'conservation_status', 'empty']

iucn_taxon = pd.read_csv('taxon.txt', delimiter = '\t', header=None)

#print("DIST:", iucn_dist.head())

iucn_taxon.rename(columns = {list(iucn_taxon)[0]:'ID', list(iucn_taxon)[1]: 'full_name', list(iucn_taxon)[9]: 'authors'}, inplace=True)

iucn_dist['ID'] = iucn_dist['ID'].astype(int)

iucn_taxon['ID'] = iucn_taxon['ID'].astype(int)

print("TAXON: ", iucn_taxon.columns)

for column in iucn_taxon.columns:
    print(iucn_taxon[column].head())

print("AUTHORS: ", iucn_taxon['authors'])

def clean_name(row):
    """
    Separate out the author from the scientific name
    """
    name = str(row['full_name']).strip()
    author = str(row['authors']).strip()

    if pd.isna(author) or not isinstance(author, str) or author.strip() == '':
        return name

    idx = name.find(author)
    
    if idx != -1:
        return name[:idx].strip().lower()  # remove space + author
    else:
        return name.lower()
    
iucn_taxon['clean_name'] = iucn_taxon.apply(clean_name, axis=1)
iucn_taxon.dropna(subset=['authors'], inplace=True)

print("CLEAN NAME: ", iucn_taxon['clean_name'])

iucn_all = pd.merge(iucn_dist, iucn_taxon, on='ID')
print(iucn_all.head())

full_data = pd.read_csv('full_data.tsv', delimiter='\t')
full_iucn = pd.merge(full_data, iucn_all, left_on='final_scientific_name', right_on='clean_name', how='left')
full_iucn.drop_duplicates(subset=['final_scientific_name'], inplace=True)
print(full_iucn.head())

print('LEN FULL DATA: ', len(full_data))
print('LEN IUCN ALL: ', len(iucn_all))
print('LEN FULL IUCN: ', len(full_iucn))

print(full_iucn['conservation_status'].unique())
crit = ['Critically Endangered', 'Extinct', 'Extinct in the Wild']

full_iucn['crit'] = full_iucn['conservation_status'].isin(crit).astype(int)

full_iucn.to_csv('full_iucn.tsv', sep='\t', index=False)

print(len(full_iucn.drop_duplicates(subset='common_name')))
print(len(full_iucn.drop_duplicates(subset='common_name'))/len(full_iucn))
