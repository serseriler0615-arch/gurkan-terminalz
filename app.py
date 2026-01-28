import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI v179", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"

st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; font-size: 16px; }
    .analysis-card { background: #0d1117; border: 1px solid #1c2128; border-radius: 8px; padding: 20px; border-left: 5px solid #ffcc00; }
    div.stButton > button { background: #111418 !important; color: #8b949e !important; border: 1px solid #1c2128 !important; border-radius: 2px !important; font-size: 10px !important; height: 22px !important; width: 100% !important; }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
</style>
""", unsafe_allow_html=True)

# --- 2. INSIDER ANALİZ MOTORU ---
def get_insider_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Teknik Veriler
        df['MA20'] = df['Close'].rolling(20).mean()
        df['Vol_Avg'] = df['Volume'].rolling(10).mean()
        
        lp = float(df['Close'].iloc[-1])
        pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        vol_ratio = df['Volume'].iloc[-1] / df['Vol_Avg'].iloc[-1] # Hacim Patlaması
        
        # ANALİZ MANTIĞI (SALAKLIKTAN KURTARILMIŞ)
        if vol_ratio > 2 and ch > 2:
            sig, clr, com = "JOKER ETKİSİ", "#ffcc00", "Hacim normalin 2 katı! Büyük bir fon veya tahtacı kağıda daldı. Akbank misali direnç falan dinlemez, momentumun peşine takılma zamanı."
        elif ch > 0 and vol_ratio < 0.5:
            sig, clr, com = "SUNİ YÜKSELİŞ", "#8b949e", "Fiyat artıyor ama hacim yok. Kimse kağıdı desteklemiyor, mal boşaltıyor olabilirler. Dikkatli ol, geri çekilme sert olur."
        elif ch < -2 and vol_ratio > 1.5:
            sig, clr, com = "PANİK SATIŞI", "#ff4b4b", "Hacimli düşüş var. Küçük yatırımcı dökülüyor ya da birileri büyük çıkış yapıyor. Tabanda güç toplamasını beklemeden girme."
        elif lp > df['MA20'].iloc[-1] and ch > 0:
            sig, clr, com = "TREND ONAYI", "#00ff88", "MA20 üzerinde kalıcıyız. Piyasa yapıcı kağıdı dinlendirerek yukarı taşıyor. Sakin ve sabırlı olan kazanır."
        else:
            sig, clr, com = "YATAY TESTERE", "#4b525d", "Kağıt testere modunda. Aşağı yukarı sert hareketlerle stop patlatıyorlar. Belirgin bir hacim gelmeden pozisyon açma."
            
        return {"p": lp, "ch": ch, "sig": sig, "clr": clr, "com": com, "df": df, "vol": vol_ratio}
    except: return None

# --- 3. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:5px;'>🤵 GÜRKAN AI : INSIDER TERMINAL</h3>", unsafe_allow_html=True)

# ARAMA VE FAVORİ (Gelişmiş)
_, mid_search, _ = st.columns([1, 2, 1])
with mid_search:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.session_state["last_sorgu"] in st.session_state["favorites"]:
            if st.button("🔴 LİSTEDEN SİL"): st.session_state["favorites"].remove(st.session_state["last_sorgu"]); st.rerun()
        else:
            if st.button("🟢 LİSTEYE EKLE"): st.session_state["favorites"].append(st.session_state["last_sorgu"]); st.rerun()

l, m, r = st.columns([0.7, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"fav_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_insider_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='analysis-card' style='border-left-color: {res['clr']}'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} INSIDER RAPORU</span><br>
                    <span style='font-size:36px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:20px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:{res['clr']}; font-weight:bold; font-size:18px;'>{res['sig']}</span><br>
                    <span style='color:#4b525d; font-size:11px;'>Hacim Gücü: {res['vol']:.1f}x</span>
                </div>
            </div>
            <div style='margin-top:15px; padding-top:10px; border-top:1px solid #1c2128;'>
                <p style='color:#ffcc00; font-size:12px; font-weight:bold; margin-bottom:5px;'>🤵 TAHTA ANALİZİ / YORUM:</p>
                <p style='color:#e1e1e1; font-style:italic; font-size:14px; line-height:1.6;'>"{res['com']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=500, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>PİYASA RADARI</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "KCHOL", "SAHOL", "PGSUS", "SISE"]:
        st.write(f"<span style='font-size:11px; color:#ffcc00;'>{rs}</span>", unsafe_allow_html=True)
        if st.button("İncele", key=f"rad_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
