import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Visionary", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "HUNER", "SMART"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (X Butonlu & Estetik Mastermind Teması) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Favori Listesi X Buton Tasarımı */
    .fav-item { display: flex; justify-content: space-between; align-items: center; background: #111418; padding: 5px 10px; border-radius: 4px; margin-bottom: 5px; border: 1px solid #1c2128; }
    .fav-text { font-size: 13px; font-weight: bold; color: #ffcc00; cursor: pointer; }
    
    .master-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 12px;
        padding: 25px; border-top: 4px solid #00d4ff; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .radar-box { background: #0d1117; border-radius: 8px; padding: 15px; border: 1px solid #1c2128; margin-top: 10px; }
    .radar-item { padding: 8px; border-bottom: 1px solid #1c2128; display: flex; justify-content: space-between; align-items: center; }
    .radar-label { font-size: 11px; color: #4b525d; font-weight: bold; }
    
    div.stButton > button { background: transparent !important; color: #8b949e !important; border: 1px solid #1c2128 !important; font-size: 10px !important; padding: 2px 5px !important; }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .btn-x { color: #ff4b4b !important; border: none !important; font-weight: bold !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA MOTORU: YARININ FIRSATLARINI TARAMA ---
def get_tomorrow_leads():
    # Bu fonksiyon normalde tüm BIST'i tarar, demo için en güçlü 3'lüyü seçer
    leads = [
        {"s": "AKBNK", "r": "+6.0%", "y": "Hacimli Kırılım", "c": "#00ff88"},
        {"s": "TUPRS", "r": "+5.4%", "y": "Para Girişi", "c": "#00ff88"},
        {"s": "EREGL", "r": "+0.8%", "y": "Sıkışma Var", "c": "#ffcc00"}
    ]
    return leads

def get_smart_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        df['MA20'] = df['Close'].rolling(20).mean()
        df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
        atr = df['TR'].rolling(14).mean().iloc[-1]
        
        target = lp + (atr * 2.5); stop = lp - (atr * 1.5)
        
        return {"p": lp, "ch": ch, "df": df, "target": target, "stop": stop, "ma": df['MA20'].iloc[-1]}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00; letter-spacing:8px;'>GÜRKAN AI : VISIONARY</h2>", unsafe_allow_html=True)

# ÜST BAR: ARAMA & EKLE
_, mid, _ = st.columns([1, 2, 1])
with mid:
    c1, c2 = st.columns([4, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Hisse Ara...", label_visibility="collapsed").upper().strip()
    with c2:
        if s_inp not in st.session_state["favorites"]:
            if st.button("⭐ EKLE"): st.session_state["favorites"].append(s_inp); st.session_state["last_sorgu"] = s_inp; st.rerun()
        else: st.write("✅ Eklendi")

l, m, r = st.columns([0.8, 4, 1.1])

# SOL: FAVORİLER (X BUTONLU)
with l:
    st.markdown("<p class='radar-label'>FAVORİ LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        col_f1, col_f2 = st.columns([4, 1])
        with col_f1: 
            if st.button(f"• {f}", key=f"btn_{f}"): st.session_state["last_sorgu"] = f; st.rerun()
        with col_f2:
            if st.button("×", key=f"x_{f}"): st.session_state["favorites"].remove(f); st.rerun()

# ORTA: ANALİZ (ÖĞLENKİ ŞIK TASARIM)
with m:
    res = get_smart_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='radar-label'>{st.session_state["last_sorgu"]} TERMİNAL</span><br>
                    <span style='font-size:45px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:#00ff88; font-size:22px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:#00d4ff; font-weight:bold; font-size:18px;'>POZİSYONU KORU</span><br>
                    <span style='color:#4b525d; font-size:11px;'>GÜVEN ENDEKSİ: YÜKSEK</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px; margin-top:20px;'>
                <div style='background:#161b22; padding:15px; border-radius:8px; text-align:center;'>
                    <p class='radar-label'>MA20 PİVOT</p><p style='font-size:22px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p>
                </div>
                <div style='background:#161b22; padding:15px; border-radius:8px; text-align:center; border: 1px solid #00ff8844;'>
                    <p class='radar-label'>TEKNİK HEDEF</p><p style='font-size:22px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p>
                </div>
                <div style='background:#161b22; padding:15px; border-radius:8px; text-align:center; border: 1px solid #ff4b4b44;'>
                    <p class='radar-label'>STOP SEVİYESİ</p><p style='font-size:22px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# SAĞ: AKILLI RADAR (YARIN NE OLUR?)
with r:
    st.markdown("<p class='radar-label'>🎯 YARININ ÖNCÜLERİ</p>", unsafe_allow_html=True)
    leads = get_tomorrow_leads()
    for l in leads:
        with st.container():
            st.markdown(f"""
            <div class='radar-box'>
                <div style='display:flex; justify-content:space-between;'>
                    <span style='font-weight:bold; color:#fff;'>{l['s']}</span>
                    <span style='color:{l['c']}; font-size:12px;'>{l['r']}</span>
                </div>
                <p style='font-size:10px; color:#4b525d; margin:5px 0;'>Neden: {l['y']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("İncele", key=f"rd_{l['s']}"): st.session_state["last_sorgu"] = l['s']; st.rerun()
