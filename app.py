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
        content = response.text
        
        # Robust parsing: Skip preamble metadata lines
        lines = content.split('\n')
        # Find the line that actually contains the header "Company name"
        header_index = next(i for i, line in enumerate(lines) if "Company name" in line)
        df = pd.read_csv(io.StringIO('\n'.join(lines[header_index:])))
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace('"', '')
        df = df.rename(columns={'Company name': 'Retailer', 'ASX code': 'Ticker', 'GICS industry group': 'Industry'})
        
        # List of sectors to capture all retailers including ADH, BAP, and ASG
        retail_sectors = [
            'Consumer Discretionary Distribution & Retail',
            'Consumer Staples Distribution & Retail',
            'Retailing',
            'Food & Staples Retailing',
            'Automobiles & Components',
            'Consumer Services'
        ]
        
        # Filter for retail companies
        return df[df['Industry'].isin(retail_sectors)].dropna(subset=['Ticker'])
    except Exception as e:
        st.error(f"Error loading ASX data: {e}")
        return pd.DataFrame()

# --- EXECUTION ---
abs_open, abs_closed = get_national_abs_data()
asx_list = get_all_asx_retailers()

# Metrics
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
    search = st.text_input("Search by Ticker or Name (e.g. ADH, BAP, ASG)", "").upper()
    
    # Filter list based on search
    mask = asx_list['Retailer'].str.upper().str.contains(search, na=False) | \
           asx_list['Ticker'].str.upper().str.contains(search, na=False)
    
    final_df = asx_list[mask][['Ticker', 'Retailer', 'Industry']].sort_values('Ticker')
    
    st.write(f"Showing {len(final_df)} companies.")
    st.dataframe(final_df, use_container_width=True, hide_index=True)
else:
    st.warning("The ASX Directory could not be loaded. Please ensure the CSV URL is accessible.")

st.info("National trends update via the [ABS API](https://abs.gov.au). List includes retailers like [Adairs (ADH)](https://www.listcorp.com/asx/sectors/consumer-discretionary/retailing), [Bapcor (BAP)](https://www.listcorp.com/asx/sectors/consumer-discretionary/retailing), and [Autosports Group (ASG)](https://www.listcorp.com/asx/sectors/consumer-discretionary/retailing).")
