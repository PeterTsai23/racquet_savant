# Import common dependencies
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import streamlit as st
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, TableColumn, DataTable, HoverTool, CrosshairTool, Legend
from bokeh.models.widgets import DataTable
from bokeh.palettes import viridis, plasma
import plotly.express as px
import plotly.graph_objects as go
from math import *
from utils import radar_rescale
    
# Set Container Width to "wide"
st.set_page_config(layout='wide')

# Set Font Style
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Get racquet specs dataframe
df = pd.read_csv('racquet_database.csv')

# Get list of specs
specs = list(df.columns)[3:].copy()
specs_numer = specs[0:len(specs)-1] # Specs with numerical values

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

#################################
#### Set Racquet Spec Ranges ####
if not error:
    st.sidebar.write('')
    st.sidebar.subheader(body='Filter Racquet Specs', divider='red')
    for s in specs:
        if not s == 'String Pattern':
            min_val = floor(sub_df[s].min())
            max_val = ceil(sub_df[s].max())
            if s == 'Polarization Index':
                step = 0.01
                min_val = float(min_val)
                max_val = float(max_val)
            else:
                step = 1
            sel_min, sel_max = st.sidebar.slider(label=s, min_value=min_val, max_value=max_val, value=(min_val, max_val), step=step)
            sub_df = sub_df[(sub_df[s] >= sel_min) & (sub_df[s] <= sel_max)].copy()
            if len(sub_df) == 0:
                break
        else:
            patterns = list(df['String Pattern'].unique())
            patterns.sort()
            select_patterns = []
            st.sidebar.write(s)
            # Structure string pattern checkboxes into 3 columns
            col_1, col_2, col_3 = st.sidebar.columns((1, 1, 1))
            for i, p in enumerate(patterns):
                if i < len(patterns)//3:
                    d_col = col_1
                elif i < 2 * (len(patterns)//3):
                    d_col = col_2
                elif i < 3 * (len(patterns)//3):
                    d_col = col_3
                else:
                    d_col = col_1
                if p in ['16x19', '18x20', '16x20']:
                    T = d_col.checkbox(p, value=True)
                else:
                    T = d_col.checkbox(p, value=False)
                if T:
                    select_patterns.append(p)
            sub_df = sub_df[sub_df['String Pattern'].isin(select_patterns)].copy()
    ########################################
    #### Select Racquets for Comparison ####
    if len(sub_df) > 1:
        ###############
        ## Set specs ##
        st.subheader('Choose up to 7 Specs to Compare')
        select_specs = []
        scol_1, scol_2, scol_3 = st.columns((1, 1, 1))
        col_len = ceil(len(specs_numer)/3)
        for i, s in enumerate(specs_numer):
            if i < col_len:
                display_col = scol_1
            elif i < 2 * col_len:
                display_col = scol_2
            else:
                display_col = scol_3
            if s in ['Headsize (sq in)', 'Weight (g)', 'Balance (cm)', 'Swingweight (kg cm^2)', 'RA Stiffness']:
                T = display_col.checkbox(s, value=True)
            else:
                T = display_col.checkbox(s, value=False)
            if T:
                select_specs.append(s)
        ###############
        # Rescale data for radar chart
        radar_df = radar_rescale(df=df, spec_cols=select_specs, scale_min=1, scale_max=5)
        if len(select_specs) > 2 and len(select_specs) < 8: 
            r1_col, empty_col, r2_col = st.columns((5, 2, 5))
            r1_col.subheader('Racquet #1')
            r2_col.subheader('Racquet #2')
            radar = go.Figure(layout=dict(width=700, height=700, autosize=False))
            fill_color_dict = {0: 'rgba(15, 10, 222, 0.3)', 1: 'rgba(242, 38, 19, 0.3)'}
            line_color_dict = {0: 'rgba(15, 10, 222, 1)', 1: 'rgba(242, 38, 19, 1)'}
            # Select racquets
            for i, rqt_col in enumerate([r1_col, r2_col]):
                sel_brand = rqt_col.selectbox(label='Brand', options=sub_df['Brand'].unique(), key=f"brand_{i}", index=i)
                sel_model = rqt_col.selectbox(label='Model', options=sub_df[sub_df['Brand'] == sel_brand]['Model'].unique(), key=f"model_{i}", index=i)
                rqt_info = sub_df[(sub_df['Brand'] == sel_brand) & (sub_df['Model'] == sel_model)].iloc[0].to_dict()
                rqt_col.write("")
                for k in rqt_info:
                    if not k in ['Brand', 'Model']:
                        if k in select_specs:
                            rqt_col.markdown(f":red[{k}: {rqt_info[k]}]")
                        else:
                            rqt_col.markdown(f"{k}: {rqt_info[k]}")
                r_vals = list(radar_df[(radar_df['Brand'] == sel_brand) & (radar_df['Model'] == sel_model) & (radar_df['Current'] == rqt_info['Current'])][select_specs].iloc[0].values)
                theta_vals = [re.sub("[\(\[].*?[\)\]]", "", s) for s in select_specs]
                radar.add_trace(
                    go.Scatterpolar( 
                        r=r_vals + [r_vals[0]], 
                        theta=theta_vals + [theta_vals[0]], 
                        fill='toself',
                        fillcolor=fill_color_dict[i],
                        line_color=line_color_dict[i],
                        name=f'{sel_brand} {sel_model}'
                    )
                )
            radar.update_layout(font_family='Arial Narrow', font_size=18, showlegend=True)
            radar.update_polars(radialaxis=dict(visible=True, range=[0, 5]))    
            st.plotly_chart(radar, use_container_width=True)
        else:
            st.error(f"Select between 3 and 7 specs to compare.")
    else:
        st.error("Not enough racquets meet the spec constraints for comparison; set a wider range of values.")
        
        

            