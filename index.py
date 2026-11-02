import os
import base64
import html

import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

from utils.api_connection import get_beneficiary_data, clear_api_cache


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Humanitarian Dashboard",
    page_icon="🌍",
    layout="wide",
)

# ============================================================
# DASHBOARD STYLES
# ============================================================

st.markdown(
    """
    <style>
        h3 {
            color: darkred !important;
            border-bottom: 1px solid darkred;
            padding: 0 !important;
            margin-bottom: 5px !important;
        }

        .block-container {
            padding-top: 20px;
            padding-bottom: 1rem;
        }

        .st-key-dashboard_header {
            background: #fff;
            padding: 10px;
            border-bottom: 2px solid darkred;
        }

        .scc-intro {
            background-color: #F4F7FA;
            border-left: 4px solid #287094;
            border-radius: 8px;
            padding: 18px 22px;
            margin: 10px 0 20px 0;
            color: #34495E;
            font-size: 16px;
            line-height: 1.4;
            text-align: justify;
        }

        .partner-heading {
            font-size: 25px;
            font-weight: 700;
            color: #164B60;
            margin-top: 30px;
            margin-bottom: 15px;
        }

        .partner-card {
            background: #F8FAFC;
            border: 2px dashed #D1DEEB;
            border-radius: 15px;
            min-height: 125px;
            padding: 20px 10px;
            margin-bottom: 15px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .partner-name {
            color: #164B60;
            font-size: 15px;
            font-weight: 650;
            line-height: 1.4;
        }

        .partner-number {
            color: #8495A8;
            font-size: 12px;
            margin-bottom: 7px;
        }

        .partner-count {
            background: #EDF3F8;
            color: #287094;
            padding: 7px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

pff = get_beneficiary_data()

# Check required fields before using the data
required_columns = {"District", "Id"}
missing_columns = required_columns.difference(pff.columns)

if missing_columns:
    st.error(
        "The RedRose dataset is missing required column(s): "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()


# ============================================================
# HEADER
# ============================================================

LOGO_PATH = "log2.png"

header = st.container(key="dashboard_header")

with header:
    c1, c2, c3 = st.columns([1, 7, 1])

    with c1:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=200)

    with c2:
        st.markdown(
            """
            <h2 style="color:#111827; margin:auto;">
                Transforming Lives Through Cash Assistance
            </h2>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        if st.button(
            "Dashboard →",
            use_container_width=True,
            type="primary",
        ):
            st.switch_page("main.py")


# ============================================================
# INTRODUCTION
# ============================================================

st.markdown(
    """
    <div class="scc-intro">
        The Somali Cash Consortium (SCC) is a collaborative humanitarian
        initiative that brings together partner organisations to deliver
        coordinated, timely and accountable cash assistance to vulnerable
        and crisis-affected households across Somalia. Through a harmonised
        approach to targeting, beneficiary registration, verification and
        cash delivery, the Consortium supports households affected by
        conflict, displacement, drought and other shocks, helping them
        meet their essential needs while preserving dignity, choice and
        flexibility. Its coordinated programming aims to strengthen the
        effectiveness, reach and consistency of humanitarian cash
        assistance, particularly in areas facing complex access and
        vulnerability challenges.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# IMPLEMENTING PARTNERS - CLICKABLE LOGO GALLERY
# ============================================================

col1, col2, col3 = st.columns([3, 2, 4])

partners = [
    {
        "name": "SSWC",
        "logo": "SSWC.jpg",
        "url": "https://sswc-som.org/",
    },
    {
        "name": "Concern Worldwide",
        "logo": "CWW.jpg",
        "url": "https://www.concern.net/",
    },
    {
        "name": "Action Against Hunger",
        "logo": "action_against_hunger.jpg",
        "url": "https://www.actionagainsthunger.org/",
    },
    {
        "name": "COOPI",
        "logo": "Coopi.png",
        "url": "https://www.coopi.org/en",
    },
    {
        "name": "GREDO",
        "logo": "gredo.jpg",
        "url": "https://gredosom.org/",
    },
    {
        "name": "Save the Children",
        "logo": "SCI.jpg",
        "url": "https://www.savethechildren.net/",
    },
    {
        "name": "DRC",
        "logo": "drc.jpg",
        "url": "https://drc.ngo/",
    },
    {
        "name": "ACTED",
        "logo": "ACTED.png",
        "url": "https://www.acted.org/",
    },
    {
        "name": "Lifeline Gedo",
        "logo": "llg2.jpg",
        "url": "https://www.lifelineorganisation.org/",
    },
    {
        "name": "NRC",
        "logo": "nrc2.gif",
        "url": "https://www.nrc.no/",
    },
]

with col1:
    st.subheader("Our Implementing Partners")

    logo_dir = "assets/partners"
    cards_html = ""

    for partner in partners:
        logo_path = os.path.join(logo_dir, partner["logo"])
        partner_name = html.escape(partner["name"])

        if os.path.isfile(logo_path):
            with open(logo_path, "rb") as image_file:
                image_data = base64.b64encode(
                    image_file.read()
                ).decode("utf-8")

            extension = os.path.splitext(logo_path)[1].lower()

            mime_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }.get(extension, "application/octet-stream")

            logo_html = (
                f'<img src="data:{mime_type};base64,{image_data}" '
                f'alt="{partner_name}" class="partner-logo">'
            )
        else:
            logo_html = (
                '<div class="partner-placeholder">Logo unavailable</div>'
            )

        partner_url = html.escape(partner["url"], quote=True)

        cards_html += f"""
            <div class="partner-logo-card">
                <a href="{partner_url}" target="_blank"
                   rel="noopener noreferrer"
                   title="Visit {partner_name} website">
                    {logo_html}
                </a>
            </div>
        """

    gallery_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}

            body {{
                margin: 0;
                padding: 2px;
                font-family: Arial, sans-serif;
            }}

            .partner-grid {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 9px;
            }}

            .partner-logo-card {{
                height: 75px;
                background: #FFFFFF;
                border: 1px solid #E4EAF0;
                border-radius: 9px;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 8px;
                transition: all 0.2s ease;
            }}

            .partner-logo-card:hover {{
                border-color: #287094;
                background: #F7FAFC;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            }}

            .partner-logo-card a {{
                display: flex;
                width: 100%;
                height: 100%;
                justify-content: center;
                align-items: center;
            }}

            .partner-logo {{
                display: block;
                max-width: 100%;
                max-height: 55px;
                width: auto;
                height: auto;
                object-fit: contain;
            }}

            .partner-placeholder {{
                font-size: 12px;
                color: #A0AAB5;
            }}
        </style>
    </head>
    <body>
        <div class="partner-grid">
            {cards_html}
        </div>
    </body>
    </html>
    """

    components.html(
        gallery_html,
        height=480,
        scrolling=False,
    )


# ============================================================
# KEY METRICS - INLINE SVG ICONS
# ============================================================

with col2:
    st.subheader("Key Metrics")

    kpi_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * { box-sizing: border-box; }

            body {
                margin: 0;
                padding: 2px;
                font-family: Arial, sans-serif;
            }

            .kpi-card {
                height: 125px;
                width: 100%;
                border-radius: 14px;
                background: #F7F9FC;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin-bottom: 14px;
                padding: 12px;
                text-align: center;
            }

            .kpi-card.total {
                background: linear-gradient(120deg, #590F10, #811B1D);
            }

            .kpi-icon {
                width: 27px;
                height: 27px;
                margin-bottom: 5px;
                color: #8B1717;
            }

            .kpi-icon svg {
                width: 100%;
                height: 100%;
                fill: none;
                stroke: currentColor;
                stroke-width: 2;
                stroke-linecap: round;
                stroke-linejoin: round;
            }

            .kpi-value {
                font-size: 32px;
                font-weight: 800;
                color: #590F10;
                line-height: 1.1;
            }

            .kpi-value span {
                font-size: 20px;
            }

            .kpi-label {
                font-size: 13px;
                color: #164B60;
                margin-top: 5px;
            }

            .kpi-card.total .kpi-icon {
                color: #E3B000;
            }

            .kpi-card.total .kpi-value {
                color: #FFFFFF;
            }

            .kpi-card.total .kpi-value span {
                color: #E3B000;
            }

            .kpi-card.total .kpi-label {
                color: #F2DADA;
            }
        </style>
    </head>

    <body>

        <div class="kpi-card">
            <div class="kpi-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M20 21v-2a4 4 0 0 0-3-3.9"/>
                    <path d="M16 3.1a4 4 0 0 1 0 7.8"/>
                </svg>
            </div>
            <div class="kpi-value">3,000,000<span>+</span></div>
            <div class="kpi-label">Total Beneficiaries • All programs</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M10.3 3.9L2.5 17.4A2 2 0 0 0 4.2 20h15.6a2 2 0 0 0 1.7-2.6L13.7 3.9a2 2 0 0 0-3.4 0z"/>
                    <path d="M12 9v4"/>
                    <path d="M12 17h.01"/>
                </svg>
            </div>
            <div class="kpi-value">2,500,000<span>+</span></div>
            <div class="kpi-label">Emergency Assistance</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/>
                    <path d="M9 12l2 2 4-4"/>
                </svg>
            </div>
            <div class="kpi-value">546,588<span>+</span></div>
            <div class="kpi-label">Social Protection</div>
        </div>

        
    </body>
    </html>
    """

    components.html(
        kpi_html,
        height=420,
        scrolling=False,
    )


# ============================================================
# GEOGRAPHICAL COVERAGE MAP
# ============================================================

with col3:
    st.subheader("Our Coverage (HIP2026)")

    GEOJSON_PATH = "somgeojson/som_admin2.geojson"

    if not os.path.exists(GEOJSON_PATH):

        st.warning(f"GeoJSON file not found: {GEOJSON_PATH}")

    else:

        try:

            # ------------------------------------------------
            # 1. LOAD GEOGRAPHICAL DATA
            # ------------------------------------------------

            gdf = gpd.read_file(GEOJSON_PATH)

            if "adm2_name" in gdf.columns:
                gdf = gdf.rename(
                    columns={"adm2_name": "District"}
                )

            if "District" not in gdf.columns:
                st.error(
                    "The GeoJSON file must contain "
                    "'adm2_name' or 'District'."
                )
                st.stop()

            # Standardise district names
            gdf["District"] = (
                gdf["District"]
                .astype(str)
                .str.strip()
            )

            # ------------------------------------------------
            # 2. PREPARE BENEFICIARY DATA
            # ------------------------------------------------

            district_summary = (
                pff.assign(
                    District=(
                        pff["District"]
                        .astype(str)
                        .str.strip()
                    )
                )
                .groupby("District", as_index=False)
                .agg(
                    BNFs=("Id", "nunique")
                )
            )

            # ------------------------------------------------
            # 3. MERGE DATA
            # ------------------------------------------------

            gdf = gdf.merge(
                district_summary,
                on="District",
                how="left"
            )

            gdf["BNFs"] = (
                pd.to_numeric(gdf["BNFs"], errors="coerce")
                .fillna(0)
            )

            # ------------------------------------------------
            # 4. CONVERT DATA TO JSON-SAFE VALUES
            # ------------------------------------------------

            # Keep geometry unchanged and convert attributes
            # to JSON-compatible Python values.

            gdf_map = gdf.copy()

            for column in gdf_map.columns:

                if column == "geometry":
                    continue

                if pd.api.types.is_datetime64_any_dtype(
                    gdf_map[column]
                ):
                    gdf_map[column] = (
                        gdf_map[column]
                        .apply(
                            lambda x: (
                                x.isoformat()
                                if pd.notna(x)
                                else None
                            )
                        )
                    )

                else:
                    gdf_map[column] = (
                        gdf_map[column]
                        .apply(
                            lambda x: (
                                x.item()
                                if isinstance(x, np.generic)
                                else x
                            )
                        )
                    )

            # Convert GeoDataFrame into a JSON-compatible
            # GeoJSON dictionary.
            geojson_data = gdf_map.__geo_interface__

            # ------------------------------------------------
            # 5. CREATE FOLIUM MAP
            # ------------------------------------------------

            m = folium.Map(
                location=[5.5, 46.0],
                zoom_start=6,
                tiles=None,
                control_scale=True
            )

            valid_bnfs = gdf.loc[
                gdf["BNFs"] > 0,
                "BNFs"
            ]

            # ------------------------------------------------
            # 6. DEFINE MAP COLOURS AND QUANTILES
            # ------------------------------------------------

            map_colors = [
                "#ffffb2",
                "#fecc5c",
                "#fd8d3c",
                "#f03b20",
                "#bd0026"
            ]

            if not valid_bnfs.empty:

                bins = np.unique(
                    np.quantile(
                        valid_bnfs,
                        [0, 0.2, 0.4, 0.6, 0.8, 1]
                    )
                ).tolist()

                # ------------------------------------------------
                # 7. MAP CLASSIFICATION
                # ------------------------------------------------

                if len(bins) >= 2:

                    class_count = len(bins) - 1

                    colors_used = map_colors[:class_count]

                    def get_color(value):

                        if pd.isna(value) or value <= 0:
                            return "#FFFFFF"

                        class_index = np.searchsorted(
                            bins[1:-1],
                            value,
                            side="right"
                        )

                        class_index = min(
                            class_index,
                            class_count - 1
                        )

                        return colors_used[class_index]

                    # ------------------------------------------------
                    # 8. MAP STYLE
                    # ------------------------------------------------

                    def style_function(feature):

                        value = feature["properties"].get(
                            "BNFs", 0
                        )

                        return {
                            "fillColor": get_color(value),
                            "color": "#666666",
                            "weight": 0.7,
                            "fillOpacity": 0.85
                        }

                    # ------------------------------------------------
                    # 9. DISTRICT TOOLTIP
                    # ------------------------------------------------

                    tooltip = folium.GeoJsonTooltip(
                        fields=["District", "BNFs"],
                        aliases=[
                            "District:",
                            "# of BNFs:"
                        ],
                        localize=True,
                        sticky=False
                    )

                    # ------------------------------------------------
                    # 10. ADD DISTRICT POLYGONS
                    # ------------------------------------------------

                    folium.GeoJson(
                        geojson_data,
                        name="Beneficiary Coverage",
                        style_function=style_function,
                        tooltip=tooltip
                    ).add_to(m)

                    # ------------------------------------------------
                    # 11. CUSTOM VERTICAL LEGEND
                    # ------------------------------------------------

                    legend_rows = ""

                    for index in reversed(
                        range(class_count)
                    ):

                        lower = bins[index]
                        upper = bins[index + 1]

                        color = colors_used[index]

                        legend_rows += f"""
                        <div style="
                            display:flex;
                            align-items:center;
                            gap:7px;
                            height:25px;
                        ">

                            <span style="
                                display:inline-block;
                                width:18px;
                                height:16px;
                                background:{color};
                                border:1px solid #999;
                                flex-shrink:0;
                            "></span>

                            <span>
                                {int(round(lower)):,} –
                                {int(round(upper)):,}
                            </span>

                        </div>
                        """

                    legend_html = f"""
                    <div style="
                        position:fixed;
                        bottom:30px;
                        right:15px;
                        z-index:9999;
                        background:white;
                        padding:12px;
                        border-radius:6px;
                        box-shadow:0 1px 6px rgba(0,0,0,0.3);
                        font-size:11px;
                        width:155px;
                    ">

                        <div style="
                            font-weight:bold;
                            margin-bottom:8px;
                            text-align:center;
                        ">
                            Number of BNFs
                        </div>

                        {legend_rows}

                        <div style="
                            display:flex;
                            align-items:center;
                            gap:7px;
                            margin-top:6px;
                        ">

                            <span style="
                                display:inline-block;
                                width:18px;
                                height:16px;
                                background:#FFFFFF;
                                border:1px solid #999;
                            "></span>

                            <span>No BNFs</span>

                        </div>

                    </div>
                    """

                    m.get_root().html.add_child(
                        folium.Element(legend_html)
                    )

                # ------------------------------------------------
                # 12. ALL DISTRICTS HAVE SAME BNF COUNT
                # ------------------------------------------------

                else:

                    st.info(
                        "All districts with beneficiaries have "
                        "the same BNF count."
                    )

                    def equal_style_function(feature):

                        value = feature["properties"].get(
                            "BNFs", 0
                        )

                        return {
                            "fillColor": (
                                "#bd0026"
                                if value > 0
                                else "#FFFFFF"
                            ),
                            "color": "#666666",
                            "weight": 0.7,
                            "fillOpacity": 0.85
                        }

                    folium.GeoJson(
                        geojson_data,
                        name="Beneficiary Coverage",
                        style_function=equal_style_function,
                        tooltip=folium.GeoJsonTooltip(
                            fields=["District", "BNFs"],
                            aliases=[
                                "District:",
                                "Number of BNFs:"
                            ],
                            localize=True
                        )
                    ).add_to(m)

            # ------------------------------------------------
            # 13. NO MATCHING BENEFICIARY RECORDS
            # ------------------------------------------------

            else:

                st.info(
                    "No beneficiary records matched the "
                    "districts in the GeoJSON file."
                )

                folium.GeoJson(
                    geojson_data,
                    name="District Boundaries",
                    style_function=lambda feature: {
                        "fillColor": "#FFFFFF",
                        "color": "#777777",
                        "weight": 0.7,
                        "fillOpacity": 0.5
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["District", "BNFs"],
                        aliases=[
                            "District:",
                            "Number of BNFs:"
                        ],
                        localize=True
                    )
                ).add_to(m)

            # ------------------------------------------------
            # 14. LAYER CONTROL
            # ------------------------------------------------

            folium.LayerControl().add_to(m)

            # ------------------------------------------------
            # 15. DISPLAY MAP
            # ------------------------------------------------

            st_folium(
                m,
                use_container_width=True,
                height=600,
                returned_objects=[]
            )

        except Exception as error:

            st.error(
                f"Unable to generate the coverage map: {error}"
            )
