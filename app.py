import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "AKBNK", "TUPRS"]
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Anahtar")
            if st.button("Sistemi Aç"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Admin Giriş"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 DARK UI ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 15px !important; color: #00ff88 !important; }
        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 12px; border: 1px solid #1c2128; }
        .skor-box { background: #0d1117; border: 1px solid #00ff88; border-radius: 12px; padding: 8px; text-align: center; }
        div.stButton > button { background-color: rgba(0, 255, 136, 0.02) !important; color: #00ff88 !important; border: 1px solid #1c2128 !important; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1])

    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        for f in st.session_state["favorites"][-7:]:
            if st.button(f"🔍 {f}", key=f"v84_f_{f}"):
                st.session_state["last_sorgu"] = f; st.rerun()

    with col_main:
        h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                direnc, destek = df['High'].tail(60).max(), df['Low'].tail(60).min()
                
                # Metrikler
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("RSI", f"{70.5:.1f}") # Örnek RSI
                with m4: st.markdown(f"<div class='skor-box'><span style='font-size:10px;'>VIP GÜVEN</span><br><b style='color:#00ff88; font-size:19px;'>%85</b></div>", unsafe_allow_html=True)

                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 VIP:</b> {h_input} grafiği şu an interaktif modda. Mouse ile yakınlaşabilirsin.</div>", unsafe_allow_html=True)

                # --- 🔍 ZOOM DESTEKLİ GRAFİK ---
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df.tail(120).index, open=df.tail(120)['Open'], high=df.tail(120)['High'],
                    low=df.tail(120)['Low'], close=df.tail(120)['Close'], name="Mum"
                ))
                
                fig.add_hline(y=direnc, line_dash="dash", line_color="#ff4b4b", opacity=0.5)
                fig.add_hline(y=destek, line_dash="dash", line_color="#0088ff", opacity=0.5)

                fig.update_layout(
                    height=350, margin=dict(l=0,r=0,t=0,b=0),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_rangeslider_visible=False,
                    xaxis=dict(showgrid=False, tickformat="%d %b"),
                    yaxis=dict(showgrid=True, gridcolor='#161b22', side='right'),
                    dragmode='zoom' # Mouse ile alan seçerek yakınlaşma aktif
                )
                
                # 'displayModeBar': True yaparak yakınlaşma araçlarını geri getirdik
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
        except: st.error("Veri hatası.")

    with col_radar:
        st.markdown("### 🚀 RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS"]
        for s in t_list:
            n = s.split('.')[0]
            if st.button(f"{n} ANALİZ", key=f"r84_{n}"):
                st.session_state["last_sorgu"] = n; st.rerun()

        # --- ADMIN BÖLÜMÜ (Geri Geldi) ---
        if st.session_state["role"] == "admin":
            st.markdown("---")
            st.markdown("### 🔐 ADMIN PANEL")
            if st.button("YENİ KEY ÜRET"):
                st.code(f"GAI-{int(time.time())}-VIP")
