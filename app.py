import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Engine v224", layout="wide", initial_sidebar_state="collapsed")

# Session State Yönetimi (Hata Önleyici)
if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS (Ultra Speed Optimized) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 20px; border-top: 4px solid #ffcc00; margin-bottom: 15px; }
    .strategy-box { background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 10px; height: 750px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #30363d; font-size: 13px; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 8px; font-weight: bold; width: 100%; height: 35px; }
</style>
""", unsafe_allow_html=True)

# --- 3. GÜÇLENDİRİLMİŞ ANALİZ MOTORU ---
@st.cache_data(ttl=60) # 1 dakikalık cache ile hızlandırma
def get_data(symbol):
    try:
        data = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if data.empty: return None
        # MultiIndex sütun hatasını temizle
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except:
        return None

def analyze_logic(df):
    try:
        lp = float(df['Close'].iloc[-1])
        pc = float(df['Close'].iloc[-2])
        ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = (100 - (100 / (1 + gain/loss))).iloc[-1]
        
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        status = "NÖTR"; col = "#8b949e"
        if lp > ma20 and vol_r > 1.1 and rsi < 65: status = "GÜÇLÜ"; col = "#00ff88"
        elif lp < ma20: status = "ZAYIF"; col = "#ff4b4b"
        elif rsi > 70: status = "ŞİŞMİŞ"; col = "#ffcc00"
        
        return {"p": lp, "ch": ch, "ma": ma20, "rsi": rsi, "vol": vol_r, "status": status, "col": col, "atr": atr}
    except:
        return None

# --- 4. UI TASARIMI ---
m_col, r_col = st.columns([3, 1])

with m_col:
    # Arama Paneli
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: s_inp = st.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ"): 
            st.session_state["last_sorgu"] = s_inp
            st.rerun()
    with c3:
        if st.button("⭐ FAVORİ"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favori Butonları
    if st.session_state["favorites"]:
        favs = st.session_state["favorites"]
        f_cols = st.columns(len(favs))
        for i, f in enumerate(favs):
            if f_cols[i].button(f):
                st.session_state["last_sorgu"] = f
                st.rerun()

    # Ana Analiz Ekranı
    df = get_data(st.session_state["last_sorgu"])
    if df is not None:
        res = analyze_logic(df)
        if res:
            st.markdown(f"""
            <div class='master-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <p class='label-mini'>{st.session_state["last_sorgu"]} // SON FİYAT</p>
                        <span style='font-size:38px; font-weight:bold;'>{res['p']:.2f}</span>
                        <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:18px;'> {res['ch']:+.2f}%</span>
                    </div>
                    <div style='text-align:right;'>
                        <p class='label-mini'>SİNYAL</p>
                        <h2 style='color:{res['col']}; margin:0;'>{res['status']}</h2>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class='strategy-box'>
                <p class='label-mini'>GÜRKAN STRATEJİ</p>
                <p style='font-size:14px; margin:5px 0;'>Hedef: <b>{res['p']+(res['atr']*2.5):.2f}</b> | Stop: <b>{res['p']-(res['atr']*1.5):.2f}</b></p>
                <p style='font-size:12px; color:#8b949e;'>RSI: {res['rsi']:.1f} | Hacim: {res['vol']:.1f}x | Pivot: {res['ma']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Veri çekilemedi. Lütfen sembolü (örn: THYAO) kontrol et veya internet bağlantısını bak.")

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 HIZLI RADAR</p>", unsafe_allow_html=True)
    container = st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    
    # Radar Döngüsü - Basit ve Hızlı
    for s in SCAN_LIST:
        try:
            r_df = get_data(s)
            if r_df is not None:
                r_res = analyze_logic(r_df)
                if r_res and r_res['status'] == "GÜÇLÜ":
                    st.markdown(f"""
                    <div class='scan-item'>
                        <div style='display:flex; justify-content:space-between;'>
                            <b style='color:#ffcc00;'>{s}</b>
                            <span style='color:#00ff88;'>%{r_res['ch']:+.1f}</span>
                        </div>
                        <div style='font-size:10px; color:#8b949e;'>Hacim: {r_res['vol']:.1f}x | RSI: {r_res['rsi']:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"GİT {s}", key=f"r_{s}"):
                        st.session_state["last_sorgu"] = s
                        st.rerun()
        except: continue
    st.markdown("</div>", unsafe_allow_html=True)
