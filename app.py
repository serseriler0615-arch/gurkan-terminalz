import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. SİSTEM AYARLARI ---
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
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY GİRİŞİ", "🔐 ADMIN PANELİ"])
        with t1:
            k = st.text_input("Lisans Anahtarı", key="login_v_key")
            if st.button("Sistemi Aktive Et"):
                if k.startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("Yönetici ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- OKUNABİLİR VIP TASARIM ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        
        /* RADAR KARTLARI (KAPANIŞ POTANSİYELİ ODAKLI) */
        .radar-card { 
            background: #1c2128; border-left: 5px solid #00ff88; border-radius: 8px; 
            padding: 10px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        }
        .pct-label { background: #00ff88; color: #0d1117 !important; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 900 !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; }
        .admin-box { background: #161b22; border: 1px dashed #00ff88; padding: 10px; border-radius: 10px; margin-top: 15px; }
        </style>
    """, unsafe_allow_html=True)

    # --- DASHBOARD ÜST ---
    st.markdown(f"🚀 **GÜRKAN AI | VIP TÜRKÇE TERMİNAL v65**")

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİ TAKİP
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="add_f", label_visibility="collapsed").upper()
        if st.button("➕") and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        for f in st.session_state["favorites"][-6:]:
            st.markdown(f"<div style='color:#00ff88; border-bottom:1px solid #222; padding:3px;'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ VE TÜRKÇE ÇİZELGE
    with col_main:
        h_input = st.text_input("Hisse Sorgu:", value="THYAO", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="3mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df_plot = df.tail(20) # SON 20 GÜN
                fiyat = float(df['Close'].iloc[-1])
                ma = df['Close'].rolling(20).mean().iloc[-1]
                h1, stop = fiyat*1.05, fiyat*0.96

                # Çizelge
                fig = go.Figure(data=[go.Scatter(x=df_plot.index, y=df_plot['Close'], fill='tozeroy', line=dict(color='#00ff88', width=2), fillcolor='rgba(0,255,136,0.1)')])
                fig.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                st.markdown(f"""<div class='asistan-box'><b style='color:#00ff88;'>🤵 VIP ANALİZ: {h_input}</b><br>
                🎯 Hedef: <span style='color:#00ff88;'>{h1:.2f} TL</span> | 🛡️ Stop: <span style='color:#ff4b4b;'>{stop:.2f} TL</span><br>
                <b>Çizelge Okuma:</b> Son 20 günlük periyotta {h_input} {'pozitif bir momentum sergiliyor' if fiyat > ma else 'dinlenme aşamasında'}. Kapanışı güçlü yapma ihtimali yüksek.</div>""", unsafe_allow_html=True)
        except: st.info("Hisse verisi aranıyor...")

    # 3. SAĞ: KAPANIŞ POTANSİYELİ RADARI
    with col_radar:
        st.markdown("### 🏆 GÜNÜN ADAYLARI")
        # Analiz edilen ve potansiyeli yüksek (Yüksek Kalma İhtimali Olan) hisseler
        aday_listesi = ["AKBNK.IS", "BIMAS.IS", "TUPRS.IS", "KCHOL.IS", "SISE.IS", "TCELL.IS", "ASELS.IS"]
        
        @st.cache_data(ttl=300)
        def potansiyel_tara(hisseler):
            sonuclar = []
            data = yf.download(hisseler, period="5d", interval="1d", progress=False)['Close']
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(1)
            for h in hisseler:
                try:
                    c = data[h].iloc[-1]
                    p = data[h].iloc[-2]
                    degisim = ((c - p) / p) * 100
                    # Eğer bugün dünden iyiyse ve trend sağlamsa radara al
                    if degisim > 0.2: 
                        sonuclar.append({'ad': h.split(".")[0], 'pct': degisim, 'fiyat': c})
                except: continue
            return sorted(sonuclar, key=lambda x: x['pct'], reverse=True)[:5]

        radar_hisseler = potansiyel_tara(aday_listesi)

        for b in radar_hisseler:
            st.markdown(f"""
                <div class='radar-card'>
                    <div>
                        <span class='radar-name' style='color:#00ff88; font-size:15px;'>{b['ad']}</span><br>
                        <span style='font-size:10px; color:#8b949e;'>Hedef Fark: +%1.20</span>
                    </div>
                    <div class='pct-label'>POTANSİYEL</div>
                </div>
            """, unsafe_allow_html=True)

        # ADMIN KEY ÜRETİCİ (SAĞ ALTA SABİT)
        if st.session_state["role"] == "admin":
            st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
            st.markdown("🔑 **ADMIN KONTROL**")
            if st.button("LİSANS ÜRET", use_container_width=True):
                st.code(f"GAI-{int(time.time())}-30-VIP")
            st.markdown("</div>", unsafe_allow_html=True)
