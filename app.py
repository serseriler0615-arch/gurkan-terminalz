import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM VE HAFIZA ---
st.set_page_config(page_title="Gürkan AI v176", layout="wide", initial_sidebar_state="collapsed")

if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]

# --- 2. CSS (Mükemmel Siyah & Mikro Kontroller) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Input Alanı */
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; }
    
    /* Strateji Kartı */
    .strategy-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 6px;
        padding: 15px; margin-bottom: 10px; border-top: 3px solid #ffcc00;
    }
    
    /* MİKRO BUTONLAR */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 2px !important;
        font-size: 10px !important; padding: 2px 5px !important; height: 22px !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    
    .label-mini { color: #4b525d; font-size: 9px; text-transform: uppercase; letter-spacing: 1.5px; }
    .signal-text { font-weight: bold; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA MOTORU (DERİN ANALİZ) ---
def get_director_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Teknik Hesaplar
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / 
                                      -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean())))
        
        lp = df['Close'].iloc[-1]; pc = df['Close'].iloc[-2]; ch = ((lp-pc)/pc)*100
        rsi = df['RSI'].iloc[-1]; ma20 = df['MA20'].iloc[-1]
        
        # Karar Yapısı
        if lp > ma20 and rsi < 60:
            sig, clr, com = "GÜÇLÜ AL", "#00ff88", "Hacim ve momentum destekli. Piyasa yapıcı mal topluyor, trend yukarı."
        elif rsi > 70:
            sig, clr, com = "DİKKAT: SAT", "#ffcc00", "Fiyat aşırı şişti (RSI 70+). Kar satışı kapıda, yeni giriş riskli."
        elif lp < ma20:
            sig, clr, com = "ZAYIF / İZLE", "#ff4b4b", "Destek seviyesi altında. Satış baskısı devam ediyor, bulaşma."
        else:
            sig, clr, com = "NÖTR", "#8b949e", "Kararsız bölge. Önemli bir haber akışı beklemek daha güvenli."
            
        return {"p": lp, "ch": ch, "sig": sig, "clr": clr, "com": com, "df": df, "rsi": rsi}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='text-align:center; color:#ffcc00; letter-spacing:4px;'>GÜRKAN AI : THE DIRECTOR</h4>", unsafe_allow_html=True)

# ARAMA VE EKLE/ÇIKAR
_, mid_search, _ = st.columns([1, 2, 1])
with mid_search:
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.session_state["last_sorgu"] in st.session_state["favorites"]:
            if st.button("ÇIKAR", type="secondary"): 
                st.session_state["favorites"].remove(st.session_state["last_sorgu"])
                st.rerun()
        else:
            if st.button("EKLE", type="primary"):
                st.session_state["favorites"].append(st.session_state["last_sorgu"])
                st.rerun()

l, m, r = st.columns([0.6, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_director_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='strategy-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} TERMİNAL</span><br>
                    <span style='font-size:32px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:16px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span class='signal-text' style='color:{res['clr']};'>{res['sig']}</span>
                    <p class='label-mini' style='margin-top:5px;'>RSI: {res['rsi']:.1f}</p>
                </div>
            </div>
            <div style='margin-top:10px; padding-top:10px; border-top:1px solid #1c2128;'>
                <p style='color:#ffcc00; font-size:11px; font-weight:bold; margin-bottom:4px;'>DIRECTOR'S NOTE:</p>
                <p style='color:#e1e1e1; font-style:italic; font-size:13px;'>"{res['com']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=480, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#0d1117', tickfont=dict(color='#30363d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>DURUM RADARI</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "K
