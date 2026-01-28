import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Neural Key...")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. MASTERMIND UI CSS ---
st.set_page_config(page_title="Gürkan AI v157", layout="wide")
st.markdown("""
<style>
    .stApp { background: #080a0d !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #111418 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 6px !important; }
    
    .quantum-card {
        background: #0d1117; border: 1px solid #ffcc0044; border-radius: 12px;
        padding: 15px; margin-bottom: 10px;
    }
    
    /* AŞIRI ZEKİ AI BOX */
    .ai-thought-box {
        background: linear-gradient(90deg, rgba(255, 204, 0, 0.05) 0%, rgba(0,0,0,0) 100%);
        border-left: 4px solid #ffcc00;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .label-text { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .val-text { font-size: 18px; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. AŞIRI ZEKİ ANALİZ MOTORU ---
def get_neural_intelligence(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        vol_avg = df['Volume'].tail(20).mean(); cur_vol = df['Volume'].iloc[-1]
        
        # RSI & MA
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # AŞIRI ZEKİ YORUM MANTIĞI
        score = 0
        if lp > ma20: score += 40
        if 45 < rsi < 65: score += 30
        if cur_vol > vol_avg: score += 30
        
        if score >= 80:
            thought = f"🔥 <b>Agresif Alım Bölgesi:</b> Hacim desteğiyle trend onaylanmış. {lp} üzerinde kalıcılık, {lp*1.05:.2f} hedefini hızlandırır."
        elif score >= 50:
            thought = f"⚖️ <b>Denge Arayışı:</b> Hisse yorulmuş ancak trendi kırmamış. Yeni giriş için {lp*0.98:.2f} desteği pusu noktasıdır."
        else:
            thought = f"⚠️ <b>Dikkat - Zayıf İvme:</b> Satış baskısı hissediliyor. RSI {rsi:.1f} ile soğuma aşamasında, nakit oranını koru."
            
        std = df['Close'].tail(20).std()
        return {"p": lp, "ch": ch, "rsi": rsi, "score": score, "h": lp+(std*2), "l": lp-(std*2), "thought": thought, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; margin-bottom:0;'>🤵 GÜRKAN AI</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555; font-size:10px; margin-bottom:20px;'>NEURAL STRATEGY TERMINAL v157</p>", unsafe_allow_html=True)

# Üst Arama
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2 = st.columns([4, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("TARAMA"): st.session_state["last_sorgu"] = s_inp; st.rerun()

col_fav, col_main = st.columns([0.8, 5])

with col_fav:
    st.markdown("<p class='label-text'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with col_main:
    res = get_neural_intelligence(st.session_state["last_sorgu"])
    if res:
        # 1. RAPOR (Sayılar)
        st.markdown(f"""
        <div class='quantum-card'>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div style='flex:1;'><p class='label-text'>FİYAT / DEĞİŞİM</p><p class='val-text'>{res['p']:.2f} <small style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"};'>({res['ch']:+.2f}%)</small></p></div>
                <div style='flex:1;'><p class='label-text'>ZEKA SKORU</p><p class='val-text' style='color:#ffcc00;'>%{res['score']}</p></div>
                <div style='flex:1;'><p class='label-text'>RSI (14)</p><p class='val-text'>{res['rsi']:.1f}</p></div>
                <div style='flex:1;'><p class='label-text'>3G TAVAN</p><p class='val-text' style='color:#00ff88;'>{res['h']:.2f}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. GÜRKAN AI (Aşırı Zeki Düşünce Katmanı)
        st.markdown(f"""
        <div class='ai-thought-box'>
            <span style='color:#ffcc00; font-weight:bold; font-size:12px;'>🤵 GÜRKAN AI ANALİZİ:</span><br>
            <span style='font-size:15px; color:#efefef;'>{res['thought']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. ÇİZELGE (Grafik)
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
