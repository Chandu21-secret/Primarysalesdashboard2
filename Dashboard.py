import streamlit as st
import pandas as pd
import requests
import hashlib, base64
from pathlib import Path

# ── App config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ── Paths ────────────────────────────────────────────────────────────────────
APP_DIR   = Path(__file__).resolve().parent
ASSETS    = APP_DIR / "assets"
STATICDIR = APP_DIR / ".streamlit" / "static"

# prefer this name; keep it in repo (case-sensitive on GitHub)
PREFERRED_LOGO = ASSETS / "bonhoeffer-logo.png"

# ====== Simple Auth (in-memory) ==============================================
def _hash(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

USERS = {
    "chandan": _hash("admin@123"),
    "shweta":  _hash("shweta@123"),
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

# ── Logo loader (robust for GitHub / Linux) ───────────────────────────────────
def _load_logo_bytes() -> tuple[bytes | None, str | None]:
    # explicit candidates first
    candidates = [
        PREFERRED_LOGO,
        ASSETS / "bonhoeffer_logo.png",
        ASSETS / "logo.png",
        ASSETS / "logo-b-2.png",
        ASSETS / "logo-B 2.png",
        STATICDIR / "bonhoeffer-logo.png",
    ]
    for p in candidates:
        if p.exists():
            return p.read_bytes(), str(p)

    # fallback: search repo for *logo*.* (case-insensitive)
    exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    for p in APP_DIR.rglob("*"):
        if "logo" in p.name.lower() and p.suffix.lower() in exts:
            try:
                return p.read_bytes(), str(p)
            except Exception:
                pass
    return None, None

# ── Brand header (CENTERED: logo + big title) ────────────────────────────────
def brandbar(title: str = "Bonhoeffer Machines"):
    logo_b, src = _load_logo_bytes()
    logo_b64 = base64.b64encode(logo_b).decode("utf-8") if logo_b else ""
    img = f"<img class='brandlogo' src='data:image/png;base64,{logo_b64}' alt='logo'/>" if logo_b64 else ""
    html = f"<div class='brandwrap'>{img}<h1 class='brandname'>{title}</h1></div>"
    st.markdown(html, unsafe_allow_html=True)
    # debug toggle: set True to see where it loaded from
    DEBUG = False
    if DEBUG:
        st.caption(f"Logo source: {src or 'NOT FOUND'}")

# ── Styles (Login dark) ───────────────────────────────────────────────────────
LOGIN_DARK_CSS = """
<style>
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
  height:100px;
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

/* remove stray dark strip under brand */
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

# ── Styles (Post-login app + sidebar gradient) ────────────────────────────────
APP_LIGHT_CSS = """
<style>
[data-testid="stHeader"]{ background:transparent !important; box-shadow:none !important; }
[data-testid="stAppViewContainer"]{
  background: linear-gradient(90deg,#B9F5C8 0%, #C3F0DD 30%, #CDE7F1 65%, #B8D2FF 100%) !important;
  background-attachment: fixed !important;
}
/* table glass */
.stDataFrame table{
  background: rgba(255,255,255,.18) !important; backdrop-filter: blur(4px) !important;
  border-radius: 8px !important;
}
</style>
"""



def inject_post_login_styles():
    st.markdown(APP_LIGHT_CSS, unsafe_allow_html=True)
  

# ── Login view ────────────────────────────────────────────────────────────────
def login_view():
    st.markdown(LOGIN_DARK_CSS, unsafe_allow_html=True)
    brandbar()  # Centered logo + title

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
inject_post_login_styles()
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
        "https://docs.google.com/spreadsheets/d/1E4Fb8O3ra8P8JpR8bWXGuJ3VkqjG0EZGGX1TeIGgtRA/export?format=csv",
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
     ],
    "Colombia":[
        "https://docs.google.com/spreadsheets/d/1e9-E9m4W6Tim929au6Lr_40eobM73fm8G1xVF-mSG2U/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1Mjcamt0QJZvSLfBdyh-q4u_P08oI7ttCQBYtR6t1sv0/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1KUhznIurYMT-xH8yKOTQ6mbVX3HQhL9m0OZc917x64M/export?format=csv"],

    
    "Brazil":[
        "https://docs.google.com/spreadsheets/d/1CjsC3Fvf6ag26QKdGmoSwgX330scuDgI9HD2xF7fDc8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1At3MMnUsYiaLbVI2_VMrFt7iepEAtHxa74nghk1jbS8/export?format=csv"],

    
    "Ecuador":[
         "https://docs.google.com/spreadsheets/d/1_xdFzYQ7HgxYVGE93qfmHrro_5UeRy-D5qWwyc7Ps-Y/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1jQzeI8jXoWwsutUJDvBZBK9VDPwVXUVu7XWDxSE3zvM/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1lbcj3MLClwPm_bh4EPAUJRz2Qu6alKDTvWDS3BmxbYg/export?format=csv"],

    
    "Paraguay":[
        "https://docs.google.com/spreadsheets/d/1HK0wTh82snG6DkaCWHUCcSxp5CiN9Up85QcBMVJm1JQ/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1_x4hu3_8Zg1yapTb46TU8251-e_Fn-AmVXzLfR4Y9qk/export?format=csv"],


    
    "Chile":[
        "https://docs.google.com/spreadsheets/d/1f40vygYZdk3euJwAbxD14sG8WZJjCdlwkm78jzAev88/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1bR0yZ0XH6Igdq9rJQEn91VIyqlnxc2ljwrmUjsKo92Q/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1acLCXYNoXD-EP5mXPqmTtK8ZG2kXng1t-_JMFlkygek/export?format=csv"],


    "Dominican Republic":[
        "https://docs.google.com/spreadsheets/d/15m77a-ZSOQUUVdT63JDxSK9tHyAykz2fFs00KUz_iKk/export?format=csv"],

    "Argentina":[
         "https://docs.google.com/spreadsheets/d/1X43vCvu63kOJHPxMtl5jL_29GTbC0llOPPKt_NFI3UI/export?format=csv",
         "https://docs.google.com/spreadsheets/d/1WP2O0WZ_7NzjXQo_AaczoL2tanMQeEXIPBozNv65k7g/export?format=csv"]   

}



secondary_segments = {
    "Mexico":   ["Gardening","Powertools","GSP"],
    "Peru":     ["Powertools","Gardening"],
    "Honduras": ["Powertools","Gardening"],
    "Panama":   ["Powertools","Gardening"],
    "Nicaragua":["Gardening"],
    "Jamaica":["Gardening","GSP"],
    "Uruguay":["Powertools"],
    "Colombia":["GSP","Gardening","Powertools"],
    "Brazil":["Powertools","Gardening"],
    "Ecuador":["GSP","Gardening","Powertools"],
    "Paraguay":["GSP","Powertools"],
    "Chile":["GSP", "Gardening","Powertools"],
    "Dominican Republic":["Powertools"],
    "Argentina":["Gardening","GSP"]
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














