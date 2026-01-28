import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM & GÜVENLİK ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI EXIT MASTER</h2>", unsafe_allow_html=True)
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Anahtarı Giriniz...")
    if st.button("STRATEJİK MERKEZİ AÇ", use_container_width=True):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. PREMIUM CSS ---
st.set_page_config(page_title="Gürkan AI PRO v150", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #05070a !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #111418 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 8px !important; transition: 0.3s; }
    div.stButton > button:hover { border-color: #ffcc00 !important; box-shadow: 0 0 10px rgba(255,204,0,0.2); }
    .exit-card { background: rgba(255, 75, 75, 0.05); border: 1px solid rgba(255, 75, 75, 0.2); padding: 15px; border-radius: 12px; margin-top: 10px; }
    .stat-label { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    .stat-val { font-size: 18px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA VE SATIŞ MOTORU ---
def get_exit_logic(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 40: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        atr = (df['High'] - df['Low']).tail(14).mean()
        
        # SATIŞ STRATEJİSİ (Planlı Çıkış)
        tp1 = round(lp + (atr * 1.5), 2)  # İlk Kar Al (%30 Satış)
        tp2 = round(lp + (atr * 3.0), 2)  # İkinci Kar Al (%30 Satış)
        tp3 = round(lp + (atr * 5.0), 2)  # Ana Hedef (%40 Satış)
        
        # İz Süren Stop (Kritik Nokta)
        trailing_stop = round(lp - (atr * 1.5), 2)
        
        # Yorulma Analizi (RSI Bazlı)
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        
        if rsi > 75: exit_note = "🚨 DİKKAT: Hisse aşırı alımda (RSI 75+). Plan: Hemen TP1 kademesini sat, nakit oranı artır."
        elif rsi > 65: exit_note = "⚠️ YORULMA: Güç kaybı başlıyor. Plan: Stop seviyesini fiyata yaklaştır, hedefleri bekle."
        else: exit_note = "✅ YOLU VAR: RSI dengeli. Plan: Sabırla kademeli satış noktalarına ulaşılmasını bekle."

        return {"p": lp, "tps": [tp1, tp2, tp3], "ts": trailing_stop, "rsi": rsi, "n": exit_note, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI EXIT MASTER v150</h4>", unsafe_allow_html=True)

_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([4, 1.2, 0.6])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("SATIŞ PLANI"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

col_f, col_m, col_r = st.columns([0.8, 4, 1])

with col_f:
    st.markdown("<p class='stat-label'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        f1, f2 = st.columns([4, 1.2])
        with f1: 
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with f2: 
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_m:
    res = get_exit_logic(st.session_state["last_sorgu"])
    if res:
        # Satış Planı Paneli
        st.markdown(f"""
        <div style='background:#111418; border:1px solid #30363d; padding:20px; border-radius:15px;'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'>
                <span style='font-size:18px; font-weight:bold; color:#ffcc00;'>{st.session_state["last_sorgu"]} KADEMELİ SATIŞ ROTASI</span>
                <span style='color:{"#ff4b4b" if res['rsi']>70 else "#00ff88"}; font-weight:bold;'>GÜÇ: {res['rsi']:.1f}</span>
            </div>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div><p class='stat-label'>MEVCUT</p><p class='stat-val'>{res['p']:.2f}</p></div>
                <div><p class='stat-label'>SATIŞ 1 (%30)</p><p class='stat-val' style='color:#00ff88;'>{res['tps'][0]}</p></div>
                <div><p class='stat-label'>SATIŞ 2 (%30)</p><p class='stat-val' style='color:#00ff88;'>{res['tps'][1]}</p></div>
                <div><p class='stat-label'>ANA HEDEF (%40)</p><p class='stat-val' style='color:#ffcc00;'>{res['tps'][2]}</p></div>
                <div><p class='stat-label' style='color:#ff4b4b;'>İZ SÜREN STOP</p><p class='stat-val' style='color:#ff4b4b;'>{res['ts']}</p></div>
            </div>
            <div class='exit-card'>
                <p style='margin:0; font-size:13px; color:#e1e1e1;'><b>🤵 GÜRKAN AI SATIŞ NOTU:</b> {res['n']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_r:
    st.markdown("<p class='stat-label'>HIZLI RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
