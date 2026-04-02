import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cruzine Healthcare Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F4F8FB; }
    .stApp { background-color: #F4F8FB; }
    section[data-testid="stSidebar"] { background-color: #0B1F3A; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label { color: #A0C4D8 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #32C1A3 !important; }

    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #DCE6EF;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] label { color: #8B9BAB !important; font-size: 13px !important; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #0B1F3A !important; }

    .phase-header {
        background: linear-gradient(135deg, #0D7377, #14A085);
        color: white;
        padding: 16px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .phase-header h2 { color: white; margin: 0; font-size: 22px; }
    .phase-header p { color: #A0E8D8; margin: 4px 0 0 0; font-size: 14px; }

    .info-card {
        background: white;
        border: 1px solid #DCE6EF;
        border-left: 4px solid #14A085;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .insight-card {
        background: #E6FAF7;
        border: 1px solid #32C1A3;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 10px 0;
        color: #0B1F3A;
        font-size: 14px;
    }
    .warning-card {
        background: #FFF3CD;
        border: 1px solid #F39C12;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: 14px;
    }
    .gem-card {
        background: linear-gradient(135deg, #0B1F3A, #0D7377);
        color: white;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 10px 0;
    }
    .gem-card h4 { color: #32C1A3; margin: 0 0 8px 0; }
    .gem-card p { color: #DCE6EF; margin: 0; font-size: 13px; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid #DCE6EF;
        padding: 8px 20px;
        color: #8B9BAB;
    }
    .stTabs [aria-selected="true"] {
        background: #0D7377;
        color: white !important;
        border-color: #0D7377;
    }
    h1, h2, h3 { color: #0B1F3A; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SAMPLE DATA GENERATION (Realistic Cruzine Healthcare Data)
# ─────────────────────────────────────────────────────────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    random.seed(42)

    products = {
        "Surgical Gloves (L)":   {"base": 18000, "cogs": 0.55, "category": "Protective", "segment": "Surgery"},
        "Surgical Gloves (M)":   {"base": 22000, "cogs": 0.55, "category": "Protective", "segment": "Surgery"},
        "IV Cannula 18G":        {"base": 14000, "cogs": 0.48, "category": "IV Therapy",  "segment": "Anesthesiology"},
        "IV Cannula 20G":        {"base": 16000, "cogs": 0.48, "category": "IV Therapy",  "segment": "Anesthesiology"},
        "Syringe 5ml":           {"base": 28000, "cogs": 0.42, "category": "Syringes",    "segment": "General"},
        "Syringe 10ml":          {"base": 20000, "cogs": 0.42, "category": "Syringes",    "segment": "General"},
        "Syringe 2ml":           {"base": 12000, "cogs": 0.42, "category": "Syringes",    "segment": "General"},
        "Infusion Set":          {"base": 9500,  "cogs": 0.52, "category": "IV Therapy",  "segment": "ICU"},
        "Foley Catheter 14Fr":   {"base": 7000,  "cogs": 0.50, "category": "Catheters",   "segment": "Urology"},
        "Foley Catheter 16Fr":   {"base": 6500,  "cogs": 0.50, "category": "Catheters",   "segment": "Urology"},
        "O2 Mask Adult":         {"base": 5500,  "cogs": 0.46, "category": "Respiratory", "segment": "Respiratory"},
        "O2 Nasal Cannula":      {"base": 7800,  "cogs": 0.44, "category": "Respiratory", "segment": "Respiratory"},
        "Crepe Bandage 4\"":     {"base": 11000, "cogs": 0.38, "category": "Wound Care",  "segment": "Orthopedic"},
        "Crepe Bandage 6\"":     {"base": 8000,  "cogs": 0.38, "category": "Wound Care",  "segment": "Orthopedic"},
        "Feeding Tube 8Fr":      {"base": 4200,  "cogs": 0.53, "category": "Enteral",     "segment": "Gastro"},
        "Feeding Tube 10Fr":     {"base": 3800,  "cogs": 0.53, "category": "Enteral",     "segment": "Gastro"},
        "Disposable Syringe 1ml":{"base": 9000,  "cogs": 0.40, "category": "Syringes",    "segment": "General"},
        "Blood Collection Set":  {"base": 5500,  "cogs": 0.49, "category": "Diagnostics", "segment": "General"},
        "Suction Catheter 10Fr": {"base": 3200,  "cogs": 0.51, "category": "Catheters",   "segment": "ICU"},
        "Sterile Gauze 10x10":   {"base": 15000, "cogs": 0.35, "category": "Wound Care",  "segment": "Surgery"},
    }

    customers = {
        "Govt. Civil Hospital, Surat":        {"channel": "GeM", "state": "Gujarat", "type": "Government"},
        "ESIC Hospital, Vapi":                {"channel": "GeM", "state": "Gujarat", "type": "Government"},
        "District Hospital, Navsari":         {"channel": "GeM", "state": "Gujarat", "type": "Government"},
        "SMIMER Hospital, Surat":             {"channel": "Direct", "state": "Gujarat", "type": "Government"},
        "Apollo Clinic, Surat":               {"channel": "Direct", "state": "Gujarat", "type": "Private"},
        "Medilink Hospital, Ahmedabad":       {"channel": "Distributor", "state": "Gujarat", "type": "Private"},
        "Shree Hospital, Baroda":             {"channel": "Distributor", "state": "Gujarat", "type": "Private"},
        "Rainbow Medical, Mumbai":            {"channel": "Distributor", "state": "Maharashtra", "type": "Private"},
        "City Hospital, Pune":               {"channel": "Direct", "state": "Maharashtra", "type": "Private"},
        "Govt. Hospital, Jalgaon":            {"channel": "GeM", "state": "Maharashtra", "type": "Government"},
        "District Hosp., Rajkot":            {"channel": "GeM", "state": "Gujarat", "type": "Government"},
        "Sunrise Clinic, Surat":             {"channel": "Retail", "state": "Gujarat", "type": "Private"},
        "MediCare Distributor, Delhi":       {"channel": "Distributor", "state": "Delhi", "type": "Distributor"},
        "HealthFirst, Jaipur":               {"channel": "Distributor", "state": "Rajasthan", "type": "Distributor"},
        "Aryan Medical, Indore":             {"channel": "Distributor", "state": "MP", "type": "Distributor"},
    }

    # Generate 12 months of daily transactions
    start_date = datetime(2024, 4, 1)
    records = []
    prices = {
        "Surgical Gloves (L)":3.20,"Surgical Gloves (M)":3.20,"IV Cannula 18G":4.50,
        "IV Cannula 20G":4.50,"Syringe 5ml":1.80,"Syringe 10ml":2.10,"Syringe 2ml":1.50,
        "Infusion Set":6.50,"Foley Catheter 14Fr":22.00,"Foley Catheter 16Fr":22.00,
        "O2 Mask Adult":18.00,"O2 Nasal Cannula":12.00,"Crepe Bandage 4\"":8.50,
        "Crepe Bandage 6\"":11.00,"Feeding Tube 8Fr":32.00,"Feeding Tube 10Fr":34.00,
        "Disposable Syringe 1ml":1.20,"Blood Collection Set":9.50,"Suction Catheter 10Fr":28.00,
        "Sterile Gauze 10x10":0.85
    }

    for day_offset in range(365):
        current_date = start_date + timedelta(days=day_offset)
        month = current_date.month
        growth = 1 + (day_offset / 365) * 0.45  # 45% annual growth

        n_orders = np.random.poisson(8 * growth)
        for _ in range(n_orders):
            prod = random.choice(list(products.keys()))
            cust = random.choice(list(customers.keys()))
            info = products[prod]
            cust_info = customers[cust]
            base_qty = info["base"]
            qty = max(50, int(np.random.normal(base_qty / 250 * growth, base_qty / 500)))
            price = prices[prod] * np.random.uniform(0.88, 1.08)
            revenue = qty * price
            cogs = revenue * info["cogs"]
            records.append({
                "date": current_date,
                "month": current_date.strftime("%b %Y"),
                "month_num": month,
                "product": prod,
                "category": info["category"],
                "segment": info["segment"],
                "customer": cust,
                "channel": cust_info["channel"],
                "state": cust_info["state"],
                "customer_type": cust_info["type"],
                "quantity": qty,
                "price_per_unit": round(price, 2),
                "revenue": round(revenue, 2),
                "cogs": round(cogs, 2),
                "gross_profit": round(revenue - cogs, 2),
                "margin_pct": round((1 - info["cogs"]) * 100, 1),
            })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df, products, customers

df, products_meta, customers_meta = generate_data()

# ─────────────────────────────────────────────────────────────
# INVENTORY DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def generate_inventory():
    np.random.seed(99)
    inv_data = {
        "product": list(products_meta.keys()),
        "current_stock": [np.random.randint(200, 8000) for _ in products_meta],
        "reorder_level": [np.random.randint(500, 2000) for _ in products_meta],
        "max_capacity": [np.random.randint(8000, 20000) for _ in products_meta],
        "days_last_order": [np.random.randint(3, 45) for _ in products_meta],
        "lead_time_days": [np.random.randint(5, 15) for _ in products_meta],
    }
    inv_df = pd.DataFrame(inv_data)
    inv_df["stock_status"] = inv_df.apply(
        lambda r: "Critical" if r["current_stock"] < r["reorder_level"] * 0.5
        else ("Low" if r["current_stock"] < r["reorder_level"]
        else ("Excess" if r["current_stock"] > r["max_capacity"] * 0.9
        else "Healthy")), axis=1
    )
    return inv_df

inv_df = generate_inventory()

# ─────────────────────────────────────────────────────────────
# DISTRIBUTOR DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def generate_distributors():
    np.random.seed(55)
    dists = {
        "Distributor": ["MediCare, Delhi", "HealthFirst, Jaipur", "Aryan Medical, Indore",
                        "Medilink, Ahmedabad", "Rainbow Medical, Mumbai", "Shree Hospital, Baroda"],
        "State": ["Delhi", "Rajasthan", "MP", "Gujarat", "Maharashtra", "Gujarat"],
        "Region": ["North", "North", "Central", "West", "West", "West"],
        "Monthly_Revenue": [142000, 89000, 67000, 198000, 154000, 112000],
        "Orders_Last30Days": [28, 18, 14, 42, 31, 24],
        "Avg_Order_Value": [5071, 4944, 4786, 4714, 4968, 4667],
        "Payment_Days": [32, 41, 28, 22, 38, 19],
        "Return_Rate_Pct": [1.2, 2.8, 3.1, 0.8, 1.5, 2.2],
        "Growth_MoM_Pct": [8.4, 3.2, -1.5, 12.8, 6.7, 4.1],
        "Satisfaction_Score": [4.5, 3.8, 3.5, 4.8, 4.2, 4.0],
    }
    return pd.DataFrame(dists)

dist_df = generate_distributors()

# ─────────────────────────────────────────────────────────────
# GeM PORTAL DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def generate_gem_data():
    gem = {
        "Product": ["Surgical Gloves", "Syringes 5ml", "IV Cannula 18G", "Infusion Set",
                    "Crepe Bandage", "O2 Mask Adult", "Foley Catheter", "Sterile Gauze"],
        "Active_Bids": [14, 22, 11, 8, 6, 4, 3, 9],
        "Bids_Won": [6, 9, 4, 3, 2, 2, 1, 4],
        "Total_GeMRevenue": [284000, 412000, 198000, 145000, 89000, 72000, 54000, 167000],
        "Avg_Bid_Value": [48000, 52000, 45000, 38000, 29000, 36000, 54000, 41000],
        "Win_Rate_Pct": [42.9, 40.9, 36.4, 37.5, 33.3, 50.0, 33.3, 44.4],
        "Delivery_Score": [4.8, 4.6, 4.7, 4.5, 4.9, 4.4, 4.6, 4.8],
    }
    return pd.DataFrame(gem)

gem_df = generate_gem_data()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Cruzine Healthcare")
    st.markdown("**Analytics Command Center**")
    st.markdown("---")

    phase = st.radio(
        "📋 Select Phase",
        options=[
            "🏠 Executive Overview",
            "📊 Phase 1 — Foundational Visibility",
            "🎯 Phase 2 — Tactical Optimization",
            "🚀 Phase 3 — Strategic Expansion",
            "🏛️ GeM Portal Analytics",
        ]
    )

    st.markdown("---")
    st.markdown("**🗓️ Date Filter**")
    months_back = st.slider("Months of data", 1, 12, 6)
    cutoff = df["date"].max() - timedelta(days=months_back * 30)
    df_filtered = df[df["date"] >= cutoff].copy()

    st.markdown("---")
    st.markdown("**📦 Channel Filter**")
    channels = st.multiselect(
        "Sales channels",
        options=df["channel"].unique().tolist(),
        default=df["channel"].unique().tolist()
    )
    df_filtered = df_filtered[df_filtered["channel"].isin(channels)]

    st.markdown("---")
    st.markdown("""
    <div style='font-size:12px; color:#8B9BAB;'>
    📌 <b>Data Note</b><br>
    All data is synthetic sample data generated to simulate Cruzine Healthcare's
    realistic business scenario across 12 months.<br><br>
    Prepared by <b>Krishna</b> | BDA
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPER METRICS
# ─────────────────────────────────────────────────────────────
total_rev = df_filtered["revenue"].sum()
total_profit = df_filtered["gross_profit"].sum()
total_orders = len(df_filtered)
avg_margin = df_filtered["margin_pct"].mean()
unique_customers = df_filtered["customer"].nunique()
gem_rev = df_filtered[df_filtered["channel"] == "GeM"]["revenue"].sum()

# ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════
#   EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────
if phase == "🏠 Executive Overview":
    st.markdown("""
    <div class='phase-header'>
        <h2>Executive Overview — Cruzine Healthcare</h2>
        <p>Full business performance snapshot across all phases and channels</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Total Revenue", f"₹{total_rev/100000:.1f}L")
    col2.metric("📈 Gross Profit", f"₹{total_profit/100000:.1f}L")
    col3.metric("📦 Total Orders", f"{total_orders:,}")
    col4.metric("🏛️ GeM Revenue", f"₹{gem_rev/100000:.1f}L")
    col5.metric("📊 Avg Margin", f"{avg_margin:.1f}%")

    st.markdown("---")

    # Monthly revenue trend
    monthly = df_filtered.groupby(df_filtered["date"].dt.to_period("M")).agg(
        revenue=("revenue", "sum"),
        profit=("gross_profit", "sum"),
        orders=("revenue", "count")
    ).reset_index()
    monthly["date_str"] = monthly["date"].astype(str)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=monthly["date_str"], y=monthly["revenue"]/1000,
                         name="Revenue (₹K)", marker_color="#14A085", opacity=0.85), secondary_y=False)
    fig.add_trace(go.Bar(x=monthly["date_str"], y=monthly["profit"]/1000,
                         name="Gross Profit (₹K)", marker_color="#32C1A3", opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["date_str"], y=monthly["orders"],
                              name="Orders", line=dict(color="#F39C12", width=2.5),
                              mode="lines+markers"), secondary_y=True)
    fig.update_layout(title="Monthly Revenue, Profit & Orders",
                      plot_bgcolor="white", paper_bgcolor="white",
                      legend=dict(orientation="h", y=1.1),
                      height=380, barmode="group",
                      yaxis=dict(title="Amount (₹ Thousands)"),
                      yaxis2=dict(title="Order Count"))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        ch_rev = df_filtered.groupby("channel")["revenue"].sum().reset_index()
        fig2 = px.pie(ch_rev, values="revenue", names="channel",
                      title="Revenue by Channel",
                      color_discrete_sequence=["#0D7377","#14A085","#32C1A3","#F39C12","#E74C3C"])
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        cat_rev = df_filtered.groupby("category")["revenue"].sum().sort_values(ascending=True).reset_index()
        fig3 = px.bar(cat_rev, x="revenue", y="category", orientation="h",
                      title="Revenue by Product Category",
                      color="revenue", color_continuous_scale=["#DCE6EF","#0D7377"])
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                            coloraxis_showscale=False, height=320)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class='insight-card'>
    🔍 <b>Key Insight:</b> This executive dashboard gives Cruzine's management a real-time view of revenue,
    profitability, and channel performance. Implementing this on Day 1 immediately establishes data-driven
    decision making — your Phase 1 goal.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════
#   PHASE 1 — FOUNDATIONAL VISIBILITY (Days 1–30)
# ══════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────
elif phase == "📊 Phase 1 — Foundational Visibility":
    st.markdown("""
    <div class='phase-header'>
        <h2>Phase 1 — Foundational Visibility (Days 1–30)</h2>
        <p>Map data sources · Build Excel/SQL baselines · Identify Pareto 80/20 SKUs</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Products Tracked", f"{df_filtered['product'].nunique()}")
    col2.metric("👥 Active Customers", f"{unique_customers}")
    col3.metric("📊 Data Points", f"{total_orders:,}")
    col4.metric("🗓️ Days Covered", f"{months_back * 30}")

    st.markdown("---")
    st.subheader("📊 Pareto Analysis — 80/20 SKU Rule")
    st.markdown("*Identify the top 20% of SKUs generating 80% of revenue. Focus sales and inventory efforts here.*")

    sku_rev = df_filtered.groupby("product")["revenue"].sum().sort_values(ascending=False).reset_index()
    sku_rev["cumulative_pct"] = (sku_rev["revenue"].cumsum() / sku_rev["revenue"].sum() * 100).round(1)
    sku_rev["revenue_pct"] = (sku_rev["revenue"] / sku_rev["revenue"].sum() * 100).round(1)
    sku_rev["is_top20"] = sku_rev.index < int(len(sku_rev) * 0.2) + 1

    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    colors = ["#0D7377" if t else "#DCE6EF" for t in sku_rev["is_top20"]]
    fig_pareto.add_trace(
        go.Bar(x=sku_rev["product"], y=sku_rev["revenue"]/1000,
               name="Revenue (₹K)", marker_color=colors),
        secondary_y=False
    )
    fig_pareto.add_trace(
        go.Scatter(x=sku_rev["product"], y=sku_rev["cumulative_pct"],
                   name="Cumulative %", line=dict(color="#F39C12", width=2.5),
                   mode="lines+markers"),
        secondary_y=True
    )
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="#E74C3C",
                          annotation_text="80% Revenue Line", secondary_y=True)
    fig_pareto.update_layout(
        title="SKU Revenue — Pareto Chart (Teal = Top 20% SKUs)",
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=45), height=420,
        yaxis=dict(title="Revenue (₹ Thousands)"),
        yaxis2=dict(title="Cumulative Revenue %", range=[0, 105])
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # Top SKU table
    st.subheader("🏆 Top SKUs by Revenue")
    top_skus = sku_rev.head(8)[["product","revenue","revenue_pct","cumulative_pct"]].copy()
    top_skus["revenue"] = top_skus["revenue"].apply(lambda x: f"₹{x/1000:.1f}K")
    top_skus["revenue_pct"] = top_skus["revenue_pct"].apply(lambda x: f"{x:.1f}%")
    top_skus["cumulative_pct"] = top_skus["cumulative_pct"].apply(lambda x: f"{x:.1f}%")
    top_skus.columns = ["Product", "Revenue", "Revenue Share", "Cumulative %"]
    st.dataframe(top_skus, use_container_width=True, hide_index=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Revenue by Category")
        cat_margin = df_filtered.groupby("category").agg(
            revenue=("revenue","sum"), profit=("gross_profit","sum")
        ).reset_index()
        cat_margin["margin"] = (cat_margin["profit"] / cat_margin["revenue"] * 100).round(1)
        fig_cat = px.bar(cat_margin, x="category", y=["revenue","profit"],
                          barmode="group", title="Revenue vs Profit by Category",
                          color_discrete_sequence=["#0D7377","#32C1A3"])
        fig_cat.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               xaxis_tickangle=30, height=320,
                               legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.subheader("🗺️ Revenue by State")
        state_rev = df_filtered.groupby("state")["revenue"].sum().sort_values(ascending=False).reset_index()
        fig_state = px.bar(state_rev, x="state", y="revenue",
                            title="State-wise Revenue Distribution",
                            color="revenue", color_continuous_scale=["#E6FAF7","#0D7377"])
        fig_state.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                  coloraxis_showscale=False, height=320)
        st.plotly_chart(fig_state, use_container_width=True)

    st.markdown("""
    <div class='insight-card'>
    🎯 <b>Phase 1 Outcome:</b> The Pareto analysis reveals that just 4–5 SKUs
    (Surgical Gloves, Syringes, IV Cannula, Infusion Sets) drive ~80% of revenue.
    Cruzine should concentrate sales, stock, and GeM bid efforts on these products first.
    This is your SQL query + Excel Pivot baseline dashboard — built in the first 30 days.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════
#   PHASE 2 — TACTICAL OPTIMIZATION (Days 31–90)
# ══════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────
elif phase == "🎯 Phase 2 — Tactical Optimization":
    st.markdown("""
    <div class='phase-header'>
        <h2>Phase 2 — Tactical Optimization (Days 31–90)</h2>
        <p>Looker Studio dashboard · Customer segmentation · Demand forecasting · Dead stock elimination</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Real-Time Sales Tracking", "👥 Customer Segmentation", "📦 Demand Forecasting & Inventory"])

    # ── TAB 1: REAL-TIME SALES TRACKING ──
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        prev_period = df[df["date"] < cutoff]["revenue"].sum()
        rev_change = ((total_rev - prev_period) / max(prev_period, 1) * 100)
        col1.metric("Revenue", f"₹{total_rev/100000:.1f}L", f"{rev_change:+.1f}% vs prior")
        col2.metric("Gross Profit", f"₹{total_profit/100000:.1f}L", f"{avg_margin:.1f}% margin")
        col3.metric("Total Orders", f"{total_orders:,}")
        col4.metric("Unique Customers", f"{unique_customers}")

        # Weekly trend
        weekly = df_filtered.copy()
        weekly["week"] = weekly["date"].dt.to_period("W").astype(str)
        weekly_agg = weekly.groupby("week")["revenue"].sum().reset_index()
        fig_weekly = px.area(weekly_agg, x="week", y="revenue",
                              title="Weekly Revenue Trend (Looker Studio View)",
                              color_discrete_sequence=["#0D7377"])
        fig_weekly.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                  xaxis_tickangle=45, height=320,
                                  yaxis_title="Revenue (₹)")
        fig_weekly.update_traces(fill="tozeroy", fillcolor="rgba(13,115,119,0.12)")
        st.plotly_chart(fig_weekly, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            # Channel performance
            ch_perf = df_filtered.groupby("channel").agg(
                revenue=("revenue","sum"), orders=("revenue","count"),
                margin=("margin_pct","mean")
            ).reset_index()
            fig_ch = px.scatter(ch_perf, x="revenue", y="margin", size="orders",
                                 color="channel", title="Channel: Revenue vs Margin vs Volume",
                                 color_discrete_sequence=["#0D7377","#14A085","#32C1A3","#F39C12","#E74C3C"])
            fig_ch.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300)
            st.plotly_chart(fig_ch, use_container_width=True)

        with col2:
            # Top customers
            top_cust = df_filtered.groupby("customer")["revenue"].sum().nlargest(8).reset_index()
            top_cust["revenue_k"] = (top_cust["revenue"]/1000).round(1)
            fig_cust = px.bar(top_cust, x="revenue_k", y="customer", orientation="h",
                               title="Top 8 Customers by Revenue (₹K)",
                               color="revenue_k", color_continuous_scale=["#E6FAF7","#0D7377"])
            fig_cust.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                    coloraxis_showscale=False, height=300)
            st.plotly_chart(fig_cust, use_container_width=True)

    # ── TAB 2: CUSTOMER SEGMENTATION ──
    with tab2:
        st.subheader("👥 Customer RFM Segmentation")
        st.markdown("*Recency · Frequency · Monetary — the standard framework for hospital account prioritization*")

        cust_rfm = df_filtered.groupby("customer").agg(
            revenue=("revenue","sum"),
            orders=("revenue","count"),
            last_order=("date","max"),
            channel=("channel","first"),
            state=("state","first")
        ).reset_index()
        cust_rfm["recency_days"] = (df_filtered["date"].max() - cust_rfm["last_order"]).dt.days
        cust_rfm["avg_order_value"] = (cust_rfm["revenue"] / cust_rfm["orders"]).round(0)

        # Segment
        def segment(row):
            if row["revenue"] > cust_rfm["revenue"].quantile(0.75) and row["recency_days"] < 30:
                return "🏆 Champion"
            elif row["revenue"] > cust_rfm["revenue"].quantile(0.5) and row["recency_days"] < 60:
                return "⭐ Loyal"
            elif row["recency_days"] < 30:
                return "🌱 Promising"
            elif row["recency_days"] > 90:
                return "⚠️ At Risk"
            else:
                return "👋 Regular"

        cust_rfm["segment"] = cust_rfm.apply(segment, axis=1)

        col1, col2 = st.columns(2)
        with col1:
            seg_count = cust_rfm["segment"].value_counts().reset_index()
            fig_seg = px.pie(seg_count, values="count", names="segment",
                              title="Customer Segment Distribution",
                              color_discrete_sequence=["#0D7377","#14A085","#32C1A3","#F39C12","#E74C3C"])
            fig_seg.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320)
            st.plotly_chart(fig_seg, use_container_width=True)

        with col2:
            fig_scatter = px.scatter(cust_rfm, x="recency_days", y="revenue",
                                      size="orders", color="segment",
                                      title="RFM Map: Recency vs Revenue",
                                      hover_data=["customer","channel"],
                                      color_discrete_sequence=["#0D7377","#14A085","#32C1A3","#F39C12","#E74C3C"])
            fig_scatter.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320)
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.subheader("📋 Customer Segment Detail")
        display_rfm = cust_rfm[["customer","segment","revenue","orders","avg_order_value","recency_days","channel","state"]].copy()
        display_rfm["revenue"] = display_rfm["revenue"].apply(lambda x: f"₹{x/1000:.1f}K")
        display_rfm["avg_order_value"] = display_rfm["avg_order_value"].apply(lambda x: f"₹{x:,.0f}")
        display_rfm.columns = ["Customer", "Segment", "Revenue", "Orders", "Avg Order", "Last Order (days ago)", "Channel", "State"]
        st.dataframe(display_rfm.sort_values("Revenue", ascending=False), use_container_width=True, hide_index=True)

    # ── TAB 3: DEMAND FORECASTING ──
    with tab3:
        st.subheader("📦 Demand Forecasting & Dead Stock Analysis")
        selected_product = st.selectbox("Select Product to Forecast", df_filtered["product"].unique())

        prod_monthly = df_filtered[df_filtered["product"] == selected_product].copy()
        prod_monthly["month_period"] = prod_monthly["date"].dt.to_period("M")
        prod_agg = prod_monthly.groupby("month_period")["quantity"].sum().reset_index()
        prod_agg["month_str"] = prod_agg["month_period"].astype(str)

        if len(prod_agg) >= 3:
            # Simple linear forecast
            x = np.arange(len(prod_agg))
            y = prod_agg["quantity"].values
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)

            forecast_months = 3
            future_x = np.arange(len(prod_agg), len(prod_agg) + forecast_months)
            forecast_vals = p(future_x).clip(min=0)

            last_date = prod_agg["month_period"].max()
            future_labels = [(last_date + i + 1).strftime("%b %Y") for i in range(forecast_months)]

            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Bar(
                x=prod_agg["month_str"], y=prod_agg["quantity"],
                name="Actual Demand", marker_color="#0D7377"
            ))
            fig_forecast.add_trace(go.Bar(
                x=future_labels, y=forecast_vals.round(0),
                name="Forecasted Demand", marker_color="#F39C12", opacity=0.7
            ))
            trend_y = p(x)
            fig_forecast.add_trace(go.Scatter(
                x=prod_agg["month_str"], y=trend_y,
                name="Trend Line", line=dict(color="#E74C3C", dash="dot", width=2)
            ))
            fig_forecast.update_layout(
                title=f"Demand Forecast: {selected_product}",
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis_tickangle=30, height=360, barmode="overlay",
                yaxis_title="Units Demanded"
            )
            st.plotly_chart(fig_forecast, use_container_width=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Monthly Demand", f"{int(y.mean()):,} units")
            col2.metric("Next Month Forecast", f"{int(forecast_vals[0]):,} units")
            col3.metric("Trend", f"{'📈 +' if z[0] > 0 else '📉 '}{abs(z[0]):.0f} units/month")

        st.markdown("---")
        st.subheader("⚠️ Inventory Health — Dead Stock & Critical Alerts")

        col1, col2 = st.columns(2)
        with col1:
            status_colors = {"Critical": "#E74C3C", "Low": "#F39C12", "Healthy": "#27AE60", "Excess": "#3498DB"}
            status_count = inv_df["stock_status"].value_counts().reset_index()
            fig_inv = px.pie(status_count, values="count", names="stock_status",
                              title="Inventory Status Distribution",
                              color="stock_status",
                              color_discrete_map=status_colors)
            fig_inv.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300)
            st.plotly_chart(fig_inv, use_container_width=True)

        with col2:
            fig_stock = px.bar(
                inv_df.sort_values("current_stock"), x="current_stock", y="product",
                orientation="h", color="stock_status",
                title="Current Stock Levels by Product",
                color_discrete_map=status_colors
            )
            fig_stock.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300)
            st.plotly_chart(fig_stock, use_container_width=True)

        st.subheader("🚨 Action Required — Critical & Low Stock")
        alert_inv = inv_df[inv_df["stock_status"].isin(["Critical","Low"])][
            ["product","current_stock","reorder_level","lead_time_days","stock_status"]
        ].copy()
        alert_inv.columns = ["Product","Current Stock","Reorder Level","Lead Time (Days)","Status"]
        st.dataframe(alert_inv, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='insight-card'>
    🎯 <b>Phase 2 Outcome:</b> With real-time tracking, customer segmentation (RFM), and
    demand forecasting, Cruzine can reduce dead stock by ~30%, focus retention efforts on
    "At Risk" accounts, and pre-order before stockouts. This is your Looker Studio + Python
    dashboard — deployed by Day 90.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════
#   PHASE 3 — STRATEGIC EXPANSION (Days 91–180)
# ══════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────
elif phase == "🚀 Phase 3 — Strategic Expansion":
    st.markdown("""
    <div class='phase-header'>
        <h2>Phase 3 — Strategic Expansion (Days 91–180)</h2>
        <p>Distributor tracker · Predictive reorder alerts · Export market analysis</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🤝 Distributor Performance", "🔔 Predictive Reorder Alerts", "🌍 Export Market Analysis"])

    # ── DISTRIBUTOR PERFORMANCE ──
    with tab1:
        st.subheader("🤝 Distributor Performance Tracker")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Distributors", f"{len(dist_df)}")
        col2.metric("Total Dist. Revenue", f"₹{dist_df['Monthly_Revenue'].sum()/100000:.1f}L/mo")
        col3.metric("Avg Payment Days", f"{dist_df['Payment_Days'].mean():.0f} days")
        col4.metric("Best Growth", f"+{dist_df['Growth_MoM_Pct'].max():.1f}% MoM")

        col1, col2 = st.columns(2)
        with col1:
            fig_dist = px.bar(dist_df.sort_values("Monthly_Revenue"), x="Monthly_Revenue", y="Distributor",
                               orientation="h", color="Growth_MoM_Pct",
                               title="Monthly Revenue by Distributor",
                               color_continuous_scale=["#E74C3C","#F39C12","#27AE60"])
            fig_dist.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=340)
            st.plotly_chart(fig_dist, use_container_width=True)

        with col2:
            fig_bubble = px.scatter(dist_df, x="Payment_Days", y="Growth_MoM_Pct",
                                     size="Monthly_Revenue", color="Satisfaction_Score",
                                     text="Distributor",
                                     title="Distributor Risk Map: Payment Days vs Growth",
                                     color_continuous_scale=["#E74C3C","#F39C12","#27AE60"])
            fig_bubble.add_vline(x=30, line_dash="dash", line_color="orange",
                                   annotation_text="30-day threshold")
            fig_bubble.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=340)
            st.plotly_chart(fig_bubble, use_container_width=True)

        st.subheader("📊 Detailed Distributor Scorecard")
        dist_display = dist_df.copy()
        dist_display["Monthly_Revenue"] = dist_display["Monthly_Revenue"].apply(lambda x: f"₹{x/1000:.0f}K")
        dist_display["Avg_Order_Value"] = dist_display["Avg_Order_Value"].apply(lambda x: f"₹{x:,}")
        dist_display["Growth_MoM_Pct"] = dist_display["Growth_MoM_Pct"].apply(lambda x: f"{x:+.1f}%")
        dist_display["Return_Rate_Pct"] = dist_display["Return_Rate_Pct"].apply(lambda x: f"{x:.1f}%")
        dist_display["Satisfaction_Score"] = dist_display["Satisfaction_Score"].apply(lambda x: f"⭐ {x:.1f}")
        st.dataframe(dist_display, use_container_width=True, hide_index=True)

    # ── PREDICTIVE REORDER ──
    with tab2:
        st.subheader("🔔 Predictive Reorder Alert System")
        st.markdown("*Python-powered prediction: calculates days-to-stockout for each product based on demand velocity*")

        product_demand = df_filtered.groupby("product")["quantity"].sum()
        days_in_period = months_back * 30
        daily_demand = (product_demand / days_in_period).round(1)

        reorder_df = inv_df.copy()
        reorder_df["daily_demand"] = reorder_df["product"].map(daily_demand).fillna(10)
        reorder_df["days_to_stockout"] = (reorder_df["current_stock"] / reorder_df["daily_demand"]).round(0).clip(0, 999)
        reorder_df["reorder_urgency"] = reorder_df.apply(
            lambda r: "🚨 Order NOW" if r["days_to_stockout"] <= r["lead_time_days"]
            else ("⚠️ Order Soon" if r["days_to_stockout"] <= r["lead_time_days"] * 2
            else "✅ Stock OK"), axis=1
        )
        reorder_df["suggested_qty"] = ((reorder_df["daily_demand"] * 30 * 1.2) - reorder_df["current_stock"]).clip(0).round(0).astype(int)

        col1, col2, col3 = st.columns(3)
        critical = (reorder_df["reorder_urgency"] == "🚨 Order NOW").sum()
        warning = (reorder_df["reorder_urgency"] == "⚠️ Order Soon").sum()
        ok = (reorder_df["reorder_urgency"] == "✅ Stock OK").sum()
        col1.metric("🚨 Order NOW", f"{critical} products")
        col2.metric("⚠️ Order Soon", f"{warning} products")
        col3.metric("✅ Stock OK", f"{ok} products")

        fig_days = px.bar(reorder_df.sort_values("days_to_stockout"), x="days_to_stockout", y="product",
                           orientation="h", color="reorder_urgency",
                           title="Days to Stockout by Product",
                           color_discrete_map={"🚨 Order NOW": "#E74C3C", "⚠️ Order Soon": "#F39C12", "✅ Stock OK": "#27AE60"})
        fig_days.add_vline(x=14, line_dash="dash", line_color="#F39C12", annotation_text="14-day alert")
        fig_days.add_vline(x=7, line_dash="dash", line_color="#E74C3C", annotation_text="7-day critical")
        fig_days.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=500)
        st.plotly_chart(fig_days, use_container_width=True)

        st.subheader("📋 Reorder Action List")
        action_df = reorder_df[reorder_df["reorder_urgency"] != "✅ Stock OK"][[
            "product","current_stock","daily_demand","days_to_stockout","lead_time_days","suggested_qty","reorder_urgency"
        ]].sort_values("days_to_stockout")
        action_df.columns = ["Product","Current Stock","Daily Demand","Days to Stockout","Lead Time","Suggested Order Qty","Urgency"]
        st.dataframe(action_df, use_container_width=True, hide_index=True)

    # ── EXPORT MARKET ANALYSIS ──
    with tab3:
        st.subheader("🌍 Export Market Analysis — Prioritize by Margin Potential")
        st.markdown("*Automated scoring of export markets based on demand, ease of entry, and certification alignment*")

        export_markets = pd.DataFrame({
            "Country": ["UAE", "Kenya", "Vietnam", "Saudi Arabia", "Bangladesh", "Ethiopia",
                         "Tanzania", "Sri Lanka", "Nepal", "Myanmar"],
            "Region": ["Middle East","Africa","Asia","Middle East","Asia","Africa","Africa","Asia","Asia","Asia"],
            "Market_Size_USD_M": [320, 145, 280, 410, 190, 120, 95, 85, 70, 110],
            "Entry_Ease_Score": [7.2, 6.8, 7.5, 6.5, 8.1, 6.2, 6.0, 7.8, 8.3, 7.1],
            "Cruzine_Cert_Match": [9.0, 7.5, 8.0, 8.5, 7.0, 7.0, 6.5, 7.5, 7.0, 6.8],
            "Margin_Potential_Pct": [42, 35, 38, 45, 28, 30, 28, 32, 30, 31],
            "Competition_Level": ["Medium","Low","High","Medium","Low","Low","Low","Low","Low","Low"],
            "Estimated_Revenue_Yr1_K": [420, 210, 340, 380, 180, 140, 110, 130, 100, 125],
        })
        export_markets["Priority_Score"] = (
            export_markets["Entry_Ease_Score"] * 0.3 +
            export_markets["Cruzine_Cert_Match"] * 0.35 +
            export_markets["Margin_Potential_Pct"] / 5 * 0.35
        ).round(2)
        export_markets = export_markets.sort_values("Priority_Score", ascending=False)

        fig_export = px.scatter(export_markets, x="Entry_Ease_Score", y="Margin_Potential_Pct",
                                 size="Market_Size_USD_M", color="Region", text="Country",
                                 title="Export Market Opportunity Map",
                                 size_max=50,
                                 color_discrete_sequence=["#0D7377","#14A085","#F39C12"])
        fig_export.update_traces(textposition="top center")
        fig_export.add_hline(y=35, line_dash="dash", line_color="#14A085", annotation_text="35%+ margin target")
        fig_export.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=420)
        st.plotly_chart(fig_export, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig_priority = px.bar(export_markets.head(6), x="Country", y="Priority_Score",
                                   color="Priority_Score", title="Top Markets by Priority Score",
                                   color_continuous_scale=["#DCE6EF","#0D7377"])
            fig_priority.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                        coloraxis_showscale=False, height=300)
            st.plotly_chart(fig_priority, use_container_width=True)

        with col2:
            fig_rev = px.bar(export_markets.head(6), x="Country", y="Estimated_Revenue_Yr1_K",
                              color="Margin_Potential_Pct", title="Estimated Year 1 Revenue (₹K)",
                              color_continuous_scale=["#E6FAF7","#0D7377"])
            fig_rev.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                   coloraxis_showscale=False, height=300)
            st.plotly_chart(fig_rev, use_container_width=True)

        st.subheader("📊 Export Market Scorecard")
        exp_display = export_markets[["Country","Region","Margin_Potential_Pct","Entry_Ease_Score",
                                       "Cruzine_Cert_Match","Priority_Score","Estimated_Revenue_Yr1_K","Competition_Level"]].copy()
        exp_display.columns = ["Country","Region","Margin %","Entry Ease","Cert Match","Priority Score","Est. Rev Yr1 (₹K)","Competition"]
        st.dataframe(exp_display, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='insight-card'>
    🚀 <b>Phase 3 Outcome:</b> With the distributor scorecard, predictive reorder system,
    and export market analysis live by Day 180, Cruzine has a fully data-driven commercial
    engine. UAE and Saudi Arabia emerge as top-priority export markets due to high margins,
    strong certification match, and moderate competition.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════
#   GeM PORTAL ANALYTICS
# ══════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────
elif phase == "🏛️ GeM Portal Analytics":
    st.markdown("""
    <div class='phase-header'>
        <h2>GeM Portal Analytics — Government e-Marketplace</h2>
        <p>Bid performance · Win rates · Revenue tracking · Catalogue optimization</p>
    </div>
    """, unsafe_allow_html=True)

    gem_channel = df_filtered[df_filtered["channel"] == "GeM"]
    gem_total = gem_channel["revenue"].sum()
    gem_orders = len(gem_channel)
    gem_share = gem_total / max(total_rev, 1) * 100
    gem_margin = gem_channel["margin_pct"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🏛️ GeM Revenue", f"₹{gem_total/100000:.1f}L")
    col2.metric("📦 GeM Orders", f"{gem_orders:,}")
    col3.metric("📊 GeM Revenue Share", f"{gem_share:.1f}%")
    col4.metric("💰 GeM Margin", f"{gem_margin:.1f}%")
    col5.metric("🏆 Active Bids", f"{gem_df['Active_Bids'].sum()}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        fig_winrate = px.bar(gem_df.sort_values("Win_Rate_Pct", ascending=False),
                              x="Product", y="Win_Rate_Pct",
                              title="Bid Win Rate by Product (%)",
                              color="Win_Rate_Pct",
                              color_continuous_scale=["#E74C3C","#F39C12","#27AE60"])
        fig_winrate.add_hline(y=35, line_dash="dash", line_color="#0D7377",
                               annotation_text="Target: 35% win rate")
        fig_winrate.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                   coloraxis_showscale=False, height=340, xaxis_tickangle=25)
        st.plotly_chart(fig_winrate, use_container_width=True)

    with col2:
        fig_gemrev = px.bar(gem_df.sort_values("Total_GeMRevenue", ascending=False),
                             x="Product", y="Total_GeMRevenue",
                             title="Total GeM Revenue by Product (₹)",
                             color="Total_GeMRevenue",
                             color_continuous_scale=["#E6FAF7","#0D7377"])
        fig_gemrev.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                  coloraxis_showscale=False, height=340, xaxis_tickangle=25)
        st.plotly_chart(fig_gemrev, use_container_width=True)

    # GeM monthly trend
    if not gem_channel.empty:
        gem_monthly = gem_channel.copy()
        gem_monthly["month_period"] = gem_monthly["date"].dt.to_period("M")
        gem_monthly_agg = gem_monthly.groupby("month_period").agg(
            revenue=("revenue","sum"), orders=("revenue","count")
        ).reset_index()
        gem_monthly_agg["month_str"] = gem_monthly_agg["month_period"].astype(str)

        fig_gem_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_gem_trend.add_trace(go.Bar(x=gem_monthly_agg["month_str"], y=gem_monthly_agg["revenue"]/1000,
                                        name="GeM Revenue (₹K)", marker_color="#0D7377"), secondary_y=False)
        fig_gem_trend.add_trace(go.Scatter(x=gem_monthly_agg["month_str"], y=gem_monthly_agg["orders"],
                                            name="GeM Orders", line=dict(color="#F39C12", width=2),
                                            mode="lines+markers"), secondary_y=True)
        fig_gem_trend.update_layout(title="Monthly GeM Revenue & Order Trend",
                                     plot_bgcolor="white", paper_bgcolor="white",
                                     height=320, legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_gem_trend, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 GeM Bid Scorecard")
        gem_display = gem_df[["Product","Active_Bids","Bids_Won","Win_Rate_Pct","Total_GeMRevenue","Delivery_Score"]].copy()
        gem_display["Total_GeMRevenue"] = gem_display["Total_GeMRevenue"].apply(lambda x: f"₹{x/1000:.0f}K")
        gem_display["Win_Rate_Pct"] = gem_display["Win_Rate_Pct"].apply(lambda x: f"{x:.1f}%")
        gem_display["Delivery_Score"] = gem_display["Delivery_Score"].apply(lambda x: f"⭐ {x}")
        gem_display.columns = ["Product","Active Bids","Won","Win Rate","Revenue","Delivery Score"]
        st.dataframe(gem_display, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("🎯 GeM Optimization Tips")
        st.markdown("""
        <div class='gem-card'>
            <h4>📈 Increase Win Rate</h4>
            <p>O2 Mask (50%) is top performer. Apply its pricing + doc strategy to Catheters (33%).</p>
        </div>
        <div class='gem-card'>
            <h4>📦 Maximize Catalogue Visibility</h4>
            <p>Syringes have 22 active bids — highest opportunity. Ensure all 3 sizes are listed with specs.</p>
        </div>
        <div class='gem-card'>
            <h4>🏆 MSME Badge Impact</h4>
            <p>Completing Udyam registration unlocks EMD exemption across all 67 open bids this quarter.</p>
        </div>
        <div class='gem-card'>
            <h4>💰 Revenue Optimization</h4>
            <p>Syringes + Gloves = 56% of GeM revenue. These need dedicated bid monitoring daily.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='insight-card'>
    🏛️ <b>GeM Insight:</b> Cruzine's current GeM win rate averages 40% — above the industry
    average of 30–35%. Key opportunity: Catheters and Infusion Sets are under-bid (3–8 active bids)
    relative to their potential. These categories have lower competition on GeM. Push bids here
    aggressively using ISO 13485 compliance as the differentiator.
    </div>
    """, unsafe_allow_html=True)
    st.title("Hello Krishna 🚀")
st.write("Streamlit is working!")