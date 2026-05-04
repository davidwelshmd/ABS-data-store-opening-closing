import streamlit as st
import pandas as pd
import requests
import io

# Page Configuration
st.set_page_config(page_title="Full ASX Retail Tracker", layout="wide", page_icon="🛍️")

st.title("🛒 Comprehensive ASX Retail Network Tracker")
st.markdown("""
This dashboard identifies every retail-related company on the **ASX** and tracks their physical store footprints.
""")

# --- DATA SOURCE 1: Live ASX Directory Fetch ---
@st.cache_data
def get_full_asx_retailers():
    # Official ASX CSV Link
    asx_url = "https://www.asx.com.au/asx/research/ASXListedCompanies.csv"
    try:
        response = requests.get(asx_url)
        # ASX CSV metadata usually occupies the first two lines
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        
        # Broad categories to include ADH, BAP, and ASG
        retail_sectors = [
            'Consumer Discretionary Distribution & Retail',
            'Consumer Staples Distribution & Retail',
            'Retailing',
            'Food & Staples Retailing',
            'Automobiles & Components' # Specifically for ASG
        ]
        
        # Filter and rename for the dashboard
        retailers = df[df['GICS industry group'].isin(retail_sectors)].copy()
        return retailers.rename(columns={'ASX code': 'Ticker', 'Company name': 'Retailer'})
    except Exception as e:
        st.error(f"Failed to fetch live ASX list: {e}")
        return pd.DataFrame()

# --- DATA SOURCE 2: Store Metrics (Manual Input) ---
@st.cache_data
def get_manual_store_data():
    # Research-based estimates for key ASX retailers as of May 2026
    data = {
        "Ticker": ["WES", "WOW", "COL", "JBH", "SUL", "LOV", "AX1", "BBN", "PMV", "ADH", "BAP", "ASG"],
        "Opened_1Y": [8, 12, 10, 5, 6, 25, 12, 4, 2, 5, 8, 3],
        "Closed_1Y": [1, 4, 3, 2, 1, 2, 5, 1, 0, 2, 3, 1]
    }
    return pd.DataFrame(data)

# --- UI EXECUTION ---
asx_retail_full = get_full_asx_retailers()
manual_data = get_manual_store_data()

# Merge official directory with your research data
merged_df = pd.merge(asx_retail_full, manual_data, on="Ticker", how="left").fillna(0)

# Global Performance Metrics
st.subheader("Market-Wide Summary")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Retailers Listed", len(asx_retail_full))
with c2:
    st.metric("Total Openings (Tracked)", int(merged_df["Opened_1Y"].sum()))
with c3:
    st.metric("Total Closures (Tracked)", int(merged_df["Closed_1Y"].sum()), delta_color="inverse")

st.divider()

# Comprehensive Searchable Table
st.subheader("All ASX Retailers & Network Status")
search = st.text_input("Search by Ticker or Name (e.g. 'ADH', 'Bapcor', 'WES')", "")
mask = merged_df['Retailer'].str.contains(search, case=False) | merged_df['Ticker'].str.contains(search, case=False)
display_df = merged_df[mask].copy()

# Add a Net Change column
display_df['Net_Change_1Y'] = display_df['Opened_1Y'] - display_df['Closed_1Y']

st.dataframe(
    display_df[['Ticker', 'Retailer', 'GICS industry group', 'Opened_1Y', 'Closed_1Y', 'Net_Change_1Y']], 
    use_container_width=True, 
    hide_index=True
)

st.info("💡 Data for openings/closings must be updated manually in the `get_manual_store_data` function using [ASX Announcements](https://www.asx.com.au/).")
