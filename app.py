import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    # --- 🎨 ESTETİK DARK UI CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        h3 { font-size: 15px !important; color: #00ff88 !important; margin-bottom: 8px !important; }
        p, span, div { color: #e0e0e0 !important; font-size: 13px !important; }
        
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            border-radius: 6px !important;
            transition: 0.3s ease;
        }
        div.stButton > button:hover { border-color: #00ff88 !important; background: rgba(0,255,136,0.08) !important; }

        .asistan-box { 
            background: rgba(13, 17, 23, 0.8); 
            border: 1px solid #1c2128;
            border-left: 4px solid #00ff88; 
            padding: 12px; 
            border-radius: 10px; 
            margin-bottom: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        .skor-box { 
            background: linear-gradient(145deg, #0d1117, #05070a);
            border: 1px solid #00ff88; 
            border-radius: 12px; 
            padding: 8px; 
            text-align: center;
            box-shadow: 0 0 15px rgba(0,255,136,0.1);
        }
        [data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 800 !important; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1])

    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        for f in st.session_state["favorites"][-7:]:
            if st.button(f"🔍 {f}", key=f"v82_f_{f}", use_container_width=True):
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
                direnc = df['High'].tail(60).max()
                destek = df['Low'].tail(60).min()

                # Teknik Hesaplamalar
                ma20 = df['Close'].rolling(20).mean(); ma50 = df['Close'].rolling(50).mean()
                delta = df['Close'].diff(); g = (delta.where(delta>0,0)).rolling(14).mean(); l = (-delta.where(delta<0,0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
                skor = (40 if fiyat > ma20.iloc[-1] else 0) + (40 if 45 < rsi < 75 else 0) + (20 if degisim > 0 else 0)

                # Metrik Satırı
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                with m4:
                    st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>VIP GÜVEN</span><br><b style='color:#00ff88; font-size:19px;'>%{int(skor)}</b></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88;'>🤵 VIP ANALİZ:</b> {h_input} Direnç: <b>{direnc:.2f}</b> | Destek: <b>{destek:.2f}</b><br>
                    <span style='font-size:12px; opacity:0.8;'>Gürkan AI Notu: Fiyat {direnc:.2f} seviyesini hacimli aşarsa yeni bir yükseliş dalgası tetiklenebilir.</span>
                </div>
                """, unsafe_allow_html=True)

                # --- 🎨 GRAFİK GÜZELLEŞTİRME ---
                fig = make_subplots(rows=1, cols=1)

                # 1. Mum Grafik (Candlestick)
                fig.add_trace(go.Candlestick(
                    x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'],
                    low=df.tail(60)['Low'], close=df.tail(60)['Close'], name="Mum",
                    increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b',
                    increasing_fillcolor='#00ff88', decreasing_fillcolor='#ff4b4b'
                ))

                # 2. Hareketli Ortalama (Yumuşak Çizgi)
                fig.add_trace(go.Scatter(x=df.tail(60).index, y=ma20.tail(60), line=dict(color='rgba(255, 255, 255, 0.4)', width=1.5), name="MA20"))

                # 3. Destek/Direnç Bölgeleri (Çizgi yerine Gradyan/Gölge)
                fig.add_hline(y=direnc, line_dash="dash", line_color="rgba(255, 75, 75, 0.5)", annotation_text="DİRENÇ", annotation_position="top left")
                fig.add_hline(y=destek, line_dash="dash", line_color="rgba(0, 136, 255, 0.5)", annotation_text="DESTEK", annotation_position="bottom left")

                fig.update_layout(
                    height=320, margin=dict(l=0,r=0,t=0,b=0),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False, xaxis_rangeslider_visible=False,
                    xaxis=dict(showgrid=False, color='#444'),
                    yaxis=dict(showgrid=True, gridcolor='#161b22', side='right', color='#444')
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.error("Veri akışında hata.")

    with col_radar:
        st.markdown("### 🚀 RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            r_data = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in t_list:
                n = s.split('.')[0]
                try:
                    c, p = r_data[n + ".IS"].iloc[-1], r_data[n + ".IS"].iloc[-2]
                    pct = ((c - p) / p) * 100
                    if st.button(f"{n} | %{pct:.1f}", key=f"v82_r_{n}", use_container_width=True):
                        st.session_state["last_sorgu"] = n; st.rerun()
                except: continue
        except: pass
