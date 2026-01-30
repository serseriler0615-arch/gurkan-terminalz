import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM VE STRATEJİ AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Strategist v223", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "EREGL", "TUPRS"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

# --- 2. CSS (PREMIUM STRATEGIST LOOK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #050505 !important; color: #e1e1e1 !important; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-left: 6px solid #ffcc00; margin-bottom: 15px; }
    .strategy-box { background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 15px; }
    .metric-item { background: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 800; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border-radius: 8px; font-weight: bold; width: 100%; transition: 0.3s; }
    div.stButton > button:hover { border-color: #ffcc00 !important; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# --- 3. STRATEJİ MOTORU (DEEP LOGIC) ---
def get_strategist_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # RSI ve Volatilite
        delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = (100 - (100 / (1 + g/l))).iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        # ZEKA: SENARYO ÜRETİMİ
        strategy = ""
        action = "İZLE / BEKLE"
        act_col = "#8b949e"
        
        if lp > ma20 and rsi < 65 and vol_r > 1.2:
            action = "GÜÇLÜ ALIM BÖLGESİ"
            act_col = "#00ff88"
            strategy = f"Hisse {ma20:.2f} üzerinde tutunuyor. Hacimli kırılım var. {lp + (atr*2):.2f} hedefiyle pozisyon korunabilir."
        elif rsi > 75:
            action = "KÂR AL / DİKKAT"
            act_col = "#ffcc00"
            strategy = "RSI aşırı alım bölgesinde. Yeni giriş riskli. Mevcut pozisyonlarda parça kâr alımı mantıklı görünüyor."
        elif lp < ma20:
            action = "RİSKLİ / SATIŞ BASKISI"
            act_col = "#ff4b4b"
            strategy = f"Pivot seviyesi ({ma20:.2f}) altında kapanışlar tehlikeli. {lp - (atr*1.5):.2f} seviyesine kadar çekilme beklenebilir."
        else:
            strategy = "Yatay seyir hakim. Net bir yön tayini için hacimli bir kırılım beklenmeli."

        return {
            "p": lp, "ch": ch, "ma20": ma20, "ma50": ma50, "rsi": rsi, "vol": vol_r, 
            "action": action, "act_col": act_col, "strategy": strategy, "df": df, "atr": atr
        }
    except: return None

# --- 4. UI ---
m_col, r_col = st.columns([3.5, 1])

with m_col:
    # Arama Barı
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("STRATEJİ SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ ET"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("⭐ FAVORİ"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favori Çubukları
    if st.session_state["favorites"]:
        f_cols = st.columns(len(st.session_state["favorites"]))
        for i, fv in enumerate(st.session_state["favorites"]):
            if f_cols[i].button(fv): st.session_state["last_sorgu"] = fv; st.rerun()

    res = get_strategist_analysis(st.session_state["last_sorgu"])
    if res:
        # Ana Analiz Kartı
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]} // ANALİST RAPORU</p>
                    <span style='font-size:42px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:20px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini'>SİNYAL GÜCÜ</p>
                    <h2 style='color:{res['act_col']}; margin:0;'>{res['action']}</h2>
                </div>
            </div>
            <div class='metric-grid'>
                <div class='metric-item'><p class='label-mini'>RSI</p><b>{res['rsi']:.1f}</b></div>
                <div class='metric-item'><p class='label-mini'>HACİM GÜCÜ</p><b>{res['vol']:.1f}x</b></div>
                <div class='metric-item'><p class='label-mini'>PİVOT (20)</p><b>{res['ma20']:.2f}</b></div>
                <div class='metric-item'><p class='label-mini'>ANA TREND</p><b>{"POZİTİF" if res['p']>res['ma50'] else "NEGATİF"}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Gürkan'ın Strateji Notu
        st.markdown(f"""
        <div class='strategy-box'>
            <p class='label-mini' style='color:#00ff88;'>⚡ GÜRKAN'IN STRATEJİK YORUMU</p>
            <p style='font-size:16px; margin:10px 0;'>{res['strategy']}</p>
            <div style='display:flex; gap:20px; border-top: 1px solid rgba(0,255,136,0.2); padding-top:10px;'>
                <span style='font-size:12px;'><b>HEDEF:</b> {res['p']+(res['atr']*2.5):.2f}</span>
                <span style='font-size:12px;'><b>STOP:</b> {res['p']-(res['atr']*1.8):.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 AKILLI RADAR</p>", unsafe_allow_html=True)
    st.markdown("<div style='background:#0d1117; border:1px solid #30363d; border-radius:15px; padding:15px; height:800px; text-align:center; color:#8b949e;'>Stratejik fırsatlar taranıyor...</div>", unsafe_allow_html=True)
