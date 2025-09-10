import streamlit as st
import pandas as pd
import requests

# ─── App Configuration ─────────────────────────────────────────────────────────
# Best practice: set_page_config sabse pehle
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ─── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            height: 100%;
            background: linear-gradient(to bottom right, #004aad, #e0f7fa);
        }
        .block-container {
            padding: 4rem;
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            box-shadow: 0 0 12px rgba(0, 0, 0, 0.05);
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(to bottom right, #e0f7fa, #284aad); 
            color: white;
        }
        h1 {
            color: #004aad;
        }
    </style>
""", unsafe_allow_html=True)
# ─── Heading ───────────────────────────────────────────────────────────────────
st.title("📊 Sales Dashboard – Primary & Secondary")

# ─── Secondary Sales Sheets (Real) ─────────────────────────────────────────────
secondary_sheets = {
    "Mexico": [
        "https://docs.google.com/spreadsheets/d/1QR37MDuFuX8tRAjBYFxwwtrW_cOZ8CVH45c-Nuy8PB8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1mSm6cLpBBvuD7CDYCu_Bm4rpmV4rRqjVbLLUk47soGc/export?format=csv",
        "https://docs.google.com/spreadsheets/d/198NNm5fBEegZ75EJVtkj5GIGH_TvvEI4O_UyjjGlvak/export?format=csv"

    ],
    "Peru": [
        "https://docs.google.com/spreadsheets/d/1Jvhi1oKED8SAviitGfRx09J3bBj9lKOBpRB9zZWcZb8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1BqWyqXH6WWhwlCHe6R2tHTMhH5JVarvlAU54siKhw2s/export?format=csv"

        
    ],
    "Honduras": [
        "https://docs.google.com/spreadsheets/d/15WN-ThUiTMoQ_zusyXPMKzSq5voKw7nfVu-gZJs2wgg/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1KKwLsm2Hp6wdhL6RWf7mJxsZrknaCHZCSlfvmhD4edM/export?format=csv"

    ],
    "Panama": [
        "https://docs.google.com/spreadsheets/d/1Ee_wOm7NDM1jtOOx4qi2kzQS9YhGg3xVsZp_lIqqSBc/export?format=csv",
        "https://docs.google.com/spreadsheets/d/11kKefnHXREvSsQaX6c4XcheaU5pefCCM2h50IGyRkTE/export?format=csv"

    ],

    "Nicaragua":[
        "https://docs.google.com/spreadsheets/d/1DHtBDqrJ7F47YNjJRIMACkDuZIZ0FTUEUT5VWo59QNU/export?format=csv"

    ]

}

# ─── Secondary Sales – country → list of segment names ─────────────────────────
secondary_segments = {
    "Mexico":   ["Gardening", "Powertools", "GSP"],
    "Peru":     ["Powertools", "Gardening"],
    "Honduras": ["Powertools", "Gardening"],
    "Panama":   ["Powertools", "Gardening"],
    "Nicaragua": ["Gardening"]
}

# ─── Primary Sales → Incoming Tabs & CSV URLs ──────────────────────────────────
sheet_id = "1u06bqzGn8HtsvOOde30bvVdsXJfvvmfHiy1m1pDhtPA"
primary_tabs = {
    "Campaign Leads":       f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
    "Generic spare parts":  f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=300540925",
    "Stevron":              f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1639890324",
    "Gardening Machinery":  f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1081396299",
    "Mechnova":             f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=319133722",
    "Stronwell":            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1167901411"
}

primary_outgoing = {
    "Rohit":  "https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv",
    "Rahul":  "https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv",
    "Ashwin": "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv",
    "Deepak": "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv",
    "Master Data":"https://docs.google.com/spreadsheets/d/1bzyOX9uIMwoTgZhTd_aiapj4ZzsEvCut2mOV5T9zBQw/export?format=csv&gid=0"
}


# ─── UI Controls ────────────────────────────────────────────────────────────────
sales_type = st.radio("Select Sales Type:", ["Primary Sales", "Secondary Sales"], key="sales_type_radio")

# Primary: default = Incoming; Secondary: default = Outgoing (dono options dikhte rahenge)
if sales_type == "Primary Sales":
    trans_type = st.radio("Select Transaction Type:", ["Incoming", "Outgoing"], index=0, key="primary_trans_type")
else:
    trans_type = st.radio("Select Transaction Type:", ["Incoming", "Outgoing"], index=1, key="secondary_trans_type")


# ─── Primary Sales / Incoming ──────────────────────────────────────────────────
if sales_type == "Primary Sales" and trans_type == "Incoming":
    tab = st.selectbox("📑 Select Primary Tab:", list(primary_tabs.keys()))
    csv_url = primary_tabs[tab]
    try:
        df = pd.read_csv(csv_url)
        st.markdown(f"### 🔗 {tab}")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Could not load '{tab}': {e}")

# ─── Primary Sales / Outgoing ──────────────────────────────────────────────────
elif sales_type == "Primary Sales" and trans_type == "Outgoing":
    st.subheader("🏷️ Primary Sales – Outgoing")

    person = st.selectbox("👤 Select Salesperson:", list(primary_outgoing.keys()))

    outgoing_sheets_map = {
        "Deepak": {
            "Brazil":      "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=0",
            "Venezuela":   "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1113481890",
            "Uruguay":     "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1583839796",
            "Panama":      "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1989264224",
            "El Salvador": "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=598646493",
            "Ecuador":     "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=2061324706",
            "Costa Rica":  "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1553706794",
            "DR":          "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1879134481",
            "Colombia":    "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=466300310",
            "Chile":       "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1619080821",
            "Argentina":   "https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=520478812"
        },
        "Rohit": {
            "Colombia":   "https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=0",
            "Honduras":   "https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=672877361",
            "Nicaragua":  "https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=894939961",
            "Panama":     "https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=566889908"
        },
        "Rahul": {
            "Mexico":     "https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=0",
            "Argentina":  "https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=640487650",
            "Ecuador":    "https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=923638360",
            "Paraguay":   "https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=1726201008",
            "Venezuela":  "https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=1203763156"
        },
        "Ashwin": {
            "Paraguay":   "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=660664074",
            "Panama":     "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=0",
            "Ecuador":    "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=336827504",
            "Mexico":     "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1650359960",
            "Argentina":  "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1333106352",
            "Colambia":   "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1503582524",
            "Chile":      "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1549438486",
            "Costa Rica": "https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1153197663"
        },
        "Master Data": {
            "Master Data": "https://docs.google.com/spreadsheets/d/1bzyOX9uIMwoTgZhTd_aiapj4ZzsEvCut2mOV5T9zBQw/export?format=csv&gid=0"
        }
    }

    if person in outgoing_sheets_map:
        country_dict = outgoing_sheets_map[person]
        country = st.selectbox("🌍 Select Country:", list(country_dict.keys()))
        csv_url = country_dict[country]
        try:
            df2 = pd.read_csv(csv_url)
            st.markdown(f"### 🔗 {person} → {country}")
            st.dataframe(df2, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Could not load '{country}': {e}")
    else:
        import re, json, requests
        raw_url    = primary_outgoing[person]
        sheet_id   = re.search(r"/d/([a-zA-Z0-9-_]+)", raw_url).group(1)
        meta_url   = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/metadata?&tqx=out:json"
        resp       = requests.get(meta_url); resp.raise_for_status()
        raw        = resp.text
        j          = json.loads(raw[raw.find("{"): raw.rfind("}")+1])
        tabs       = [(s["properties"]["title"], s["properties"]["sheetId"]) for s in j["sheets"]]
        for title, gid in tabs:
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
            try:
                df_tab = pd.read_csv(url)
                st.markdown(f"### 🔗 {person} → {title}")
                st.dataframe(df_tab, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Could not load '{title}': {e}")

# ─── Secondary Sales / Outgoing (DATA YAHIN DIKHEGA) ──────────────────────────
elif sales_type == "Secondary Sales" and trans_type == "Outgoing":
    country = st.selectbox("🌍 Select Country:", list(secondary_sheets.keys()))
    links   = secondary_sheets[country]
    segs    = secondary_segments[country]
    sel     = st.selectbox("📄 Select Segment:", segs)
    idx     = segs.index(sel)
    url     = links[idx]

    st.markdown(f"### 🔗 {sel} – {country}")
    try:
        df = pd.read_csv(url)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error loading '{sel}': {e}")

# ─── Secondary Sales / Incoming (disabled) ─────────────────────────────────────
elif sales_type == "Secondary Sales" and trans_type == "Incoming":
    st.info("🚧 Secondary Sales / Incoming is disabled. Please select 'Outgoing'.")






