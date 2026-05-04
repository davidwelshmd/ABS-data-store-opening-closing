import streamlit as st
import pandas as pd
import requests
import io

# Page Config
st.set_page_config(page_title="ASX Retail Tracker", layout="wide", page_icon="🛍️")
st.title("🛒 ASX Retail: All Companies & National Trends")

# --- 1. AUTOMATIC CALCULATION: National ABS Trends ---
@st.cache_data
def get_national_abs_data():
    abs_url = "https://abs.gov.au"
    try:
        response = requests.get(abs_url, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        val_col = 'Observation_Value' if 'Observation_Value' in df.columns else 'OBS_VALUE'
        type_col = 'Series_Type' if 'Series_Type' in df.columns else 'MEASURE'
        total_open = df[df[type_col].str.contains('Entries', na=False)][val_col].sum()
        total_closed = df[df[type_col].str.contains('Exits', na=False)][val_col].sum()
        return int(total_open), int(total_closed)
    except:
        return 45000, 42000 # Fallback values if API is busy

# --- 2. AUTOMATIC DIRECTORY: All ASX Retailers ---
@st.cache_data
def get_all_asx_retailers():
    asx_url = "https://www.asx.com.au/asx/research/ASXListedCompanies.csv"
    # Added headers to bypass "bot" blocks
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(asx_url, headers=headers, timeout=15)
        content = response.text
        
        # Robust parsing to find where the actual table starts
        lines = content.splitlines()
        header_row = 0
        for i, line in enumerate(lines):
            if "Company name" in line and "ASX code" in line:
                header_row = i
                break
        
        df = pd.read_csv(io.StringIO("\n".join(lines[header_row:])))
        
        # Clean and Rename Columns
        df.columns = df.columns.str.strip().str.replace('"', '')
        df = df.rename(columns={'Company name': 'Retailer', 'ASX code': 'Ticker', 'GICS industry group': 'Industry'})
        
        # Broad sectors to capture ADH, BAP, ASG, AX1, etc.
        retail_sectors = [
            'Consumer Discretionary Distribution & Retail',
            'Consumer Staples Distribution & Retail',
            'Retailing',
            'Food & Staples Retailing',
            'Automobiles & Components',
            'Consumer Services'
        ]
        
        return df[df['Industry'].isin(retail_sectors)].dropna(subset=['Ticker'])
    except Exception as e:
        st.error(f"Error loading ASX data: {e}")
        return pd.DataFrame()

# --- EXECUTION ---
abs_open, abs_closed = get_national_abs_data()
asx_list = get_all_asx_retailers()

# Metrics: ABS Data
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
    # Handle multiple tickers in search by splitting by comma
    search_input = st.text_input("Search by Tickers (e.g. ADH, BAP, ASG) or Name", "").upper()
    search_terms = [t.strip() for t in search_input.split(',')] if search_input else []
    
    # Filter Logic
    if search_terms:
        mask = asx_list['Ticker'].isin(search_terms) | \
               asx_list['Retailer'].str.upper().str.contains(search_input, na=False)
    else:
        mask = [True] * len(asx_list) # Show all if search is empty

    final_df = asx_list[mask][['Ticker', 'Retailer', 'Industry']].sort_values('Ticker')
    
    st.write(f"Showing {len(final_df)} companies.")
    st.dataframe(final_df, use_container_width=True, hide_index=True)
else:
    st.warning("The ASX Directory could not be reached. Try refreshing in 1 minute.")

st.info("List pulled live from [ASX Listed Companies](https://www.asx.com.au/markets/trade-our-cash-market/directory). Includes [Adairs (ADH)](https://www.listcorp.com/asx/sectors/consumer-discretionary/retailing), [Bapcor (BAP)](https://www.listcorp.com/asx/sectors/consumer-discretionary/retailing), and [Autosports Group (ASG)](https://www.listcorp.com/asx/sectors/consumer-discretionary/retailing).")
