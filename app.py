import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        k = st.text_input("Giriş Anahtarı", type="password")
        if st.button("Sistemi Başlat"):
            if k.startswith("GAI-"): 
                st.session_state["access_granted"] = True; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP v96", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE (HATASIZ) ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .asistan-box { 
            background: #0d1117; border-left: 5px solid #00ff88; padding: 15px; 
            border-radius: 10px; border: 1px solid #1c2128; color: #e0e0e0; margin-bottom: 20px;
        }
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.05) !important;
            color: #00ff88 !important; border: 1px solid #1c2128 !important;
            text-align: left !important; font-family: monospace !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.4])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in list(st.session_state["favorites"]):
            c1, c2 = st.columns([4, 1])
            if c1.button(f"🔍 {f}", key=f"fav_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            if c2.button("X", key=f"del_{f}"):
                st.session_state["favorites"].remove(f); st.rerun()

    # 2. ORTA: ANALİZ + AI YORUM
    with col_main:
        h1, h2 = st.columns([3, 1])
        h_input = h1.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper()
        if h2.button("⭐ EKLE") and h_input not in st.session_state["favorites"]:
            st.session_state["favorites"].append(h_input); st.rerun()

        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            # GÜVENLİ VERİ ÇEKME
            df = yf.download(sembol, period="3mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                tahmin = fiyat * (1 + (degisim/200)) # Gürkan AI Projeksiyonu

                # 🤵 GÜRKAN AI YORUMU
                yon = "yükseliş" if degisim > 0 else "düşüş"
                renk = "#00ff88" if degisim > 0 else "#ff4b4b"
                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88;'>🤵 GÜRKAN AI ÖZEL ARAŞTIRMASI:</b><br>
                    <b>{h_input}</b> bugün <span style='color:{renk}'>%{degisim:.2f} {yon}</span> eğiliminde. 
                    Verileri taradım; yarın fiyatın <b>{tahmin:.2f} ₺</b> seviyelerini test etmesini bekliyorum.
                </div>
                """, unsafe_allow_html=True)

                st.metric(f"{h_input} GÜNCEL", f"{fiyat:.2f} ₺", f"%{degisim:.2f}")

                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Hisse bulunamadı.")
        except:
            st.warning("Veri çekilemedi, lütfen tekrar deneyin.")

    # 3. SAĞ: STABİL RADAR
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS"]
        for s in t_list:
            n = s.split('.')[0]
            try:
                # Radar için sadece son 2 günü çekerek sistemi yormuyoruz
                r_val = yf.download(s, period="2d", progress=False)['Close']
                if not r_val.empty:
                    c = r_val.iloc[-1]
                    if st.button(f"{n.ljust(6)} | {c:>7.2f}", key=f"r_{n}", use_container_width=True):
                        st.session_state["last_sorgu"] = n; st.rerun()
            except: continue
