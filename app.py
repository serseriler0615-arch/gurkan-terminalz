import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Turbo v225", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "EREGL", "TUPRS"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

# Radar için ana hisse listesi
SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 20px; border-left: 5px solid #ffcc00; margin-bottom: 15px; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 10px; height: 800px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border-radius: 8px; font-weight: bold; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
@st.cache_data(ttl=300)
def get_bulk_data(symbols):
    # Tüm listeyi tek seferde çekiyoruz (Hızın anahtarı bu!)
    tickers = [s + ".IS" for s in symbols]
    data = yf.download(tickers, period="40d", interval="1d", progress=False, group_by='ticker')
    return data

def single_analyze(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # RSI Basit
        delta = df['Close'].diff(); gain = delta.where(delta > 0, 0).rolling(14).mean(); loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = (100 - (100 / (1 + gain/loss))).iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        status = "POZİTİF" if lp > ma20 else "NEGATİF"
        col = "#00ff88" if lp > ma20 else "#ff4b4b"
        
        return {"p": lp, "ch": ch, "ma": ma20, "rsi": rsi, "vol": vol_r, "status": status, "col": col, "df": df, "atr": atr}
    except: return None

# --- 4. LAYOUT ---
m_col, r_col = st.columns([3, 1])

with m_col:
    # Arama
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("⭐ FAVORİ"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favoriler
    if st.session_state["favorites"]:
        f_cols = st.columns(len(st.session_state["favorites"]))
        for i, f in enumerate(st.session_state["favorites"]):
            if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

    # Analiz Paneli
    res = single_analyze(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]} // CANLI</p>
                    <span style='font-size:40px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{res['col']}; font-size:20px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini'>DURUM</p>
                    <h2 style='color:{res['col']}; margin:0;'>{res['status']}</h2>
                </div>
            </div>
            <div style='display:flex; gap:20px; margin-top:15px; font-size:13px; color:#8b949e;'>
                <span>RSI: <b>{res['rsi']:.1f}</b></span>
                <span>HACİM: <b>{res['vol']:.1f}x</b></span>
                <span>PİVOT: <b>{res['ma']:.2f}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 RADAR SİNYALLERİ</p>", unsafe_allow_html=True)
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    
    # Radar Veri İşleme
    bulk_data = get_bulk_data(SCAN_LIST)
    for s in SCAN_LIST:
        try:
            ticker_data = bulk_data[s + ".IS"]
            # Eğer veri MultiIndex geldiyse düzelt
            if isinstance(ticker_data, pd.DataFrame):
                cp = ticker_data['Close'].iloc[-1]
                pc = ticker_data['Close'].iloc[-2]
                ch = ((cp-pc)/pc)*100
                ma = ticker_data['Close'].rolling(20).mean().iloc[-1]
                
                # Radar kriteri: Trend pozitifse listele
                if cp > ma:
                    st.markdown(f"""
                    <div class='scan-item'>
                        <div style='display:flex; justify-content:space-between;'>
                            <b style='color:#ffcc00;'>{s}</b>
                            <span style='color:#00ff88;'>%{ch:+.1f}</span>
                        </div>
                        <p style='font-size:10px; color:#8b949e; margin:5px 0;'>Trend Pozitif (MA20 Üstü)</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"GİT {s}", key=f"r_{s}"):
                        st.session_state["last_sorgu"] = s
                        st.rerun()
        except: continue
    st.markdown("</div>", unsafe_allow_html=True)
