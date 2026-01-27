import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "AKBNK", "TUPRS"]
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP")
        k = st.text_input("💎 VIP KEY", type="password")
        if st.button("BAŞLAT"):
            if k.startswith("GAI-"): 
                st.session_state["access_granted"] = True
                st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 ULTRA DARK UI CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 15px !important; color: #00ff88 !important; margin-bottom: 8px !important; }
        p, span, div { color: #e0e0e0 !important; font-size: 13px !important; }
        
        /* Buton Tasarımı - Beyazlık Yok */
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            border-radius: 4px !important;
            padding: 4px !important;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            border-color: #00ff88 !important;
            box-shadow: 0 0 10px rgba(0,255,136,0.15);
        }

        .asistan-box { 
            background: #0d1117; 
            border-left: 4px solid #00ff88; 
            padding: 10px; 
            border-radius: 6px; 
            margin-bottom: 12px;
            border: 1px solid #1c2128;
            border-left: 4px solid #00ff88;
        }

        .skor-box { 
            background: #0d1117; 
            border: 1px solid #00ff88; 
            border-radius: 8px; 
            padding: 8px; 
            text-align: center;
        }
        [data-testid="stMetricValue"] { font-size: 20px !important; color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        for f in st.session_state["favorites"][-7:]:
            if st.button(f"🔍 {f}", key=f"v80_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
        
        new_f = st.text_input("", placeholder="+Ekle", key="v80_add", label_visibility="collapsed").upper().strip()
        if new_f and len(new_f) > 2:
            if new_f not in st.session_state["favorites"]:
                st.session_state["favorites"].append(new_f); st.rerun()

    # 2. ORTA: ANA ANALİZ
    with col_main:
        h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                delta = df['Close'].diff(); g = (delta.where(delta>0,0)).rolling(14).mean(); l = (-delta.where(delta<0,0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
                skor = (40 if fiyat > ma20 else 0) + (40 if 45 < rsi < 75 else 0) + (20 if degisim > 0 else 0)

                # Metrikler
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                with m4:
                    st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>GÜVEN</span><br><b style='color:#00ff88; font-size:18px;'>%{int(skor)}</b></div>", unsafe_allow_html=True)

                # Gürkan AI Yorum
                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 GÜRKAN AI:</b> {h_input} %{int(skor)} güven skoru ile {'pozitif' if skor > 60 else 'izleme'} bölgesinde. RSI: {int(rsi)}.</div>", unsafe_allow_html=True)

                # Grafik
                fig = go.Figure(data=[go.Scatter(x=df.tail(50).index, y=df.tail(50)['Close'], fill='tozeroy', line=dict(color='#00ff88', width=2), fillcolor='rgba(0,255,136,0.04)')])
                fig.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1c2128', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.error("Veri hatası.")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("### 🚀 RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            r_data = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in t_list:
                n = s.split('.')[0]
                try:
                    c, p = r_data[s].iloc[-1], r_data[s].iloc[-2]
                    pct = ((c - p) / p) * 100
                    if st.button(f"{n} | %{pct:.1f}", key=f"v80_r_{n}", use_container_width=True):
                        st.session_state["last_sorgu"] = n; st.rerun()
                except: continue
        except: pass
