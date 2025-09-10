import streamlit as st
import pandas as pd
import requests



st.markdown("""
    <style>
    /* 1) Smooth animated gradient background */
    @keyframes bgMove {
        0%   { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    .stApp {
        background: linear-gradient(270deg, #89f7fe, #66a6ff, #c2e9fb, #84fab0);
        background-size: 200% 200%;
        animation: bgMove 15s ease infinite !important;
    }

    /* 2) All text dark gray for readability */
    .stApp, .stApp * {
        color: #222 !important;
    }

    /* 3) Glassmorphic sidebar */
    .stSidebar .sidebar-content {
        background: rgba(255,255,255,0.25) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 12px !important;
    }

    /* 4) Button styling */
    .stButton>button {
        background: #66a6ff !important;
        color: #fff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.4em 1.2em !important;
        transition: background 0.2s !important;
    }
    .stButton>button:hover {
        background: #89f7fe !important;
    }

    /* 5) Attractive single‐color dropdown (like your screenshot) */
    .stSelectbox select,
    select {
        /* remove default arrow */
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;

        /* white rounded box */
        background-color: #ffffff !important;
        color: #222222 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5em 1em !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        cursor: pointer !important;

        /* custom arrow icon */
        background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23222'/%3E%3C/svg%3E");
        background-repeat: no-repeat !important;
        background-position: right 1em center !important;
    }
    .stSelectbox select:hover,
    select:hover {
        box-shadow: 0 3px 8px rgba(0,0,0,0.15) !important;
    }
    .stSelectbox select:focus,
    select:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(102,166,255,0.4) !important;
    }
    .stSelectbox option,
    option {
        background-color: #fff !important;
        color: #222 !important;
        padding: 0.4em !important;
    }

    /* 6) Header styling */
    h1 {
        font-size: 2.4rem !important;
        text-align: center;
        margin-bottom: 0.5em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    h2 {
        color: #334155 !important;
        font-size: 1.6rem !important;
    }

    /* 7) DataFrame background */
    .stDataFrame table {
        background: rgba(255,255,255,0.2) !important;
        backdrop-filter: blur(4px) !important;
        border-radius: 8px !important;
    }
    .stDataFrame th, .stDataFrame td {
        color: #222 !important;
    }
    </style>
""", unsafe_allow_html=True)



# ─── App Configuration & Heading ───────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard – Primary & Secondary")

# ✅ Secondary Sales Sheets (Real)
secondary_sheets = {
    
   
    "Mexico": [
        
        "https://docs.google.com/spreadsheets/d/1QR37MDuFuX8tRAjBYFxwwtrW_cOZ8CVH45c-Nuy8PB8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1mSm6cLpBBvuD7CDYCu_Bm4rpmV4rRqjVbLLUk47soGc/export?format=csv"    ],


    "Peru" :[
        "https://docs.google.com/spreadsheets/d/1Jvhi1oKED8SAviitGfRx09J3bBj9lKOBpRB9zZWcZb8/export?format=csv"

    ],

    "Honduras": [
        "https://docs.google.com/spreadsheets/d/15WN-ThUiTMoQ_zusyXPMKzSq5voKw7nfVu-gZJs2wgg/export?format=csv"

        
    ],

    "Panama": ["https://docs.google.com/spreadsheets/d/1Ee_wOm7NDM1jtOOx4qi2kzQS9YhGg3xVsZp_lIqqSBc/export?format=csv"]                    

                
}


# ─── Secondary Sales – country → list of segment names ────────────────────
secondary_segments = {
    
   
   
    "Mexico":   ["Gardening", "Powertools"],
    
         
    "Peru":               ["Powertools"],
    "Honduras":           ["Powertools"],
    "Panama":             ["Pawertools"]

}


# ─── Primary Sales → Incoming Tabs & CSV URLs ─────────────────────────────────
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
sales_type = st.radio("Select Sales Type:",      ["Primary Sales", "Secondary Sales"])
trans_type = st.radio("Select Transaction Type:", ["Incoming", "Outgoing"])

# ─── Handle Primary Sales / Incoming ───────────────────────────────────────────
if sales_type == "Primary Sales" and trans_type == "Incoming":
    tab = st.selectbox("📑 Select Primary Tab:", list(primary_tabs.keys()))
    csv_url = primary_tabs[tab]
    try:
        df = pd.read_csv(csv_url)
        st.markdown(f"### 🔗 {tab}")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Could not load '{tab}': {e}")


# ─── Handle Primary Sales / Outgoing ───────────────────────────────────────────
elif sales_type == "Primary Sales" and trans_type == "Outgoing":
    st.subheader("🏷️ Primary Sales – Outgoing")

    # 1) सेल्सपरसन चुनें
    person = st.selectbox("👤 Select Salesperson:", list(primary_outgoing.keys()))

    # 2) हर सेल्सपर्सन के लिए hard-coded country→CSV URLs
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


       "Master Data":{
           
           "Master Data": "https://docs.google.com/spreadsheets/d/1bzyOX9uIMwoTgZhTd_aiapj4ZzsEvCut2mOV5T9zBQw/export?format=csv&gid=0"

       }
    }

    # 3) अगर person mapping में है तो सिर्फ़ उसके countries दिखाएँ
    if person in outgoing_sheets_map:
        country_dict = outgoing_sheets_map[person]
        country = st.selectbox("🌍 Select Country:", list(country_dict.keys()))
        csv_url = country_dict[country]

        # 4) CSV लोड और दिखाएँ
        try:
            df2 = pd.read_csv(csv_url)
            st.markdown(f"### 🔗 {person} → {country}")
            st.dataframe(df2, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Could not load '{country}': {e}")

    # 5) अन्य सेल्सपर्सन के लिए fallback (metadata-based)
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




# ─── Secondary Sales → Incoming ────────────────────────────────────────────
elif sales_type == "Secondary Sales" and trans_type == "Incoming":
    country = st.selectbox("🌍 Select Country:", list(secondary_sheets.keys()))
    links   = secondary_sheets[country]
    
    # Sheet 1/2 की जगह segment names
    segs  = secondary_segments[country]
    sel   = st.selectbox("📄 Select Segment:", segs)
    idx   = segs.index(sel)
    url   = links[idx]
    
    st.markdown(f"### 🔗 {sel} – {country}")
    try:
        df = pd.read_csv(url)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error loading '{sel}': {e}")

# ─── Handle Secondary Sales / Outgoing ─────────────────────────────────────────
elif sales_type == "Secondary Sales" and trans_type == "Outgoing":
    st.info("🚧 Secondary Sales / Outgoing is under construction.")



   

