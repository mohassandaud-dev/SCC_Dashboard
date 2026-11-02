import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import numpy as np
import requests
from requests.auth import HTTPBasicAuth
import os
from datetime import date


# =============================================================
# 1. CONFIGURATION
# =============================================================
API_URL = (
    "https://somcc.redrosecps.com/"
    "externalapi/customQuery/queryToJson"
    "?queryName=BeneficiaryDetailsV2"
)
username = st.secrets["redrose"]["username"]
password = st.secrets["redrose"]["password"]


CASE_LOAD_VALUES = ["og_2026", "OG_2026"]
MODALITY_VALUES = [
    "CCCM Referral",
    "Nutrition Referral",
    "Hard to Reach",
    "Accessible",
    "Protection Referral",
]


# =============================================================
# 2. DATA LOADING
# =============================================================
@st.cache_data(ttl=600, show_spinner="Loading beneficiary data from RedRose API...")
def load_data():
    response = requests.get(
        API_URL,
        auth=HTTPBasicAuth(username, password),
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    records = payload.get("data", payload) if isinstance(payload, dict) else payload
    return pd.DataFrame(records)


try:
    pff = load_data()
except requests.exceptions.HTTPError as e:
    st.error(f"RedRose API returned an HTTP error: {e}")
    st.stop()
except requests.exceptions.RequestException as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error loading data: {e}")
    st.stop()




GEOJSON_PATH = "somgeojson/som_admin2.geojson"
LOGO_PATH = "log2.png"

DASHBOARD_PALETTE11 = [
    "#7e0d00", "#b30000", "#ff0000", "#ff305a", "#ff85a4"
]

red_scale = [
    "#FFE5E5",  # very pale red
    "#FFB3B3",  # light red
    "#FF6666",  # soft red
    "#E60000",  # strong red
    "#990000",  # deep red
    "#4D0000",  # very dark red
]

DASHBOARD_PALETTE = [
 "#d00413", "#ea4200", "#fd6a00", "#ff9800", "#ffbe00", "#ffe000", "#ffff00"
]

red_scale = [
    "#FFD9CC",  # pale peach-red
    "#FF9E7A",  # light orange-red
    "#F4511E",  # vivid orange-red
    "#D81B1B",  # pure bright red
    "#8E0E1C",  # deep crimson
    "#4A0410",  # near-black maroon
]

DASHBOARD_PALETTE2 = [
    "#67000D", "#A50F15", "#D7301F",
    "#EF6548", "#F46D43", "#FCAE4B",
]

GENDER_COLORS = {"Female": "#D7301F", "Male": "#EF6548"}
# =============================================================
# 3. DATA PREPARATION
# =============================================================
pff = pff[
    (pff["Caseload"].isin(CASE_LOAD_VALUES))
    & (pff["Modality"].isin(MODALITY_VALUES))
].copy()

pff = pff.rename(columns={
    "ADM L1": "FMS",
    "ADM L2": "Region",
    "ADM L3": "District",
    "ADM L4": "Village",
})

# Precompute unique options for filter dropdowns
UNIQUE_AGENCIES = sorted(pff["Agency"].dropna().unique().tolist())


# =============================================================
# 4. PAGE CONFIG & STYLES
# =============================================================
st.set_page_config(page_title="Humanitarian Dashboard", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 0px;
        padding-bottom: 1rem;
    }
    #humanitarian-dashboard { margin-top: -30px; z-index: 900000; }
    .ssstElementContainer {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    div[data-testid="stPlotlyChart"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        overflow: hidden !important; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .st-key-dashboard_header {
        background: #fff;
        padding: 10px 10px;
        border-radius: 0px;
        margin-top: -30px;
        border-bottom: darkred 2px solid;
    }
    .st-key-filter_header {
        padding: 0px 10px 10px 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        background: #E85D045;
        border: 1px solid #E85D04;
    }
    .filter-header {
        background: #D00000;
        color: white;
        display: flex;
        align-items: center;
        padding-left: 8px;
        font-size: 20px;
        font-weight: 700;
        gap: 12px;
        border-bottom: 1px #867B79 solid;
        border-radius: 10px !important;
    }
    .filter-header i { font-size: 18px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<link rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
""", unsafe_allow_html=True)


# =============================================================
# 5. HELPER: KPI CARD
# =============================================================
def kpi_card(title, value, icon, color="#2563eb"):
    st.html(f"""
        <div style="
            background-color: white;
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            width: 100%;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
                color: #6b7280;
                font-size: 15px;
            ">
                <i class="{icon}" style="color: {color}; font-size: 20px;"></i>
                <span>{title}</span>
            </div>
            <div style="
                margin-top: 10px;
                font-size: 32px;
                font-weight: 700;
                color: #111827;
            ">
                {value}
            </div>
        </div>
        """)


# =============================================================
# 6. HEADER
# =============================================================
header = st.container(key="dashboard_header")
with header:
    c1, c2 = st.columns([1, 8])
    with c1:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
    with c2:
        st.markdown(
            "<h2 style='color:#111827; margin:auto;'>Humanitarian Dashboard</h2>",
            unsafe_allow_html=True,
        )


# =============================================================
# 7. FILTERS
# =============================================================
filters = st.container(key="filter_header")
with filters:
    st.markdown(
        '<div class="filter-header">'
        '<i class="fa-solid fa-filter"></i>'
        '<span>Filters</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)

    with sc1:
        agency = st.selectbox(
            "Agency",
            ["All"] + UNIQUE_AGENCIES,
            key="filter_agency",
        )
    sub_agency = pff if agency == "All" else pff[pff["Agency"] == agency]

    with sc2:
        region_options = sorted(sub_agency["Region"].dropna().unique().tolist())
        region = st.selectbox(
            "Region",
            ["All"] + region_options,
            key="filter_region",
        )
    sub_region = sub_agency if region == "All" else sub_agency[sub_agency["Region"] == region]

    with sc3:
        district_options = sorted(sub_region["District"].dropna().unique().tolist())
        district = st.selectbox(
            "District",
            ["All"] + district_options,
            key="filter_district",
        )
    sub_district = sub_region if district == "All" else sub_region[sub_region["District"] == district]

    with sc4:
        st.write("Placeholder")
    with sc5:
        date_range = st.date_input(
            "Select date range",
            value=(date(2026, 1, 1), date.today()),
            format="DD/MM/YYYY",
            key="filter_date_range"
        )
        # Apply date filter
        filtered_data = sub_district.copy()
        filtered_data["Registration Date"] = pd.to_datetime(
            filtered_data["Registration Date"],
            errors="coerce",
            dayfirst=True
        )
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

            start_date, end_date = date_range

            filtered_data = filtered_data[
                filtered_data["Registration Date"].notna() &
                (filtered_data["Registration Date"].dt.date >= start_date) &
                (filtered_data["Registration Date"].dt.date <= end_date)
            ]

        # 6. Display results
        #st.write("Filtered records:", len(filtered_data))
filtered_data = filtered_data #sub_district

#Format some column values 
filtered_data["Marginalised"] = (
            filtered_data["Marginalised"]
            .astype("string")
            .str.strip()
            .str.lower()
            .map({
                "yes": "Yes",
                "no": "No"
            })
        )
# =============================================================
# 8. KPI CARDS
# =============================================================
t_bnfs = filtered_data["Id"].nunique() if "Id" in filtered_data else 0
t_district = filtered_data["District"].nunique()
t_villages = filtered_data["Village"].nunique() if "Village" in filtered_data else 0
t_agencies = filtered_data["Agency"].nunique()
t_modality = filtered_data["Modality"].nunique()

female_bnfs = (
    filtered_data.query("Gender == 'Female'")["Id"].nunique()
    if "Gender" in filtered_data.columns else 0
)
pct_female = (female_bnfs / t_bnfs * 100) if t_bnfs else 0

card1, card2, card3, card4, card5, card6 = st.columns(6)
with card1:
    kpi_card("Beneficiaries", f"{t_bnfs:,}", "fa-solid fa-users", "#14b30e")
with card2:
    kpi_card("Districts", f"{t_district:,}", "fa-solid fa-house", "#2563eb")
with card3:
    kpi_card("Villages", f"{t_villages:,}", "fa-solid fa-location-dot", "#f00f00")
with card4:
    kpi_card("Agencies", f"{t_agencies:,}", "fa-solid fa-building", "#9333ea")
with card5:
    kpi_card("Modalities", f"{t_modality:,}", "fa-solid fa-layer-group", "#0891b2")
with card6:
    kpi_card("Female %", f"{pct_female:.1f}%", "fa-solid fa-venus", "#db2777")


# =============================================================
# 9. TABS
# =============================================================
t1, t2, t3 = st.tabs(["Analysis", "Target Vs Reach", "Overview"])

# ----------------- T1: Analysis -----------------
with t1:
    c1, c2, c3 = st.columns(3)

    # --- Chart 1: BNFs by Modality ---
    with c1:
        modality_dist = (
            filtered_data
            .groupby("Modality", as_index=False)
            .agg(BNFs=("Id", "nunique"))
            .sort_values("BNFs", ascending=False)
        )

        fig = px.bar(
            modality_dist,
            x="Modality",
            y="BNFs",
            color="Modality",
            color_discrete_sequence=DASHBOARD_PALETTE,
            title="BNFs by Modality",
        )
        fig.update_layout(
            showlegend=False,
            barmode="stack",
            yaxis_title=None,
            xaxis_title=None,
            autosize=False,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False,"responsive": True})

    # --- Chart 2: BNFs by Agency & Modality ---
    with c2:
        by_agency = (
            filtered_data
            .groupby(["Agency", "Modality"], as_index=False)
            .agg(BNFs=("Id", "nunique"))
        )
        agency_order = (
            by_agency.groupby("Agency")["BNFs"]
            .sum().sort_values(ascending=False).index.tolist()
        )

        fig2 = px.bar(
            by_agency,
            x="Agency",
            y="BNFs",
            color="Modality",
            color_discrete_sequence=DASHBOARD_PALETTE,
            category_orders={"Agency": agency_order},
            title="BNFs by Agency & Modality",
        )
        fig2.update_layout(
            legend=dict(
                title=None,
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="left",
                itemwidth=30,
                x=0,
            ),
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True,
                        config={"displayModeBar": False})

    # --- Chart 3: BNFs by Gender ---
    with c3:
        hh_gender = (
            filtered_data
            .groupby("Gender", as_index=False)
            .agg(BNFs=("Id", "nunique"))
        )
        fig3 = px.pie(
            hh_gender,
            names="Gender",
            values="BNFs",
            color="Gender",
            color_discrete_map=GENDER_COLORS,
            hole=0.55,
            title="BNFs by Gender",
        )
        fig3.update_layout(
            legend=dict(
                title=None,
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
            ),
            margin=dict(l=20, r=40, t=20, b=20),
        )
        st.plotly_chart(fig3, use_container_width=True,
                        config={"displayModeBar": False})

    #Row two columns 
#--------------------------------------------------------------------
    pie_cols1, pie_cols2,pie_cols3,pie_cols4=st.columns(4)
    with pie_cols1:
        fcs=(
            filtered_data
            .groupby("FCS_Cat",as_index=False)
            .agg(BNFs=("Id","nunique"))
        )

        fcs_order = (
            fcs.groupby("FCS_Cat")["BNFs"]
            .sum().sort_values(ascending=False).index.tolist()
        )
       
        fig4=px.pie(
            fcs,
            names="FCS_Cat",
            values="BNFs",
            hole=0.5,
            color="BNFs",
            color_discrete_sequence=DASHBOARD_PALETTE,
            category_orders={"FCS_Cat": fcs_order},
            title="FCS Categories"  
        )
        fig4.update_layout(
                    legend=dict(
                        title=None,
                        orientation="h",
                        yanchor="top",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                    ),
                    margin=dict(l=20, r=40, t=40, b=10),
                )
        st.plotly_chart(
            fig4,
            key="fcs"
        )
    with pie_cols2:
        lcsi=(
            filtered_data
            .groupby("LCSI_Cat",as_index=False)
            .agg(BNFs=("Id","nunique"))
            )
        
        lcsi_orders = (
            lcsi.groupby("LCSI_Cat")["BNFs"]
            .sum().sort_values(ascending=False).index.tolist()
            )
               
        fig5=px.pie(
            lcsi,
            names="LCSI_Cat",
            values="BNFs",
            hole=0.5,
            color="BNFs",
            color_discrete_sequence=DASHBOARD_PALETTE,
            category_orders={"LCSI_Cat": fcs_order},
            title="LCSI Categories"  
            )
        fig5.update_layout(
            legend=dict(
            title=None,
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            ),
            margin=dict(l=20, r=40, t=40, b=10),
            )
    
        st.plotly_chart(
                fig5,
                key="lcsi"
                )
    with pie_cols3:
        hh_status=(
            filtered_data
            .groupby("Type",as_index=False)
            .agg(BNFs=("Id","nunique"))
            )
                
        status_orders = (
            hh_status.groupby("Type")["BNFs"]
            .sum().sort_values(ascending=False).index.tolist()
            )
                       
        fig6=px.pie(
            hh_status,
            names="Type",
            values="BNFs",
            hole=0.5,
            color="BNFs",
            color_discrete_sequence=DASHBOARD_PALETTE,
            category_orders={"Type": fcs_order},
            title="HH Status"  
            )
        fig6.update_layout(
            legend=dict(
            title=None,
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            ),
            margin=dict(l=20, r=40, t=40, b=10),
            )
            
        st.plotly_chart(
            fig6,
            key="type"
            )
    with pie_cols4:
        marginalised=(
            filtered_data
            .groupby("Marginalised",as_index=False)
            .agg(BNFs=("Id","nunique"))
        )

        fig7=px.pie(
            marginalised,
            names="Marginalised",
            values="BNFs",
            color="BNFs",
            color_discrete_sequence=DASHBOARD_PALETTE,
            hole=0.5,
            title="Marginalised Status"

        )
        fig7.update_layout(
            legend=dict(
                title=None,
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
            ),
            margin=dict(l=20, r=40, t=40, b=40),
        )

        st.plotly_chart(
            fig7,
            key="Marginalised"
        )
        

    # --- Chart 4: BNFs by District (full width) ---
    
    reg_dists = (
        filtered_data
        .groupby("District", as_index=False)
        .agg(BNFs=("Id", "nunique"))
    )
    district_order = (
        reg_dists.sort_values("BNFs", ascending=False)["District"].tolist()
    )

    pp = px.bar(
        reg_dists,
        x="District",
        y="BNFs",
        color="BNFs",
        color_continuous_scale=DASHBOARD_PALETTE[::-1],
        category_orders={"District": district_order},
        title="BNFs by District",
    )
    pp.update_layout(
        yaxis_title="BNFs",
        xaxis_title=None,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(pp, use_container_width=True,
                    config={"displayModeBar": False},
                    key="district_chart")


# ----------------- T2: Data -----------------
with t2:
    rc1,rc2=st.columns(2)
    with rc1:

        registered=(
            filtered_data
            .groupby(["Agency", "District", "Modality"])
            .size()
            .reset_index(name="Count")
        )
        st.dataframe(registered)
    with rc2:
        st.dataframe(registered)
# ----------------- T3: Overview / Map -----------------
with t3:
    st.subheader("District Coverage Map")

    if not os.path.exists(GEOJSON_PATH):
        st.warning(f"GeoJSON file not found: {GEOJSON_PATH}")
    else:
        gdf = gpd.read_file(GEOJSON_PATH).rename(columns={"adm2_name": "District"})
        district_summary = (
            filtered_data
            .groupby("District", as_index=False)
            .agg(BNFs=("Id", "nunique"))
        )
        gdf = gdf.merge(district_summary, on="District", how="left")
        gdf = gdf[["District", "geometry", "BNFs"]]

        m = folium.Map(location=[5.5, 46.0], zoom_start=6, tiles=None)

        valid_bnfs = gdf["BNFs"].dropna()
        if len(valid_bnfs) > 0:
            bins = sorted(set(np.quantile(
                valid_bnfs, [0, 0.2, 0.4, 0.6, 0.8, 1]
            ).tolist()))

            folium.Choropleth(
                geo_data=gdf.to_json(),
                data=gdf,
                columns=["District", "BNFs"],
                key_on="feature.properties.District",
                fill_color="YlOrRd",
                fill_opacity=0.9,
                line_opacity=0.9,
                legend_name="Number of BNFs",
                bins=bins,
                nan_fill_color="white",
            ).add_to(m)
        else:
            st.info("No BNF data available for mapping.")

        st_folium(
            m,
            use_container_width=True,
            height=600,
            returned_objects=[],
        )