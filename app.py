import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : The Prophet", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"

# --- 2. CSS (Maksimum Karizma & Minimum Boşluk) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; font-size: 16px; }
    
    .prophet-card {
        background: linear-gradient(145deg, #0d1117, #080a0d);
        border: 1px solid #1c2128; border-radius: 12px;
        padding: 25px; border-top: 4px solid #ffcc00; margin-bottom: 15px;
    }
    
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
        font-size: 10px !important; height: 24px !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; }
    .news-box { background: #080a0d; padding: 10px; border-radius: 6px; border-left: 2px solid #30363d; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 3. PROPHET ANALİZ MOTORU ---
def get_prophet_analysis(symbol):
    try:
        # Veri çekme (Haberler dahil)
        ticker = yf.Ticker(symbol + ".IS")
        df = ticker.history(period="6mo")
        news = ticker.news[:3] # Son 3 kritik haber
        
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        # PARA AKIŞI (MFI) & VOLATİLİTE
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        pos_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        neg_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        mfi = 100 - (100 / (1 + pos_flow / neg_flow))
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp - pc) / pc) * 100
        cur_mfi = mfi.iloc[-1]
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]

        # HABER DUYARLILIĞI (Simüle - Gerçek haber başlıklarına göre analiz)
        sentiment_score = 0
        news_summary = ""
        if news:
            for n in news:
                title = n['title'].lower()
                news_summary += f"• {n['title'][:60]}...<br>"
                if any(x in title for x in ['artış', 'rekor', 'alım', 'pozitif', 'kar']): sentiment_score += 1
                if any(x in title for x in ['düşüş', 'kayıp', 'negatif', 'satış', 'risk']): sentiment_score -= 1
        
        # KAHİN KARARI
        if sentiment_score > 0 and cur_mfi > 60:
            sig, clr, com = "TAM GAZ (STRONG BUY)", "#00ff88", "Hem haber akışı hem para girişi pozitif! Tahtacı büyük oynuyor, dirençler sadece kağıt üzerinde kalacak."
        elif sentiment_score < 0 and ch > 0:
            sig, clr, com = "AYI TUZAĞI (BEWARE)", "#ffcc00", "Fiyat yükseliyor ama haberler kötü ve para çıkışı seziliyor. Küçük yatırımcıyı içeri çekip mal boşaltabilirler, dikkat!"
        elif cur_mfi < 30:
            sig, clr, com = "DİP TOPLAMA (ACCUMULATION)", "#00d4ff", "Fiyat ölü taklidi yapıyor ama alttan alttan para girişi var. Sessizce pozisyon artırma zamanı."
        elif vol_ratio > 2.5:
            sig, clr, com = "JOKER UYARISI", "#ff00ff", "Hacim patlaması! Ya dev bir kurumsal giriş var ya da operasyon başlıyor. Koltuğunu sıkı tut."
        else:
            sig, clr, com = "BEKLE VE GÖR", "#8b949e", "Piyasa şu an kağıdı tartıyor. Net bir haber veya para hareketi oluşmadan mermi harcama."
            
        return {"p": lp, "ch": ch, "sig": sig, "clr": clr, "com": com, "df": df, "mfi": cur_mfi, "news": news_summary}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:6px; font-weight:lighter;'>GÜRKAN AI : THE PROPHET</h3>", unsafe_allow_html=True)

# ARAMA & KONTROL
_, mid_search, _ = st.columns([1, 2, 1])
with mid_search:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("KEŞFET"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.session_state["last_sorgu"] in st.session_state["favorites"]:
            if st.button("🔴 SİL"): st.session_state["favorites"].remove(st.session_state["last_sorgu"]); st.rerun()
        else:
            if st.button("🟢 EKLE"): st.session_state["favorites"].append(st.session_state["last_sorgu"]); st.rerun()

l, m, r = st.columns([0.7, 4, 0.9])

with l:
    st.markdown("<p class='label-mini'>TAKİP LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"fav_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_prophet_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='prophet-card' style='border-top-color: {res['clr']}'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} STRATEJİK İSTİHBARAT</span><br>
                    <span style='font-size:42px; font-weight:bold; color:#fff;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:22px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <div style='background:{res['clr']}22; color:{res['clr']}; padding:8px 15px; border-radius:6px; border:1px solid {res['clr']}; font-weight:bold;'>{res['sig']}</div>
                    <p class='label-mini' style='margin-top:10px;'>PARA AKIŞI: {res['mfi']:.1f}</p>
                </div>
            </div>
            <div style='margin-top:20px; padding:15px; background:rgba(255,204,0,0.05); border-radius:8px; border-left:3px solid #ffcc00;'>
                <p style='color:#ffcc00; font-size:12px; font-weight:bold; margin-bottom:5px;'>🤵 KAHİNİN ÖNGÖRÜSÜ:</p>
                <p style='color:#e1e1e1; font-size:15px; line-height:1.6;'>"{res['com']}"</p>
            </div>
            <div style='margin-top:15px;'>
                <p class='label-mini'>SON RADAR KAYITLARI (HABERLER)</p>
                <div class='news-box' style='font-size:12px; color:#a1a1a1;'>{res['news'] if res['news'] else "Haber akışı sakin."}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>DÜNYA RADARI</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "KCHOL", "EREGL", "THYAO", "SISE", "ASTOR"]:
        st.write(f"<div style='margin-bottom:2px;'><span style='color:#ffcc00; font-size:11px;'>{rs}</span></div>", unsafe_allow_html=True)
        if st.button("İncele", key=f"r_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
