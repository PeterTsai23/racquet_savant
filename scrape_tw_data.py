# Import dependencies
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.preprocessing import StandardScaler

######################################
#### Scrape Data From TWU Website ####
######################################

# Set up BeautifulSoup scraper
url = "https://twu.tennis-warehouse.com/cgi-bin/recommender.cgi"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# Scrape data from current and non-current racquets separately
datapoints_not_current = soup.find_all("div", class_="circlegrey notcurrent")
datapoints_current = soup.find_all("div", class_="circlegrey current")

#############################
#### Configure Dataframe ####
#############################

# Define columns to extract
idx_to_col = {
    1: 'Brand', 
    2: 'Model', 
    4: 'Headsize (sq in)', 
    5: 'Length (in)', 
    6: 'Swingweight (kg cm^2)',
    7: 'Twistweight (kg cm^2)',
    14: 'Vibration Frequency (Hz)',
    15: 'Sweet Zone (sq in)',
    16: 'Weight (g)',
    17: 'Balance (cm)',
    24: 'RA Stiffness'
}
# Create dataframe 
racquets_data = []
for k, datapoints in enumerate([datapoints_current, datapoints_not_current]):
    for d in datapoints:
        racquet_dict = {}
        if k == 0:
            racquet_dict['Current'] = True
        else:
            racquet_dict['Current'] = False
        spec_list = d.attrs['id'].split('||')
        for i in idx_to_col:
            try:
                value = spec_list[i]
                if i == 2:
                    value = ' '.join(value.split('_'))
                elif i > 2:
                    value = float(value)
                racquet_dict[idx_to_col[i]] = value
            except:
                racquet_dict[idx_to_col[i]] = None
        racquet_dict['String Pattern'] = f'{spec_list[-3]}x{spec_list[-2][0:2]}'
        racquets_data.append(racquet_dict)
df = pd.DataFrame(racquets_data)
df.dropna(inplace=True)

##############################################################
#### Add Columns for Recoil Weight and Polarization Index ####
##############################################################

df['Recoil Weight (kg cm^2)'] = df['Swingweight (kg cm^2)'] - (0.001*df['Weight (g)'] * (df['Balance (cm)'] - 10)**2)
df['Recoil Weight (kg cm^2)'] = df['Recoil Weight (kg cm^2)'].apply(lambda x: int(round(x, 0)))
df['Polarization Index'] = df['Recoil Weight (kg cm^2)']/df['Weight (g)']
df['Polarization Index'] = df['Polarization Index'].apply(lambda x: round(x, 2))

#############################
#### Save df to CSV File ####
#############################

# Reorder columns
df_cols = [
    'Current',
    'Brand',
    'Model',
    'Headsize (sq in)', 
    'Length (in)', 
    'Weight (g)', 
    'Balance (cm)', 
    'Swingweight (kg cm^2)', 
    'Twistweight (kg cm^2)', 
    'Recoil Weight (kg cm^2)', 
    'Polarization Index',
    'Sweet Zone (sq in)',
    'RA Stiffness',
    'Vibration Frequency (Hz)',
    'String Pattern'
]
df = df[df_cols].copy()
specs_numer = df_cols[3:14]

# Replace incorrect values
df['Headsize (sq in)'].replace(11.0, 115.0, inplace=True)
df['Twistweight (kg cm^2)'].replace(115.0, 11.5, inplace=True)

# Aggregate duplicated racquets by averaging
df = df.groupby(by=['Current', 'Brand', 'Model', 'String Pattern'], as_index=False)[specs_numer].mean()
df = df[df_cols].copy()

# Save to file
df.to_csv('racquet_database.csv', index=False)
