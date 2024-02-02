import numpy as np
import pandas as pd
from math import *

def radar_rescale(df, spec_cols, scale_min, scale_max):
    
    radar_df = df[spec_cols].copy()
    delta = scale_max - scale_min
    for c in radar_df.columns:
        max_val = radar_df[c].max()
        min_val = radar_df[c].min()
        radar_df[c] = ((np.array(df[c]) - min_val)/(max_val - min_val) * delta) + scale_min
        
    return radar_df
        