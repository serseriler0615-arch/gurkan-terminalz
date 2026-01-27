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
    st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS"]

# --- GİRİŞ KONTROL ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Giriş Anahtarı", type="password")
            if st.button("Sistemi Başlat"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2026!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP v99", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP TRENDY STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .asistan-box { background: #0d1117; border-left: 5px solid #00ff88; padding: 12px; border-radius: 8px; border: 1px solid #1c2128; font-size: 13px; margin-bottom: 15px; }
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.05) !important;
            color: #00ff88 !important; border: 1px solid #1c2128 !important;
            text-align: left !important; font-family: 'Courier New', monospace !important; font-size: 12px !important;
        }
        .admin-mini { padding: 10px; border: 1px dashed #00ff88; border-radius: 5px; margin-bottom: 20px; background: rgba(0,255,136,0.02); }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔐 KOMPAKT ADMİN PANELİ (ÜSTTE KÜÇÜK) ---
    if st.session_state["role"] == "admin":
        with st.container():
            c1, c2, c3, c4 = st.columns([1, 1, 1.5, 0.5])
            with c1: s_gun = st.selectbox("Süre", [30, 90, 365], label_visibility="collapsed")
            with c2: 
                if st.button("💎 KEY ÜRET"):
                    st.session_state["generated_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
            with c3: 
                if "generated_key" in st.session_state: st.code(st.session_state["generated_key"])
            with c4:
                if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.4])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in list(st.session_state["favorites"]):
            cx, cy = st.columns([4, 1])
            if cx.button(f"🔍 {f}", key=f"v99_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            if cy.button("X", key=f"v99_d_{f}"):
                st.session_state["favorites"].remove(f); st.rerun()

    # 2. ORTA: ANALİZ VE GÜRKAN AI
    with col_main:
        h1, h2 = st.columns([3, 1])
        h_input = h1.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper()
        if h2.button("⭐ LİSTEYE EKLE") and h_input not in st.session_state["favorites"]:
            st.session_state["favorites"].append(h_input); st.rerun()

        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                tahmin = fiyat * (1 + (degisim/160))

                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88;'>🤵 GÜRKAN AI ANALİZ:</b> {h_input} bugün %{degisim:.2f} hareketle {fiyat:.2f} ₺ seviyesinde. 
                    <b>Yarın beklentim:</b> Fiyatın <b>{tahmin:.2f} ₺</b> civarını görmesi yönünde.
                </div>
                """, unsafe_allow_html=True)

                st.metric(f"{h_input}", f"{fiyat:.2f} ₺", f"%{degisim:.2f}")
                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Veri hatası.")

    # 3. SAĞ: TRENDY RADAR (FULL)
    with col_radar:
        st.markdown("### 🚀 TRENDY RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "BIMAS.IS", "SISE.IS", "KCHOL.IS"]
        try:
            r_data = yf.download(t_list, period="2d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in t_list:
                n = s.split('.')[0]
                c, p = r_data[s].iloc[-1], r_data[s].iloc[-2]
                pct = ((c - p) / p) * 100
                sign = "↑" if pct > 0 else "↓"
                label = f"{sign} {n.ljust(6)} | {c:>7.2f} | {pct:+.1f}%"
                if st.button(label, key=f"rad_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
        except: st.write("Yükleniyor...")
