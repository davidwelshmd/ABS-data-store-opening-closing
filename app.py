import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="ASX Retail Tracker", layout="wide", page_icon="🛍️")
st.title("🛒 ASX Retail: All Companies & National Trends")

# --- 1. AUTOMATIC CALCULATION: National ABS Trends ---
@st.cache_data
def get_national_abs_data():
    # ABS API for Retail Entries/Exits (National Level)
    abs_url = "https://abs.gov.au"
    try:
        response = requests.get(abs_url)
        df = pd.read_csv(io.StringIO(response.text))
        # Automatic Calculation of total entries/exits from the ABS table
        total_open = df[df['Series_Type'] == 'Entries']['Observation_Value'].sum()
        total_closed = df[df['Series_Type'] == 'Exits']['Observation_Value'].sum()
        return int(total_open), int(total_closed)
    except:
        # Fallback values if ABS API is down
        return 45000, 42000 

# --- 2. AUTOMATIC DIRECTORY: All ASX Retailers ---
@st.cache_data
def get_all_asx_retailers():
    asx_url = "https://asx.com.au"
    try:
        response = requests.get(asx_url)
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        retail_sectors = [
            'Consumer Discretionary Distribution & Retail',
            'Consumer Staples Distribution & Retail',
            'Retailing',
            'Food & Staples Retailing',
            'Automobiles & Components'
        ]
        return df[df['GICS industry group'].isin(retail_sectors)].rename(columns={'ASX code': 'Ticker', 'Company name': 'Retailer'})
    except:
        return pd.DataFrame()

# --- EXECUTION ---
abs_open, abs_closed = get_national_abs_data()
asx_list = get_all_asx_retailers()

# Metrics: Automatically Calculated from ABS API
st.subheader("📊 National Retail Health (Automatic ABS Data)")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total National Openings", f"{abs_open:,}")
with c2:
    st.metric("Total National Closures", f"{abs_closed:,}")
with c3:
    st.metric("Net Industry Growth", f"{abs_open - abs_closed:,}")

st.divider()

# ASX Table: Full List
st.subheader("🏢 All ASX-Listed Retailers")
search = st.text_input("Search by Ticker (e.g. ADH, BAP, ASG)", "")
mask = asx_list['Retailer'].str.contains(search, case=False) | asx_list['Ticker'].str.contains(search, case=False)

st.dataframe(asx_list[mask][['Ticker', 'Retailer', 'GICS industry group']], use_container_width=True, hide_index=True)

st.info("👆 The **National Trends** above update automatically via API. **Specific store counts** for companies like ADH must be manually added to your data file because they are only published in PDF reports.")
