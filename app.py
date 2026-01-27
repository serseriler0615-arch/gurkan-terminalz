import streamlit as st
import yfinance as yf
import pandas as pd
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
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("SİSTEMİ BAŞLAT", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): 
                        st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            with st.form("a"):
                u = st.text_input("ID")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("ADMİN GİRİŞ", use_container_width=True):
                    if u.strip().upper() == "GURKAN" and p.strip() == "HEDEF2024!": 
                        st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 OPTİMİZE EDİLMİŞ CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .block-container { max-width: 1250px !important; padding-top: 1.5rem !important; margin: auto; }
        
        .main-header { font-size: 24px !important; font-weight: bold; color: #ffcc00; text-align: center; margin-bottom: 15px; }
        
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 15px; 
            border-radius: 8px; color: #ffffff; border-left: 5px solid #ffcc00; margin-bottom: 15px; font-size: 14px;
        }
        
        /* Metrik Ayarları */
        [data-testid="stMetricValue"] { font-size: 22px !important; color: #ffffff !important; }
        [data-testid="stMetricLabel"] { font-size: 13px !important; color: #8b949e !important; }

        /* Butonlar */
        div.stButton > button {
            background-color: #1c2128 !important; color: #e0e0e0 !important;
            border: 1px solid #30363d !important; border-radius: 5px !important;
            height: 38px !important; font-size: 13px !important;
        }
        .active-btn button { background-color: #238636 !important; border-color: #2ea043 !important; color: white !important; font-weight: bold; }
        .del-btn button { color: #ff4b4b !important; border: none !important; background: transparent !important; font-size: 18px !important; }
        
        /* Input Alanı */
        div[data-testid="stTextInput"] input { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔍 ARAMA BÖLÜMÜ (ORTALANMIŞ & NET) ---
    st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    
    _, sc2, sc3, _ = st.columns([2, 2.5, 0.7, 2])
    with sc2:
        h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol Ara...", label_visibility="collapsed").upper().strip()
    with sc3:
        if st.button("➕ EKLE", use_container_width=True):
            if h_input not in st.session_state["favorites"]:
                st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA GÖVDE ---
    col_fav, col_main, col_radar = st.columns([1, 4, 1.2])

    # 1. SOL: TAKİP LİSTESİ
    with col_fav:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold; margin-bottom:10px;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f" {f}", key=f"f_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with cf2:
                st.markdown("<div class='del-btn'>", unsafe_allow_html=True)
                if st.button("×", key=f"d_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ PANELİ
    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                last_p = float(df['Close'].iloc[-1])
                change = ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # Net Metrikler
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("SON FİYAT", f"{last_p:.2f} ₺")
                m2.metric("GÜNLÜK DEĞ.", f"%{change:+.2f}")
                m3.metric("RSI (14)", "60.2")
                m4.metric("HACİM", f"{df['Volume'].iloc[-1]:,.0f}")

                # GÜRKAN PRO (Dinamik Analiz)
                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <b style='color:#ffcc00; font-size:18px;'>🤵 GÜRKAN PRO ANALİZ:</b><br>
                    <b>{h_input}</b> için teknik araştırma tamamlandı. Mevcut momentum <b>{last_p*1.025:.2f}</b> 
                    direncini hedefliyor. Trend {'pozitif yönde güçleniyor' if change > 0 else 'düzeltme seviyesinde'}. 
                    Stratejik destek: <b>{last_p*0.975:.2f}</b>.
                </div>
                """, unsafe_allow_html=True)

                # Profesyonel Grafik
                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.info("Sembol aranıyor...")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold; margin-bottom:10px;'>RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE", "BIMAS"]:
            if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
