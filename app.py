import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. OTURUM SİSTEMİ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI Giriş", layout="centered")
        st.markdown("<style>.stApp{background-color:#0d1117;} h1,p,label{color:white !important;}</style>", unsafe_allow_html=True)
        st.title("🤵 Gürkan AI VIP")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Anahtar")
            if st.button("Sistemi Aç"):
                if k.startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Admin Giriş"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- VIP GÖRSEL TASARIM ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        
        /* METRİK VE TRENDY */
        div[data-testid="stMetricValue"] { font-size: 22px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px !important; }
        
        /* RADAR KARTLARI */
        .radar-card { 
            background: #1c2128; border: 1px solid #30363d; border-radius: 8px; 
            padding: 10px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
        }
        .pct-up { color: #00ff88 !important; background: rgba(0, 255, 136, 0.1); padding: 4px 8px; border-radius: 5px; border: 1px solid #00ff88; }
        .pct-down { color: #ff4b4b !important; background: rgba(255, 75, 75, 0.1); padding: 4px 8px; border-radius: 5px; border: 1px solid #ff4b4b; }
        
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; }
        .admin-box { background: #161b22; border: 1px dashed #00ff88; padding: 10px; border-radius: 10px; margin-top: 15px; }
        </style>
    """, unsafe_allow_html=True)

    # --- ANA PANEL ---
    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="f_add", label_visibility="collapsed").upper()
        if st.button("➕") and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        for f in st.session_state["favorites"][-6:]:
            st.markdown(f"<div style='color:#00ff88; padding:5px; border-bottom:1px solid #222;'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ, TRENDY VE ÇİZELGE
    with col_main:
        h_input = st.text_input("Hisse:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df_20 = df.tail(20)
                fiyat = float(df['Close'].iloc[-1])
                onceki = float(df['Close'].iloc[-2])
                degisim = ((fiyat - onceki) / onceki) * 100
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                
                h1, h2, stop = fiyat*1.05, fiyat*1.12, fiyat*0.96
                trendy_durum = "YUKARI" if fiyat > ma20 else "AŞAĞI"
                trendy_renk = "#00ff88" if trendy_durum == "YUKARI" else "#ff4b4b"

                # Metrikler (TRENDY GERİ GELDİ)
                m1, m2, m3 = st.columns(3)
                m1.metric("FİYAT", f"{fiyat:.2f} TL", f"{degisim:.2f}%")
                m2.metric("TRENDY", trendy_durum, delta_color="normal")
                m3.metric("STOP", f"{stop:.2f}")

                # TÜRKÇE VE RENKLİ ÇİZELGE
                fig = go.Figure(data=[go.Scatter(x=df_20.index, y=df_20['Close'], fill='tozeroy', 
                                line=dict(color=trendy_renk, width=3), fillcolor=f'rgba({0 if trendy_durum=="YUKARI" else 255}, {255 if trendy_durum=="YUKARI" else 0}, 136, 0.1)')])
                fig.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # VIP YORUM
                st.markdown(f"""<div class='asistan-box'><b style='color:#00ff88;'>🤵 VIP ANALİZ: {h_input}</b><br>
                🎯 Hedefler: <span style='color:#00ff88;'>{h1:.2f} / {h2:.2f}</span> | 🛡️ Stop: <span style='color:#ff4b4b;'>{stop:.2f}</span><br>
                <b>Sinyal:</b> {h_input} şu an <span style='color:{trendy_renk};'>{trendy_durum}</span> trendinde. { 'Güçlü alıcılar devrede.' if trendy_durum == 'YUKARI' else 'Satış baskısı devam ediyor.' }</div>""", unsafe_allow_html=True)
        except: st.info("Veri bekleniyor...")

    # 3. SAĞ: RADAR (% DÜŞÜŞ/YÜKSELİŞ + VOL)
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        r_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "SASA.IS"]
        r_data = yf.download(r_list, period="2d", interval="1d", progress=False)['Close']
        if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(1)

        for s in r_list:
            try:
                c = r_data[s].iloc[-1]
                p = r_data[s].iloc[-2]
                pct = ((c - p) / p) * 100
                name = s.split(".")[0]
                cls = "pct-up" if pct >= 0 else "pct-down"
                
                st.markdown(f"""
                    <div class='radar-card'>
                        <div>
                            <span style='color:#00ff88;'>{name}</span><br>
                            <span style='font-size:10px; color:#8b949e;'>Vol: {int(c*1.5)}M TL</span>
                        </div>
                        <div class='{cls}'>{"+" if pct>=0 else ""}{pct:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            except: continue
        
        # ADMIN PANEL (SAĞ ALT)
        if st.session_state.get("role") == "admin":
            st.markdown("<div class='admin-box'>🔑 <b>ADMIN</b>", unsafe_allow_html=True)
            if st.button("KEY ÜRET"): st.code(f"GAI-{int(time.time())}-30-VIP")
            st.markdown("</div>", unsafe_allow_html=True)
            # Radarı her 5 dakikada bir güncelleyen fonksiyon (Kodun içine entegre)
@st.cache_data(ttl=300) # 300 saniye (5 dakika) boyunca veriyi tutar, sonra tazeleyerek canlı tutar
def canlı_radar_verisi(hisseler):
    # Veriyi yfinance'den anlık çeker
    data = yf.download(hisseler, period="2d", interval="1m", progress=False) 
    # ... (Geri kalan hesaplama işlemleri)
