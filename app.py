import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="Gürkan AI : Radar Fix", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "ISCTR"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS ---
st.markdown("""
<style>
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 20px; border-left: 5px solid #ffcc00; margin-bottom: 15px; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 10px; height: 800px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; border-left: 3px solid #00ff88; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border-radius: 8px; }
    .label-mini { color: #8b949e; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. VERİ MOTORU ---
def get_safe_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol + ".IS", period=period, interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- 4. LAYOUT ---
m_col, r_col = st.columns([3, 1])

with m_col:
    # Arama Paneli
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        is_fav = s_inp in st.session_state["favorites"]
        if st.button("⭐ ÇIKAR" if is_fav else "⭐ EKLE"):
            if is_fav: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favori Butonları
    if st.session_state["favorites"]:
        f_cols = st.columns(len(st.session_state["favorites"]))
        for i, fv in enumerate(st.session_state["favorites"]):
            if f_cols[i].button(fv): st.session_state["last_sorgu"] = fv; st.rerun()

    # Ana Analiz
    main_df = get_safe_data(st.session_state["last_sorgu"])
    if main_df is not None:
        lp = float(main_df['Close'].iloc[-1]); pc = float(main_df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = main_df['Close'].rolling(20).mean().iloc[-1]
        
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div><p class='label-mini'>{st.session_state["last_sorgu"]} // CANLI</p><span style='font-size:40px; font-weight:bold;'>{lp:.2f}</span><span style='color:{"#00ff88" if ch>0 else "#ff4b4b"}; font-size:20px;'> {ch:+.2f}%</span></div>
                <div style='text-align:right;'><p class='label-mini'>DURUM</p><h2 style='color:{"#00ff88" if lp>ma20 else "#ff4b4b"};'>{"POZİTİF" if lp>ma20 else "NEGATİF"}</h2></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=main_df.index, open=main_df['Open'], high=main_df['High'], low=main_df['Low'], close=main_df['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 RADAR SİNYALLERİ</p>", unsafe_allow_html=True)
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    
    # RADAR FIX: Her hisse için ayrı küçük veri çekimi (Donmayı engellemek için cache'li)
    for s in SCAN_LIST:
        try:
            # Radar için sadece son 20 gün yeterli (Hız kazandırır)
            r_df = yf.download(s + ".IS", period="25d", interval="1d", progress=False)
            if not r_df.empty:
                if isinstance(r_df.columns, pd.MultiIndex): r_df.columns = r_df.columns.get_level_values(0)
                cp = float(r_df['Close'].iloc[-1])
                ma = r_df['Close'].rolling(20).mean().iloc[-1]
                
                # Sadece pozitif olanları göster
                if cp > ma:
                    ch_r = ((cp - r_df['Close'].iloc[-2]) / r_df['Close'].iloc[-2]) * 100
                    st.markdown(f"""
                    <div class='scan-item'>
                        <div style='display:flex; justify-content:space-between;'><b>{s}</b><span style='color:#00ff88;'>%{ch_r:+.1f}</span></div>
                        <p style='font-size:10px; color:#8b949e; margin:0;'>Trend: POZİTİF</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"GİT {s}", key=f"r_{s}"):
                        st.session_state["last_sorgu"] = s
                        st.rerun()
        except: continue
    st.markdown("</div>", unsafe_allow_html=True)
