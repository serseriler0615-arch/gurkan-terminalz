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

# --- GİRİŞ FONKSİYONU (ADMİN PANELİ DAHİL) ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY GİRİŞİ", "🔐 YÖNETİCİ PANELİ"])
        
        with t1:
            k = st.text_input("Giriş Anahtarı", type="password")
            if st.button("Sistemi Başlat"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
                else: st.error("Geçersiz Anahtar!")
        
        with t2:
            u = st.text_input("Admin ID")
            p = st.text_input("Admin Şifre", type="password")
            if st.button("Admin Olarak Gir"):
                if u.upper() == "GURKAN" and p == "HEDEF2026!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
                else: st.error("Yetkisiz Giriş!")
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP v98", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .asistan-box { background: #0d1117; border-left: 5px solid #00ff88; padding: 15px; border-radius: 10px; border: 1px solid #1c2128; color: #e0e0e0; margin-bottom: 20px; }
        .admin-panel { background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88; padding: 20px; border-radius: 10px; margin-top: 20px; }
        div.stButton > button { background-color: rgba(0, 255, 136, 0.05) !important; color: #00ff88 !important; border: 1px solid #1c2128 !important; font-family: monospace; }
        </style>
    """, unsafe_allow_html=True)

    # --- ADMİN ÖZEL PANELİ (ÜST KISIMDA) ---
    if st.session_state["role"] == "admin":
        with st.expander("🔐 VIP LİSANS ÜRETİM MERKEZİ", expanded=True):
            col_k1, col_k2, col_k3 = st.columns([1, 1, 1])
            with col_k1:
                sure = st.selectbox("Lisans Süresi", [30, 90, 365], format_func=lambda x: f"{x} Günlük")
            with col_k2:
                isim = st.text_input("Kullanıcı Adı/ID", placeholder="Örn: Ahmet")
            with col_k3:
                if st.button("💎 YENİ KEY OLUŞTUR", use_container_width=True):
                    yeni_key = f"GAI-{sure}-{int(time.time()) % 10000}-VIP"
                    st.success(f"Key Üretildi: {yeni_key}")
                    st.code(yeni_key)
            if st.button("🚪 ADMİN ÇIKIŞI"):
                st.session_state["access_granted"] = False; st.rerun()

    # --- ANA TERMİNAL ---
    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.4])

    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in list(st.session_state["favorites"]):
            c1, c2 = st.columns([4, 1])
            if c1.button(f"🔍 {f}", key=f"fav_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            if c2.button("X", key=f"del_{f}"):
                st.session_state["favorites"].remove(f); st.rerun()

    with col_main:
        h1, h2 = st.columns([3, 1])
        h_input = h1.text_input("HİSSE ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper()
        if h2.button("⭐ EKLE"):
            if h_input not in st.session_state["favorites"]: st.session_state["favorites"].append(h_input); st.rerun()

        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                tahmin = fiyat * (1 + (degisim/180))

                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88; font-size:16px;'>🤵 GÜRKAN AI ÖZEL ARAŞTIRMASI:</b><br>
                    <b>{h_input}</b> hissesini inceledim. Yarın fiyatın <b>{tahmin:.2f} ₺</b> seviyelerini test etmesini bekliyorum.
                </div>
                """, unsafe_allow_html=True)

                st.metric(f"{h_input} GÜNCEL", f"{fiyat:.2f} ₺", f"%{degisim:.2f}")
                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.warning("Veri çekilemedi.")

    with col_radar:
        st.markdown("### 🚀 TRENDY RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS"]
        try:
            r_data = yf.download(t_list, period="2d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in t_list:
                n = s.split('.')[0]
                c = r_data[s].iloc[-1]
                p = r_data[s].iloc[-2]
                pct = ((c - p) / p) * 100
                btn_label = f"{n.ljust(6)} | {c:>7.2f} | {pct:+.1f}%"
                if st.button(btn_label, key=f"r_v98_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
        except: pass
