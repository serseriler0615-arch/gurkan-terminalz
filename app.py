import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Sistem Anahtarı...")
    if st.button("TERMİNALİ AÇ"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. ARCHITECT UI CSS ---
st.set_page_config(page_title="Gürkan AI v158", layout="wide")
st.markdown("""
<style>
    .stApp { background: #05070a !important; color: #e1e1e1 !important; }
    
    /* Panel Tasarımları */
    .report-card {
        background: #0d1117; border: 1px solid #30363d; border-radius: 10px;
        padding: 15px; margin-bottom: 10px;
    }
    
    .ai-box {
        background: rgba(255, 204, 0, 0.03);
        border-left: 5px solid #ffcc00;
        padding: 15px; border-radius: 4px;
        margin: 10px 0;
    }

    /* Butonlar */
    div.stButton > button {
        background: #161b22 !important; color: #ffcc00 !important;
        border: 1px solid #30363d !important; border-radius: 6px !important;
        font-size: 12px !important; transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; background: #1c2128 !important; }

    .label { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .value { font-size: 18px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA VE VERİ MOTORU ---
def get_architect_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # Teknik Göstergeler
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # Zeka Skoru & Yorum
        score = 0
        if lp > ma20: score += 40
        if 45 < rsi < 65: score += 30
        if df['Volume'].iloc[-1] > df['Volume'].tail(10).mean(): score += 30
        
        if score >= 75: thought = f"🚀 **Trend Güçlü:** {lp} üzerinde kalıcılık ivmeyi artırır. Hacim onayı var."
        elif score >= 45: thought = f"⚖️ **Yatay Bekleyiş:** RSI {rsi:.1f} ile dengede. Belirgin bir yön kırılımı beklenmeli."
        else: thought = f"⚠️ **Zayıf Sinyal:** Satış baskısı hakim. Destek bölgelerine kadar nakit korumak mantıklı."

        std = df['Close'].tail(20).std()
        return {"p": lp, "ch": ch, "rsi": rsi, "score": score, "h": lp+(std*1.8), "l": lp-(std*1.8), "thought": thought, "df": df}
    except: return None

# --- 4. ARAYÜZ (ARCHITECT LAYOUT) ---
st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI</h2>", unsafe_allow_html=True)

# Üst Arama ve Favori Ekleme
_, mid, _ = st.columns([1, 2, 1])
with mid:
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ ET", use_container_width=True): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕ EKLE", use_container_width=True):
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# Ana Panel
col_side, col_main, col_radar = st.columns([0.8, 4, 0.8])

with col_side:
    st.markdown("<p class='label'>FAVORİLERİM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        fc1, fc2 = st.columns([3, 1])
        if fc1.button(f, key=f"fav_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        if fc2.button("X", key=f"del_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_architect_data(st.session_state["last_sorgu"])
    if res:
        # 1. RAPOR KARTI
        st.markdown(f"""
        <div class='report-card'>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div style='flex:1;'><p class='label'>FİYAT / %</p><p class='value'>{res['p']:.2f} <small style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"};'>({res['ch']:+.2f}%)</small></p></div>
                <div style='flex:1;'><p class='label'>ZEKA SKORU</p><p class='value' style='color:#ffcc00;'>%{res['score']}</p></div>
                <div style='flex:1;'><p class='label'>RSI</p><p class='value'>{res['rsi']:.1f}</p></div>
                <div style='flex:1;'><p class='label'>ÜST HEDEF</p><p class='value' style='color:#00ff88;'>{res['h']:.2f}</p></div>
                <div style='flex:1;'><p class='label'>ALT DESTEK</p><p class='value' style='color:#ff4b4b;'>{res['l']:.2f}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. GÜRKAN AI STRATEJİK YORUM
        st.markdown(f"""
        <div class='ai-box'>
            <span style='color:#ffcc00; font-weight:bold; font-size:11px;'>🤵 GÜRKAN AI STRATEJİK ANALİZ</span><br>
            <span style='font-size:14px;'>{res['thought']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. GRAFİK
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_radar:
    st.markdown("<p class='label'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"rad_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
