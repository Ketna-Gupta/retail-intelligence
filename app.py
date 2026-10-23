
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ====================== PAGE CONFIGURATION ======================

st.set_page_config(
    page_title="Retail Intelligence",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e7eaf1;
    padding: 16px;
    border-radius: 12px;
}
h1, h2, h3 {
    color: #172554;
}
</style>
""", unsafe_allow_html=True)

st.title("RETAIL INTELLIGENCE")
st.caption("Sales performance • Profitability • Business decisions")

# ====================== DATA SOURCE ======================

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "valiotti/plotly-superstore/main/superstore.csv"
)

LOCAL_OPTIONS = [
    Path("superstore.csv"),
    Path("superstore_sales.csv"),
    Path("superstore_sales.csv.csv"),
    Path("data/superstore.csv"),
    Path("Sample - Superstore.csv")
]

# ====================== LOAD AND CLEAN DATA ======================

@st.cache_data(show_spinner="Loading retail data...")
def load_data():

    path = next(
        (p for p in LOCAL_OPTIONS if p.exists()),
        None
    )

    if path:
        data = pd.read_csv(path, encoding="latin1")
        source = f"Local file: {path}"
    else:
        data = pd.read_csv(DATA_URL, encoding="latin1")
        source = "Public GitHub dataset"

    data.columns = data.columns.astype(str).str.strip()

    # Required columns available in the current CSV
    required = [
        "Order Date",
        "Region",
        "Category",
        "Sub-Category",
        "Segment",
        "Sales",
        "Profit",
        "Quantity"
    ]

    missing = [
        col for col in required
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            "Required columns missing: "
            + ", ".join(missing)
            + "\nColumns found: "
            + ", ".join(data.columns)
        )

    # Convert date
    data["Order Date"] = pd.to_datetime(
        data["Order Date"],
        errors="coerce"
    )

    # Convert numeric columns
    for col in ["Sales", "Profit", "Quantity"]:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    rows_before = len(data)

    # Remove records with missing required values
    data = data.dropna(
        subset=required
    ).copy()

    # Remove duplicate records
    data = data.drop_duplicates()

    # Remove invalid transactions
    data = data[
        (data["Sales"] >= 0) &
        (data["Quantity"] > 0)
    ].copy()

    if data.empty:
        raise ValueError(
            "No valid transaction records remain after cleaning."
        )

    # Create analysis columns
    data["Order Month"] = (
        data["Order Date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    data["Profit Margin (%)"] = (
        data["Profit"]
        / data["Sales"].replace(0, float("nan"))
        * 100
    )

    cleaning_info = {
        "before": rows_before,
        "after": len(data),
        "removed": rows_before - len(data)
    }

    return data, source, cleaning_info


# ====================== HANDLE LOADING ERRORS ======================

try:
    df, source_label, cleaning_info = load_data()

except Exception as exc:
    st.error("The dataset could not be loaded.")
    st.code(str(exc))
    st.info(
        "Place your CSV beside app.py. "
        "Supported filenames include superstore.csv "
        "and superstore_sales.csv."
    )
    st.stop()


# ====================== SIDEBAR FILTERS ======================

with st.sidebar:

    st.header("Explore the data")

    st.caption(
        "Filters apply to all dashboard sections."
    )

    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()

    date_range = st.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = min_date
        end_date = max_date

    all_regions = sorted(
        df["Region"].dropna().unique().tolist()
    )

    all_categories = sorted(
        df["Category"].dropna().unique().tolist()
    )

    all_segments = sorted(
        df["Segment"].dropna().unique().tolist()
    )

    regions = st.multiselect(
        "Region",
        all_regions,
        default=all_regions
    )

    categories = st.multiselect(
        "Category",
        all_categories,
        default=all_categories
    )

    segments = st.multiselect(
        "Customer segment",
        all_segments,
        default=all_segments
    )

    st.divider()

    st.caption(f"Source: {source_label}")

    st.caption(
        f"Rows retained: {cleaning_info['after']:,}"
    )

    st.caption(
        f"Rows removed during cleaning: "
        f"{cleaning_info['removed']:,}"
    )


# ====================== APPLY FILTERS ======================

filtered = df[
    (df["Order Date"].dt.date >= start_date)
    & (df["Order Date"].dt.date <= end_date)
    & (df["Region"].isin(regions))
    & (df["Category"].isin(categories))
    & (df["Segment"].isin(segments))
].copy()

if filtered.empty:
    st.warning(
        "No records match these filters. "
        "Please widen your selection."
    )
    st.stop()


# ====================== KPI CALCULATIONS ======================

sales_total = filtered["Sales"].sum()
profit_total = filtered["Profit"].sum()

record_count = len(filtered)

profit_margin = (
    profit_total / sales_total * 100
    if sales_total != 0 else 0
)

avg_sales_per_record = (
    sales_total / record_count
    if record_count else 0
)


# ====================== DASHBOARD NAVIGATION ======================

dashboard_tab = st.radio(
    "Dashboard",
    [
        "Executive Overview",
        "Product & Profitability",
        "Business Insights"
    ],
    horizontal=True
)


# ====================== EXECUTIVE OVERVIEW ======================

if dashboard_tab == "Executive Overview":

    st.subheader("Executive Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Revenue",
        f"${sales_total:,.0f}"
    )

    c2.metric(
        "Profit",
        f"${profit_total:,.0f}"
    )

    c3.metric(
        "Order-line records",
        f"{record_count:,}"
    )

    c4.metric(
        "Profit margin",
        f"{profit_margin:.1f}%"
    )

    st.caption(
        f"Average sales per order-line record: "
        f"${avg_sales_per_record:,.2f}. "
        "This is not average order value."
    )

    # Monthly performance
    monthly = (
        filtered.groupby("Order Month", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.line(
            monthly,
            x="Order Month",
            y="Sales",
            markers=True,
            title="Monthly Revenue Trend"
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue ($)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        region_perf = (
            filtered.groupby("Region", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )

        fig = px.bar(
            region_perf,
            x="Region",
            y=["Sales", "Profit"],
            barmode="group",
            title="Revenue vs Profit by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Category analysis
    category_perf = (
        filtered.groupby("Category", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
    )

    fig = px.bar(
        category_perf,
        x="Category",
        y="Sales",
        color="Profit",
        color_continuous_scale="Teal",
        title="Category Revenue and Profitability"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "Business takeaway: Revenue alone does not measure "
        "business success. Always compare revenue with profit."
    )


# ====================== PRODUCT & PROFITABILITY ======================

elif dashboard_tab == "Product & Profitability":

    st.subheader("Product & Profitability")

    subcategory_perf = (
        filtered.groupby("Sub-Category", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum")
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            subcategory_perf.sort_values("Profit"),
            x="Profit",
            y="Sub-Category",
            orientation="h",
            color="Profit",
            color_continuous_scale="RdYlGn",
            title="Profit by Sub-Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.scatter(
            subcategory_perf,
            x="Sales",
            y="Profit",
            size="Units",
            color="Sub-Category",
            hover_data=["Units"],
            title="Sub-Category Sales vs Profit"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("### Sub-Category Performance Ranking")

    st.dataframe(
        subcategory_perf.sort_values(
            "Sales",
            ascending=False
        ).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "The supplied CSV does not contain Product Name "
        "or Discount columns. Therefore, the analysis is "
        "performed at sub-category level."
    )


# ====================== BUSINESS INSIGHTS ======================

else:

    st.subheader("Business Insights & Action Priorities")

    region_perf = (
        filtered.groupby("Region", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
    )

    region_perf["Margin (%)"] = (
        region_perf["Profit"]
        / region_perf["Sales"].replace(0, float("nan"))
        * 100
    )

    segment_perf = (
        filtered.groupby("Segment", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
    )

    subcategory_perf = (
        filtered.groupby("Sub-Category", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
    )

    # Regional margin chart
    fig = px.bar(
        region_perf.sort_values("Margin (%)"),
        x="Region",
        y="Margin (%)",
        color="Margin (%)",
        color_continuous_scale="RdYlGn",
        title="Regional Profit Margin"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("### Findings from Current Filters")

    if not region_perf.empty:

        highest_revenue = region_perf.loc[
            region_perf["Sales"].idxmax()
        ]

        st.write(
            f"- **Largest revenue region:** "
            f"{highest_revenue['Region']} with "
            f"${highest_revenue['Sales']:,.0f} revenue "
            f"and ${highest_revenue['Profit']:,.0f} profit."
        )

        valid_margin = region_perf.dropna(
            subset=["Margin (%)"]
        )

        if not valid_margin.empty:

            lowest_margin = valid_margin.loc[
                valid_margin["Margin (%)"].idxmin()
            ]

            st.write(
                f"- **Lowest-margin region:** "
                f"{lowest_margin['Region']} at "
                f"{lowest_margin['Margin (%)']:.1f}% margin. "
                "Investigate product mix and costs."
            )

    # Loss-making subcategories
    loss_subcategories = subcategory_perf[
        subcategory_perf["Profit"] < 0
    ].sort_values("Profit")

    if not loss_subcategories.empty:

        worst = loss_subcategories.iloc[0]

        st.write(
            f"- **Largest loss sub-category:** "
            f"{worst['Sub-Category']} with net profit "
            f"${worst['Profit']:,.0f}. "
            "Review pricing, assortment and fulfillment costs."
        )

    else:

        st.write(
            "- No loss-making sub-categories appear "
            "under the current filters."
        )

    # Segment profitability
    if not segment_perf.empty:

        best_segment = segment_perf.loc[
            segment_perf["Profit"].idxmax()
        ]

        st.write(
            f"- **Highest total profit segment:** "
            f"{best_segment['Segment']} with "
            f"${best_segment['Profit']:,.0f} profit."
        )

    # Business recommendations
    st.markdown("### Recommended Business Actions")

    st.write(
        "1. Review sub-categories with negative profit "
        "before increasing promotion or inventory."
    )

    st.write(
        "2. Investigate low-margin regions by comparing "
        "product mix and service/fulfillment costs."
    )

    st.write(
        "3. Explore profitable customer segments with "
        "retention and cross-selling ideas. Validate results "
        "with a controlled test."
    )

    st.write(
        "4. Monitor monthly sales and profit together "
        "so revenue growth is not mistaken for better "
        "profitability."
    )

    st.caption(
        "These recommendations are hypotheses to validate "
        "with business context. This dataset does not establish "
        "causal effects."
    )


# ====================== FILTERED DATA & DOWNLOAD ======================

st.divider()

st.subheader("Filtered Transaction Records")

st.caption(
    f"{len(filtered):,} order-line records "
    "shown after filters."
)

export_data = filtered.drop(
    columns=[
        "Order Month",
        "Profit Margin (%)"
    ],
    errors="ignore"
).to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Data (CSV)",
    data=export_data,
    file_name="filtered_retail_transactions.csv",
    mime="text/csv"
)

with st.expander("Preview Records"):

    st.dataframe(
        filtered.head(100),
        use_container_width=True,
        hide_index=True
    )
