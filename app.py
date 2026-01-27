import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM VE GİRİŞ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS", "BIMAS"]
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
            u, p = st.text_input("Admin ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP v90", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .news-card { background: #0d1117; border-left: 3px solid #00ff88; padding: 10px; border-radius: 5px; margin-bottom: 8px; border: 1px solid #1c2128; }
        .news-time { color: #8b949e; font-size: 10px; margin-bottom: 4px; }
        .news-title { color: #e0e0e0; font-size: 12px; font-weight: bold; }
        div.stButton > button { background-color: rgba(0, 255, 136, 0.02) !important; color: #00ff88 !important; border: 1px solid #1c2128 !important; }
        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 12px; border-radius: 8px; border: 1px solid #1c2128; }
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

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in st.session_state["favorites"][-8:]:
            if st.button(f"🔍 {f}", key=f"v90_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()

    # 2. ORTA: ANALİZ + HABERLER
    with col_main:
        h1, h2 = st.columns([3, 1])
        with h1: h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        with h2:
            if st.button(f"Birim: {st.session_state['currency']}", use_container_width=True):
                st.session_state["currency"] = "USD" if st.session_state["currency"] == "TRY" else "TRY"; st.rerun()

        sembol = h_input if "." in h_input else h_input + ".IS"
        ticker = yf.Ticker(sembol)
        
        try:
            df = ticker.history(period="6mo")
            if not df.empty:
                if st.session_state["currency"] == "USD": df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] / usd_rate
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{curr_sym}{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("RSI", "52.4")
                with m4: st.markdown(f"<div style='background:#0d1117; border:1px solid #00ff88; border-radius:10px; padding:8px; text-align:center;'><span style='font-size:10px;'>VIP PUAN</span><br><b style='color:#00ff88; font-size:18px;'>%90</b></div>", unsafe_allow_html=True)

                # GRAFİK
                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=320, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22'))
                st.plotly_chart(fig, use_container_width=True)

                # --- 🗞️ CANLI HABER AKIŞI ---
                st.markdown("### 🗞️ SON DAKİKA HABERLERİ")
                news = ticker.news[:5] # Son 5 haberi al
                if news:
                    for item in news:
                        tm = time.strftime('%H:%M', time.localtime(item['providerPublishTime']))
                        st.markdown(f"""
                        <div class='news-card'>
                            <div class='news-time'>🕒 {tm} - {item['publisher']}</div>
                            <div class='news-title'>{item['title']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Bu hisse için güncel haber akışı bulunamadı.")
        except: st.error("Veri akışında bir sorun oluştu.")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("### 🚀 SİNYAL RADARI")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        r_all = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
        for s in t_list:
            n = s.split('.')[0]
            try:
                c, p = r_all[s].iloc[-1], r_all[s].iloc[-2]
                pct = ((c - p) / p) * 100
                btn_txt = f"🔍 {n.ljust(6)} | {c:>7.2f} | {pct:+.1f}%"
                if st.button(btn_txt, key=f"v90_r_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
            except: continue
        
        if st.session_state["role"] == "admin":
            st.markdown("---")
            if st.button("💎 LİSANS ÜRET"): st.code(f"GAI-{int(time.time())}-VIP")
