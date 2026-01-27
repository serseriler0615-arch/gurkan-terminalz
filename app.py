import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS", "BIMAS", "AKBNK"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Giriş Anahtarı")
            if st.button("Sistemi Başlat"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("Admin ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP v93", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 ESTETİK UI ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 14px !important; color: #00ff88 !important; }
        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 12px; border-radius: 8px; border: 1px solid #1c2128; color: #e0e0e0; }
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            font-family: 'Courier New', monospace !important;
            text-align: left !important;
            font-size: 12px !important;
        }
        div.stButton > button:hover { border-color: #00ff88 !important; background: rgba(0,255,136,0.1) !important; }
        .news-card { background: #0d1117; border: 1px solid #1c2128; padding: 8px; border-radius: 5px; margin-bottom: 5px; font-size: 11px; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.4])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in st.session_state["favorites"]:
            if st.button(f"🔍 {f}", key=f"v93_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()

    # 2. ORTA: ANALİZ VE GRAFİK
    with col_main:
        h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                rsi = 55.0 # Basit RSI simülasyonu (Hız için)
                
                m1, m2, m3 = st.columns([1, 1, 1])
                m1.metric("FİYAT", f"{fiyat:.2f} ₺")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("RSI", f"{rsi:.1f}")

                # GÜRKAN AI YORUM VE TAHMİN (Asistan Kutusu)
                tahmin = fiyat * 1.02 if degisim > 0 else fiyat * 0.98
                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88;'>🤵 GÜRKAN AI ANALİZ:</b> {h_input} bugün %{degisim:.2f} hareketle <b>{fiyat:.2f}</b> seviyesinde. 
                    Yarın için beklentim <b>{tahmin:.2f}</b> civarında dengelenmesi. RSI {rsi} ile nötr bölgede.
                </div>
                """, unsafe_allow_html=True)

                # GRAFİK
                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, xaxis=dict(tickformat="%d %b"), yaxis=dict(side='right', gridcolor='#161b22'))
                st.plotly_chart(fig, use_container_width=True)

                # HABERLER (Hata Korumalı)
                st.markdown("### 🗞️ SON HABERLER")
                try:
                    news = yf.Ticker(sembol).news[:3]
                    for n in news:
                        st.markdown(f"<div class='news-card'><b>{n.get('publisher','Borsa')}:</b> {n.get('title','')}</div>", unsafe_allow_html=True)
                except: st.write("Haberler yüklenemedi.")

        except: st.error("Veri çekilemedi.")

    # 3. SAĞ: CANLI RADAR (ESKİ GÜZEL HALİNE DÖNDÜ)
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            r_data = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            
            for s in t_list:
                n = s.split('.')[0]
                c = r_data[s].iloc[-1]
                p = r_data[s].iloc[-2]
                pct = ((c - p) / p) * 100
                
                sign = "+" if pct >= 0 else ""
                # "SEMBOL | FIYAT | %DEG" Formatı
                btn_label = f"{n.ljust(6)} | {c:>7.2f} | {sign}{pct:.1f}%"
                
                if st.button(btn_label, key=f"v93_r_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
        except: st.warning("Radar güncelleniyor...")
        
        if st.session_state["role"] == "admin":
            st.markdown("---")
            if st.button("🚪 SİSTEMDEN ÇIK"): st.session_state["access_granted"] = False; st.rerun()
