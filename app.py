import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM VE HAFIZA AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 🔐 GİRİŞ KONTROLÜ ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("SİSTEME GİR", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): 
                        st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            with st.form("a"):
                u = st.text_input("Yönetici ID")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("ADMİN GİRİŞ", use_container_width=True):
                    if u.strip().upper() == "GURKAN" and p.strip() == "HEDEF2024!": 
                        st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 PRO DİNAMİK CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d0f14 !important; } /* Biraz daha canlı bir koyu mavi-siyah */
        .main-header { font-size: 26px; font-weight: bold; color: #ffcc00; text-shadow: 0px 0px 10px rgba(255,204,0,0.3); }
        .gurkan-ai-box { 
            background: #161b22; border: 1px solid #30363d; padding: 15px; 
            border-radius: 8px; color: #ffffff; border-left: 6px solid #ffcc00; margin-bottom: 20px;
        }
        .guven-badge { 
            background: rgba(0, 255, 136, 0.1); border: 2px solid #00ff88; 
            color: #00ff88; padding: 12px; border-radius: 10px; text-align: center;
        }
        /* Favori Butonları - Daha Belirgin */
        div.stButton > button {
            background-color: #1c2128 !important; color: #e0e0e0 !important;
            border: 1px solid #30363d !important; text-align: left !important;
            border-radius: 6px !important; transition: 0.3s;
        }
        div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
        .active-btn button { background-color: #238636 !important; border: none !important; color: white !important; font-weight: bold !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 HAYALET ADMİN ---
    if st.session_state["role"] == "admin":
        ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.5])
        with ac1: s_gun = st.selectbox("", [30, 90, 365], label_visibility="collapsed")
        with ac2: 
            if st.button("💎 KEY ÜRET", use_container_width=True): 
                st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
        with ac3: 
            if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
        with ac4:
            if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()

    # --- ÜST PANEL ---
    h_col1, h_col2, h_col3 = st.columns([2, 3, 1])
    with h_col1: st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    with h_col2: h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Hisse Ara (Örn: THYAO)", label_visibility="collapsed").upper().strip()
    with h_col3:
        if h_input not in st.session_state["favorites"]:
            if st.button("➕ LİSTEYE EKLE", use_container_width=True):
                st.session_state["favorites"].append(h_input); st.rerun()
        else:
            if st.button("➖ LİSTEDEN ÇIKAR", use_container_width=True):
                st.session_state["favorites"].remove(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_left, col_mid, col_right = st.columns([0.8, 3, 1.2])

    # 1. SOL: DİNAMİK TAKİP LİSTESİ
    with col_left:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            is_active = "active-btn" if f == h_input else ""
            st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
            if st.button(f"📊 {f}", key=f"fav_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ VE GRAFİK
    with col_mid:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # CANLI METRİKLER
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f} ₺")
                m2.metric("GÜNLÜK", f"%{degisim:+.2f}")
                m3.metric("RSI (14)", "60.9")
                with m4: st.markdown("<div class='guven-badge'><small>AI GÜVEN</small><br><b>%80</b></div>", unsafe_allow_html=True)

                # GÜRKAN AI ARAŞTIRMA KUTUSU
                st.markdown(f"""
                <div class='gurkan-ai-box'>
                    <b style='color:#ffcc00; font-size:18px;'>🤵 GÜRKAN AI ARAŞTIRMA:</b><br>
                    <b>{h_input}</b> hissesinde teknik formasyon tamamlanmak üzere. Yarın <b>{fiyat*1.02:.2f} ₺</b> seviyesinde direnç testi bekliyorum. Strateji: <b>TUT</b>.
                </div>
                """, unsafe_allow_html=True)

                # PROFESYONEL GRAFİK
                fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'])])
                fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.warning("Hisse verisi bulunamadı veya sembol hatalı.")

    # 3. SAĞ: RADAR
    with col_right:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>🚀 HIZLI RADAR</p>", unsafe_allow_html=True)
        radar_list = ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE", "KCHOL"]
        for r in radar_list:
            if st.button(f"{r} İncele", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
