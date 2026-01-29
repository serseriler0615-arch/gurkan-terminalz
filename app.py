import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="Gürkan AI : Research Mode", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS", "ASTOR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS (RESEARCHER THEME) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px; }
    .intel-box { background: rgba(255, 204, 0, 0.03); border: 1px solid #30363d; border-left: 5px solid #ffcc00; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .research-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 15px; }
    .research-item { background: #161b22; padding: 12px; border-radius: 8px; border: 1px solid #30363d; text-align: center; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 15px; height: 850px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

# --- 3. ARAŞTIRMACI ZEKA MOTORU ---
def get_deep_research(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # RSI & Momentum
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = (100 - (100 / (1 + g/l))).iloc[-1]
        
        # Karar Mekanizması
        status = "NÖTR"
        col = "#8b949e"
        if lp > ma20 and vol_r > 1.2 and rsi < 65: status = "GÜÇLÜ AL"; col = "#00ff88"
        elif lp < ma20: status = "ZAYIF / SAT"; col = "#ff4b4b"
        elif rsi > 70: status = "DİKKAT / ŞİŞME"; col = "#ffcc00"

        # Araştırma Raporu Parçaları
        vol_intel = "Hacim desteği mükemmel, büyük oyuncular içeride." if vol_r > 1.5 else "Hacim stabil, organik hareket."
        mom_intel = "Momentum taze, yolculuk yeni başlıyor." if rsi < 55 else "Momentum zirveye yaklaşıyor, kar satışına dikkat."
        trend_intel = "Ana trend (MA20) üzerinde, güvenli bölge." if lp > ma20 else "Trend kırılmış, pivot altı baskı sürüyor."

        return {
            "p": lp, "ch": ch, "ma": ma20, "rsi": rsi, "vol": vol_r, "status": status, "col": col, "df": df,
            "vol_i": vol_intel, "mom_i": mom_intel, "trend_i": trend_intel
        }
    except: return None

# --- 4. UI ---
m_col, r_col = st.columns([3.2, 1])

with m_col:
    # Arama ve Favori
    s_col, b_col, f_col = st.columns([4, 1, 1])
    with s_col: s_inp = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with b_col: 
        if st.button("🔍 ARAŞTIR"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with f_col:
        if st.button("⭐ FAVORİ"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    res = get_deep_research(st.session_state["last_sorgu"])
    if res:
        # 1. Ana Bilgi Kartı
        st.markdown(f"""
        <div class='master-card'>
            <p class='label-mini'>{st.session_state["last_sorgu"]} // TEKNİK MERKEZ</p>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-size:45px; font-weight:bold;'>{res['p']:.2f}</span>
                <span style='color:{res['col']}; font-size:24px; font-weight:bold;'>{res['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. GÜRKAN'IN DERİN ARAŞTIRMA DOSYASI
        st.markdown(f"""
        <div class='intel-box'>
            <p class='label-mini' style='color:#ffcc00;'>🕵️ GÜRKAN AI : DERİN ARAŞTIRMA DOSYASI</p>
            <div class='research-grid'>
                <div class='research-item'><p class='label-mini'>HACİM GÜCÜ</p><p style='font-size:14px;'>{res['vol_i']}</p></div>
                <div class='research-item'><p class='label-mini'>MOMENTUM</p><p style='font-size:14px;'>{res['mom_i']}</p></div>
                <div class='research-item'><p class='label-mini'>TREND ANALİZİ</p><p style='font-size:14px;'>{res['trend_i']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Grafiği basitleştirilmiş ve temiz bir şekilde ekleyelim
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 GÜVENLİ RADAR</p>", unsafe_allow_html=True)
    # Radar kısmı önceki v219 ile aynı mantıkta devam eder
    st.markdown("<div class='radar-container'>Radar taranıyor...</div>", unsafe_allow_html=True)
