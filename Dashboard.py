import streamlit as st
import pandas as pd
import requests
import hashlib, base64
from pathlib import Path

# ── App config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ── Paths (robust for GitHub/Linux) ───────────────────────────────────────────
APP_DIR   = Path(__file__).resolve().parent
ASSETS    = APP_DIR / "assets"
STATICDIR = APP_DIR / ".streamlit" / "static"
PREFERRED_LOGO = ASSETS / "bonhoeffer-logo.png"   # keep this file in repo (case-sensitive)

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

# ── Logo loader (search common locations; works on GitHub deploys) ────────────
def _load_logo_bytes():
    candidates = [
        PREFERRED_LOGO,
        ASSETS / "logo.png",
        ASSETS / "bonhoeffer_logo.png",
        ASSETS / "logo-b-2.png",
        STATICDIR / "bonhoeffer-logo.png",
    ]
    for p in candidates:
        if p.exists():
            try:
                return p.read_bytes()
            except Exception:
                pass
    # fallback: scan repo for *logo*.{png,jpg,jpeg,webp,svg}
    exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    for p in APP_DIR.rglob("*"):
        if "logo" in p.name.lower() and p.suffix.lower() in exts:
            try:
                return p.read_bytes()
            except Exception:
                pass
    return None

# ── Brand header (CENTERED: logo + big title) ────────────────────────────────
def brandbar(title: str = "Bonhoeffer Machines"):
    b = _load_logo_bytes()
    b64 = base64.b64encode(b).decode("utf-8") if b else ""
    img = f"<img class='brandlogo' src='data:image/png;base64,{b64}' alt='logo'/>" if b64 else ""
    html = f"<div class='brandwrap'>{img}<h1 class='brandname'>{title}</h1></div>"
    st.markdown(html, unsafe_allow_html=True)  # IMPORTANT: no st.write()/st.code()

# ── Styles (Login dark) ───────────────────────────────────────────────────────
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
  height:100px;              /* change if you want bigger/smaller */
  width:auto; object-fit:contain;
  border-radius:12px;
  filter: drop-shadow(0 6px 18px rgba(0,0,0,.35));
}
.brandname{
  margin:0; font-size:3.2rem; line-height:1.05; font-weight:800;
  color:#e5e7eb; letter-spacing:.2px;
}
@media (max-width: 640px){
  .brandlogo{ height:64px; }
  .brandname{ font-size:2rem; }
}

/* remove any stray strip under brand */
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
  border:1.5px solid #243144 !important; border-radius:10px !important;
}
.stSelectbox div[data-baseweb="select"]>div{
  background:#0f172a !important; color:#e5e7eb !important;
  border:1.5px solid #243144 !important; border-radius:10px !important;
}
label{ color:#cbd5e1 !important; }
.stButton>button{
  background: linear-gradient(90deg,#2563eb,#06b6d4) !important;
  color:#fff !important; border:none !important; border-radius:10px !important;
  padding:.55em 1.2em !important; box-shadow: 0 8px 24px rgba(2,132,199,.35);
}
.stButton>button:hover{ filter:brightness(1.05); }
</style>
"""

# ── Styles (Post-login app base) ──────────────────────────────────────────────
APP_LIGHT_CSS = """
<style>
[data-testid="stHeader"]{ background:transparent !important; box-shadow:none !important; }
/* MAIN (right) background */
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

# ── Force sidebar gradient + select hover/active + radio red ─────────────────
SIDEBAR_FORCE_CSS = """
<style>
:root{ --sb-grad: linear-gradient(180deg,#3D6CFF 0%,#7FAAFF 40%,#B8D3FF 75%,#FFFFFF 100%); }
aside[data-testid="stSidebar"], section[data-testid="stSidebar"]{
  background: transparent !important; position: relative; min-height: 100vh; overflow: visible !important;
}
aside[data-testid="stSidebar"]::before, section[data-testid="stSidebar"]::before{
  content:""; position:absolute; inset:0; background: var(--sb-grad) !important; z-index: 0;
}
aside[data-testid="stSidebar"] *, section[data-testid="stSidebar"] *{
  background: transparent !important; background-color: transparent !important;
}
aside[data-testid="stSidebar"]::after, section[data-testid="stSidebar"]::after{
  content:""; position:absolute; top:0; bottom:0; right:0; width:2px;
  background: linear-gradient(to bottom,rgba(255,255,255,.70),rgba(255,255,255,.35),rgba(255,255,255,.70));
  z-index: 1; pointer-events:none;
}
</style>
"""

SIDEBAR_HOVER_FIX_CSS = """
<style>
/* Sidebar selectbox: visible hover + focus ring (base) */
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div{
  background: rgba(255,255,255,.14) !important;
  border: 1.5px solid rgba(255,255,255,.35) !important;
  border-radius: 10px !important;
  transition: box-shadow .15s ease, background .15s ease, border-color .15s ease;
}
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div:hover{
  background: rgba(255,255,255,.20) !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,.35) !important;
}
/* Dropdown options overlay */
div[role="listbox"] [role="option"]{
  border-radius: 8px !important;
  margin: 2px 6px !important;
  padding: 8px 10px !important;
}
div[role="listbox"] [role="option"]:hover{
  background: rgba(59,130,246,.18) !important;
}
div[role="listbox"] [role="option"][aria-selected="true"]{
  background: rgba(59,130,246,.28) !important;
  outline: 2px solid rgba(59,130,246,.55) !important;
  outline-offset: 0 !important;
  position: relative;
}
div[role="listbox"] [role="option"][aria-selected="true"]::after{
  content: "✓";
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  font-weight: 700;
}
</style>
"""

RADIO_RED_CSS = """
<style>
/* Sidebar radios: red indicator & hover */
aside[data-testid="stSidebar"] input[type="radio"]{
  accent-color:#ef4444 !important; /* native radios fallback */
}
/* BaseWeb radios used by Streamlit */
aside[data-testid="stSidebar"] [data-baseweb="radio"] label > div:first-child{
  border-color: rgba(239,68,68,.85) !important;
  transition: box-shadow .15s, border-color .15s, background .15s;
}
aside[data-testid="stSidebar"] [data-baseweb="radio"] label:hover > div:first-child{
  box-shadow: 0 0 0 3px rgba(239,68,68,.35) !important;
}
aside[data-testid="stSidebar"] [data-baseweb="radio"] label[aria-checked="true"] > div:first-child{
  background:#ef4444 !important;
  border-color:#ef4444 !important;
  box-shadow: 0 0 0 3px rgba(239,68,68,.30) !important;
}
aside[data-testid="stSidebar"] [data-baseweb="radio"] label[aria-checked="true"] svg{
  color:#fff !important; fill:#fff !important;
}
</style>
"""

# Active dropdown highlight: red label + arrow rotate + red ring when open/focused
SIDEBAR_SELECT_ACTIVE_CSS = """
<style>
/* base already set by hover fix; add clear active/open cues */
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div[aria-expanded="true"],
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div:focus-within{
  border-color:#ef4444 !important;
  box-shadow: 0 0 0 3px rgba(239,68,68,.40) !important;
  background: rgba(255,255,255,.24) !important;
}
/* label turns red for active dropdown */
aside[data-testid="stSidebar"] .stSelectbox:hover > label,
aside[data-testid="stSidebar"] .stSelectbox:focus-within > label{
  color:#ef4444 !important; font-weight:700 !important;
}
/* arrow anim + active color */
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] svg{
  transition: transform .2s ease, color .2s ease;
}
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div[aria-expanded="true"] svg{
  transform: rotate(180deg);
  color:#ef4444 !important;
}
/* options: selected = red bg + tick */
div[role="listbox"] [role="option"][aria-selected="true"]{
  background: rgba(239,68,68,.22) !important;
  outline: 2px solid rgba(239,68,68,.55) !important;
}
div[role="listbox"] [role="option"][aria-selected="true"]::after{
  content:"✓"; position:absolute; right:10px; top:50%; transform:translateY(-50%); font-weight:700;
}
</style>
"""

# Stronger ring + z-index fixes so red ring definitely appears
SIDEBAR_SELECT_RING_FIX_CSS = """
<style>
/* Make sure ring is not clipped anywhere */
aside[data-testid="stSidebar"], section[data-testid="stSidebar"],
aside [data-testid="stSidebarContent"], aside [data-testid="stVerticalBlock"]{
  overflow: visible !important;
}
/* Base look with higher z so ring shows above gradient */
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div{
  position: relative;
  z-index: 2;
  background: rgba(255,255,255,.14) !important;
  border: 1.5px solid rgba(255,255,255,.35) !important;
  border-radius: 10px !important;
}
/* Hover = red ring */
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div:hover{
  border-color:#ef4444 !important;
  box-shadow: 0 0 0 3px rgba(239,68,68,.40) !important;
  background: rgba(255,255,255,.20) !important;
}
/* Focus/Open = stronger red ring */
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div:focus-within,
aside[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div[aria-expanded="true"]{
  border-color:#ef4444 !important;
  box-shadow: 0 0 0 3px rgba(239,68,68,.48) !important;
  background: rgba(255,255,255,.24) !important;
}
/* Options menu on top */
div[role="listbox"]{ z-index: 9999 !important; }
</style>
"""

def inject_post_login_styles():
    st.markdown(APP_LIGHT_CSS, unsafe_allow_html=True)

    st.markdown(SIDEBAR_FORCE_CSS, unsafe_allow_html=True)
    st.sidebar.markdown(SIDEBAR_FORCE_CSS, unsafe_allow_html=True)

    st.markdown(SIDEBAR_HOVER_FIX_CSS, unsafe_allow_html=True)
    st.sidebar.markdown(SIDEBAR_HOVER_FIX_CSS, unsafe_allow_html=True)

    st.markdown(RADIO_RED_CSS, unsafe_allow_html=True)
    st.sidebar.markdown(RADIO_RED_CSS, unsafe_allow_html=True)

    st.markdown(SIDEBAR_SELECT_ACTIVE_CSS, unsafe_allow_html=True)
    st.sidebar.markdown(SIDEBAR_SELECT_ACTIVE_CSS, unsafe_allow_html=True)

    st.markdown(SIDEBAR_SELECT_RING_FIX_CSS, unsafe_allow_html=True)
    st.sidebar.markdown(SIDEBAR_SELECT_RING_FIX_CSS, unsafe_allow_html=True)

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





