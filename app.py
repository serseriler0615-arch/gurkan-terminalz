import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Deep Search Key", type="password", placeholder="Neural Key...")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. DEEP SEARCH UI CSS ---
st.set_page_config(page_title="Gürkan AI v164", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #020406 !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 4px !important; width: 100%; }
    .oracle-card { background: #0a0d12; border: 1px solid #1c2128; border-radius: 15px; padding: 20px; margin-bottom: 10px; border-top: 4px solid #ffcc00; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .research-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0; }
    .research-item { background: rgba(255, 255, 255, 0.03); padding: 10px; border-radius: 8px; border: 1px solid #1c2128; text-align: center; }
    .label { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .val { font-size: 20px; font-weight: bold; font-family: 'Courier New', monospace; }
    .accuracy-tag { background: #ffcc00; color: #000; padding: 2px 10px; border-radius: 10px; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. DERİN ARAŞTIRMA MOTORU ---
def get_deep_research(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        rets = df['Close'].pct_change().dropna()
        
        # 1. DERİN ARAŞTIRMA: Volatilite & Standart Sapma (Kahinlik Katmanı)
        vol = rets.tail(60).std() # Son 3 ayın karakteri
        short_vol = rets.tail(10).std() # Son 2 haftanın paniği/coşkusu
        
        # Kesinlik Skoru (Eğer kısa ve uzun dönem volatilite uyumluysa kesinlik artar)
        accuracy = 100 - (abs(vol - short_vol) / vol * 100)
        accuracy = max(min(accuracy, 98), 65) # Mantıklı sınırlar
        
        # Beklenen Hareket (Z-Skoru %99 Güven Aralığı ile derinleştirildi)
        p_move = (rets.tail(20).mean() + (vol * 2.58)) * 100 
        m_move = (rets.tail(20).mean() - (vol * 2.58)) * 100
        
        # 2. KARAR MEKANİZMASI
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].tail(10).mean()
        
        if lp > ma20 and vol_ratio > 1.1:
            dec = "GÜÇLÜ ONAY"; clr = "#00ff88"; note = "Hacim ve Trend eşleşti. Kesinlik yüksek."
        elif lp < ma20 and vol_ratio > 1.1:
            dec = "SERT BASKI"; clr = "#ff4b4b"; note = "Satış hacmi artıyor. İstatistiksel risk yüksek."
        else:
            dec = "BELİRSİZ"; clr = "#ffcc00"; note = "Hacim yetersiz, tahmin gücü zayıf."
            
        return {"p": lp, "ch": ((lp-pc)/pc)*100, "p_m": p_move, "m_m": m_move, "acc": accuracy, "dec": dec, "clr": clr, "note": note, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI : NEURAL DEEP-SEARCH</h3>", unsafe_allow_html=True)

# ARAMA & RADAR ÜST PANEL
_, mid, _ = st.columns([1, 2, 1])
with mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ARAŞTIR"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"):
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

col_fav, col_main, col_rad = st.columns([0.8, 4, 0.8])

with col_fav:
    st.markdown("<p class='label'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        cf1, cf2 = st.columns([4, 1])
        if cf1.button(f, key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()
        if cf2.button("X", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_deep_research(st.session_state["last_sorgu"])
    if res:
        # ANA DERİN ARAŞTIRMA KARTI
        st.markdown(f"""
        <div class='oracle-card'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>
                <span class='accuracy-tag'>🎯 TAHMİN GÜCÜ: %{res['acc']:.1f}</span>
                <span style='color:{res['clr']}; font-weight:bold; font-size:14px;'>{res['dec']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div style='flex:1;'><p class='label'>FİYAT</p><p class='val'>{res['p']:.2f}</p></div>
                <div style='flex:1;'><p class='label'>GÜNLÜK %</p><p class='val' style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"};'>{res['ch']:+.2f}%</p></div>
            </div>
            <div class='research-grid'>
                <div class='research-item'>
                    <p class='label' style='color:#00ff88;'>MAX KAR İHTİMALİ</p>
                    <p class='val' style='color:#00ff88;'>+%{res['p_m']:.2f}</p>
                </div>
                <div class='research-item'>
                    <p class='label' style='color:#ff4b4b;'>MAX ZARAR RİSKİ</p>
                    <p class='val' style='color:#ff4b4b;'>-%{abs(res['m_m']):.2f}</p>
                </div>
            </div>
            <p style='font-size:12px; color:#8b949e; text-align:center; font-style:italic;'>"{res['note']}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # GRAFİK
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_rad:
    st.markdown("<p class='label'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "ISCTR", "KCHOL"]:
        if st.button(f"⚡ {r}", key=f"r_{r}"): st.session_state["last_sorgu"] = r; st.rerun()
