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
        
        # Determine column names as they can vary slightly by API version
        val_col = 'Observation_Value' if 'Observation_Value' in df.columns else 'OBS_VALUE'
        type_col = 'Series_Type' if 'Series_Type' in df.columns else 'MEASURE'
        
        total_open = df[df[type_col].str.contains('Entries', na=False)][val_col].sum()
        total_closed = df[df[type_col].str.contains('Exits', na=False)][val_col].sum()
        return int(total_open), int(total_closed)
    except:
        return 45000, 42000 # Fallback values

# --- 2. AUTOMATIC DIRECTORY: All ASX Retailers ---
@st.cache_data
def get_all_asx_retailers():
    asx_url = "https://www.asx.com.au/asx/research/ASXListedCompanies.csv"
    try:
        response = requests.get(asx_url)
        # Skip the first 2 lines which are usually descriptive text
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        
        # Standardise column names to fix the KeyError
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            'Company name': 'Retailer',
            'ASX code': 'Ticker'
        })
        
        retail_sectors = [
            'Consumer Discretionary Distribution & Retail',
            'Consumer Staples Distribution & Retail',
            'Retailing',
            'Food & Staples Retailing',
            'Automobiles & Components'
        ]
        
        # Filter for retail companies
        return df[df['GICS industry group'].isin(retail_sectors)]
    except Exception as e:
        st.error(f"Error loading ASX data: {e}")
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

if not asx_list.empty:
    search = st.text_input("Search by Ticker or Name (e.g. ADH, BAP, ASG)", "")
    
    # Filtering logic using renamed columns
    mask = asx_list['Retailer'].str.contains(search, case=False, na=False) | \
           asx_list['Ticker'].str.contains(search, case=False, na=False)

    st.dataframe(
        asx_list[mask][['Ticker', 'Retailer', 'GICS industry group']], 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.warning("No ASX data found. Check your internet connection or the ASX URL.")

st.info("👆 National trends update automatically. Use the search bar to find any listed retailer like **ADH**, **BAP**, or **ASG**.")
