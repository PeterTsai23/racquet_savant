import numpy as np
import pandas as pd
from math import *
import streamlit as st
import base64

def radar_rescale(df, spec_cols, scale_min, scale_max):
    
    radar_df = df[['Current', 'Brand', 'Model'] + spec_cols].copy()
    delta = scale_max - scale_min
    for c in spec_cols:
        max_val = radar_df[c].max()
        min_val = radar_df[c].min()
        radar_df[c] = ((np.array(df[c]) - min_val)/(max_val - min_val) * delta) + scale_min
        
    return radar_df