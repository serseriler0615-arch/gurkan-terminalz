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

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Anahtar")
            if st.button("Sistemi Aç"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 14px !important; color: #00ff88 !important; letter-spacing: 1px; }
        
        /* Radar Butonları: Sinyal Destekli */
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            border-radius: 4px !important;
            font-family: 'Courier New', monospace !important;
            font-size: 11px !important;
            margin-bottom: -5px !important;
            text-align: left !important;
        }
        div.stButton > button:hover { border-color: #00ff88 !important; background: rgba(0,255,136,0.1) !important; }

        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 10px; border-radius: 8px; border: 1px solid #1c2128; }
        .skor-box { background: #0d1117; border: 1px solid #00ff88; border-radius: 10px; padding: 8px; text-align: center; }
        [data-testid="stMetricValue"] { font-size: 20px !important; color: #fff !important; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.4])

    # --- HIZLI ANALİZ FONKSİYONU ---
    def get_signal(hisse_df):
        try:
            c = hisse_df['Close'].iloc[-1]
            p = hisse_df['Close'].iloc[-2]
            ma20 = hisse_df['Close'].rolling(20).mean().iloc[-1]
            # RSI
            delta = hisse_df['Close'].diff(); g = (delta.where(delta>0,0)).rolling(14).mean(); l = (-delta.where(delta<0,0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
            
            if rsi < 35: return "🟢 AL"
            if rsi > 70: return "🔴 SAT"
            if c > ma20 and c > p: return "🟡 GÜÇ"
            return "⚪ İZLE"
        except: return "⚪ --"

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        for f in st.session_state["favorites"][-8:]:
            if st.button(f"🔍 {f}", key=f"v87_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()

    # 2. ORTA: ANALİZ VE GRAFİK
    with col_main:
        h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                direnc, destek = df['High'].tail(60).max(), df['Low'].tail(60).min()
                
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                
                # Dinamik RSI
                delta = df['Close'].diff(); g = (delta.where(delta>0,0)).rolling(14).mean(); l = (-delta.where(delta<0,0)).rolling(14).mean()
                rsi_val = 100 - (100 / (1 + (g/l))).iloc[-1]
                m3.metric("RSI (14)", f"{rsi_val:.1f}")
                
                skor_val = int((40 if fiyat > destek else 0) + (40 if rsi_val < 70 else 0) + 20)
                with m4: st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>VIP SKOR</span><br><b style='color:#00ff88; font-size:18px;'>%{skor_val}</b></div>", unsafe_allow_html=True)

                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 GÜRKAN AI:</b> {h_input} için sinyal tablosu sağda güncellendi. Grafik üzerinden yakınlaştırma yapabilirsin.</div>", unsafe_allow_html=True)

                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'], name="Mum"))
                fig.add_hline(y=direnc, line_dash="dash", line_color="#ff4b4b", opacity=0.3)
                fig.add_hline(y=destek, line_dash="dash", line_color="#0088ff", opacity=0.3)
                fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, xaxis=dict(showgrid=False, tickformat="%d %b"), yaxis=dict(showgrid=True, gridcolor='#161b22', side='right'), dragmode='zoom')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        except: st.error("Veri hatası.")

    # 3. SAĞ: SİNYAL DESTEKLİ RADAR
    with col_radar:
        st.markdown("### 🚀 VIP SİNYAL RADARI")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            # Tüm radar verisini bir kerede çek
            r_all = yf.download(t_list, period="1mo", interval="1d", progress=False)
            if isinstance(r_all.columns, pd.MultiIndex):
                close_data = r_all['Close']
            else:
                close_data = r_all
            
            for s in t_list:
                n = s.split('.')[0]
                try:
                    h_df = r_all.xs(s, level=1, axis=1) if isinstance(r_all.columns, pd.MultiIndex) else r_all
                    if isinstance(r_all.columns, pd.MultiIndex):
                        h_df = r_all.iloc[:, r_all.columns.get_level_values(1) == s]
                        h_df.columns = h_df.columns.get_level_values(0)
                    
                    c = h_df['Close'].iloc[-1]
                    p = h_df['Close'].iloc[-2]
                    pct = ((c - p) / p) * 100
                    sig = get_signal(h_df)
                    
                    # Buton Etiketi: SİNYAL | SEMBOL | FIYAT | %
                    btn_label = f"{sig} | {n.ljust(5)} | {c:>7.2f} | {pct:+.1f}%"
                    
                    if st.button(btn_label, key=f"v87_r_{n}", use_container_width=True):
                        st.session_state["last_sorgu"] = n; st.rerun()
                except: continue
        except: st.warning("Sinyaller taranıyor...")

        if st.session_state["role"] == "admin":
            st.markdown("---")
            if st.button("💎 LİSANS ÜRET"): st.code(f"GAI-{int(time.time())}-VIP")
