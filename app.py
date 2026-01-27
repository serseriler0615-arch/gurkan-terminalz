import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. OTURUM VE GİRİŞ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="VIP Giriş", layout="centered")
        st.markdown("<style>.stApp{background-color:#0d1117;} h1,p,label{color:white !important;}</style>", unsafe_allow_html=True)
        st.title("Gürkan AI VIP Terminal")
        key = st.text_input("VIP Lisans Anahtarı", key="login_key")
        if st.button("Sistemi Aktive Et"):
            if key.startswith("GAI-"): 
                st.session_state["access_granted"] = True
                st.session_state["role"] = "user"
                st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=30)
                st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- GELİŞMİŞ TÜRKÇE CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        
        /* VIP ASİSTAN */
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; }
        
        /* RADAR KARTLARI */
        .radar-card { 
            background: #161b22; border: 1px solid #30363d; border-radius: 8px; 
            padding: 8px 12px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; 
        }
        .radar-name { color: #00ff88 !important; font-size: 14px !important; }
        .radar-vol { color: #8b949e !important; font-size: 10px !important; }
        .radar-pct { font-size: 13px !important; padding: 3px 8px; border-radius: 5px; min-width: 60px; text-align: right; }
        .pct-up { color: #00ff88 !important; background: rgba(0, 255, 136, 0.1); border: 1px solid #00ff88; }
        .pct-down { color: #ff4b4b !important; background: rgba(255, 75, 75, 0.1); border: 1px solid #ff4b4b; }
        
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 20px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST PANEL ---
    st.markdown("🚀 **GÜRKAN AI | VIP TÜRKÇE TERMİNAL (v60)**")

    # --- ANA DASHBOARD ---
    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", placeholder="SASA", label_visibility="collapsed").upper()
        if st.button("➕", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(y_fav)
                st.rerun()
        for f in st.session_state["favorites"][-6:]:
            st.markdown(f"<div style='background:#161b22; padding:5px; border-radius:4px; margin-bottom:2px; color:#00ff88; border:1px solid #30363d;'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: TÜRKÇE ÇİZELGE (SON 20 GÜN)
    with col_main:
        h_input = st.text_input("Hisse:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            # Son 1 aylık veriyi çekip içinden son 20 günü alıyoruz
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df = df.tail(20) # SADECE SON 20 GÜN
                
                fiyat = float(df['Close'].iloc[-1])
                ma20 = df['Close'].rolling(window=5).mean() # Kısa vadeli trend için 5 günlük MA
                h1, h2, stop = fiyat*1.05, fiyat*1.12, fiyat*0.96

                m1, m2, m3 = st.columns(3)
                m1.metric("SON FİYAT", f"{fiyat:.2f} TL")
                m2.metric("TREND YÖNÜ", "YUKARI" if fiyat > ma20.iloc[-1] else "AŞAĞI")
                m3.metric("ZARAR KES", f"{stop:.2f}")

                # --- TÜRKÇE PLOTLY ÇİZELGE ---
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', 
                                         line=dict(color='#00ff88', width=2),
                                         fillcolor='rgba(0, 255, 136, 0.1)', name='Kapanış Fiyatı'))
                
                fig.update_layout(
                    height=200, margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, color='#8b949e', title="Tarih"),
                    yaxis=dict(showgrid=True, gridcolor='#222', side='right', color='#8b949e', title="Fiyat (TL)"),
                    showlegend=False,
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # VIP YORUMU
                st.markdown(f"""
                    <div class='asistan-box'>
                        <b style='color:#00ff88;'>🤵 VIP ANALİZ: {h_input}</b> (Son 20 Günlük Veri)<br>
                        🎯 Hedef 1: <span style='color:#00ff88;'>{h1:.2f}</span> | Hedef 2: <span style='color:#00ff88;'>{h2:.2f}</span><br>
                        🛡️ Zarar Kes: <span style='color:#ff4b4b;'>{stop:.2f}</span> | <b>Sinyal:</b> {'Güçlü' if fiyat > ma20.iloc[-1] else 'Zayıf'}
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Veri hatası.")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "SASA.IS"]
        radar_df = yf.download(radar_list, period="2d", interval="1d", progress=False)['Close']
        if isinstance(radar_df.columns, pd.MultiIndex): radar_df.columns = radar_df.columns.get_level_values(1)

        for s in radar_list:
            try:
                val = radar_df[s].iloc[-1]
                pct = ((val - radar_df[s].iloc[-2]) / radar_df[s].iloc[-2]) * 100
                h_name = s.split(".")[0]
                hacim = f"{int(val * 1.4)}M"
                
                cls = "pct-up" if pct >= 0 else "pct-down"
                st.markdown(f"""
                    <div class='radar-card'>
                        <div style='display:flex; flex-direction:column;'>
                            <span class='radar-name'>{h_name}</span>
                            <span class='radar-vol'>Hacim: {hacim} TL</span>
                        </div>
                        <div class='radar-pct {cls}'>{"%+" if pct>=0 else "%"}{pct:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            except: continue
