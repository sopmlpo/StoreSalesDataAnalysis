"""
Store Sales Data Analysis Dashboard
This Streamlit app provides interactive visualization and analysis of store sales data.
"""

# Import required libraries
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend for matplotlib
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")  # Suppress warning messages

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="StoreSalesData",
    page_icon=":bar_chart:",
    layout="wide"
)

# Page Title and Style
st.title(" :bar_chart: Demo Store Sales Data Analysis")
st.markdown(
    '<style>div.block-container{padding-top:3rem;}<style>',
    unsafe_allow_html=True
)

# =============================================================================
# Data Loading Section
# =============================================================================
# File upload functionality
allowed_extensions = ["csv", "txt", "xlsx", "xls"]
uploaded_file = st.file_uploader(
    ":file_folder: Upload a file",
    type=allowed_extensions
)

# Load data from uploaded file or use default
if uploaded_file is not None:
    filename = uploaded_file.name
    st.write(filename)
    df = pd.read_excel(filename)
else:
    file_path = "./Projects2025/streamlit_portfolio_website"
    df = pd.read_excel("Superstore.xls")

# =============================================================================
# Date Range Selection
# =============================================================================
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Calculate date range
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

# Date input widgets
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter data based on selected date range
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# =============================================================================
# Sidebar Filters
# =============================================================================
st.sidebar.header("Choose your filter: ")

# Region Filter
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# State Filter - Dynamic based on selected Region
state = st.sidebar.multiselect("Pick your State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# City Filter - Dynamic based on selected State
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Complex filtering logic based on selected filters
if not region and not state and not city:
    filtered_df = df  # No filters applied
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]  # Only region filter
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]  # Only state filter
elif state and city:
    filtered_df = df3[df3["State"].isin(state) & df3["City"].isin(city)]  # State and city
elif region and city:
    filtered_df = df3[df3["Region"].isin(region) & df3["City"].isin(city)]  # Region and city
elif region and state:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state)]  # Region and state
elif city:
    filtered_df = df3[df3["City"].isin(city)]  # Only city filter
else:
    # All filters applied
    filtered_df = df3[df3["Region"].isin(region) & 
                     df3["State"].isin(state) & 
                     df3["City"].isin(city)]

# =============================================================================
# Sales Analysis Visualizations
# =============================================================================
# Calculate category-wise sales
category_df = filtered_df.groupby(
    by=["Category"],
    as_index=False
)["Sales"].sum()

# Category-wise Sales Bar Chart
with col1: 
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", 
                 text = ["${:,.2f}".format(x) for x in category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig, use_container_width=True, height = 200)

# Region-wise Sales Donut Chart
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(
        filtered_df,
        values="Sales",
        names="Region",
        hole=0.5  # Creates a donut chart
    )
    fig.update_traces(
        text=filtered_df["Region"],
        textposition="outside"
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

# =============================================================================
# Detailed Data Views
# =============================================================================
cl1, cl2 = st.columns(2)

# Category Data View and Download
with cl1:
    with st.expander("Category_ViewData"):
        st.dataframe(category_df.style.format({'Sales': '${:,.2f}'}))
        csv = category_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Category.csv",
            mime="text/csv",
            help="Click here to download the data as a CSV file"
        )

# Region Data View and Download
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.dataframe(region.style.format({'Sales': '${:,.2f}'}))
        csv = region.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Region.csv",
            mime="text/csv",
            help="Click here to download the data as a CSV file"
        )

# =============================================================================
# Time Series Analysis
# =============================================================================
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

# Create time series line chart
linechart = pd.DataFrame(
    filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()
).reset_index()

fig2 = px.line(
    linechart,
    x="month_year",
    y='Sales',
    labels={"Sales": "Amount"},
    height=500,
    width=1000,
    template="gridon"
)
st.plotly_chart(fig2, use_container_width=True)

# Time Series Data View
with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data",
        data=csv,
        file_name="TimeSeries.csv",
        mime="text/csv"
    )

# =============================================================================
# Hierarchical Analysis
# =============================================================================
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(
    filtered_df,
    path=["Region", "Category", "Sub-Category"],
    values="Sales",
    hover_data=["Sales"],
    color="Sub-Category"
)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

# =============================================================================
# Segment and Category Analysis
# =============================================================================
chart1, chart2 = st.columns((2))

# Segment-wise Sales Pie Chart
with chart1:
    st.subheader("Segment wise Sales")
    fig = px.pie(
        filtered_df,
        values="Sales",
        names="Segment",
        template="plotly_dark"
    )
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Category-wise Sales Pie Chart
with chart2:
    st.subheader("Category wise Sales")
    fig = px.pie(
        filtered_df,
        values="Sales",
        names="Category",
        template="gridon"
    )
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# Summary Tables
# =============================================================================
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    # Sample data table
    df_sample = df[0:5][["Region", "State", "City", "Category",
                         "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    # Month-wise sub-category analysis
    st.markdown("Month wise Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(
        data=filtered_df,
        values="Sales",
        index=["Sub-Category"],
        columns="month"
    )
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# =============================================================================
# Sales and Profit Analysis
# =============================================================================
# Scatter plot of Sales vs Profit
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1.update_layout(
    title="Relationship between Sales and Profits",
    title_font_size=20,
    xaxis_title="Sales",
    yaxis_title="Profit",
    xaxis_title_font_size=19,
    yaxis_title_font_size=19
)
st.plotly_chart(data1, use_container_width=True)

# =============================================================================
# Additional Data Views
# =============================================================================
# Detailed data view with gradient coloring
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download complete dataset
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Data",
    data=csv,
    file_name="Data.csv",
    mime="text/csv"
)