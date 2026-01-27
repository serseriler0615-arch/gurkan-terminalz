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
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            border-radius: 4px !important;
            transition: 0.3s;
        }
        div.stButton > button:hover { border-color: #00ff88 !important; }
        .asistan-box { 
            background: #0d1117; 
            border-left: 4px solid #00ff88; 
            padding: 10px; 
            border-radius: 6px; 
            margin-bottom: 12px;
            border: 1px solid #1c2128;
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

    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        for f in st.session_state["favorites"][-7:]:
            if st.button(f"🔍 {f}", key=f"v81_f_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()

    with col_main:
        h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # --- OTOMATİK DESTEK/DİRENÇ HESABI ---
                # Son 60 günün en yüksek ve düşüğü
                direnc = df['High'].tail(60).max()
                destek = df['Low'].tail(60).min()
                pivot = (direnc + destek + fiyat) / 3

                # Teknik Metrikler
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                delta = df['Close'].diff(); g = (delta.where(delta>0,0)).rolling(14).mean(); l = (-delta.where(delta<0,0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
                skor = (40 if fiyat > ma20 else 0) + (40 if 45 < rsi < 75 else 0) + (20 if degisim > 0 else 0)

                # Üst Panel
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                with m4:
                    st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>GÜVEN</span><br><b style='color:#00ff88; font-size:18px;'>%{int(skor)}</b></div>", unsafe_allow_html=True)

                # Gürkan AI Yorum + Seviyeler
                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88;'>🤵 VIP ANALİZ:</b> {h_input} için kritik <b>Direnç: {direnc:.2f}</b> | <b>Destek: {destek:.2f}</b><br>
                    <span style='font-size:12px; opacity:0.8;'>Görünüm: {fiyat/direnc*100:.1f}% direnç yakınlığı. {'Kırılım beklenebilir.' if fiyat > ma20 else 'Desteğe dönüş riskine dikkat.'}</span>
                </div>
                """, unsafe_allow_html=True)

                # GRAFİK + DESTEK/DİRENÇ ÇİZGİLERİ
                fig = go.Figure()
                # Ana Fiyat
                fig.add_trace(go.Scatter(x=df.tail(60).index, y=df.tail(60)['Close'], name="Fiyat", line=dict(color='#00ff88', width=2), fill='tozeroy', fillcolor='rgba(0,255,136,0.03)'))
                # Direnç Hattı (Kırmızımsı Kesik)
                fig.add_hline(y=direnc, line_dash="dash", line_color="#ff4b4b", annotation_text="DİRENÇ", annotation_position="top left")
                # Destek Hattı (Mavimsi Kesik)
                fig.add_hline(y=destek, line_dash="dash", line_color="#0088ff", annotation_text="DESTEK", annotation_position="bottom left")
                
                fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1c2128', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.error("Veri hatası.")

    with col_radar:
        st.markdown("### 🚀 RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        r_data = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
        if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
        for s in t_list:
            n = s.split('.')[0]
            try:
                c, p = r_data[n + ".IS"].iloc[-1], r_data[n + ".IS"].iloc[-2]
                pct = ((c - p) / p) * 100
                if st.button(f"{n} | %{pct:.1f}", key=f"v81_r_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
            except: continue
