import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="AU Retail Pulse", layout="wide")
st.title("🇦🇺 Comprehensive AU Retail Performance Tracker")

# --- DATA SOURCE 1: Official ASX Directory ---
@st.cache_data
def get_all_asx_retailers():
    # Direct link to official ASX CSV
    asx_url = "https://www.asx.com.au/asx/research/ASXListedCompanies.csv"
    try:
        # ASX CSV often starts with some skipable header rows
        response = requests.get(asx_url)
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        
        # Filter for retail-related GICS industry groups
        retail_sectors = [
            'Consumer Discretionary Distribution & Retail',
            'Consumer Staples Distribution & Retail',
            'Retailing'
        ]
        retailers = df[df['GICS industry group'].isin(retail_sectors)]
        return retailers
    except Exception as e:
        st.error(f"Error fetching ASX list: {e}")
        return pd.DataFrame()

# --- DATA SOURCE 2: Expanded Manual Data ---
def get_performance_data():
    # Expand this dictionary with more retailers from the ASX list
    data = {
        "Retailer": [
            "JB Hi-Fi", "Woolworths", "Wesfarmers (Bunnings)", "Premier Investments", 
            "Super Retail Group", "Coles Group", "Harvey Norman", "Lovisa", 
            "Nick Scali", "Myer", "Accent Group", "Adairs", "Baby Bunting"
        ],
        "Ticker": [
            "JBH", "WOW", "WES", "PMV", "SUL", "COL", "HVN", "LOV", "NCK", "MYR", "AX1", "ADH", "BBN"
        ],
        "SSS_1Y (%)": [4.5, -1.2, 3.8, -0.5, 2.1, 2.0, -1.5, 10.0, 1.2, -2.0, 1.5, -3.0, -5.0],
        "Stores_Opened_1Y": [5, 12, 8, 3, 4, 10, 2, 50, 4, 0, 15, 2, 3],
        "Stores_Closed_1Y": [1, 2, 0, 10, 2, 1, 5, 2, 0, 4, 3, 5, 2]
    }
    return pd.DataFrame(data)

# --- UI EXECUTION ---
st.subheader("Live ASX Retail Directory")
asx_list = get_all_asx_retailers()
if not asx_list.empty:
    st.write(f"Found {len(asx_list)} retail-related companies currently listed on the ASX.")
    with st.expander("View Full ASX Retail Directory"):
        st.dataframe(asx_list, use_container_width=True)

st.divider()

st.subheader("Performance Comparison (1-Year)")
perf_df = get_performance_data()

# Selection box to pick from the manual performance data
selected = st.multiselect("Select Retailers to Compare", perf_df["Retailer"].tolist(), default=perf_df["Retailer"].tolist()[:5])
filtered_df = perf_df[perf_df["Retailer"].isin(selected)]

if not filtered_df.empty:
    st.bar_chart(filtered_df.set_index("Retailer")["SSS_1Y (%)"])
    st.dataframe(filtered_df, use_container_width=True)
