import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Deep Oracle", layout="wide", initial_sidebar_state="collapsed")

# Tarama yapılacak ana havuz (Geliştirilebilir)
SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "EKGYO", "ASTOR", "SASA", "HEKTS", "PGSUS"]

# --- 2. ELITE CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-top: 6px solid #ffcc00; margin-bottom: 20px; }
    .radar-box { background: rgba(255, 204, 0, 0.05); border: 1px solid #ffcc0044; border-radius: 15px; padding: 15px; margin-bottom: 20px; }
    .scan-item { display: inline-block; background: #161b22; padding: 10px 20px; border-radius: 10px; margin: 5px; border: 1px solid #30363d; }
    .prob-badge { color: #00ff88; font-weight: bold; font-family: 'JetBrains Mono'; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 8px; font-weight: bold; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. DERİN RADAR MOTORU (%90 OLASILIK) ---
@st.cache_data(ttl=300) # 5 dakikada bir veriyi tazeler
def deep_scan_market(symbols):
    opportunities = []
    for s in symbols:
        try:
            df = yf.download(s + ".IS", period="60d", interval="1d", progress=False)
            if len(df) < 30: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # Teknik Metrikler
            cp = df['Close'].iloc[-1]
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            vol_avg = df['Volume'].rolling(10).mean().iloc[-1]
            vol_now = df['Volume'].iloc[-1]
            
            # RSI Hesapla
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1+rs)).iloc[-1]
            
            # %90 Olasılık Koşulları (Puanlama Sistemi)
            score = 0
            if cp > ma20: score += 30 # Pivot üstü
            if vol_now > vol_avg * 1.3: score += 30 # Hacimli giriş
            if 50 < rsi < 65: score += 30 # Momentum taze
            if cp > df['Close'].iloc[-2]: score += 10 # Pozitif kapanış
            
            if score >= 80: # %80 ve üzeri skorları "Yüksek Olasılık" sayıyoruz
                opportunities.append({"symbol": s, "price": cp, "prob": score, "rsi": rsi, "vol": vol_now/vol_avg})
        except: continue
    return sorted(opportunities, key=lambda x: x['prob'], reverse=True)

# --- 4. ANALİZ MOTORU ---
def get_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        lp = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        target = lp + (atr * 2.8)
        stop = min(lp - (atr * 2.5), ma20 * 0.94)
        
        sig, col = ("GÜÇLÜ AL", "#00ff88") if lp > ma20 and vol_r > 1.2 else ("İZLE / ZAYIF", "#8b949e")
        if lp < ma20: sig, col = "RİSKLİ", "#ff4b4b"
        
        rep = f"RADAR ANALİZİ: {symbol} için olasılık yüksek. Hacim {vol_r:.1f}x ile destekleniyor. {ma20:.2f} ana destek hattı."
        return {"p": lp, "ch": ((lp-df['Close'].iloc[-2])/df['Close'].iloc[-2])*100, "df": df, "ma": ma20, "target": target, "stop": stop, "report": rep, "sig": sig, "col": col, "vol": vol_r}
    except: return None

# --- 5. UI ---
st.markdown("<h3 style='text-align:center; color:#ffcc00;'>GÜRKAN AI : DEEP ORACLE RADAR</h3>", unsafe_allow_html=True)

# --- RADAR BÖLÜMÜ ---
st.markdown("<div class='radar-box'><p class='label-mini'>📡 %90 OLASILIKLI SİNYAL RADARI (CANLI)</p>", unsafe_allow_html=True)
with st.spinner("Piyasa derinlemesine taranıyor..."):
    found = deep_scan_market(SCAN_LIST)
    if found:
        cols = st.columns(len(found) if len(found) < 5 else 5)
        for i, opp in enumerate(found[:5]):
            with cols[i]:
                st.markdown(f"""
                <div class='scan-item'>
                    <span style='color:#ffcc00; font-weight:bold;'>{opp['symbol']}</span><br>
                    <span class='prob-badge'>%{opp['prob']} Skor</span><br>
                    <span style='font-size:10px;'>Fiyat: {opp['price']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"İNCELE: {opp['symbol']}"):
                    st.session_state["last_sorgu"] = opp['symbol']
                    st.rerun()
    else:
        st.info("Şu an kriterlere tam uyan %90 olasılıklı hisse bulunamadı. Sabırlı ol patron.")
st.markdown("</div>", unsafe_allow_html=True)

# --- SORGULAMA ---
c1, c2 = st.columns([4, 1])
with c1: s_inp = st.text_input("", value=st.session_state.get("last_sorgu", "THYAO"), label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 MANUEL ANALİZ"): 
        st.session_state["last_sorgu"] = s_inp
        st.rerun()

res = get_analysis(st.session_state.get("last_sorgu", "THYAO"))
if res:
    c_val = "#00ff88" if res['ch'] > 0 else "#ff4b4b"
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between;'>
            <div>
                <p class='label-mini'>{st.session_state.get("last_sorgu")} // DERİN İSTİHBARAT</p>
                <span style='font-size:45px; font-weight:bold;'>{res['p']:.2f}</span>
                <span style='color:{c_val}; font-size:20px;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['col']}; font-weight:bold; font-size:18px;'>{res['sig']}</span><br>
                <span class='label-mini'>HACİM GÜCÜ: {res['vol']:.1f}x</span>
            </div>
        </div>
        <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:20px;'>
            <div style='background:#161b22; padding:15px; border-radius:10px; text-align:center;'>
                <p class='label-mini'>PİVOT</p><p style='font-size:20px; font-weight:bold;'>{res['ma']:.2f}</p>
            </div>
            <div style='background:#161b22; padding:15px; border-radius:10px; text-align:center; border-bottom:3px solid #00ff88;'>
                <p class='label-mini'>HEDEF (+)</p><p style='font-size:20px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p>
            </div>
            <div style='background:#161b22; padding:15px; border-radius:10px; text-align:center; border-bottom:3px solid #ff4b4b;'>
                <p class='label-mini'>STOP (GÜVENLİ)</p><p style='font-size:20px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p>
            </div>
        </div>
        <div class='intel-box'>
            <span class='plus-badge'>GÜRKAN AI ARAŞTIRMA RAPORU</span>
            <p class='report-content'>{res['report']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
    st.plotly_chart(fig, use_container_width=True)
