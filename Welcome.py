import streamlit as st

# Set Font Style
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Insert RS logo
st.image('rs_logo_black.jpeg', use_column_width=True)

# Page content
st.markdown(
    """
    ##### Racquet Savant provides a user-friendly interactive tool for exploring the technical specifications of racquets within an extensive dataset† that contains both discontinued and currently available models. The app is separated into three pages, each with a different functionality.
    
    #### Discover 
    Filter the database to discover racquets that meet the desired spec ranges
    
    #### Compare
    Visualize how two racquets compare with one another
    
    #### Match 
    Search for similar racquets based on a set of user-defined specs 
    
    † All spec data is scraped from the publicly accessible Tennis Warehouse University website
"""
)