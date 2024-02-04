# Import common dependencies
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import streamlit as st
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, TableColumn, DataTable, HoverTool, CrosshairTool, Legend, CategoricalColorMapper
from bokeh.models.widgets import DataTable
from bokeh.palettes import viridis, plasma
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist
from math import *
from utils import radar_rescale
    
# Set Container Width to "wide"
st.set_page_config(layout='wide')

# Set Font Style
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Get racquet specs dataframe
df = pd.read_csv('racquet_database.csv')
df_cols = list(df.columns)

# Get list of specs
specs = list(df.columns)[3:].copy()
specs_numer = specs[0:len(specs)-1] # Specs with numerical values

# StandardScaler numerical columns
scaler = StandardScaler()
scaler.fit(df[specs_numer].copy())

##################################
#### Select Availability Type ####
st.sidebar.subheader(body='Retail Availability', divider='red')
current_dict = {'Available': True, 'Discontinued': False}
availability = []
for t in ['Available', 'Discontinued']:
    T = st.sidebar.checkbox(label=t, value=True)
    if T:
        availability.append(current_dict[t])
sub_df = df[df['Current'].isin(availability)].copy()
if len(sub_df) < 1:
    error = st.error('Please choose at least one availability type.')
else:
    error = False

#######################
#### Select Brands ####
if not error:
    # Get list of brands
    brands = ['All Brands'] + list(sub_df['Brand'].unique())
    st.sidebar.subheader(body='Select Brands', divider='red')
    select_brands = []
    # Structure brand checkboxes into 2 columns
    col1, col2 = st.sidebar.columns((1, 1))
    for i, b in enumerate(brands):
        if i < len(brands)//2:
            display_col = col1
        elif i < 2 * (len(brands)//2):
            display_col = col2
        else:
            display_col = col1
        brand_label = ' '.join(b.split('_'))
        if b in ['Head', 'Wilson', 'Yonex', 'Babolat', 'Prince', 'Tecnifibre', 'Dunlop']:
            T = display_col.checkbox(brand_label, value=True)
        else:
            T = display_col.checkbox(brand_label, value=False)
        if T: 
            select_brands.append(b)
    if not 'All Brands' in select_brands:
        sub_df = sub_df[sub_df['Brand'].isin(select_brands)].copy()
    if len(sub_df) < 1:
        error = st.error('Please choose at least one brand.')
    else:
        error = False

#######################################
#### Set Relative Spec Importances ####
if not error:
    sub_df.reset_index(drop=True, inplace=True)
    # Select target racquet
    st.subheader('Select Target Racquet')
    rqt_col, empty_1, empty_2 = st.columns((1, 1, 1))
    sel_brand = rqt_col.selectbox(label='Brand', options=sub_df['Brand'].unique(), key=f"brand_{i}", index=0)
    sel_model = rqt_col.selectbox(label='Model', options=sub_df[sub_df['Brand'] == sel_brand]['Model'].unique(), key=f"model_{i}", index=0)
    rqt_idx = sub_df.index[(sub_df['Brand'] == sel_brand) & (sub_df['Model'] == sel_model)].to_list()[0]
    # Set spec importance weights
    st.divider()
    st.subheader('Set Relative Importances of Specs')
    st.write('')
    st.markdown("""
        The sliders enable you to find similar racquets based on the specs you care most about matching by assigning a relative "weight" to each spec between a value of 0 and 100. For example, if you care only to match swingweight and RA stiffness, set all other spec importances to zero but keep importance values for swingweight and RA stiffness at the same non-zero number. If you wish to prioritize matching swingweight and treat stiffness as a secondary spec, you can set the swingweight slider all the way to the right and less so for the stiffness slider (e.g., Swingweight - 100, RA Stiffness - 85). The default setting will treat every spec equally.   
    """)
    st.divider()
    empty_0, spec_col_1, empty_1, spec_col_2, empty_2 = st.columns((1, 5, 1, 5, 1))
    weight_vector = []
    for i, s in enumerate(specs_numer):
        if i < len(specs_numer)//2:
            weight = spec_col_1.slider(label=s, min_value=0, max_value=100, value=50)
        else:
            weight = spec_col_2.slider(label=s, min_value=0, max_value=100, value=50)
        weight_vector.append(weight)
    weight_vector = np.array(weight_vector)
    # Scaler transform sub_df
    sub_df_norm = scaler.transform(sub_df[specs_numer])
    # Add weights
    weighted_matrix = np.array(sub_df_norm) * weight_vector
    ###############################
    #### Find Similar Racquets ####
    spec_col_1.write("")
    if spec_col_1.button('Search for Similar', type='primary'):
        # Calculate distances
        dist_vector = cdist(weighted_matrix[rqt_idx, :].reshape(1, -1), weighted_matrix).ravel()
        sub_df['similarity_dist'] = dist_vector
        sub_df.drop(index=rqt_idx, inplace=True)
        # Sort dataframe by similarity
        sub_df.sort_values('similarity_dist', inplace=True)
        sub_df['Similarity Rank'] = sub_df['similarity_dist'].rank(method='max')
        sub_df = sub_df[['Similarity Rank'] + df_cols].copy()
        # Display results
        table = go.Figure(data=[go.Table(
            header=dict(
                values = list(sub_df.columns),
                align = 'center'
            ),
            cells=dict(
                values = [sub_df[c] for c in sub_df.columns],
                align = 'center',
            )
        )])
        table.update_traces(
            cells_font=dict(
                family = 'Arial Narrow',
                color = 'black'
            ),
            header_font=dict(
                family = 'Arial Narrow',
                color = 'black'
            )
        )
        st.write("")
        st.plotly_chart(table, use_container_width=True)
    