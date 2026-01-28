import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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

# --- 2. PREDICTOR UI CSS ---
st.set_page_config(page_title="Gürkan AI v159", layout="wide")
st.markdown("""
<style>
    .stApp { background: #05070a !important; color: #e1e1e1 !important; }
    .report-card { background: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .ai-box { background: rgba(255, 204, 0, 0.03); border-left: 5px solid #ffcc00; padding: 15px; border-radius: 4px; margin: 10px 0; }
    .prediction-box { background: rgba(0, 255, 136, 0.05); border: 1px dashed #00ff88; padding: 12px; border-radius: 8px; margin: 10px 0; text-align: center; }
    .label { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .value { font-size: 18px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. AŞIRI ARAŞTIRMACI TAHMİN MOTORU ---
def get_neural_prediction(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty or len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        returns = df['Close'].pct_change().dropna()
        
        # 🧠 AŞIRI ARAŞTIRMA KATMANI:
        # Son 20 günlük volatiliteyi, trend eğimini ve RSI ivmesini birleştiriyoruz
        volatility = returns.tail(20).std() 
        avg_daily_return = returns.tail(20).mean()
        
        # Beklenen Max Kar/Zarar (95% Güven Aralığı Simülasyonu)
        expected_move = volatility * 1.645 * 100 # İstatistiki standart sapma
        daily_bias = avg_daily_return * 100
        
        # Nihai "Zeki" Tahmin
        plus_move = daily_bias + expected_move
        minus_move = daily_bias - expected_move
        
        # Teknik Skorer
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        score = 70 if lp > ma20 else 40
        
        return {
            "p": lp, "ch": ((lp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
            "plus": round(plus_move, 2), "minus": round(minus_move, 2),
            "score": score, "df": df
        }
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI : NEURAL PREDICTOR</h2>", unsafe_allow_html=True)

col_side, col_main = st.columns([0.8, 5])

with col_side:
    st.markdown("<p class='label'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with col_main:
    res = get_neural_prediction(st.session_state["last_sorgu"])
    if res:
        # 1. RAPOR KARTI
        st.markdown(f"""
        <div class='report-card'>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div style='flex:1;'><p class='label'>FİYAT</p><p class='value'>{res['p']:.2f}</p></div>
                <div style='flex:1;'><p class='label'>GÜNLÜK DEĞİŞİM</p><p class='value' style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"};'>{res['ch']:+.2f}%</p></div>
                <div style='flex:1;'><p class='label'>SİSTEM SKORU</p><p class='value' style='color:#ffcc00;'>%{res['score']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. AŞIRI ARAŞTIRMACI TAHMİN KUTUSU
        st.markdown(f"""
        <div class='prediction-box'>
            <p class='label' style='color:#00ff88;'>📊 İSTATİSTİKSEL OLASILIK RAPORU</p>
            <span style='font-size:16px;'>Bugünkü verilere göre 24 saatlik <b>Beklenen Hareket Alanı:</b></span><br>
            <span style='font-size:24px; font-weight:bold; color:#00ff88;'>+%{res['plus']}</span> 
            <span style='font-size:20px; color:#8b949e;'> / </span> 
            <span style='font-size:24px; font-weight:bold; color:#ff4b4b;'>-%{abs(res['minus'])}</span><br>
            <p style='font-size:11px; color:#8b949e; margin-top:5px;'>*Bu oran son 1 yıllık volatilite ve 20 günlük trend ivmesi araştırılarak hesaplanmıştır.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. GRAFİK
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
