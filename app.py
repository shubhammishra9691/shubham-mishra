import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="Company Data Analytics Dashboard",
    layout="wide",
    )

# Then continue with the rest of the script
st.title("📊 Company Sales Dashboard")

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# Load data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("//Users//romykumari//Downloads//company_Data.csv")
        return data
    except FileNotFoundError:
        st.error("Error: company_Data.csv not found. Please ensure the file is in the correct directory.")
        st.stop()

df = load_data()

# Data preprocessing
df['ShelveLoc'] = df['ShelveLoc'].astype('category')
df['Urban'] = df['Urban'].map({'Yes': True, 'No': False})
df['US'] = df['US'].map({'Yes': True, 'No': False})

# Sidebar filters
st.sidebar.header("🔍 Filter Data")

# Numeric filters
min_sales, max_sales = st.sidebar.slider(
    "Sales Range:",
    min_value=float(df['Sales'].min()),
    max_value=float(df['Sales'].max()),
    value=(float(df['Sales'].min()), float(df['Sales'].max()))
)

min_price, max_price = st.sidebar.slider(
    "Price Range:",
    min_value=float(df['Price'].min()),
    max_value=float(df['Price'].max()),
    value=(float(df['Price'].min()), float(df['Price'].max()))
)

# Categorical filters
shelve_locs = st.sidebar.multiselect(
    "Shelve Location:",
    options=list(df['ShelveLoc'].unique()),
    default=list(df['ShelveLoc'].unique())
)

urban_filter = st.sidebar.radio(
    "Urban Location:",
    options=['All', 'Yes', 'No'],
    index=0
)

us_filter = st.sidebar.radio(
    "US Location:",
    options=['All', 'Yes', 'No'],
    index=0
)

# Apply filters
filtered_df = df[
    (df['Sales'] >= min_sales) & (df['Sales'] <= max_sales) &
    (df['Price'] >= min_price) & (df['Price'] <= max_price) &
    (df['ShelveLoc'].isin(shelve_locs))
]

if urban_filter != 'All':
    filtered_df = filtered_df[filtered_df['Urban'] == (urban_filter == 'Yes')]

if us_filter != 'All':
    filtered_df = filtered_df[filtered_df['US'] == (us_filter == 'Yes')]

# Main dashboard
st.title("📈 Company Data Analytics Dashboard")
st.markdown("""
    <style>
    .big-font {
        font-size:18px !important;
    }
    </style>
    <p class="big-font">Interactive dashboard for exploring company sales performance and market characteristics.</p>
""", unsafe_allow_html=True)

# KPI cards
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
with col2:
    st.metric("Average Sales", f"${filtered_df['Sales'].mean():,.2f}")
with col3:
    st.metric("Products Analyzed", filtered_df.shape[0])
with col4:
    st.metric("Avg Advertising Spend", f"${filtered_df['Advertising'].mean():,.2f}")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Analysis", "💰 Pricing Insights", "📊 Market Characteristics", "🔍 Deep Dive"])

with tab1:
    st.subheader("Sales Performance Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Sales distribution
        fig = px.histogram(
            filtered_df, 
            x='Sales', 
            nbins=30, 
            title='Sales Distribution',
            color='ShelveLoc'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales vs Advertising
        fig = px.scatter(
            filtered_df,
            x='Advertising',
            y='Sales',
            color='ShelveLoc',
            title='Sales vs Advertising Spend',
            trendline='lowess'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Sales by location
    fig = px.box(
        filtered_df,
        x='ShelveLoc',
        y='Sales',
        color='US',
        title='Sales Distribution by Shelf Location and US Market'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Pricing Strategy Insights")
    
    col1, col2 = st.columns(2)
    with col1:
        # Price vs Sales
        fig = px.scatter(
            filtered_df,
            x='Price',
            y='Sales',
            color='ShelveLoc',
            title='Price vs Sales Relationship',
            trendline='ols'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price distribution
        fig = px.box(
            filtered_df,
            x='ShelveLoc',
            y='Price',
            title='Price Distribution by Shelf Location'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Price elasticity analysis
    st.subheader("Price Elasticity Analysis")
    price_bins = pd.qcut(filtered_df['Price'], q=4)
    price_elasticity = filtered_df.groupby(price_bins)['Sales'].mean().reset_index()
    price_elasticity['Price Midpoint'] = price_elasticity['Price'].apply(lambda x: (x.left + x.right)/2)
    
    fig = px.line(
        price_elasticity,
        x='Price Midpoint',
        y='Sales',
        title='Average Sales by Price Range',
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Market Characteristics")
    
    col1, col2 = st.columns(2)
    with col1:
        # Urban vs Rural sales
        urban_sales = filtered_df.groupby('Urban')['Sales'].mean().reset_index()
        fig = px.bar(
            urban_sales,
            x='Urban',
            y='Sales',
            title='Average Sales: Urban vs Rural',
            labels={'Urban': 'Urban Location', 'Sales': 'Average Sales'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # US vs Non-US sales
        us_sales = filtered_df.groupby('US')['Sales'].mean().reset_index()
        fig = px.bar(
            us_sales,
            x='US',
            y='Sales',
            title='Average Sales: US vs Non-US',
            labels={'US': 'US Market', 'Sales': 'Average Sales'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation heatmap
    st.subheader("Feature Correlation Matrix")
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
    corr_matrix = filtered_df[numeric_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title='Correlation Between Numeric Features'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Deep Dive Analysis")
    
    # Multi-variable analysis
    analysis_type = st.selectbox(
        "Select Analysis Type:",
        ["Sales vs Price & Advertising", "Sales vs Income & Population", "Sales vs Age & Education"]
    )
    
    if analysis_type == "Sales vs Price & Advertising":
        fig = px.scatter_3d(
            filtered_df,
            x='Price',
            y='Advertising',
            z='Sales',
            color='ShelveLoc',
            title='3D View: Sales vs Price & Advertising'
        )
    elif analysis_type == "Sales vs Income & Population":
        fig = px.scatter_3d(
            filtered_df,
            x='Income',
            y='Population',
            z='Sales',
            color='ShelveLoc',
            title='3D View: Sales vs Income & Population'
        )
    else:
        fig = px.scatter_3d(
            filtered_df,
            x='Age',
            y='Education',
            z='Sales',
            color='ShelveLoc',
            title='3D View: Sales vs Age & Education'
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Dynamic query builder
    st.subheader("Custom Data Exploration")
    
    x_axis = st.selectbox("X-axis", filtered_df.select_dtypes(include=['number', 'category']).columns)
    y_axis = st.selectbox("Y-axis", filtered_df.select_dtypes(include=['number']).columns, index=1)
    color_by = st.selectbox("Color by", filtered_df.select_dtypes(include=['category']).columns)
    
    fig = px.scatter(
        filtered_df,
        x=x_axis,
        y=y_axis,
        color=color_by,
        hover_data=filtered_df.columns,
        title=f"{y_axis} vs {x_axis} by {color_by}"
    )
    st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("🔎 Filtered Data Preview")
st.dataframe(filtered_df.head(50), use_container_width=True)

# Download button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_company_data.csv',
    mime='text/csv'
)

# Add some space at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
