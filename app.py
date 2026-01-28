import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI v170", layout="wide", initial_sidebar_state="collapsed")

if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 2. KUSURSUZ OBSIDIAN CSS (Sıfır Beyazlık, Keskin Hatlar) ---
st.markdown("""
<style>
    /* Saf Karanlık Arkaplan */
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Input Alanı */
    .stTextInput>div>div>input {
        background: #0d1117 !important; color: #ffcc00 !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
        text-align: center; font-family: monospace;
    }

    /* Ana Kart Tasarımı */
    .status-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 8px;
        padding: 15px; margin-bottom: 15px; border-top: 3px solid #ffcc00;
    }

    /* MİKRO BUTONLAR (Senin İstediğin Küçüklükte) */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 3px !important;
        font-size: 10px !important; padding: 2px 8px !important;
        min-height: 22px !important; height: 22px !important; width: auto !important;
        transition: 0.2s; display: block; margin: 0 auto;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }

    /* Radar ve Liste Yazıları */
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 5px; }
    .radar-box { background: #080a0d; border-bottom: 1px solid #161b22; padding: 6px 0; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ FONKSİYONU ---
def get_clean_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="3mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        lp = df['Close'].iloc[-1]
        pc = df['Close'].iloc[-2]
        ch = ((lp - pc) / pc) * 100
        return {"p": lp, "ch": ch, "df": df}
    except: return None

# --- 4. RADAR VERİSİ ---
def get_radar_list():
    stocks = ["THYAO", "ASELS", "AKBNK", "ISCTR", "EREGL", "TUPRS", "KCHOL"]
    res = []
    for s in stocks:
        try:
            d = yf.download(s + ".IS", period="2d", progress=False)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            c = ((d['Close'].iloc[-1] - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
            res.append({"s": s, "ch": c})
        except: continue
    return res

# --- 5. ARAYÜZ YERLEŞİMİ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:4px; font-weight:lighter;'>GÜRKAN AI</h3>", unsafe_allow_html=True)

# ARAMA BARI (Orta Üst)
_, mid_search, _ = st.columns([1.5, 1, 1.5])
with mid_search:
    c_in, c_ok = st.columns([3, 1])
    with c_in: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c_ok: 
        if st.button("OK", use_container_width=True): 
            st.session_state["last_sorgu"] = s_inp
            st.rerun()

# ANA SÜTUNLAR
col_list, col_chart, col_radar = st.columns([0.7, 4, 0.8])

with col_list:
    st.markdown("<p class='label-mini'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"fav_{f}", use_container_width=True):
            st.session_state["last_sorgu"] = f
            st.rerun()

with col_chart:
    res = get_clean_data(st.session_state["last_sorgu"])
    if res:
        # Özet Kartı
        st.markdown(f"""
        <div class='status-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span style='color:#8b949e; font-size:12px;'>{st.session_state["last_sorgu"]}</span><br>
                    <span style='font-size:32px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:18px; margin-left:10px;'>{res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini' style='margin:0;'>DURUM</p>
                    <p style='color:#ffcc00; font-weight:bold; font-size:14px; margin:0;'>{"MOMENTUM OK" if res['ch'] > 0 else "İZLEMEDE"}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df'].index, close=res['df']['Close'])])
        fig.update_layout(height=500, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')),
                          xaxis=dict(gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_radar:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    radar_items = get_radar_list()
    for r in radar_items:
        st.markdown(f"""
        <div class='radar-box'>
            <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
                <span style='color:#ffcc00; font-size:11px;'>{r['s']}</span>
                <span style='color:{"#00ff88" if r['ch']>0 else "#ff4b4b"}; font-size:10px;'>{r['ch']:+.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("İncele", key=f"rad_{r['s']}"):
            st.session_state["last_sorgu"] = r['s']
            st.rerun()
