import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go



df = pd.read_csv("Nassau_Candy_Distributor.csv")
# # Show confirmation
# #st.success("File loaded successfully ✅")
df = df[df["Sales"] > 0]
df = df[df["Units"] > 0]
# # Show shape
# #st.write("Shape of dataset:", df.shape)

# # Show first 5 rows
# #st.dataframe(df.head())

# Convert Order Date
df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
df = df.dropna(subset=["Order Date"])

# Create Margin %
df["Margin %"] = (df["Gross Profit"] / df["Sales"]) * 100



st.set_page_config(page_title="Product Profitability Dashboard", layout="wide")

st.markdown("""
<style>

/* ===== PAGE LAYOUT ===== */

.block-container{
    padding-top: 5rem;
    padding-bottom: 1rem;
    padding-left: 9rem;
    padding-right: 9rem;
}

/* Reduce gap between sidebar and content */
section.main > div {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}

/* ===== TITLE ===== */

h1{
    text-align:left;
    font-size:40px;
    font-weight:700;
}

/* ===== SECTION TITLES ===== */

h2{
    font-size:30px;
}

h3{
    font-size:24px;
}

/* ===== KPI CARDS ===== */

.kpi-box{
    padding:10px;
    border-radius:10px;
    color:white;
    text-align:center;
    font-family:Arial;
}

.kpi-title{
    font-size:18px;
}

.kpi-value{
    font-size:32px;
    font-weight:bold;
}

/* ===== KPI COLORS ===== */

.margin{background:#1f4e79;}
.unit{background:#2a9d8f;}
.revenue{background:#264653;}
.profit{background:#2b7a78;}
.volatility{background:#e76f51;}

/* ===== CHART TITLES ===== */

.js-plotly-plot .plotly .gtitle{
    font-size:20px !important;
}

/* ===== TABLE FONT ===== */

.stDataFrame{
    font-size:30px;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* ===== SIDEBAR WIDTH ===== */

section[data-testid="stSidebar"] {
    width: 340px !important;
}

/* Sidebar text slightly bigger */

section[data-testid="stSidebar"] * {
    font-size: 18px;
}

</style>
""", unsafe_allow_html=True)
st.title("📊 Product Profitability & Margin Performance Dashboard — Nassau Candy Distributor")
st.markdown("<br><br>", unsafe_allow_html=True)

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Order Date"].min(), df["Order Date"].max()]
)

division_filter = st.sidebar.multiselect(
    "Select Division",
    df["Division"].unique(),
    default=df["Division"].unique()
)


margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    float(df["Margin %"].min()),
    float(df["Margin %"].max()),
    0.0
)





# Apply filters   
filtered_df = df[
    (df["Division"].isin(division_filter)) &
    (df["Margin %"] >= margin_threshold) &
    (df["Order Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order Date"] <= pd.to_datetime(date_range[1]))
]

products = filtered_df["Product Name"].unique()

product_search = st.sidebar.selectbox(
    "Select Product",
    ["All"] + list(products)
)

if product_search != "All":
    filtered_df = filtered_df[
        filtered_df["Product Name"] == product_search
    ]
# -------------------------------
# KPI Calculations
# -------------------------------

# Gross Margin
gross_margin = (
    filtered_df["Gross Profit"].sum() / filtered_df["Sales"].sum() * 100
    if filtered_df["Sales"].sum() != 0 else 0
)

# Profit per Unit
profit_per_unit = (
    filtered_df["Gross Profit"].sum() / filtered_df["Units"].sum()
    if filtered_df["Units"].sum() != 0 else 0
)

# Revenue Contribution
product_sales = filtered_df.groupby("Product Name")["Sales"].sum()

revenue_contribution = (
    (product_sales.max() / filtered_df["Sales"].sum()) * 100
    if filtered_df["Sales"].sum() != 0 else 0
)

# Profit Contribution
product_profit = filtered_df.groupby("Product Name")["Gross Profit"].sum()

profit_contribution = (
    (product_profit.max() / filtered_df["Gross Profit"].sum()) * 100
    if filtered_df["Gross Profit"].sum() != 0 else 0
)

# Margin Volatility
margin_volatility = (
    filtered_df["Margin %"].std()
    if not filtered_df.empty else 0
)

# -------------------------------
# KPI Display
# -------------------------------


col1,col2,col3,col4,col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-box margin">
        <div class="kpi-title">Gross Margin (%)</div>
        <div class="kpi-value">{gross_margin:.2f}%</div>
    </div>
    """,unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-box unit">
        <div class="kpi-title">Profit per Unit</div>
        <div class="kpi-value">{profit_per_unit:.2f}</div>
    </div>
    """,unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-box revenue">
        <div class="kpi-title">Revenue Contribution</div>
        <div class="kpi-value">{revenue_contribution:.2f}%</div>
    </div>
    """,unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-box profit">
        <div class="kpi-title">Profit Contribution</div>
        <div class="kpi-value">{profit_contribution:.2f}%</div>
    </div>
    """,unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-box volatility">
        <div class="kpi-title">Margin Volatility</div>
        <div class="kpi-value">{margin_volatility:.2f}</div>
    </div>
    """,unsafe_allow_html=True)
    
   
st.markdown("<br><br>", unsafe_allow_html=True)  
# -------------------------------
# Product Profitability Overview
# -------------------------------

st.subheader("Product Profitability Overview")

product_summary = filtered_df.groupby("Product Name").agg({
    "Sales":"sum",
    "Gross Profit":"sum",
    "Margin %":"mean"
}).reset_index()

# Sort by Margin % (Highest first)
product_summary = product_summary.sort_values(by="Margin %", ascending=True)

fig1 = px.bar(
    product_summary,
    x="Margin %",
    y="Product Name",
    orientation="h",
    title="Product Margin Leaderboard",
    height=600   # smaller height
)

st.plotly_chart(fig1, use_container_width=True)

# Profit Contribution Treemap
fig2 = px.treemap(
    filtered_df,
    path=["Division","Product Name"],
    values="Gross Profit",
    title="Profit Contribution by Product"
)

st.plotly_chart(fig2, use_container_width=True)
# -------------------------------
# Division Performance Dashboard
# -------------------------------

st.subheader("Division Performance")

division_summary = filtered_df.groupby("Division").agg({
    "Sales":"sum",
    "Gross Profit":"sum"
}).reset_index()

fig3 = px.bar(
    division_summary,
    x="Division",
    y=["Sales","Gross Profit"],
    barmode="group",
    title="Revenue vs Profit by Division"
)

st.plotly_chart(fig3, use_container_width=True)

# Margin distribution
fig4 = px.box(
    filtered_df,
    x="Division",
    y="Margin %",
    title="Margin Distribution by Division"
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# Cost vs Margin Diagnostics
# -------------------------------

st.subheader("Cost vs Margin Diagnostics")

fig5 = px.scatter(
    filtered_df,
    x="Cost",
    y="Sales",
    color="Division",
    size="Gross Profit",
    hover_data=["Product Name"],
    title="Cost vs Sales Analysis"
)

st.plotly_chart(fig5, use_container_width=True)

# -------------------------------
st.markdown("### ⚠️ Margin Risk Flags")

risk_products = filtered_df.groupby("Product Name").agg({
    "Sales": "sum",
    "Gross Profit": "sum",
    "Margin %": "mean"
}).reset_index()

risk_products = risk_products[risk_products["Margin %"] < 10].sort_values("Margin %")

st.dataframe(risk_products)
# -------------------------------
# Profit Concentration (Pareto)
# -------------------------------

st.subheader("Profit Concentration Analysis")

sales_by_product = filtered_df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)

pareto_df = sales_by_product.reset_index()

pareto_df["Cumulative %"] = pareto_df["Sales"].cumsum() / pareto_df["Sales"].sum() * 100

fig6 = go.Figure()

fig6.add_bar(
    x=pareto_df["Product Name"],
    y=pareto_df["Sales"],
    name="Sales"
)

fig6.add_scatter(
    x=pareto_df["Product Name"],
    y=pareto_df["Cumulative %"],
    name="Cumulative %",
    yaxis="y2"
)

fig6.update_layout(
    title="Pareto Analysis (Revenue Concentration)",
    yaxis=dict(title="Sales"),
    yaxis2=dict(
        title="Cumulative %",
        overlaying="y",
        side="right"
    ),
    xaxis_tickangle=-45
)

st.plotly_chart(fig6, use_container_width=True)
st.subheader("Revenue Dependency Indicator")

# Sort products by sales
sales_by_product = filtered_df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)

pareto_df = sales_by_product.reset_index()
pareto_df["Cumulative %"] = pareto_df["Sales"].cumsum() / pareto_df["Sales"].sum() * 100

# Select products contributing up to 80% revenue
top_products = pareto_df[pareto_df["Cumulative %"] <= 80]["Sales"].sum()
total_sales = pareto_df["Sales"].sum()

dependency_percent = (top_products / total_sales) * 100

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=dependency_percent,
    title={"text": "Revenue Dependency (Top 80% Products)"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "darkblue"}
    }
))

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Margin Volatility Over Time
# -------------------------------

st.subheader("Margin Volatility Over Time")

margin_time = filtered_df.groupby("Order Date")["Margin %"].mean().reset_index()

fig7 = px.line(
    margin_time,
    x="Order Date",
    y="Margin %",
    title="Margin Trend Over Time"
)

st.plotly_chart(fig7, use_container_width=True)


# # ---------------- FOOTER ---------------- #

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<style>
.footer {
    position: relative;
    text-align: center;
    padding: 20px;
    margin-top: 40px;
    border-top: 1px solid #444;
}

.footer a {
    text-decoration: none;
    padding: 10px 18px;
    margin: 8px;
    border-radius: 8px;
    font-weight: 600;
    display: inline-block;
}

.github {
    background-color: #24292e;
    color: white !important;
}

.linkedin {
    background-color: #0A66C2;
    color: white !important;
}

.footer a:hover {
    opacity: 0.8;
}
</style>

<div class="footer">

<h5>👩‍💻 Created by Prachi Patil</h5>

<a class="github" href="https://github.com/prachipatil1301" target="_blank">
🚀 GitHub
</a>

<a class="linkedin" href="https://linkedin.com/in/prachi-patil-5a3a61392" target="_blank">
💼 LinkedIn
</a>

</div>
""", unsafe_allow_html=True)
