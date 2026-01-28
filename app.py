import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. GLOBAL AYARLAR ---
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; }
    
    /* STRATEJİ KARTLARI */
    .strategy-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 6px;
        padding: 15px; margin-bottom: 10px; border-left: 5px solid #ffcc00;
    }
    .signal-box { padding: 5px 15px; border-radius: 4px; font-weight: bold; font-size: 14px; display: inline-block; }
    
    /* MİKRO BUTONLAR */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 2px !important;
        font-size: 10px !important; padding: 2px 5px !important; height: 22px !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
</style>
""", unsafe_allow_html=True)

if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"

# --- 2. ZEKA VE SİNYAL MOTORU ---
def get_tactical_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Gösterge Hesapları
        df['MA20'] = df['Close'].rolling(20).mean()
        df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / 
                                      -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean())))
        
        lp = df['Close'].iloc[-1]
        pc = df['Close'].iloc[-2]
        ch = ((lp - pc) / pc) * 100
        rsi = df['RSI'].iloc[-1]
        ma = df['MA20'].iloc[-1]
        
        # AL-SAT KARAR MEKANİZMASI
        if lp > ma and rsi < 65:
            signal = "GÜÇLÜ AL"; clr = "#00ff88"; comment = "Trend üzerinde, hacim destekli yükseliş bekliyorum. Hedef %2-3."
        elif lp < ma and rsi > 35:
            signal = "ZAYIF / SAT"; clr = "#ff4b4b"; comment = "Destek kırıldı, baskı artabilir. İzlemede kalmak mantıklı."
        elif rsi > 70:
            signal = "AŞIRI ALIM / DİKKAT"; clr = "#ffcc00"; comment = "Fiyat şişti, kar realizasyonu gelebilir. Yeni alım riskli."
        else:
            signal = "NÖTR / BEKLE"; clr = "#8b949e"; comment = "Yön belirsiz. Önemli bir kırılım bekleniyor."
            
        return {"p": lp, "ch": ch, "sig": signal, "clr": clr, "com": comment, "df": df, "rsi": rsi}
    except: return None

# --- 3. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; font-weight:lighter; letter-spacing:4px;'>🤵 GÜRKAN AI ORACLE</h3>", unsafe_allow_html=True)

_, mid_s, _ = st.columns([1.5, 1, 1.5])
with mid_s:
    c_in, c_ok = st.columns([4, 1])
    with c_in: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c_ok: 
        if st.button("SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()

l, m, r = st.columns([0.7, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>LİSTEM</p>", unsafe_allow_html=True)
    for f in ["THYAO", "AKBNK", "ISCTR", "EREGL", "ASELS"]:
        if st.button(f, key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_tactical_analysis(st.session_state["last_sorgu"])
    if res:
        # STRATEJİ VE YORUM PANALİ
        st.markdown(f"""
        <div class='strategy-card' style='border-left-color: {res['clr']};'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} TERMİNAL</span><br>
                    <span style='font-size:32px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:18px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <div class='signal-box' style='background:{res['clr']}22; color:{res['clr']}; border:1px solid {res['clr']};'>
                        {res['sig']}
                    </div>
                    <p class='label-mini' style='margin-top:10px;'>RSI: {res['rsi']:.1f}</p>
                </div>
            </div>
            <div style='margin-top:15px; padding-top:10px; border-top:1px solid #1c2128;'>
                <span style='color:#ffcc00; font-size:12px; font-weight:bold;'>🤵 AI YORUMU:</span>
                <p style='color:#e1e1e1; font-style:italic; margin:0; font-size:14px;'>"{res['com']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR SİNYAL</p>", unsafe_allow_html=True)
    for rd in ["TUPRS", "KCHOL", "SAHOL", "PGSUS", "SISE"]:
        st.markdown(f"<div style='margin-bottom:2px;'><span style='color:#ffcc00; font-size:11px; font-weight:bold;'>{rd}</span></div>", unsafe_allow_html=True)
        if st.button("İncele", key=f"r_{rd}"): st.session_state["last_sorgu"] = rd; st.rerun()
