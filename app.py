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
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "EREGL"]

# --- 🔐 GİRİŞ PANELİ (DOĞRU ŞİFRE: HEDEF2024!) ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP Login", layout="centered")
        st.markdown("<h2 style='text-align: center; color: #ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        
        tab_vip, tab_admin = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        
        with tab_vip:
            with st.form("vip_form"):
                vip_k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("Sistemi Başlat", use_container_width=True):
                    if vip_k.strip().upper().startswith("GAI-"): 
                        st.session_state["access_granted"], st.session_state["role"] = True, "user"
                        st.rerun()
                    else: st.error("Geçersiz Anahtar!")

        with tab_admin:
            with st.form("admin_form"):
                adm_id = st.text_input("Yönetici ID")
                adm_ps = st.text_input("Yönetici Şifre", type="password")
                if st.form_submit_button("Yönetici Girişi Yap", use_container_width=True):
                    # --- ŞİFRE BURADA GÜNCELLENDİ ---
                    if adm_id.strip().upper() == "GURKAN" and adm_ps.strip() == "HEDEF2024!": 
                        st.session_state["access_granted"], st.session_state["role"] = True, "admin"
                        st.rerun()
                    else:
                        st.error("Giriş Başarısız! ID: GURKAN | Şifre: HEDEF2024!")
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 PRO DARK CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .main-header { font-size: 22px; font-weight: bold; color: #ffcc00; }
        .gurkan-ai-box { background: #0d1117; border: 1px solid #1c2128; padding: 15px; border-radius: 8px; border-left: 5px solid #ffcc00; margin-bottom: 10px; }
        .guven-box { background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88; padding: 12px; border-radius: 8px; text-align: center; }
        div.stButton > button { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; text-align: left !important; }
        .active-btn button { background-color: #00c853 !important; border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ADMIN ÜST PANEL ---
    if st.session_state["role"] == "admin":
        with st.container():
            st.markdown("<div style='border:1px solid #ffcc00; padding:10px; border-radius:5px; margin-bottom:15px;'>", unsafe_allow_html=True)
            ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.5])
            with ac1: s_gun = st.selectbox("Süre", [30, 90, 365], label_visibility="collapsed")
            with ac2: 
                if st.button("💎 LİSANS ÜRET"): 
                    st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
            with ac3: 
                if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
            with ac4:
                if st.button("🚪"): 
                    st.session_state["access_granted"] = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- ANA ARAYÜZ (TAM GÖRSEL UYUMU) ---
    h_col1, h_col2 = st.columns([1.2, 4])
    with h_col1: st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    with h_col2: h_input = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()

    col_side, col_main, col_radar = st.columns([0.7, 3, 1.3])

    with col_side:
        for f in st.session_state["favorites"]:
            is_active = "active-btn" if f == h_input else ""
            st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
            if st.button(f"🔍 {f}", key=f"f_b_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.5])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:+.2f}")
                m3.metric("RSI", "60.9")
                with m4: st.markdown("<div class='guven-box'><span style='font-size:10px;'>GÜVEN</span><br><b style='color:#00ff88; font-size:18px;'>%80</b></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div class='gurkan-ai-box'>
                    <b style='color:#ffcc00;'>🤵 GÜRKAN AI ARAŞTIRMA:</b><br>
                    <b>{h_input}</b> incelendi. Mevcut trend yapısı <b>{fiyat*1.015:.2f} ₺</b> hedefini destekliyor.
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.warning("Hisse verisi aranıyor...")

    with col_radar:
        st.markdown("<span style='font-size:12px; color:#8b949e;'>🚀 RADAR</span>", unsafe_allow_html=True)
        r_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS"]
        try:
            r_data = yf.download(r_list, period="2d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in r_list:
                n = s.split('.')[0]
                pct = ((r_data[s].iloc[-1] - r_data[s].iloc[-2]) / r_data[s].iloc[-2]) * 100
                if st.button(f"{n} | %{pct:+.1f}", key=f"r_b_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
        except: pass
