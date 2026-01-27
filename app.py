import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. OTURUM ---
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
        st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Key", type="password")
                if st.form_submit_button("GİRİŞ", use_container_width=True):
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

    # --- 🎨 ULTRA MİKRO CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        /* Tüm içeriği daralt */
        .block-container { max-width: 1100px !important; padding-top: 0.5rem !important; padding-bottom: 0rem !important; margin: auto; }
        
        .main-header { font-size: 18px !important; font-weight: bold; color: #ffcc00; text-align: center; margin-bottom: 5px; }
        
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 8px 12px; 
            border-radius: 4px; color: #ffffff; border-left: 3px solid #ffcc00; margin-bottom: 8px; font-size: 12px;
        }
        
        /* Metrikleri Küçült */
        [data-testid="stMetricValue"] { font-size: 16px !important; font-weight: bold !important; }
        [data-testid="stMetricLabel"] { font-size: 10px !important; color: #8b949e !important; }
        [data-testid="stMetricDelta"] { font-size: 11px !important; }

        /* Butonları Mikro Yap */
        div.stButton > button {
            background-color: #1c2128 !important; color: #e0e0e0 !important;
            border: 1px solid #30363d !important; border-radius: 3px !important;
            height: 28px !important; font-size: 11px !important; padding: 0px 5px !important;
        }
        .active-btn button { background-color: #238636 !important; border-color: #2ea043 !important; color: white !important; }
        .del-btn button { color: #ff4b4b !important; border: none !important; background: transparent !important; font-size: 14px !important; height: 28px !important; }
        
        /* Sütun aralarını daralt */
        [data-testid="column"] { padding: 0 5px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔍 ÜST BAR (KÜÇÜK VE MERKEZİ) ---
    st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    
    # Arama motoru kolonlarını çok daha dar yaptık
    _, sc2, sc3, _ = st.columns([3, 2, 0.5, 3])
    with sc2:
        h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Hisse...", label_visibility="collapsed").upper().strip()
    with sc3:
        if st.button("➕"):
            if h_input not in st.session_state["favorites"]:
                st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_fav, col_main, col_radar = st.columns([0.7, 3.5, 0.8])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("<p style='color:#444; font-size:9px; margin-bottom:5px; font-weight:bold;'>LİSTE</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([3, 1])
            with cf1:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f"{f}", key=f"f_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with cf2:
                st.markdown("<div class='del-btn'>", unsafe_allow_html=True)
                if st.button("×", key=f"d_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ
    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="3mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                last_p = float(df['Close'].iloc[-1])
                change = ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # Metrikler (Sıkıştırılmış)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("FİYAT", f"{last_p:.2f}")
                m2.metric("GÜNLÜK", f"%{change:+.2f}")
                m3.metric("HACİM", f"{df['Volume'].iloc[-1]:,.0f}")
                m4.metric("DİRENÇ", f"{last_p*1.02:.2f}")

                # GÜRKAN PRO (Mini Kutu)
                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <b>🤵 GÜRKAN PRO:</b> {h_input} {'yükseliş trendinde' if change > 0 else 'düzeltme aşamasında'}. 
                    Güvenli bölge: <b>{last_p*0.98:.2f}</b>, Hedef: <b>{last_p*1.03:.2f}</b>.
                </div>
                """, unsafe_allow_html=True)

                # Grafik (Mikro Boyut)
                fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
                fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9)))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.empty()

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("<p style='color:#444; font-size:9px; margin-bottom:5px; font-weight:bold;'>RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "SISE"]:
            if st.button(f"{r}", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
