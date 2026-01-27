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
    # Başlangıç listesi
    st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS", "BIMAS"]

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
    st.set_page_config(page_title="Gürkan AI VIP v94", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 14px !important; color: #00ff88 !important; margin-bottom: 10px; }
        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 12px; border-radius: 8px; border: 1px solid #1c2128; color: #e0e0e0; }
        
        /* Favori ve Radar Butonları */
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            font-family: 'Courier New', monospace !important;
            text-align: left !important;
        }
        div.stButton > button:hover { border-color: #00ff88 !important; background: rgba(0,255,136,0.1) !important; }
        
        /* Favori Ekle/Çıkar Butonları */
        .fav-action-btn button {
            padding: 2px 10px !important;
            font-size: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.4])

    # 1. SOL: DİNAMİK FAVORİ LİSTESİ
    with col_fav:
        st.markdown("### ⭐ TAKİP LİSTEM")
        for f in st.session_state["favorites"]:
            cols = st.columns([4, 1])
            with cols[0]:
                if st.button(f"🔍 {f}", key=f"v94_f_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
            with cols[1]:
                if st.button("X", key=f"del_{f}", help="Listeden Çıkar"):
                    st.session_state["favorites"].remove(f); st.rerun()

    # 2. ORTA: ANALİZ VE FAVORİ EKLEME
    with col_main:
        h1, h2 = st.columns([3, 1])
        with h1:
            h_input = st.text_input("HİSSE ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        with h2:
            # FAVORİYE EKLEME BUTONU
            if h_input not in st.session_state["favorites"]:
                if st.button("⭐ LİSTEYE EKLE", use_container_width=True):
                    st.session_state["favorites"].append(h_input); st.rerun()
            else:
                st.button("✅ LİSTEDE", disabled=True, use_container_width=True)

        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                m1, m2, m3 = st.columns([1, 1, 1])
                m1.metric("FİYAT", f"{fiyat:.2f} ₺")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("DURUM", "BOĞA" if degisim > 0 else "AYI")

                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 GÜRKAN AI:</b> <b>{h_input}</b> şu an takip listende {'yer alıyor' if h_input in st.session_state['favorites'] else 'değil'}. Grafikte son 80 mumluk trendi görüyorsun.</div>", unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Veri çekilemedi. Lütfen sembolü kontrol edin.")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            r_data = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_all.columns, pd.MultiIndex): r_all.columns = r_all.columns.get_level_values(0)
            
            for s in t_list:
                n = s.split('.')[0]
                c = r_data[s].iloc[-1]
                p = r_data[s].iloc[-2]
                pct = ((c - p) / p) * 100
                sign = "+" if pct >= 0 else ""
                btn_label = f"{n.ljust(6)} | {c:>7.2f} | {sign}{pct:.1f}%"
                
                if st.button(btn_label, key=f"v94_r_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
        except: st.warning("Radar güncelleniyor...")
