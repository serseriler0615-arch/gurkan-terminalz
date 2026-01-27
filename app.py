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
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Giriş Anahtarı", type="password")
            if st.button("Sistemi Başlat"):
                if k.startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2026!": st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 GÖRSELDEKİ BİREBİR TASARIM (CSS) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0a0a0a !important; }
        .main-header { font-size: 24px; font-weight: bold; color: #ffcc00; margin-bottom: 20px; }
        .asistan-box { 
            background: #0d1117; border: 1px solid #1c2128; padding: 15px; 
            border-radius: 5px; color: #e0e0e0; margin-bottom: 10px;
        }
        .guven-box {
            background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88;
            padding: 15px; border-radius: 10px; text-align: center;
        }
        div.stButton > button {
            background-color: #161b22 !important; color: #ffffff !important;
            border: 1px solid #30363d !important; text-align: left !important;
            border-radius: 4px !important; height: 45px !important;
        }
        .active-btn button { background-color: #00c853 !important; border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔐 KOMPAKT ADMİN ŞERİDİ ---
    if st.session_state["role"] == "admin":
        ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.5])
        with ac1: s_gun = st.selectbox("Süre", [30, 90, 365], label_visibility="collapsed")
        with ac2: 
            if st.button("💎 KEY ÜRET"): st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
        with ac3: 
            if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
        with ac4:
            if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()

    # --- ÜST PANEL (LOGO VE ARAMA) ---
    h_col1, h_col2 = st.columns([1, 4])
    with h_col1: st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    with h_col2: h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Hisse ara...", label_visibility="collapsed").upper()

    col_side, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_side:
        for f in st.session_state["favorites"]:
            is_active = "active-btn" if f == h_input else ""
            st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
            if st.button(f"🔍 {f}", key=f"btn_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ VE GRAFİK
    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # METRİKLER (GÖRSELDEKİ GİBİ)
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.5])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:+.2f}")
                m3.metric("RSI", "60.9")
                with m4: st.markdown("<div class='guven-box'><span style='font-size:12px;'>GÜVEN</span><br><b style='color:#00ff88; font-size:20px;'>%80</b></div>", unsafe_allow_html=True)

                # 🤵 GÜRKAN AI VIP ANALİZ KUTUSU
                st.markdown(f"""
                <div class='asistan-box'>
                    <span style='color:#ffcc00;'>🏆 VIP ANALİZ:</span> {h_input} için kritik <b>Direnç: {fiyat*1.05:.2f}</b> | <b>Destek: {fiyat*0.92:.2f}</b><br>
                    <span style='font-size:13px; color:#8b949e;'>Görünüm: Yarın fiyatın {fiyat*1.02:.2f} ₺ test etmesini bekliyorum. Trend pozitif.</span>
                </div>
                """, unsafe_allow_html=True)

                # GRAFİK (DİRENÇ/DESTEK ÇİZGİLİ)
                fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'])])
                fig.add_hline(y=fiyat*1.05, line_dash="dash", line_color="red", annotation_text="DİRENÇ")
                fig.add_hline(y=fiyat*0.92, line_dash="dash", line_color="cyan", annotation_text="DESTEK")
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Veri çekilemedi.")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("🚀 RADAR")
        r_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            r_data = yf.download(r_list, period="2d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in r_list:
                n = s.split('.')[0]
                pct = ((r_data[s].iloc[-1] - r_data[s].iloc[-2]) / r_data[s].iloc[-2]) * 100
                if st.button(f"{n} | %{pct:+.1f}", key=f"rad_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
        except: pass
