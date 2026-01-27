import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM VE GİRİŞ (ADMİN GERİ GELDİ) ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "AKBNK", "TUPRS"]
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"
if "currency" not in st.session_state:
    st.session_state["currency"] = "TRY"

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
            u = st.text_input("Admin ID")
            p = st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 14px !important; color: #00ff88 !important; }
        div.stButton > button { background-color: rgba(0, 255, 136, 0.02) !important; color: #00ff88 !important; border: 1px solid #1c2128 !important; font-size: 11px !important; }
        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 12px; border-radius: 8px; border: 1px solid #1c2128; }
        .target-box { background: rgba(0, 255, 136, 0.05); border: 1px dashed #00ff88; padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # KUR VERİSİ
    @st.cache_data(ttl=3600)
    def get_usd_rate():
        try: return float(yf.download("USDTRY=X", period="1d", progress=False)['Close'].iloc[-1])
        except: return 34.50

    usd_rate = get_usd_rate()
    curr_sym = "$" if st.session_state["currency"] == "USD" else "₺"

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.4])

    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in st.session_state["favorites"][-8:]:
            if st.button(f"🔍 {f}", key=f"v89_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()

    with col_main:
        h1, h2 = st.columns([3, 1])
        with h1: h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        with h2:
            if st.button(f"Birim: {st.session_state['currency']}", use_container_width=True):
                st.session_state["currency"] = "USD" if st.session_state["currency"] == "TRY" else "TRY"; st.rerun()

        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="1y", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                if st.session_state["currency"] == "USD": df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] / usd_rate
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # --- 🎯 HEDEF FİYAT HESAPLAMA (Özellik 3) ---
                zirve = df['High'].max()
                hedef = zirve * 1.15 # Teknik zirve + %15 VIP potansiyel
                potansiyel = ((hedef - fiyat) / fiyat) * 100

                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{curr_sym}{fiyat:.2f}")
                m2.metric("POTANSİYEL", f"%{potansiyel:.1f}")
                m3.metric("HEDEF", f"{curr_sym}{hedef:.2f}")
                with m4: st.markdown(f"<div style='background:#0d1117; border:1px solid #00ff88; border-radius:10px; padding:8px; text-align:center;'><span style='font-size:10px;'>VIP GÜVEN</span><br><b style='color:#00ff88; font-size:18px;'>%88</b></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88;'>🤵 GÜRKAN AI:</b> {h_input} için orta vadeli hedefimiz <b>{curr_sym}{hedef:.2f}</b>. 
                    Bu seviyeye kadar <b>%{potansiyel:.1f}</b> yükseliş alanı mevcut.
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'])])
                fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, xaxis=dict(showgrid=False, tickformat="%d %b"), yaxis=dict(showgrid=True, gridcolor='#161b22', side='right'), dragmode='zoom')
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Veri hatası.")

    with col_radar:
        st.markdown("### 🚀 SİNYAL RADARI")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        r_all = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
        if isinstance(r_all.columns, pd.MultiIndex): r_all.columns = r_all.columns.get_level_values(0)
        for s in t_list:
            n = s.split('.')[0]
            try:
                c, p = r_all[s].iloc[-1], r_all[s].iloc[-2]
                pct = ((c - p) / p) * 100
                btn_txt = f"🔍 {n.ljust(6)} | {c:>7.2f} | {pct:+.1f}%"
                if st.button(btn_txt, key=f"v89_r_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
            except: continue
        
        # --- ADMİN PANELİ GERİ GELDİ ---
        if st.session_state["role"] == "admin":
            st.markdown("---")
            st.markdown("### 🔐 ADMİN TOOLS")
            if st.button("💎 YENİ KEY ÜRET"): st.code(f"GAI-{int(time.time())}-VIP")
            if st.button("🚪 ÇIKIŞ YAP"): st.session_state["access_granted"] = False; st.rerun()
