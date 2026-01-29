import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="Gürkan AI : Favorite Manager", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 15px; }
    .intel-box { background: rgba(255, 204, 0, 0.03); border: 1px solid #30363d; border-left: 5px solid #ffcc00; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .research-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; }
    .research-item { background: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; text-align: center; }
    
    /* Favori Butonları Özel Tasarım */
    .fav-bar { display: flex; gap: 10px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px; }
    
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 10px; font-weight: bold; }
    .price-main { font-size: 40px; font-weight: bold; font-family: 'JetBrains Mono'; color: #fff; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --- 3. YARDIMCI FONKSİYONLAR ---
def get_research(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = (100 - (100 / (1 + g/l))).iloc[-1]
        
        status = "NÖTR"; col = "#8b949e"
        if lp > ma20 and vol_r > 1.2 and rsi < 68: status = "GÜÇLÜ AL"; col = "#00ff88"
        elif lp < ma20: status = "SAT / ZAYIF"; col = "#ff4b4b"
        elif rsi > 70: status = "AŞIRI ŞİŞME"; col = "#ffcc00"
        return {"p": lp, "ch": ch, "ma": ma20, "rsi": rsi, "vol": vol_r, "status": status, "col": col, "df": df}
    except: return None

# --- 4. LAYOUT ---
m_col, r_col = st.columns([3.2, 1])

with m_col:
    # Arama ve Favori Yönetimi
    c1, c2, c3, c4 = st.columns([4, 1, 1, 0.5])
    with c1: s_inp = st.text_input("HİSSE ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        # Favori Ekle/Çıkar Mantığı
        is_fav = s_inp in st.session_state["favorites"]
        btn_label = "⭐ ÇIKAR" if is_fav else "⭐ EKLE"
        if st.button(btn_label):
            if is_fav: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()
    with c4:
        if st.button("❌", help="Tüm favorileri temizle"):
            st.session_state["favorites"] = []
            st.rerun()

    # FAVORİ BUTONLARI
    if st.session_state["favorites"]:
        st.markdown("<p class='label-mini'>HIZLI ERİŞİM</p>", unsafe_allow_html=True)
        fav_list = st.session_state["favorites"]
        f_cols = st.columns(len(fav_list) if len(fav_list) > 0 else 1)
        for i, fv in enumerate(fav_list):
            if f_cols[i].button(fv, key=f"btn_{fv}"):
                st.session_state["last_sorgu"] = fv; st.rerun()

    # ANALİZ VE ARAŞTIRMA
    res = get_research(st.session_state["last_sorgu"])
    if res:
        card_html = """
        <div class='master-card'>
            <p class='label-mini'>SYM // TEKNİK ANALİZ</p>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span class='price-main'>PRICE</span>
                <span style='color:C_COL; font-size:24px; font-weight:bold;'>ST_TXT</span>
            </div>
            <div style='margin-top:10px; color:CH_COL; font-weight:bold;'>Günlük: CHG%</div>
        </div>
        """.replace("SYM", st.session_state["last_sorgu"]).replace("PRICE", f"{res['p']:.2f}").replace("ST_TXT", res['status'])\
           .replace("C_COL", res['col']).replace("CHG", f"{res['ch']:+.2f}").replace("CH_COL", "#00ff88" if res['ch']>0 else "#ff4b4b")
        st.markdown(card_html, unsafe_allow_html=True)

        intel_html = """
        <div class='intel-box'>
            <p class='label-mini' style='color:#ffcc00;'>🕵️ GÜRKAN AI : DERİN İSTİHBARAT</p>
            <div class='research-grid'>
                <div class='research-item'><p class='label-mini'>HACİM</p><p style='font-size:12px;'>VOL_I</p></div>
                <div class='research-item'><p class='label-mini'>MOMENTUM</p><p style='font-size:12px;'>RSI_I</p></div>
                <div class='research-item'><p class='label-mini'>TREND</p><p style='font-size:12px;'>TRND_I</p></div>
            </div>
        </div>
        """.replace("VOL_I", "Para Girişi Var" if res['vol']>1.2 else "Hacim Normal")\
           .replace("RSI_I", "İştah Pozitif" if res['rsi']<65 else "Riskli Bölge")\
           .replace("TRND_I", "Güvenli Limit" if res['p']>res['ma'] else "Pivot Altı Tehlike")
        st.markdown(intel_html, unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 GÜVENLİ RADAR</p>", unsafe_allow_html=True)
    st.markdown("<div style='background:#0d1117; border:1px solid #30363d; border-radius:20px; padding:15px; height:800px; overflow-y:auto;'>Radar Aktif...</div>", unsafe_allow_html=True)
