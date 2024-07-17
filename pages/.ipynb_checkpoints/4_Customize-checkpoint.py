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
st.subheader("Balanced Customization")
    
            