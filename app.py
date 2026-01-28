import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & HAFIZA ---
st.set_page_config(page_title="Gürkan AI : Mastermind", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "HUNER", "SMART"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (Öğlenki O Şık Tasarımın Gelişmiş Hali) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; font-size: 18px; border-radius: 4px; }
    
    .master-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 8px;
        padding: 24px; border-top: 4px solid #00d4ff; margin-bottom: 20px;
    }
    
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
        font-size: 11px !important; height: 26px !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
    .metric-box { background: #161b22; padding: 12px; border-radius: 6px; border: 1px solid #21262d; text-align: center; }
    .metric-val { font-family: 'Courier New', monospace; font-size: 22px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. AKILLI ANALİZ MOTORU ---
def get_mastermind_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Matematiksel Zeka (ATR & Trend)
        df['MA20'] = df['Close'].rolling(20).mean()
        df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
        df['ATR'] = df['TR'].rolling(14).mean()
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        atr = float(df['ATR'].iloc[-1]); ma20 = float(df['MA20'].iloc[-1])
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]

        # Dinamik Hedef/Stop (Zeka Buradan Geliyor)
        target = lp + (atr * 2.1)
        stop = lp - (atr * 1.5)
        
        # KARAR VE STRATEJİK RAPOR
        if lp > ma20 and vol_ratio > 1.5:
            sig, clr, com = "GÜÇLÜ AL / MOMENTUM", "#00ff88", f"Tahtada agresif alıcılar devrede. Hacim normalin {vol_ratio:.1f} katı. Fiyat MA20 ({ma20:.2f}) üzerinde kaldığı sürece ana hedef {target:.2f} seviyesidir. Trende eşlik edilmeli."
        elif lp < ma20 and vol_ratio > 1.2:
            sig, clr, com = "ZAYIF / SATIŞ BASKISI", "#ff4b4b", f"20 günlük kritik eşik kırıldı. Tahtacı mal boşaltıyor. {stop:.2f} altındaki kapanışlar satışı hızlandırır. Şu aşamada izlemek en doğrusu."
        elif lp > ma20:
            sig, clr, com = "POZİSYONU KORU", "#00d4ff", f"Trend kanalı içinde sağlıklı bir konsolidasyon mevcut. Ani bir hacim girişi direnci kırabilir. {ma20:.2f} desteği ana pivot noktamız."
        else:
            sig, clr, com = "BEKLE / KARARSIZ", "#8b949e", "Fiyat ve hacim dengede. Büyük bir haber akışı veya fon girişi olmadan yön tayini zor. Kırılım beklemek mermiyi doğru kullanmanı sağlar."
            
        return {"p": lp, "ch": ch, "sig": sig, "clr": clr, "com": com, "df": df, "ma20": ma20, "target": target, "stop": stop}
    except: return None

# --- 4. ARAYÜZ (GÖSEL 4'ÜN GÜNCELLENMİŞ HALİ) ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:6px;'>🤵 GÜRKAN AI : MASTERMIND</h3>", unsafe_allow_html=True)

# ÜST PANEL: ARAMA + EKLE/SİL
_, mid_search, _ = st.columns([1, 2, 1])
with mid_search:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.session_state["last_sorgu"] in st.session_state["favorites"]:
            if st.button("ÇIKAR"): st.session_state["favorites"].remove(st.session_state["last_sorgu"]); st.rerun()
        else:
            if st.button("EKLE"): st.session_state["favorites"].append(st.session_state["last_sorgu"]); st.rerun()

l, m, r = st.columns([0.8, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_mastermind_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card' style='border-top-color: {res['clr']}'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} TERMİNAL VERİSİ</span><br>
                    <span style='font-size:42px; font-weight:bold; font-family:monospace;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:22px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:{res['clr']}; font-weight:bold; font-size:20px;'>{res['sig']}</span><br>
                    <span style='color:#4b525d; font-size:11px;'>GÜVEN ENDEKSİ: YÜKSEK</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px;'>
                <div class='metric-box'><p class='label-mini'>MA20 PİVOT</p><p class='metric-val' style='color:#8b949e;'>{res['ma20']:.2f}</p></div>
                <div class='metric-box'><p class='label-mini'>TEKNİK HEDEF</p><p class='metric-val' style='color:#00ff88;'>{res['target']:.2f}</p></div>
                <div class='metric-box'><p class='label-mini'>STOP SEVİYESİ</p><p class='metric-val' style='color:#ff4b4b;'>{res['stop']:.2f}</p></div>
            </div>
            <div style='margin-top:20px; padding:15px; background:rgba(255,204,0,0.03); border-radius:6px; border-left:4px solid #ffcc00;'>
                <p style='color:#ffcc00; font-size:12px; font-weight:bold; margin-bottom:4px;'>STRATEJİK RAPOR:</p>
                <p style='color:#e1e1e1; font-size:15px; line-height:1.6;'>"{res['com']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Profesyonel Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "KCHOL", "SAHOL", "PGSUS", "SISE", "AKBNK"]:
        if st.button(rs, key=f"r_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
