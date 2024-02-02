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
import plotly.graph_objects as go
from math import *
    
# Set Container Width to "wide"
st.set_page_config(layout='wide')

# Set Font Style
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Get racquet specs dataframe
df = pd.read_csv('racquet_database.csv')

# Get list of specs
specs = list(df.columns)[3:].copy()

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
    else:
        select_brands = brands[1:]
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

    ##############################
    #### Set Specs to Display ####
    spec_cols, col_emp_2, col_emp_3, col_emp_4 = st.columns((1, 1, 1, 1))
    with spec_cols:
        s1 = st.selectbox('Select Spec #1', specs[0:len(specs)-1], index=2)
        s2 = st.selectbox('Select Spec #2', specs[0:len(specs)-1], index=3)
        s1_no_unit = re.sub("\(.*?\)", "", s1).strip()
        s2_no_unit = re.sub("\(.*?\)", "", s2).strip()

    if len(sub_df) > 0:
        ###########################
        #### Plot Racquet Data ####
        st.write('')
        hover = HoverTool(tooltips=[('Brand', '@Brand'), ('Model', '@Model')])
        scatter_source = ColumnDataSource(sub_df)
        color_mapper = CategoricalColorMapper(
            factors=[b for b in sub_df['Brand'].unique()], 
            palette=viridis(len(select_brands))
        )
        scatter_chart = figure(width=1000, height=800, tools=[hover, 'crosshair', 'box_zoom', 'reset'], x_axis_label=s1, y_axis_label=s2)
        scatter_chart.add_layout(Legend(), 'right')
        scatter_chart.circle(x=s1, y=s2, size=10, color=dict(field='Brand', transform=color_mapper), line_alpha=1.0, line_color='gray', fill_alpha=0.7, legend_group='Brand', source=scatter_source)
        scatter_chart.xaxis.axis_label_text_font_size = '18pt'
        scatter_chart.yaxis.axis_label_text_font_size = '18pt'
        scatter_chart.xaxis.major_label_text_font_size = '14pt'
        scatter_chart.yaxis.major_label_text_font_size = '14pt'
        st.bokeh_chart(figure=scatter_chart, use_container_width=False)
        ####################
        #### Plot Table ####
        sub_df.sort_values(by=['Brand', 'Current', 'Model'])
        table = go.Figure(data=[go.Table(
            header=dict(
                values = list(sub_df.columns),
                fill_color = ['#CDAFAF' if c in [s1, s2] else 'lightgrey' for c in sub_df.columns],
                align = 'center'
            ),
            cells=dict(
                values = [sub_df[c] for c in sub_df.columns],
                align = 'center',
                fill_color = ['#FFC7C7' if c in [s1, s2] else '#FFFFFF' for c in sub_df.columns]
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
        csv_file = sub_df.to_csv()
        st.download_button(label="Download Table", data=csv_file, file_name="racquet_specs.csv", type='primary')
    else:
        st.error('There are no racquets that fit the selection of specs.')
    
            