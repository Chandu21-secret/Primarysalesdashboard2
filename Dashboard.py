import streamlit as st
import pandas as pd
import requests
import hashlib, base64, os
from pathlib import Path

# ── App config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Project-relative logo path (change if needed)
LOGO_PATH = r"C:\\Users\\Lenovo\\OneDrive - BONHOEFFER MACHINES PRIVATE LIMITED\\Dasboard.P.S\\logo-B 2.png"


# ====== Simple Auth (in-memory) ==============================================
def _hash(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

USERS = {
    "chandan": _hash("admin@123"),
    "rohit":  _hash("rohit@123"),
    "rahul":  _hash("rahul@123"),
    "ashwin": _hash("ashwin@123"),
    "deepak": _hash("deepak@123"),
}

def logged_in() -> bool:
    return st.session_state.get("auth_ok") is True

def logout():
    for k in ["auth_ok", "user"]:
        st.session_state.pop(k, None)
    st.rerun()

# ── Brand header (CENTERED: logo + big title) ────────────────────────────────
def brandbar(title: str = "Bonhoeffer Machines", logo_path: Path = LOGO_PATH):
    logo_b64 = ""
    p = Path(logo_path)
    if p.exists():
        with open(p, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    logo_img = (
        f"<img class='brandlogo' src='data:image/png;base64,{logo_b64}' alt='logo'/>"
        if logo_b64 else ""
    )
    st.markdown(f"""
    <div class="brandwrap">
        {logo_img}
        <h1 class="brandname">{title}</h1>
    </div>
    """, unsafe_allow_html=True)

# ── Styles (Login dark + App light) ───────────────────────────────────────────
LOGIN_DARK_CSS = """
<style>
/* remove header/toolbar/decoration space */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
button[kind="header"], .stDeployButton { display:none !important; }
main .block-container{ padding-top:8px !important; }

/* Dark background */
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1000px 500px at -10% -10%, #0b1220 20%, transparent 60%),
    radial-gradient(900px 500px at 110% -10%, #0b1220 20%, transparent 60%),
    linear-gradient(90deg,#0f172a 0%, #0c1a2b 50%, #0b1322 100%) !important;
  color:#e5e7eb !important;
}

/* Kill any old pill/brandbar leftovers */
.brandbar, .brandbar *{ display:none !important; }

/* ===== Brand (CENTERED) ===== */
.brandwrap{
  width:100%;
  margin:8px 0 12px;
  display:flex;
  justify-content:center;
  align-items:center;
  gap:18px;
  text-align:center;
}
.brandlogo{
  height:100px;            /* adjust for bigger/smaller logo */
  width:auto;
  object-fit:contain;
  border-radius:12px;
  filter: drop-shadow(0 6px 18px rgba(0,0,0,.35));
}
.brandname{
  margin:0;
  font-size:3.2rem;
  line-height:1.05;
  font-weight:800;
  color:#e5e7eb;
  letter-spacing:.2px;
}
@media (max-width: 640px){
  .brandlogo{ height:64px; }
  .brandname{ font-size:2rem; }
}

/* ===== kill the stray dark strip under the brand ===== */
.brandwrap + div:not(.login-card){ display:none !important; }
.brandwrap + div:empty{ display:none !important; }
main .block-container hr,
main .block-container [role="separator"]{ display:none !important; }

/* Login card + inputs */
.login-card{
  max-width: 880px; margin: 8px auto 24px; padding: 22px 22px;
  background: rgba(3,7,18,.75); backdrop-filter: blur(8px);
  border:1px solid rgba(255,255,255,.08); border-radius: 14px;
  box-shadow: 0 16px 40px rgba(0,0,0,.45);
}
.login-card h2{ color:#e5e7eb; margin:0 0 4px; }
.login-card p{ color:#94a3b8; margin:0 0 16px; }

.stTextInput>div>div>input, .stPassword>div>div>input{
  background:#0f172a !important; color:#e5e7eb !important;
  border:1px solid #243144 !important; border-radius:10px !important;
}
.stSelectbox div[data-baseweb="select"]>div{
  background:#0f172a !important; color:#e5e7eb !important;
  border:1px solid #243144 !important; border-radius:10px !important;
}
label{ color:#cbd5e1 !important; }

.stButton>button{
  background: linear-gradient(90deg,#2563eb,#06b6d4) !important;
  color:#fff !important; border:none !important; border-radius:10px !important;
  padding:.55em 1.2em !important; box-shadow:0 8px 24px rgba(2,132,199,.35);
}
.stButton>button:hover{ filter:brightness(1.05); }
</style>
"""

APP_LIGHT_CSS = """
<style>
/* Header clean */
[data-testid="stHeader"]{ background:transparent !important; box-shadow:none !important; }

/* MAIN (right) background */
[data-testid="stAppViewContainer"]{
  background: linear-gradient(90deg,#B9F5C8 0%, #C3F0DD 30%, #CDE7F1 65%, #B8D2FF 100%) !important;
  background-attachment: fixed !important;
}

/* ==== SIDEBAR (left) : blue → white gradient ==== */
aside[data-testid="stSidebar"]{
  background: linear-gradient(180deg,
              #3D6CFF 0%,
              #7FAAFF 40%,
              #B8D3FF 75%,
              #FFFFFF 100%) !important;
  min-height: 100vh;         /* gradient full height */
  position: relative;
}

/* Make all inner wrappers transparent so gradient shows */
aside[data-testid="stSidebar"] > div,
aside[data-testid="stSidebar"] [data-testid="stSidebarContent"],
aside[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
aside[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
aside[data-testid="stSidebar"] *{
  background: transparent !important;
  background-color: transparent !important;
}

/* Optional: subtle divider line on right edge */
aside[data-testid="stSidebar"]::after{
  content:""; position:absolute; top:0; bottom:0; right:0; width:2px;
  background: linear-gradient(to bottom,
              rgba(255,255,255,.70),
              rgba(255,255,255,.35),
              rgba(255,255,255,.70));
  pointer-events:none;
}

/* Table glass (same as before) */
.stDataFrame table{
  background: rgba(255,255,255,.18) !important; backdrop-filter: blur(4px) !important;
  border-radius: 8px !important;
}
</style>
"""




# ── Login view ────────────────────────────────────────────────────────────────
def login_view():
    st.markdown(LOGIN_DARK_CSS, unsafe_allow_html=True)
    brandbar()  # Bonhoeffer Machines + centered big logo

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>🔐 Team Login</h2><p>Please sign in to continue</p>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("User Name").strip()
            designation = st.selectbox(
                "Designation",
                ["Software Developer", "Sales Executive", "Manager", "Intern", "Other"], index=0,
            )
        with col2:
            department = st.selectbox(
                "Department",
                ["Sales", "Marketing", "GSP", "Operations", "HR", "IT", "Finance", "Other"], index=0,
            )
            password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            key = username.lower()
            if key in USERS and USERS[key] == _hash(password):
                st.session_state["auth_ok"] = True
                st.session_state["user"] = {
                    "username": username,
                    "designation": designation,
                    "department": department,
                }
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Gate: show login first ────────────────────────────────────────────────────
if not logged_in():
    login_view()
    st.stop()

# ── Post-login top UI (title + sidebar) ───────────────────────────────────────
st.markdown(APP_LIGHT_CSS, unsafe_allow_html=True)
st.title("📊 Sales Dashboard – Primary & Secondary")

sb = st.sidebar
u = st.session_state.get("user", {})
with sb:
    st.markdown(f"**👋 Logged in as:** {u.get('username','')}  \n"
                f"**{u.get('designation','')} – {u.get('department','')}**")
    st.button("Logout", on_click=logout, type="secondary")

# =========================
# secondary_sheets WILL START BELOW THIS LINE
# =========================




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
    ],
     "Jamaica":[
        "https://docs.google.com/spreadsheets/d/1Mxu810CoTJaQdJHUFPPzUnRd9ncGDK2V8wNAwpmf3bg/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1wPyc1LZVaVNgIrUJy5oRqj-JvpyIYqyhJ5pvgNnJano/export?format=csv"
     ],
     "Uruguay":[
        "https://docs.google.com/spreadsheets/d/1S3tCmjy5rXj4KrDuaejDEPK-Kquf5dz3IUq2Bs67DY0/export?format=csv"
     ]
}
secondary_segments = {
    "Mexico":   ["Gardening","Powertools","GSP"],
    "Peru":     ["Powertools","Gardening"],
    "Honduras": ["Powertools","Gardening"],
    "Panama":   ["Powertools","Gardening"],
    "Nicaragua":["Gardening"],
    "Jamaica":["Gardening","GSP"],
    "Uruguay":["Powertools"]
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

# ── Sidebar controls ──────────────────────────────────────────────────────────
sales_type = sb.radio("Select Sales Type:", ["Primary Sales", "Secondary Sales"], key="sales_type_radio")
if sales_type == "Primary Sales":
    trans_type = sb.radio("Select Transaction Type:", ["Incoming", "Outgoing"], index=0, key="primary_trans_type")
else:
    trans_type = sb.radio("Select Transaction Type:", ["Incoming", "Outgoing"], index=1, key="secondary_trans_type")

# ── Main content ──────────────────────────────────────────────────────────────
if sales_type == "Primary Sales" and trans_type == "Incoming":
    tab = sb.selectbox("📑 Select Primary Tab:", list(primary_tabs.keys()))
    csv_url = primary_tabs[tab]
    st.markdown(f"### 🔗 {tab}")
    try:
        df = pd.read_csv(csv_url)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Could not load '{tab}': {e}")

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
        import re, json
        raw_url  = primary_outgoing[person]
        sid      = re.search(r"/d/([a-zA-Z0-9-_]+)", raw_url).group(1)
        meta_url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/metadata?&tqx=out:json"
        try:
            resp = requests.get(meta_url); resp.raise_for_status()
            raw  = resp.text
            j    = json.loads(raw[raw.find('{'): raw.rfind('}')+1])
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

elif sales_type == "Secondary Sales" and trans_type == "Incoming":
    st.subheader("📥 Secondary Sales – Incoming")
    st.info("🚧 This section is under construction. Please switch to **Outgoing** to view data.")



