# Importing the required libraries

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image


import pandas as pd
pd.options.display.float_format = '{:.2f}'.format

import warnings
warnings.filterwarnings('ignore')

# --- Set Page Configuration ---
st.set_page_config(layout='wide')


Used_Car=pd.read_csv('DriveArabia_All_uae_updated.csv',thousands =",")
Used_Car.head(5)
print(Used_Car.head(5))
# Thousands functions is kept to convert all the values to thousands


# Load your data (assuming it's in 'DriveArabia_All_uae_updated.csv')
Used_Car = pd.read_csv('DriveArabia_All_uae_updated.csv', thousands=",")

# --- Dashboard Title and Introduction ---
st.title("Used Car Sales Dashboard (UAE - DriveArabia Data)")
st.markdown("Analyzing used car listings data from DriveArabia in the UAE.")


## --- Data Cleaning ---
import re  # Import the regular expression library

def clean_approx_cost(cost_str):
    if isinstance(cost_str, str):
        cost_str = cost_str.replace("AED ", "").replace(",", "").replace("*", "").strip()
        # Use regular expression to find all numbers in the string
        numbers = re.findall(r'\d+\.?\d*', cost_str)
        if len(numbers) == 2:
            try:
                return (float(numbers[0]), float(numbers[1]))
            except ValueError:
                return (None, None)
        elif len(numbers) == 1:
            try:
                return (float(numbers[0]), float(numbers[0]))  # If only one number, assume it's both min and max
            except ValueError:
                return (None, None)
        else:
            return (None, None)
    return (None, None)

cost_tuples = Used_Car['Approx Cost'].apply(clean_approx_cost)
Used_Car['Min Cost'] = [cost[0] for cost in cost_tuples]
Used_Car['Max Cost'] = [cost[1] for cost in cost_tuples]

# Convert 'Model Year' to integer
Used_Car['Model Year'] = pd.to_numeric(Used_Car['Model Year'], errors='coerce').dropna().astype(int)

# Add Logo
try:
    logo = Image.open("logo.png")  # Ensure 'logo.png' is in the same directory
    st.sidebar.image(logo, width=150)
except FileNotFoundError:
    st.sidebar.markdown("Logo not found")

# --- Sidebar for Filters ---
st.sidebar.header("Sales Performance Dashboard", divider=True)

# Manufacturer filter
manufacturers = sorted(Used_Car['Manufacturer'].unique())
selected_manufacturers = st.sidebar.multiselect("Select Manufacturer(s)", manufacturers, default=manufacturers[:10])
filtered_df = Used_Car[Used_Car['Manufacturer'].isin(selected_manufacturers)]

# Model Year filter
years = sorted(filtered_df['Model Year'].unique())
selected_years = st.sidebar.multiselect("Select Model Year(s)", years, default=years[:5])
filtered_df = filtered_df[filtered_df['Model Year'].isin(selected_years)]

# Body Type filter
body_types = sorted(filtered_df['Body Type'].unique())
selected_body_types = st.sidebar.multiselect("Select Body Type(s)", body_types, default=body_types[:5])
filtered_df = filtered_df[filtered_df['Body Type'].isin(selected_body_types)]


# --- KPIs ---
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3, gap="large",border=True) # Adjust gap as needed

# Calculate KPIs based on the filtered data
average_min_price_kpi = filtered_df['Min Cost'].mean()
average_max_price_kpi = filtered_df['Max Cost'].mean()
number_of_listings_kpi = filtered_df.shape[0]

with col1:
    st.metric("Average Min Price (AED)", f"{average_min_price_kpi:,.2f}" if pd.notna(average_min_price_kpi) else "N/A")

with col2:
    st.metric("Average Max Price (AED)", f"{average_max_price_kpi:,.2f}" if pd.notna(average_max_price_kpi) else "N/A")

with col3:
    st.metric("Number of Listings", number_of_listings_kpi)


# --- Tabs for Different Analyses ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Manufacturer Analysis", "Price Analysis", "Model Year Analysis", "Body Type Analysis", "Origin Analysis"])

# --- Manufacturer Analysis Tab ---
with tab2:
    st.subheader("Listings by Manufacturer")
    listings_by_manufacturer = filtered_df['Manufacturer'].value_counts().reset_index()
    listings_by_manufacturer.columns = ['Manufacturer', 'Number of Listings']
    if not listings_by_manufacturer.empty:
        fig_manufacturer_bar = px.bar(listings_by_manufacturer, x='Manufacturer', y='Number of Listings',
                                     title='Number of Listings by Manufacturer',
                                     labels={'Number of Listings': 'Number of Listings'})
        st.plotly_chart(fig_manufacturer_bar, use_container_width=True)
    else:
        st.warning("No listings available based on the current filters.")

# --- Price Analysis Tab ---
with tab1:
    st.subheader("Model Year vs. Average Price")
    if not filtered_df.empty and 'Min Cost' in filtered_df.columns and 'Max Cost' in filtered_df.columns:
        avg_price_by_year = filtered_df.groupby('Model Year')[['Min Cost', 'Max Cost']].mean().reset_index()
        avg_price_by_year['Average Price'] = (avg_price_by_year['Min Cost'] + avg_price_by_year['Max Cost']) / 2
        fig_price_vs_year = px.scatter(avg_price_by_year, x='Model Year', y='Average Price',
                                      title='Average Price by Model Year (Approximation)',
                                      labels={'Average Price': 'Average Price (AED)'})
        st.plotly_chart(fig_price_vs_year, use_container_width=True)
    else:
        st.warning("Insufficient data to display Model Year vs. Average Price plot.")

    st.subheader("Distribution of Minimum Prices")
    if not filtered_df.empty and 'Min Cost' in filtered_df.columns:
        fig_min_price_hist = px.histogram(filtered_df, x='Min Cost', nbins=20,
                                         title='Distribution of Minimum Prices',
                                         labels={'Min Cost': 'Minimum Price (AED)'})
        st.plotly_chart(fig_min_price_hist, use_container_width=True)
    else:
        st.warning("Insufficient price data to display the distribution of minimum prices.")

    st.subheader("Distribution of Maximum Prices")
    if not filtered_df.empty and 'Max Cost' in filtered_df.columns:
        fig_max_price_hist = px.histogram(filtered_df, x='Max Cost', nbins=20,
                                         title='Distribution of Maximum Prices',
                                         labels={'Max Cost': 'Maximum Price (AED)'})
        st.plotly_chart(fig_max_price_hist, use_container_width=True)
    else:
        st.warning("Insufficient price data to display the distribution of maximum prices.")

# --- Model Year Analysis Tab ---
with tab3:
    st.subheader("Listings by Model Year")
    listings_by_year = filtered_df['Model Year'].value_counts().sort_index().reset_index()
    listings_by_year.columns = ['Model Year', 'Number of Listings']
    if not listings_by_year.empty:
        fig_year_bar = px.bar(listings_by_year, x='Model Year', y='Number of Listings',
                             title='Number of Listings by Model Year',
                             labels={'Number of Listings': 'Number of Listings'})
        st.plotly_chart(fig_year_bar, use_container_width=True)
    else:
        st.warning("No listings available based on the current filters.")

# --- Body Type Analysis Tab ---
with tab4:
    st.subheader("Listings by Body Type")
    listings_by_body_type = filtered_df['Body Type'].value_counts().reset_index()
    listings_by_body_type.columns = ['Body Type', 'Number of Listings']
    if not listings_by_body_type.empty:
        fig_body_type_bar = px.bar(listings_by_body_type, x='Body Type', y='Number of Listings',
                                     title='Number of Listings by Body Type',
                                     labels={'Number of Listings': 'Number of Listings'})
        st.plotly_chart(fig_body_type_bar, use_container_width=True)
    else:
        st.warning("No listings available based on the current filters.")

# --- Origin Analysis Tab ---
with tab5:
    st.subheader("Listings by Origin Country")
    listings_by_origin = filtered_df['Origin Country'].value_counts().nlargest(10).reset_index()
    listings_by_origin.columns = ['Origin Country', 'Number of Listings']
    if not listings_by_origin.empty:
        fig_origin_bar_chart = px.bar(listings_by_origin, x='Origin Country', y='Number of Listings',
                                       title='Top 10 Origin Countries of Listed Cars',
                                       labels={'Number of Listings': 'Number of Listings'})
        st.plotly_chart(fig_origin_bar_chart, use_container_width=True)
    else:
        st.warning("No listings available based on the current filters.")
