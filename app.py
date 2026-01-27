import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. OTURUM VE SİSTEM ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 🔐 GİRİŞ SİSTEMİ ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("SİSTEME GİR", use_container_width=True):
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

    # --- 🎨 RENKLİ TERMİNAL CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .block-container { max-width: 1250px !important; padding-top: 1rem !important; margin: auto; }
        
        /* Analiz Kutusu ve Renkli Yazılar */
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 18px; 
            border-radius: 10px; color: #ffffff; border-left: 6px solid #ffcc00; margin-bottom: 15px;
        }
        .text-green { color: #00ff88; font-weight: bold; }
        .text-red { color: #ff4b4b; font-weight: bold; }
        .text-yellow { color: #ffcc00; font-weight: bold; }
        .text-blue { color: #00d4ff; font-weight: bold; }
        
        /* Metriklerin Renklenmesi */
        [data-testid="stMetricValue"] { font-size: 24px !important; }

        /* Butonlar */
        div.stButton > button { background-color: #1c2128 !important; border: 1px solid #30363d !important; border-radius: 6px !important; height: 38px !important; }
        .active-btn button { background-color: #238636 !important; border-color: #2ea043 !important; color: white !important; font-weight: bold; }
        .del-btn button { color: #ff4b4b !important; border: none !important; background: transparent !important; font-size: 18px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ADMIN PANEL ---
    if st.session_state["role"] == "admin":
        ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.4])
        with ac1: s_gun = st.selectbox("Süre", [30, 90, 365, 999], label_visibility="collapsed")
        with ac2: 
            if st.button("💎 KEY ÜRET", use_container_width=True): 
                st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
        with ac3: 
            if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
        with ac4:
            if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()
        st.divider()

    # --- 🔍 ÜST BAR ---
    st.markdown("<h2 style='color:#ffcc00; text-align:center; font-size:26px;'>★ GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
    _, sc2, sc3, _ = st.columns([2, 2.5, 0.7, 2])
    with sc2:
        h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol Ara...", label_visibility="collapsed").upper().strip()
    with sc3:
        if st.button("➕ EKLE", use_container_width=True):
            if h_input not in st.session_state["favorites"]:
                st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_fav, col_main, col_radar = st.columns([1, 4, 1.2])

    with col_fav:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>TAKİP</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f"{f}", key=f"f_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with cf2:
                if st.button("×", key=f"d_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()

    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                # --- 🧠 ZEKA VE RENK HESAPLARI ---
                last_p = float(df['Close'].iloc[-1])
                change = ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
                
                # RSI Hesapla
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                
                # Renk Belirleyiciler
                c_rsi = "text-red" if rsi > 70 else ("text-green" if rsi < 30 else "text-blue")
                c_ma = "text-green" if last_p > ma20 else "text-red"
                c_chg = "text-green" if change > 0 else "text-red"

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("SON FİYAT", f"{last_p:.2f} ₺")
                m2.metric("GÜNLÜK", f"%{change:+.2f}")
                m3.metric("RSI (14)", f"{rsi:.1f}")
                m4.metric("20G ORT", f"{ma20:.2f}")

                # --- 🤵 GÜRKAN PRO ANALİZ (RENKLİ METİNLER) ---
                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <b style='color:#ffcc00; font-size:20px;'>🤵 GÜRKAN PRO ANALİZ</b><br><br>
                    <p style='font-size:16px; line-height:1.8;'>
                        Hisse: <span class='text-blue'>{h_input}</span> | Durum: <span class='{c_chg}'>{'YÜKSELİŞTE' if change > 0 else 'DÜŞÜŞTE'}</span><br>
                        • RSI Değeri: <span class='{c_rsi}'>{rsi:.1f}</span> ({'Aşırı Alım - Riskli' if rsi > 70 else ('Aşırı Satım - Fırsat' if rsi < 30 else 'Normal Bölge')})<br>
                        • Trend Analizi: Fiyat, 20 günlük ortalamanın <span class='{c_ma}'>{'ÜZERİNDE' if last_p > ma20 else 'ALTINDA'}</span> seyrediyor.<br>
                        • Hedef Bölge: <span class='text-green'>{last_p*1.025:.2f} ₺</span> | Destek: <span class='text-red'>{last_p*0.975:.2f} ₺</span><br>
                        <b>STRATEJİ:</b> <span style='background:#ffcc00; color:black; padding:2px 6px; border-radius:4px;'>{'POZİSYONU KORU' if last_p > ma20 else 'TEPKİ BEKLE'}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.info("Veri analiz ediliyor...")

    with col_radar:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE"]:
            if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
