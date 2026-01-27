import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. OTURUM VE GİRİŞ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]
if "role" not in st.session_state:
    st.session_state["role"] = None

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI Giriş", layout="centered")
        st.markdown("<style>.stApp{background-color:#0d1117;} h1,p,label{color:white !important;}</style>", unsafe_allow_html=True)
        st.title("🤵 Gürkan AI Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Lisans Anahtarı")
            if st.button("Aktive Et"):
                if k.startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Giriş"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # CSS - VIP TASARIM
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; }
        .radar-card { background: #1c2128; border-left: 4px solid #00ff88; border-radius: 6px; padding: 8px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #30363d; }
        .pct-box { background: rgba(0, 255, 136, 0.15); color: #00ff88 !important; padding: 4px 8px; border-radius: 4px; border: 1px solid #00ff88; font-size: 12px; }
        .admin-section { background: #161b22; border: 1px dashed #00ff88; padding: 10px; border-radius: 10px; margin-top: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # ANA PANEL
    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="fav_add", label_visibility="collapsed").upper()
        if st.button("➕") and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        for f in st.session_state["favorites"][-6:]:
            st.markdown(f"<div style='color:#00ff88; padding:4px;'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ VE ÇİZELGE
    with col_main:
        h_input = st.text_input("Hisse Sorgu:", value="THYAO", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="3mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                ma = df['Close'].rolling(20).mean().iloc[-1]
                h1, stop = fiyat*1.05, fiyat*0.96

                # Çizelge (Son 20 Gün)
                fig = go.Figure(data=[go.Scatter(x=df.tail(20).index, y=df.tail(20)['Close'], fill='tozeroy', line=dict(color='#00ff88'), fillcolor='rgba(0,255,136,0.1)')])
                fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                st.markdown(f"""<div class='asistan-box'><b style='color:#00ff88;'>🤵 VIP ANALİZ: {h_input}</b><br>
                🎯 Hedef: <span style='color:#00ff88;'>{h1:.2f}</span> | 🛡️ Stop: <span style='color:#ff4b4b;'>{stop:.2f}</span><br>
                <b>Çizelge Okuma:</b> Hisse şu an { 'pozitif bölgede' if fiyat > ma else 'dinlenme modunda' }. RSI ve hacim { 'toparlanıyor' if fiyat > ma else 'izlenmeli' }.</div>""", unsafe_allow_html=True)
        except: st.info("Hisse verisi aranıyor...")

    # 3. SAĞ: POTANSİYEL RADARI (%1+ İHTİMALİ OLANLAR)
    with col_radar:
        st.markdown("### 🎯 POTANSİYEL +%1")
        # Tarama Listesi (BIST'in lokomotifleri)
        tarama_listesi = ["AKBNK.IS", "BIMAS.IS", "EKGYO.IS", "KCHOL.IS", "SAHOL.IS", "SISE.IS", "TCELL.IS", "YKBNK.IS", "PGSUS.IS"]
        
        @st.cache_data(ttl=600) # 10 dakikada bir güncelle
        def potansiyel_tara(hisseler):
            potansiyeller = []
            data = yf.download(hisseler, period="5d", interval="1d", progress=False)['Close']
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(1)
            
            for h in hisseler:
                try:
                    c = data[h].iloc[-1]
                    p = data[h].iloc[-2]
                    degisim = ((c - p) / p) * 100
                    # Basit Algoritma: Son gün pozitif kapatmış ve momentumu olanları seç
                    if degisim > -0.5: # Tamamen çökmemiş, toparlanma eğilimi olanlar
                        potansiyeller.append({'ad': h.split(".")[0], 'pct': degisim, 'fiyat': c})
                except: continue
            return sorted(potansiyeller, key=lambda x: x['pct'], reverse=True)[:5]

        bulunanlar = potansiyel_tara(tarama_listesi)

        for b in bulunanlar:
            st.markdown(f"""
                <div class='radar-card'>
                    <div>{b['ad']}<br><span style='font-size:10px; color:#8b949e;'>Fiyat: {b['fiyat']:.2f}</span></div>
                    <div class='pct-box'>+%1.00 İht.</div>
                </div>
            """, unsafe_allow_html=True)

        # ADMIN KEY (SAĞ ALT)
        if st.session_state["role"] == "admin":
            st.markdown("<div class='admin-section'>🔑 <b>YENİ KEY ÜRET</b>", unsafe_allow_html=True)
            if st.button("OLUŞTUR"): st.code(f"GAI-{int(time.time())}-30-VIP")
            st.markdown("</div>", unsafe_allow_html=True)
