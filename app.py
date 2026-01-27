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
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "AKBNK", "TUPRS"]
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"
if "currency" not in st.session_state:
    st.session_state["currency"] = "TRY"

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        k = st.text_input("💎 VIP KEY")
        if st.button("Sistemi Aç"):
            if k.startswith("GAI-"): 
                st.session_state["access_granted"] = True; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 14px !important; color: #00ff88 !important; }
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            font-family: 'Courier New', monospace !important;
            font-size: 11px !important;
        }
        .currency-btn {
            background: #1c2128 !important;
            color: #00ff88 !important;
            border: 1px solid #00ff88 !important;
            font-weight: bold !important;
        }
        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 10px; border-radius: 8px; border: 1px solid #1c2128; }
        .skor-box { background: #0d1117; border: 1px solid #00ff88; border-radius: 10px; padding: 8px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    # KUR VERİSİ ÇEK (Global kullanım için)
    @st.cache_data(ttl=3600)
    def get_usd_rate():
        try:
            usd_data = yf.download("USDTRY=X", period="1d", progress=False)
            return float(usd_data['Close'].iloc[-1])
        except: return 30.0 # Hata durumunda güvenli varsayılan

    usd_rate = get_usd_rate()
    curr_symbol = "$" if st.session_state["currency"] == "USD" else "₺"

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.4])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in st.session_state["favorites"][-8:]:
            if st.button(f"🔍 {f}", key=f"v88_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()

    # 2. ORTA: ANALİZ VE GRAFİK
    with col_main:
        h1, h2 = st.columns([3, 1])
        with h1:
            h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        with h2:
            # PARA BİRİMİ SEÇİCİ
            if st.button(f"Para Birimi: {st.session_state['currency']}", key="curr_toggle", use_container_width=True):
                st.session_state["currency"] = "USD" if st.session_state["currency"] == "TRY" else "TRY"
                st.rerun()

        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                # KUR DÖNÜŞÜMÜ
                if st.session_state["currency"] == "USD":
                    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] / usd_rate
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                direnc, destek = df['High'].tail(60).max(), df['Low'].tail(60).min()
                
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{curr_symbol}{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("KUR", f"₺{usd_rate:.2f}")
                
                with m4: st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>VIP SKOR</span><br><b style='color:#00ff88; font-size:18px;'>%84</b></div>", unsafe_allow_html=True)

                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 GÜRKAN AI:</b> Analiz şu an <b>{st.session_state['currency']}</b> bazlıdır. Dolar bazlı direnç: {curr_symbol}{direnc:.2f}</div>", unsafe_allow_html=True)

                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'], name=st.session_state["currency"]))
                fig.add_hline(y=direnc, line_dash="dash", line_color="#ff4b4b", opacity=0.3)
                fig.add_hline(y=destek, line_dash="dash", line_color="#0088ff", opacity=0.3)
                fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, xaxis=dict(showgrid=False, tickformat="%d %b"), yaxis=dict(showgrid=True, gridcolor='#161b22', side='right'), dragmode='zoom')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        except: st.error("Veri hatası.")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("### 🚀 SİNYAL RADARI")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            r_all = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_all.columns, pd.MultiIndex): r_all.columns = r_all.columns.get_level_values(0)
            
            for s in t_list:
                n = s.split('.')[0]
                try:
                    c = r_all[s].iloc[-1]
                    # Radar her zaman TL gösterir (Sabitlik için)
                    p = r_all[s].iloc[-2]
                    pct = ((c - p) / p) * 100
                    btn_label = f"🔍 {n.ljust(6)} | {c:>7.2f} | {pct:+.1f}%"
                    if st.button(btn_label, key=f"v88_r_{n}", use_container_width=True):
                        st.session_state["last_sorgu"] = n; st.rerun()
                except: continue
        except: st.warning("Veriler güncelleniyor...")
