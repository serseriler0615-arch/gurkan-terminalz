import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="Gürkan AI v184", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"

st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; font-family: monospace; }
    .analysis-card { background: #0d1117; border: 1px solid #1c2128; border-radius: 4px; padding: 20px; border-top: 4px solid #ffcc00; }
    div.stButton > button { background: #111418 !important; color: #8b949e !important; border: 1px solid #1c2128 !important; border-radius: 2px !important; font-size: 10px !important; height: 22px !important; }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; }
    .metric-value { font-family: monospace; font-size: 20px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- 2. TEKNİK ANALİZ MOTORU ---
def get_execution_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Matematiksel Göstergeler
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        # ATR (Volatilite bazlı stop seviyesi için)
        df['TR'] = pd.concat([df['High'] - df['Low'], 
                             abs(df['High'] - df['Close'].shift(1)), 
                             abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
        df['ATR'] = df['TR'].rolling(14).mean()
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = float(df['MA20'].iloc[-1]); atr = float(df['ATR'].iloc[-1])
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]

        # HEDEF VE STOP HESABI
        target = lp + (atr * 1.5)
        stop_loss = lp - (atr * 1.2)
        
        # KURUMSAL KARAR MEKANİZMASI
        if vol_ratio > 1.8 and lp > ma20:
            sig, clr, com = "ALIM POZİSYONU", "#00ff88", f"Fiyat direnç bölgesi üzerinde hacimli kapanış yaptı. Momentum pozitif. Teknik hedef {target:.2f} seviyesidir. {stop_loss:.2f} altı kapanışlar stop-loss olarak değerlendirilmelidir."
        elif lp < ma20 and vol_ratio > 1.2:
            sig, clr, com = "SATIŞ BASKISI", "#ff4b4b", f"20 günlük hareketli ortalamanın altında hacimli kırılım gerçekleşti. Satış baskısı derinleşebilir. Bir sonraki destek bölgesi {stop_loss:.2f} seviyesindedir."
        elif lp > ma20:
            sig, clr, com = "POZİSYONU KORU", "#00d4ff", f"Trend kanalı içerisinde konsolide oluyor. 20 günlük ortalama ({ma20:.2f}) destek olarak çalışmaktadır. Yeni alım için hacim onayı beklenmelidir."
        else:
            sig, clr, com = "BEKLE / NÖTR", "#8b949e", "Teknik göstergeler yön tayini için yetersiz. Volatilite daralması mevcut, kırılım yönü takip edilmelidir."
            
        return {"p": lp, "ch": ch, "sig": sig, "clr": clr, "com": com, "df": df, "ma20": ma20, "target": target, "stop": stop_loss}
    except: return None

# --- 3. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:5px;'>🤵 GÜRKAN AI : EXECUTIONER</h3>", unsafe_allow_html=True)

# KONTROL PANELİ
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
    st.markdown("<p class='label-mini'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_execution_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='analysis-card' style='border-top-color: {res['clr']}'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} VERİ ANALİZİ</span><br>
                    <span style='font-size:38px; font-weight:bold; font-family:monospace;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:20px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:{res['clr']}; font-weight:bold; font-size:18px; letter-spacing:1px;'>{res['sig']}</span><br>
                    <span style='color:#4b525d; font-size:11px;'>Sinyal Gücü: Yüksek</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-bottom:15px;'>
                <div style='background:#111418; padding:10px; border-radius:4px;'>
                    <p class='label-mini' style='margin:0;'>20 GÜN ORT.</p>
                    <p class='metric-value' style='margin:0; color:#8b949e;'>{res['ma20']:.2f}</p>
                </div>
                <div style='background:#111418; padding:10px; border-radius:4px;'>
                    <p class='label-mini' style='margin:0;'>TEKNİK HEDEF</p>
                    <p class='metric-value' style='margin:0; color:#00ff88;'>{res['target']:.2f}</p>
                </div>
                <div style='background:#111418; padding:10px; border-radius:4px;'>
                    <p class='label-mini' style='margin:0;'>ZARAR KES (STOP)</p>
                    <p class='metric-value' style='margin:0; color:#ff4b4b;'>{res['stop']:.2f}</p>
                </div>
            </div>
            <div style='padding-top:10px; border-top:1px solid #1c2128;'>
                <p style='color:#ffcc00; font-size:11px; font-weight:bold; margin-bottom:5px;'>STRATEJİK RAPOR:</p>
                <p style='color:#e1e1e1; font-size:14px; line-height:1.5;'>{res['com']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR SİSTEMİ</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "KCHOL", "SAHOL", "PGSUS", "SISE"]:
        if st.button(rs, key=f"r_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
