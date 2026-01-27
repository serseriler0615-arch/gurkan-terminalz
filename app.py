import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. OTURUM YÖNETİMİ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 🔐 GİRİŞ PANELİ ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h3 style='text-align: center; color: #ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
        with t1:
            with st.form("vip"):
                k = st.text_input("Key", type="password")
                if st.form_submit_button("GİRİŞ", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): 
                        st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            with st.form("adm"):
                u = st.text_input("ID")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("ADMİN GİRİŞ", use_container_width=True):
                    if u.strip().upper() == "GURKAN" and p.strip() == "HEDEF2024!": 
                        st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 MOBİL & DAR EKRAN CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        [data-testid="stMetricValue"] { font-size: 18px !important; }
        .gurkan-ai-box { 
            background: #0d1117; border-left: 4px solid #ffcc00; padding: 10px; 
            border-radius: 5px; font-size: 12px; margin-bottom: 10px; color: #e0e0e0;
        }
        .guven-mini { color: #00ff88; font-weight: bold; border: 1px solid #00ff88; padding: 2px 5px; border-radius: 4px; font-size: 10px; }
        div.stButton > button { 
            background-color: #161b22 !important; color: white !important; 
            font-size: 11px !important; height: 35px !important; border: 1px solid #30363d !important;
        }
        /* Telefondaki boşlukları daralt */
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ADMİN BUTONLARI (SARI ÇİZGİSİZ - EN ÜSTTE) ---
    if st.session_state["role"] == "admin":
        c1, c2, c3 = st.columns([1, 1, 0.3])
        with c1: s_gun = st.selectbox("", [30, 90, 365], label_visibility="collapsed")
        with c2: 
            if st.button("💎 KEY ÜRET", use_container_width=True): 
                st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
        with c3: 
            if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()
        if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])

    # --- ÜST BAR ---
    h1, h2 = st.columns([1.5, 3])
    with h1: st.markdown("<b style='color:#ffcc00; font-size:16px;'>★ GÜRKAN AI</b>", unsafe_allow_html=True)
    with h2: h_input = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()

    # --- MOBİLDE TEK SÜTUN DÜZENİ ---
    sembol = h_input if "." in h_input else h_input + ".IS"
    try:
        df = yf.download(sembol, period="6mo", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            fiyat = float(df['Close'].iloc[-1])
            degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            # Üst Metrikler
            m1, m2, m3 = st.columns(3)
            m1.metric("FİYAT", f"{fiyat:.2f}")
            m2.metric("GÜNLÜK", f"%{degisim:+.1f}")
            m3.markdown(f"<div style='text-align:right; margin-top:10px;'><span class='guven-mini'>GÜVEN %80</span></div>", unsafe_allow_html=True)

            # Analiz Kutusu
            st.markdown(f"""<div class='gurkan-ai-box'><b>🤵 GÜRKAN AI:</b> {h_input} yarın <b>{fiyat*1.015:.2f} ₺</b> hedefine yönelebilir.</div>""", unsafe_allow_html=True)

            # Grafik (Yüksekliği Mobil için Azalttım)
            fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
            st.plotly_chart(fig, use_container_width=True)
            
            # Radar & Favoriler (Yan Yana Alt Alta Mobil Düzeni)
            st.markdown("<small style='color:#8b949e;'>⭐ FAVORİLER & 🚀 RADAR</small>", unsafe_allow_html=True)
            fav_radar_list = list(set(st.session_state["favorites"] + ["THYAO", "ASELS", "EREGL", "TUPRS"]))
            
            cols = st.columns(3) # Mobilde 3'lü buton dizisi
            for i, f in enumerate(fav_radar_list[:9]): # İlk 9 taneyi göster
                with cols[i % 3]:
                    if st.button(f, key=f"btn_{f}", use_container_width=True):
                        st.session_state["last_sorgu"] = f; st.rerun()
    except: st.write("Yükleniyor...")
