import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="Gürkan AI v183", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"

st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; }
    .analysis-card { background: #0d1117; border: 1px solid #1c2128; border-radius: 8px; padding: 20px; border-left: 8px solid #ffcc00; }
    div.stButton > button { background: #111418 !important; color: #8b949e !important; border: 1px solid #1c2128 !important; border-radius: 2px !important; font-size: 10px !important; height: 22px !important; width: 100% !important; }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; }
    .signal-bold { font-size: 24px; font-weight: 900; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SERT ANALİZ MOTORU ---
def get_aggressive_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Kritik Metrikler
        df['MA20'] = df['Close'].rolling(20).mean()
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        rmf = tp * df['Volume']
        pos = rmf.where(tp > tp.shift(1), 0).rolling(14).sum()
        neg = rmf.where(tp < tp.shift(1), 0).rolling(14).sum()
        mfi = 100 - (100 / (1 + pos / neg))
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        cur_mfi = mfi.iloc[-1]; vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # AGRESİF KARAR MEKANİZMASI
        if vol_ratio > 1.8 and ch > 1.5 and cur_mfi < 75:
            sig, clr, com = "HEMEN AL / YÜKLEN", "#00ff88", f"Tahtacı masaya oturdu! {vol_ratio:.1f}x hacim patlaması var. Kağıt direnci parçalıyor, bu trend kaçmaz. GİRİŞ YAP!"
        elif cur_mfi > 82:
            sig, clr, com = "KAÇ / MAL BOŞALT", "#ff4b4b", "Para akışı zirve yaptı, tahtacı elindeki malı devrediyor. Buradan alanı üzerler. DERHAL ÇIK!"
        elif lp > df['MA20'].iloc[-1] and ch > 0 and cur_mfi > 50:
            sig, clr, com = "POZİSYON ARTIR", "#00d4ff", "Trend desteği (MA20) üzerinde mermi tazeliyor. Alıcılar hala iştahlı. Hedef yukarı, EKLEME YAP!"
        elif lp < df['MA20'].iloc[-1] and ch < -1:
            sig, clr, com = "GİRME / UZAK DUR", "#ff4b4b", "Kağıt kan kaybediyor. Destekler kırılmış, alıcılar piyasada yok. Elinde varsa SAT, yoksa BULAŞMA!"
        elif cur_mfi < 30 and ch > -0.5:
            sig, clr, com = "DİPTEN TOPLA", "#ffcc00", "Fiyat ölü taklidi yapıyor ama para girişi sinsice başladı. Tahtacı sessizce mal topluyor. İLK KURŞUNU AT!"
        else:
            sig, clr, com = "BEKLE / TUZAK OLABİLİR", "#8b949e", "Hacim zayıf, yön belirsiz. Sahte hareketlerle küçük yatırımcıyı avlıyorlar. Net bir hacim görmeden kımıldama!"
            
        return {"p": lp, "ch": ch, "sig": sig, "clr": clr, "com": com, "df": df, "mfi": cur_mfi}
    except: return None

# --- 3. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:5px;'>🤵 GÜRKAN AI : AGGRESSIVE TERMINAL</h3>", unsafe_allow_html=True)

# KONTROL
_, mid_search, _ = st.columns([1, 2, 1])
with mid_search:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("SİNYAL ÇAK"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.session_state["last_sorgu"] in st.session_state["favorites"]:
            if st.button("🔴 SİL"): st.session_state["favorites"].remove(st.session_state["last_sorgu"]); st.rerun()
        else:
            if st.button("🟢 EKLE"): st.session_state["favorites"].append(st.session_state["last_sorgu"]); st.rerun()

l, m, r = st.columns([0.7, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>PORTFÖYÜM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_aggressive_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='analysis-card' style='border-left-color: {res['clr']}'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} AGRESİF SİNYAL</span><br>
                    <span style='font-size:38px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:20px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span class='signal-bold' style='color:{res['clr']};'>{res['sig']}</span><br>
                    <span style='color:#4b525d; font-size:11px;'>Para Trafiği: %{res['mfi']:.0f}</span>
                </div>
            </div>
            <div style='margin-top:15px; padding-top:10px; border-top:1px solid #1c2128;'>
                <p style='color:#ffcc00; font-size:12px; font-weight:bold; margin-bottom:5px;'>🤵 GÜRKAN AI TALİMATI:</p>
                <p style='color:#fff; font-size:16px; font-weight:bold;'>"{res['com']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=480, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "KCHOL", "EREGL", "ASELS", "SISE"]:
        st.write(f"<span style='color:#ffcc00; font-size:11px;'>{rs}</span>", unsafe_allow_html=True)
        if st.button("Gözlem", key=f"r_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
    
