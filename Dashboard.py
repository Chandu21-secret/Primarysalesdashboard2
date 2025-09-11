import streamlit as st
import pandas as pd
import requests

# ── App config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes bgMove{0%{background-position:0% 50%}100%{background-position:100% 50%}}
.stApp{
  background:linear-gradient(270deg,#89f7fe,#66a6ff,#c2e9fb,#84fab0);
  background-size:200% 200%; animation:bgMove 15s ease infinite !important;
}
.stApp, .stApp *{color:#222 !important}

/* Sidebar gradient + glass */
[data-testid="stSidebar"]{
  background: linear-gradient(180deg,#cfe3ff 0%, #9bb8ff 45%, #5580ff 75%, #2f59d9 100%);
}
.stSidebar .sidebar-content{
  background:rgba(255,255,255,.18) !important; backdrop-filter: blur(10px) !important;
  border-radius:12px !important; padding-top:.5rem !important;
}

/* Main container spacing */
.main .block-container{ padding-top: 1rem; }

/* Inputs */
.stButton>button{
  background:#66a6ff !important; color:#fff !important; border:none !important;
  border-radius:6px !important; padding:.45em 1.1em !important;
}
.stButton>button:hover{ background:#89f7fe !important }
.stSelectbox select, select{
  -webkit-appearance:none; appearance:none; background:#fff !important; color:#222 !important;
  border:none !important; border-radius:8px !important; padding:.55em 1em !important;
  box-shadow:0 2px 6px rgba(0,0,0,.1) !important; cursor:pointer !important;
  background-image:url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23222'/%3E%3C/svg%3E");
  background-repeat:no-repeat !important; background-position:right .9em center !important;
}
.stDataFrame table{ background:rgba(255,255,255,.2) !important; backdrop-filter:blur(4px) !important; border-radius:8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Title (RIGHT) ─────────────────────────────────────────────────────────────
st.title("📊 Sales Dashboard – Primary & Secondary")

# ── Data sources ───────────────────────────────────────────────────────────────
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
secondary_segments = {
    "Mexico":   ["Gardening","Powertools","GSP"],
    "Peru":     ["Powertools","Gardening"],
    "Honduras": ["Powertools","Gardening"],
    "Panama":   ["Powertools","Gardening"],
    "Nicaragua":["Gardening"]
}

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

outgoing_sheets_map = {
    "Deepak": {
        "Brazil":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=0",
        "Venezuela":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1113481890",
        "Uruguay":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1583839796",
        "Panama":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1989264224",
        "El Salvador":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=598646493",
        "Ecuador":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=2061324706",
        "Costa Rica":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1553706794",
        "DR":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1879134481",
        "Colombia":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=466300310",
        "Chile":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=1619080821",
        "Argentina":"https://docs.google.com/spreadsheets/d/14vR6FE01iC2hVweBiY1vjGpvVHnCDSSERDNXiRGZyoI/export?format=csv&gid=520478812"
    },
    "Rohit": {
        "Colombia":"https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=0",
        "Honduras":"https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=672877361",
        "Nicaragua":"https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=894939961",
        "Panama":"https://docs.google.com/spreadsheets/d/1GGP5SjqukB05BlsgO8LbtUEypaxU6erCENBn30e6Jgc/export?format=csv&gid=566889908"
    },
    "Rahul": {
        "Mexico":"https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=0",
        "Argentina":"https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=640487650",
        "Ecuador":"https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=923638360",
        "Paraguay":"https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=1726201008",
        "Venezuela":"https://docs.google.com/spreadsheets/d/1FRBXNVnQLx4kCypiKPAYk0LT0Ih1UtYQLkIWqVQP8zE/export?format=csv&gid=1203763156"
    },
    "Ashwin": {
        "Paraguay":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=660664074",
        "Panama":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=0",
        "Ecuador":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=336827504",
        "Mexico":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1650359960",
        "Argentina":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1333106352",
        "Colambia":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1503582524",
        "Chile":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1549438486",
        "Costa Rica":"https://docs.google.com/spreadsheets/d/1W7zy8XheNiUpNAO6XOrPkF414KMCrs6C6UECiybZ154/export?format=csv&gid=1153197663"
    },
    "Master Data": {
        "Master Data":"https://docs.google.com/spreadsheets/d/1bzyOX9uIMwoTgZhTd_aiapj4ZzsEvCut2mOV5T9zBQw/export?format=csv&gid=0"
    }
}

# ── Sidebar controls (LEFT) ────────────────────────────────────────────────────
sb = st.sidebar
sb.header("Controls")

sales_type = sb.radio("Select Sales Type:", ["Primary Sales", "Secondary Sales"], key="sales_type_radio")

# Primary: default Incoming; Secondary: default Outgoing (but both visible)
if sales_type == "Primary Sales":
    trans_type = sb.radio("Select Transaction Type:", ["Incoming", "Outgoing"], index=0, key="primary_trans_type")
else:
    trans_type = sb.radio("Select Transaction Type:", ["Incoming", "Outgoing"], index=1, key="secondary_trans_type")

# ── Main content (RIGHT) ───────────────────────────────────────────────────────
# Primary / Incoming
if sales_type == "Primary Sales" and trans_type == "Incoming":
    tab = sb.selectbox("📑 Select Primary Tab:", list(primary_tabs.keys()))
    csv_url = primary_tabs[tab]
    st.markdown(f"### 🔗 {tab}")
    try:
        df = pd.read_csv(csv_url)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Could not load '{tab}': {e}")

# Primary / Outgoing
elif sales_type == "Primary Sales" and trans_type == "Outgoing":
    st.subheader("🏷️ Primary Sales – Outgoing")
    person = sb.selectbox("👤 Select Salesperson:", list(primary_outgoing.keys()))

    if person in outgoing_sheets_map:
        country_dict = outgoing_sheets_map[person]
        country = sb.selectbox("🌍 Select Country:", list(country_dict.keys()))
        csv_url = country_dict[country]
        st.markdown(f"### 🔗 {person} → {country}")
        try:
            df2 = pd.read_csv(csv_url)
            st.dataframe(df2, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Could not load '{country}': {e}")
    else:
        # Fallback: auto-list tabs for this person's sheet
        import re, json
        raw_url  = primary_outgoing[person]
        sid      = re.search(r"/d/([a-zA-Z0-9-_]+)", raw_url).group(1)
        meta_url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/metadata?&tqx=out:json"
        try:
            resp = requests.get(meta_url); resp.raise_for_status()
            raw  = resp.text
            j    = json.loads(raw[raw.find("{"): raw.rfind("}")+1])
            tabs = [(s["properties"]["title"], s["properties"]["sheetId"]) for s in j["sheets"]]
            for title, gid in tabs:
                url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
                try:
                    df_tab = pd.read_csv(url)
                    st.markdown(f"### 🔗 {person} → {title}")
                    st.dataframe(df_tab, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Could not load '{title}': {e}")
        except Exception as e:
            st.error(f"Metadata fetch failed: {e}")

# Secondary / Outgoing (DATA HERE)
elif sales_type == "Secondary Sales" and trans_type == "Outgoing":
    country = sb.selectbox("🌍 Select Country:", list(secondary_sheets.keys()))
    links   = secondary_sheets[country]
    segs    = secondary_segments[country]
    sel     = sb.selectbox("📄 Select Segment:", segs)
    idx     = segs.index(sel)
    url     = links[idx]

    st.markdown(f"### 🔗 {sel} – {country}")
    try:
        df = pd.read_csv(url)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error loading '{sel}': {e}")

# Secondary / Incoming (UNDER CONSTRUCTION)
elif sales_type == "Secondary Sales" and trans_type == "Incoming":
    st.subheader("📥 Secondary Sales – Incoming")
    st.info("🚧 This section is under construction. Please switch to **Outgoing** to view data.")
