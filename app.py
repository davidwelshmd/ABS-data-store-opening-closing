import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="AU Retail Store Tracker", layout="wide")
st.title("📍 AU Retail: Store Openings & Closings")

# --- DATA SOURCE 1: Official ASX Directory (Automated) ---
@st.cache_data
def get_asx_retail_directory():
    asx_url = "https://asx.com.au"
    try:
        response = requests.get(asx_url)
        # Skip the first two header rows from ASX
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        
        # Filter for retail sectors
        retail_sectors = [
            'Consumer Discretionary Distribution & Retail',
            'Consumer Staples Distribution & Retail',
            'Retailing'
        ]
        return df[df['GICS industry group'].isin(retail_sectors)]
    except:
        return pd.DataFrame()

# --- DATA SOURCE 2: Store Count Data ---
@st.cache_data
def get_store_data():
    # You can move these to a CSV later, but here is the simplified structure
    data = {
        "Retailer": [
            "JB Hi-Fi", "Woolworths", "Bunnings", "Coles", 
            "Lovisa", "Myer", "Super Retail Group", "Accent Group", 
            "Harvey Norman", "Beacon Lighting"
        ],
        "Ticker": ["JBH", "WOW", "WES", "COL", "LOV", "MYR", "SUL", "AX1", "HVN", "BLX"],
        "Stores_Opened_1Y":,
        "Stores_Closed_1Y":,
        "Stores_Opened_3Y":,
        "Stores_Closed_3Y": [5, 10, 4, 8, 12, 6, 10, 15, 4, 2]
    }
    return pd.DataFrame(data)

# --- APP UI ---
asx_retailers = get_asx_retail_directory()
store_df = get_store_data()

# 1. Macro View
st.subheader("Total Tracked Network Changes")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Openings (Last 12m)", store_df["Stores_Opened_1Y"].sum())
with col2:
    st.metric("Total Closures (Last 12m)", store_df["Stores_Closed_1Y"].sum())

# 2. Filtering & Comparison
st.divider()
selected = st.multiselect("Select Retailers to Compare", store_df["Retailer"].tolist(), default=store_df["Retailer"].tolist()[:5])
filtered_df = store_df[store_df["Retailer"].isin(selected)]

# 3. Visualization
st.subheader("Net Growth (Openings vs Closures)")
# Calculating Net Growth for the chart
filtered_df["Net_Growth_1Y"] = filtered_df["Stores_Opened_1Y"] - filtered_df["Stores_Closed_1Y"]
st.bar_chart(filtered_df.set_index("Retailer")[["Stores_Opened_1Y", "Stores_Closed_1Y"]])

# 4. Data Table
st.subheader("Store Network Details")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

with st.expander("Search Full ASX Retail Directory"):
    st.write("This list is pulled live from the ASX website.")
    st.dataframe(asx_retailers[['Company name', 'ASX code', 'GICS industry group']], use_container_width=True)
