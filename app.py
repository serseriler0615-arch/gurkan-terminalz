import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM & GÜVENLİK ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 2. ELİT GİRİŞ EKRANI ---
if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("""<div style='text-align:center; padding:50px;'>
        <h1 style='color:#ffcc00; font-family:serif; letter-spacing:3px;'>🤵 GÜRKAN AI</h1>
        <p style='color:#8b949e; font-style:italic;'>Piyasanın şifrelerini çözmeye hazır mısın?</p>
    </div>""", unsafe_allow_html=True)
    vk = st.text_input("Giriş Anahtarı", type="password", label_visibility="collapsed", placeholder="Anahtarı Giriniz...")
    if st.button("SİSTEMİ UYANDIR", use_container_width=True):
        if vk.strip().upper() == "HEDEF2026" or vk.startswith("GAI-"):
            st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 3. PREMIUM MATRIX CSS ---
st.set_page_config(page_title="Gürkan AI PRO v148", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #080a0d !important; color: #e1e1e1 !important; }
    
    /* Özel Buton Tasarımı */
    div.stButton > button {
        background: linear-gradient(145deg, #161b22, #0b0d11) !important;
        color: #ffcc00 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
        transition: 0.4s;
    }
    div.stButton > button:hover {
        border-color: #ffcc00 !important;
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.3);
        transform: translateY(-2px);
    }
    
    /* Gürkan AI Özel Kartı */
    .oracle-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255, 204, 0, 0.2);
        padding: 20px;
        border-radius: 20px;
        border-left: 5px solid #ffcc00;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .neon-text { color: #ffcc00; text-shadow: 0 0 10px rgba(255,204,0,0.5); }
    .stat-label { font-size: 10px; color: #8b949e; letter-spacing: 1px; }
    .stat-val { font-size: 20px; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 4. THE ORACLE ANALİZ MOTORU ---
def get_oracle_logic(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); ch = ((lp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # RSI & Güç
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        
        # Karakterli Yorumlar
        if lp > ma20 and rsi < 65:
            n = "Rüzgar arkadan esiyor patron. Teknik olarak her şey yerli yerinde, sakin kalıp trendi izleyelim."
            s, c = "GÜVENLİ LİMAN", "#00ff88"
        elif rsi > 70:
            n = "Hisse biraz fazla ısınmış. Buralarda yeni alım riskli olabilir, kar cebine yakışır mı dersin?"
            s, c = "DİKKAT: SICAK", "#ff4b4b"
        elif lp < ma20:
            n = "Hissede bir durgunluk var. Kendi kabuğuna çekilmiş, desteğe dokunmasını beklemek daha zekice olur."
            s, c = "GÜÇ TOPLUYOR", "#ffcc00"
        else:
            n = "Piyasa kararsız. Net bir yön tayin edene kadar izleme listesinde kalsın."
            s, c = "BEKLEMEDE", "#8b949e"

        up = round((df['Close'].tail(15).std() * 2.5 / lp) * 100, 1)
        return {"p": lp, "ch": ch, "up": max(up, 1.5), "rsi": rsi, "n": n, "c": c, "s": s, "df": df}
    except: return None

# --- 5. ANA EKRAN ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; font-family:serif;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)

# Şık Arama
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([4, 1.2, 0.6])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed", placeholder="Hisse Kodu...").upper().strip()
    with c2: 
        if st.button("ANALİZ", use_container_width=True): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# Gövde
col_f, col_m, col_r = st.columns([0.8, 4, 1])

with col_f:
    st.markdown("<p class='stat-label'>ÖZEL LİSTE</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        f1, f2 = st.columns([4, 1.2])
        with f1: 
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with f2: 
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_m:
    res = get_oracle_logic(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='oracle-card'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>
                <span class='neon-text' style='font-size:18px; font-weight:bold;'>{st.session_state["last_sorgu"]} ANALİZİ</span>
                <span style='background:{res['c']}; color:black; padding:3px 12px; border-radius:30px; font-size:10px; font-weight:bold;'>{res['s']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div><p class='stat-label'>FİYAT</p><p class='stat-val'>{res['p']:.2f}</p></div>
                <div><p class='stat-label'>GÜNLÜK</p><p class='stat-val' style='color:{res['c']};'>{res['ch']:+.2f}%</p></div>
                <div><p class='stat-label'>RSI (14)</p><p class='stat-val'>{res['rsi']:.1f}</p></div>
                <div><p class='stat-label'>HEDEF POTANSİYEL</p><p class='stat-val' style='color:#00ff88;'>+% {res['up']}</p></div>
            </div>
            <div style='margin-top:20px; padding:15px; background:rgba(0,0,0,0.2); border-radius:10px;'>
                <p style='font-size:14px; color:#e1e1e1; margin:0; line-height:1.5;'><b>🤵 Gürkan AI Notu:</b> {res['n']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=15,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9, color='#8b949e')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_r:
    st.markdown("<p class='stat-label'>SICAK RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
