
import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth


# =============================================================
# 1. CONFIGURATION
# =============================================================

API_URL = (
    "https://somcc.redrosecps.com/"
    "externalapi/customQuery/queryToJson"
    "?queryName=BeneficiaryDetailsV2"
)

CASE_LOAD_VALUES = ["og_2026", "OG_2026"]

MODALITY_VALUES = [
    "CCCM Referral",
    "Nutrition Referral",
    "Hard to Reach",
    "Accessible",
    "Protection Referral",
]


# =============================================================
# 2. CACHED API CONNECTION
# =============================================================

@st.cache_data(
    ttl=3600,
    show_spinner="Loading beneficiary data from RedRose API..."
)
def load_data(api_url, username, password):

    response = requests.get(
        api_url,
        auth=HTTPBasicAuth(username, password),
        timeout=60
    )

    response.raise_for_status()

    payload = response.json()

    records = (
        payload.get("data", payload)
        if isinstance(payload, dict)
        else payload
    )

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError("RedRose API returned an empty dataset.")

    return df


# =============================================================
# 3. DATA PREPARATION
# =============================================================

def prepare_data(pff):

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

    return pff


# =============================================================
# 4. MAIN DATA CONNECTION FUNCTION
# =============================================================

def get_beneficiary_data():

    try:

        username = st.secrets["redrose"]["username"]
        password = st.secrets["redrose"]["password"]

        # This uses the shared cache on both pages
        pff = load_data(
            API_URL,
            username,
            password
        )

        # Prepare the cached data for the dashboard
        pff = prepare_data(pff)

        return pff

    except requests.exceptions.HTTPError as e:
        st.error(f"RedRose API HTTP error: {e}")
        st.stop()

    except requests.exceptions.Timeout:
        st.error("RedRose API connection timed out.")
        st.stop()

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to RedRose API.")
        st.stop()

    except requests.exceptions.RequestException as e:
        st.error(f"RedRose API connection error: {e}")
        st.stop()

    except KeyError:
        st.error("RedRose API credentials are missing in secrets.toml.")
        st.stop()

    except Exception as e:
        st.error(f"Unexpected error loading data: {e}")
        st.stop()


# =============================================================
# 5. CLEAR CACHE WHEN REFRESHING
# =============================================================

def clear_api_cache():

    load_data.clear()
