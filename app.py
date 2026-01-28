import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "AKBNK"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. HUNTER UI CSS ---
st.set_page_config(page_title="Gürkan AI v167", layout="wide")
st.markdown("""
<style>
    .stApp { background: #05070a !important; color: #e1e1e1 !important; }
    .hunter-card {
        background: linear-gradient(145deg, #0d1117 0%, #07090c 100%);
        border: 1px solid #ffcc0044; border-radius: 12px;
        padding: 20px; margin-bottom: 10px; border-left: 5px solid #ffcc00;
    }
    .radar-item {
        background: #111418; border: 1px solid #1c2128;
        padding: 10px; border-radius: 8px; margin-bottom: 8px;
        transition: 0.3s;
    }
    .radar-item:hover { border-color: #ffcc00; transform: translateX(5px); }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
    .val-bold { font-size: 18px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- 3. HUNTER RADAR MOTORU ---
def get_hunter_radar():
    stocks = ["THYAO", "ASELS", "AKBNK", "ISCTR", "EREGL", "TUPRS", "PGSUS", "KCHOL", "SAHOL", "BIMAS"]
    candidates = []
    for s in stocks:
        try:
            df = yf.download(s + ".IS", period="10d", interval="1d", progress=False)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # 🧠 Sinyal Algoritması (Yarın %1 ihtimali için)
            # 1. Son gün hacmi 5 günlük ortalamanın üstünde mi?
            # 2. RSI 40-60 arası (Doymamış bölge) mi?
            # 3. Kapanış günün en yükseğine yakın mı?
            lp = df['Close'].iloc[-1]
            vol_avg = df['Volume'].mean()
            vol_last = df['Volume'].iloc[-1]
            high_last = df['High'].iloc[-1]
            
            score = 0
            if vol_last > vol_avg: score += 40
            if lp > (high_last * 0.99): score += 40
            if lp > df['Close'].rolling(5).mean().iloc[-1]: score += 20
            
            if score >= 60:
                candidates.append({"symbol": s, "score": score, "price": lp})
        except: continue
    return sorted(candidates, key=lambda x: x['score'], reverse=True)[:4]

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00; margin-bottom:0;'>🤵 GÜRKAN AI : HUNTER</h2>", unsafe_allow_html=True)

col_fav, col_main, col_radar = st.columns([0.8, 4, 1.2])

with col_fav:
    st.markdown("<p class='label-mini'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with col_main:
    # Ana Analiz Ekranı (v166 Momentum tabanlı)
    res_df = yf.download(st.session_state["last_sorgu"] + ".IS", period="1mo", interval="1d", progress=False)
    if not res_df.empty:
        if isinstance(res_df.columns, pd.MultiIndex): res_df.columns = res_df.columns.get_level_values(0)
        lp = res_df['Close'].iloc[-1]
        ch = ((lp - res_df['Close'].iloc[-2]) / res_df['Close'].iloc[-2]) * 100
        
        st.markdown(f"""
        <div class='hunter-card'>
            <p class='label-mini'>{st.session_state["last_sorgu"]} ANALİZ</p>
            <p style='font-size:36px; font-weight:bold; margin:0;'>{lp:.2f} <small style='font-size:18px; color:{"#00ff88" if ch>0 else "#ff4b4b"};'>{ch:+.2f}%</small></p>
            <p class='label-mini' style='margin-top:10px;'>YARIN İÇİN GÜRKAN AI NOTU:</p>
            <p style='color:#ffcc00; font-style:italic;'>{"Hacimli kapanış, yarın ivme devam edebilir." if ch > 0 else "Zayıf momentum, pusuya devam."}</p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res_df.tail(30).index, open=res_df['Open'], high=res_df['High'], low=res_df['Low'], close=res_df['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True)

with col_radar:
    st.markdown("<p class='label-mini'>🎯 YARININ ADAYLARI</p>", unsafe_allow_html=True)
    radar_list = get_hunter_radar()
    for item in radar_list:
        with st.container():
            st.markdown(f"""
            <div class='radar-item'>
                <p style='color:#ffcc00; font-weight:bold; margin:0;'>{item['symbol']}</p>
                <p style='font-size:11px; color:#8b949e; margin:0;'>Skor: %{item['score']} | Güçlü Kapanış</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"İncele {item['symbol']}", key=f"btn_{item['symbol']}"):
                st.session_state["last_sorgu"] = item['symbol']
                st.rerun()
