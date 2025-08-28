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
    "Jamaica": [
        "https://docs.google.com/spreadsheets/d/1SIXzRosL4PagXjdgGd3uaem6gCwcyrvt648XVD8G1IY/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1joLyY3BHs6oUXTDGIZAVqk5VAHHUZk8h3xWmJqID1iA/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1rusnBIRJoJR0_sYDN_sE1Iq58jzrSsg0sBk_dQej6YY/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1Sk55vLxK4HOE8P7bzt3nE603KaKyal_uxJPYTuMEpvk/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1EufC5MhePH1ZaoraeHN0AzuvCF7_s3BC_zu64gZ09KQ/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1EufC5MhePH1ZaoraeHN0AzuvCF7_s3BC_zu64gZ09KQ/export?format=csv",
        "https://docs.google.com/spreadsheets/d/13AzE0TKZKNj4nNvB30BQeQ8ni5UE-bVs82k5v3yDOd8/export?format=csv"
                

    ],
    "Colombia": [
        "https://docs.google.com/spreadsheets/d/1JY80YG1oS0nqp13OHwG8lLOcKc6iWw74nYvTPHsxR4M/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1QD-Znj03f5yZXsyWMdo0qXqAj5wBLWvd1K-xHf0VYXw/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1OXblGTYXSk9DvxHjXieLZVirmzq4nKGjtDPL7U4EpNU/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1QEU9_tw0vllbq1gOPAZ-KDBAabqlq2wCMaRHMc3w47Y/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1OBdUpO1t5nTnsWCtkhHlJ1CZZn4JZORctyIJrs_oSSk/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1DgqJuV942YMtP8gD4Uj57DifGp7sIck3h7GoBXugr1Y/export?format=csv"

    ],
    "Ecuador": [
        "https://docs.google.com/spreadsheets/d/1jtk1GXTgVJi_5NDodczN0nyuVD3i5gbGsVWORl-wrZ4/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1OsESiw-9e5y3xEQSyhWbh3_6ugbWOGwwdgjYLSSo6O4/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1Sg0QfEpDy38WcA9mp5eXNMczRc9u08tXs-3zgVtjFWs/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1UMOfrJ_Is4-B0Vfqsr7BQdt8nje9S66Mj5cHIE891Zk/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1ROBZvOsZfqArFT66FrkRBNdzjI12Zy1-JOk34acmjiA/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1VA1kz5RDcSa2-BCt0CM8l0xwjMf_6Ht8yzgQ9BqA-lg/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1DL9x0haATrdUHZV9Im7cFgIJJqU6S8PCykuDpb7pYJQ/export?format=csv",
        "https://docs.google.com/spreadsheets/d/12_doGxcFY4uGSfIBRrIJUtxK1j7sOf9PMKYUp-SUPRQ/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1Zfvp-qtxf9e9AcXdvMU717vIzSPNKEf4KbIpVcABIXA/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1UMOfrJ_Is4-B0Vfqsr7BQdt8nje9S66Mj5cHIE891Zk/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1ROBZvOsZfqArFT66FrkRBNdzjI12Zy1-JOk34acmjiA/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1_n0xIMwv6T_lkrqBxLNDSMdtAMudOKdmE-50zIw3Y2s/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1dZwrtBC7E9b5m7YaPZO4axLEjN8VbhYgFDdowAGWTEE/export?format=csv"
    ],
    "Mexico": [
        "https://docs.google.com/spreadsheets/d/1p1LpIhcUOcnjYDdrGEhkfQ8kwKMckXqEzT9M_mAOpC0/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1tkNx01URKj3X06QHcCKrEpeKCmZKkAzF9ZJdkMK_iAA/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1BaGypwBvJM8xbU_WD_Xp9-vU1G1hsmVL0werN2HkTcU/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1sfDFzk02mB6xqh5W9y23BWBqXG5QT_Yk6pmqWdzfEyU/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1DuvYzjrr0wAEUnRdbKAYjwjhwsLil6tDEJe2Jm6oRmw/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1PWZ5sSI-RuGTs9CRjKdHr3znRauT6M2b8K2zTo5b22s/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1gijUgQ-s3YVML6AdvWNZCYjPKx9LYN8p4Wf6skOlHb8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1g5tML2NTzmzLlHoDx60Pr3oBYky428iRu2lNEvQ8uk8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1v_MsfijmfXFyGeUomiCpQtZ1g_-nJfG61uI1ImOSsYU/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1Y-R5MGRK8LHYIrbapsdqcG8SKMg3iIhA_7UhdLoOeto/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1rVdnYe5kS9HUiYj8-MYj1FrjNoZ8E3msaID2fXQlFg8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/17LwDP3TaY-YirJUgYzxECHg2KajSXAUOed8KZMZ1TE0/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1BLNZMqWAafnYYtVnSJNIOll6n1MDKzkVEZxhixh9CtI/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1rXcIEv2rDrharOHsfe6nT1JeIn1Nc8Rw6s4kh5ZyAZk/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1B4ZIj8nK-mxXtGYi9sjjbEe0m18JA-EJ069ZUmpcrbg/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1ViYLN_0vWv49vgxbRq-JZzOAqWr-HMB8_dE3dn_BGr8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1QR37MDuFuX8tRAjBYFxwwtrW_cOZ8CVH45c-Nuy8PB8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1ZH1vtqX4VpbLAZMMj5-Ta05lkRvby6GiHIAfxLctkYY/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1uVN_7BZqk7VcitxXcdQP0JRNhD8AjNgZ0ThmGMaFp2Y/export?format=csv",        
        "https://docs.google.com/spreadsheets/d/1th2mbHpK3O6LT3YznoLEeK_kzry-l2V15NGjSrAcSr0/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1BPWPRjMO8H3o89LSQojbO8Zthj3DPghxkdMruG1NsDA/export?format=csv",
        "https://docs.google.com/spreadsheets/d/174KOikG3t1_91aDC1zdzPxhGcchijsfm_78wQxOc1Vw/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1e1DlLyiLOZMpKZ4fptZ23yURduLsZh26lii6iTXXs24/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1VEZbM37DoXWiGlEX9Ks1T7UgKB4L9NqZZOLM-9-yX48/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1Z-uAaGNf0FO_mkLLQ1zZGAg1zT_MVXnLd_XLnNJ1P3E/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1HLVR58dIsNF0GvsNGVrHYXWLIeFiBuPlPVaYTuJDeus/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1iebmuNHQIc-e4Ad-nA7bYl01WH_s02xcS71ioPKWAsY/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1sfDFzk02mB6xqh5W9y23BWBqXG5QT_Yk6pmqWdzfEyU/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1NGTlgC3c_rQBQ0lGZ6E7MU41_0nt79jM9PBh9Uhqve8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1FW52n7fKpGQAoOUl6wVQNlRoI78bds5X4PEXpZRY3HM/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1O2TZWrkquWxnAqqqI3UvnK9ULFxbYBLoUfoJt0ls3j8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/17m6xM24N6WwwRvQB99MD3sjCRDB8gUPkS4yMbovpo-E/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1DuvYzjrr0wAEUnRdbKAYjwjhwsLil6tDEJe2Jm6oRmw/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1WgCRTIfnxJ5cu7l6oVF7WmZ5x_SuOQ6Zt6MUi35fXr8/export?format=csv"



    ],
    "Argentina": [
        "https://docs.google.com/spreadsheets/d/13a6etQr6o9BwR4h_1HWFJK9XAZjHFvbhjeWTxkh8JLM/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1KLxD62Uk6IcecgW083G6ifIhQ9ZFfQ7n5bumztguuzk/export?format=csv"
    ],

    "Chile": [
        "https://docs.google.com/spreadsheets/d/1KNEScmeUlMqmWuCBDZDbAviZsgt1tJebRTnbz4IAhf0/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1DWOo4hsI82FfmNVUJwMQ4UhlT73fgidEY-zq9KjPsSo/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1DgqJuV942YMtP8gD4Uj57DifGp7sIck3h7GoBXugr1Y/export?format=csv",
        "https://docs.google.com/spreadsheets/d/14zg9cfuhLjqfapDUgcLCt9YOPmQFsBiCrlCfDeV0F7w/export?format=csv"
    ],

    "Brazil":[
        "https://docs.google.com/spreadsheets/d/1FEW_pD5N8EE0ZhVVse8sPIh3YAQmnxBmvc4RKtG4Kas/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1hhVMw17w5ilpYJrX5Oalpererfeci0rFOLM_eJkDWHw/export?format=csv"
        
    ],

    "Argentina":[
        "https://docs.google.com/spreadsheets/d/13a6etQr6o9BwR4h_1HWFJK9XAZjHFvbhjeWTxkh8JLM/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1loMmb80Jm0j7krU1mMLHXxoxWoWrtREC7uWpedqk9K8/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1g0jqn8ZctNw7CFcxOg80kg8rkTt6Oq3oIrMkuj0CjQU/export?format=csv",
        "https://docs.google.com/spreadsheets/d/13a6etQr6o9BwR4h_1HWFJK9XAZjHFvbhjeWTxkh8JLM/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1loMmb80Jm0j7krU1mMLHXxoxWoWrtREC7uWpedqk9K8/export?format=csv"


    ],

    "Dominican Republic":[
        "https://docs.google.com/spreadsheets/d/1GrkGk_LVLKT3kA0wQ5WE4GLCr1A2iQyNVQmjA3xOs14/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1D0vCRz58eGBRr0zCUjPpMk3ujgXAXYsTjoA-HIGximw/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1QOsXj7hiodKAkH5XOORXHXKEBd8Cq1YZNa3N0NPZeGk/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1QiujbU5fyRLX6N21PJpLgtQgT3Gv4Idbpiic7W1iN_g/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1_78w9mg6Y9ogmO-yUUChHtdQHJCF8VLqL1sv4pVimnQ/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1qsIFE2ReCzr7KMbJQdL8sf9-YGOJxndmZXumJOyi9To/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1aQNROI_TxrVVm2QwekLNmiZ1tbdE9Pr13KhmKKDJ-og/export?format=csv",
        "https://docs.google.com/spreadsheets/d/19tjPjkduRrHJ7ZA4-WAa39bCwe_TiaPcajpXSJuHDdg/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1nmqieET8auhQH3MaLVH3Qdtvb1CkeBuc3_UjnkvxOno/export?format=csv"

    ],

    "Paraguay":[
        "https://docs.google.com/spreadsheets/d/18LdylZkeQkB4DKDlhYJlY1JFUvD4ypSPW0w5EupnVb4/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1C1y-HxgsfoPX2N2U9xLA3VCuUKx2_uFCzjqG3GVcJXE/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1-CJLE3ZnbPrYVM-j4ul47zfBBt5_I3mFhtFsoj1B2eg/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1n4GsytxLeZeYvNH10x20Fa--jwoLJ0KaNeTILZWgt4U/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1Y7gFYYWwUZr9E2os5BSG9ZrsH0RALR4c5jq1ienYrXg/export?format=csv",
        "https://docs.google.com/spreadsheets/d/18miP2TXKW3Vayr0P7fx3sP9bMzvQnnvIf7S0cfXco1o/export?format=csv"
        
    ],

    "Uruguay":[
        "https://docs.google.com/spreadsheets/d/16_UVCPH3Rvs9dH-DXnyOn9AG-06uye3ul5VF_eHWisw/export?format=csv",
        "https://docs.google.com/spreadsheets/d/16HgzT__N2wjCmdnRR9kFjh-MNR8YCnXjLxXZeZ_O_qw/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1sIU18Y7DZ8j-ndUG5nT-S4V58PQ0CpyhP-QfLoQuS3A/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1pyLVShuhZ10ztmWbwe5-PhsOYlj1YKwuP16APDJ-Hhw/export?format=csv"
    ],

    "Peru" :[
        "https://docs.google.com/spreadsheets/d/1Jvhi1oKED8SAviitGfRx09J3bBj9lKOBpRB9zZWcZb8/export?format=csv"

    ],

    "Honduras": [
        "https://docs.google.com/spreadsheets/d/1xnxboZrEcAP5VnCOnzfhscxZP6q4PNzbR9wvho3wX2g/export?format=csv",
        "https://docs.google.com/spreadsheets/d/1NVyMI5R2cT8OGCOdtcjz7x6JQvm-kjLJfuPefjivffs/export?format=csv"
    ]
                
}


# ─── Secondary Sales – country → list of segment names ────────────────────
secondary_segments = {
    "Jamaica":            ["Gardening 1", "Gardening2", "GSP1", "GSP2", "Gardening3", "Powertools1","Poertools2"],
    "Colombia":           ["GSP1", "GSP2", "Gardening1", "Gardening2", "Powertools1"],
    "Ecuador":            ["GSP1", "GSP2", "GSP3", "GSP4", "GSP5","GSP6","Gardening1", "Gardening2", "Gardening3","powertools1",  "powertools2",  "powertools3",  "powertools4"],
    "Mexico":             ["Gardening1", "Gardening2", "Gardening3","Gardening4", "Gardening5", "Gardening6", "Gardening7", "Gardening8", "Gardening9", "Gardening10", "Gardening11", "Gardening12", "Gardening13", "Gardening14", "Gardening15", "Gardening16", "powertools1",  "powertools2",  "powertools3",  "powertools4",
                           "powertools5",  "powertools6",  "powertools7",  "powertools8","powertools9",  "powertools10", "powertools11", "powertools12"],
    "Argentina":          ["GSP1", "GSP2","powertools1","Gardening1", "Gardening2"],
    "Chile":              ["Gardening1", "GSP1", "powertools1", "powertools2"],
    "Brazil":             ["Gardening1", "Gardening2"],
    "Dominican Republic": ["Gardening1", "Gardening2", "Gardening3", "GSP1", "GSP2", "GSP3", "Powetools1","Powertools2","Powertools3"],
    "Paraguay":           ["Gardening1", "Gardening2", "GSP1","GSP2","Powertools1","Powertools2"],
    "Uruguay":            ["Gardening1", "Gardening2","GSP1","GSP2"],
    "Peru":               ["Powertools1"],
    "Honduras":           ["Powertools1","Powertools2"]

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



   
