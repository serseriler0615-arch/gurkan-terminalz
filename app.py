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
            if k.startswith("GAI-"): st.session_state["access_granted"] = True; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 KOMPAKT DARK CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        /* Yazı Boyutlarını Küçült */
        h3 { font-size: 14px !important; margin-bottom: 5px !important; color: #00ff88 !important; }
        p, div, span { font-size: 12px !important; color: #e0e0e0 !important; }
        
        /* Boşlukları (Padding) Daralt */
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        .stButton > button {
            padding: 2px 5px !important;
            min-height: 25px !important;
            font-size: 11px !important;
            background-color: rgba(0, 255, 136, 0.05) !important;
            color: #00ff88 !important;
            border: 1px solid #30363d !important;
        }
        
        /* Gürkan AI Yorum Kutusu Sıkıştırma */
        .asistan-box { 
            background: #0d1117; 
            border-left: 3px solid #00ff88; 
            padding: 8px 12px; 
            border-radius: 5px; 
            margin-bottom: 10px;
            line-height: 1.2;
        }

        /* Skor Kutusu Sıkıştırma */
        .skor-box { 
            background: #0d1117; 
            border: 1px solid #00ff88; 
            border-radius: 8px; 
            padding: 5px; 
            text-align: center;
        }

        /* Metrikleri Küçült */
        [data-testid="stMetricValue"] { font-size: 18px !important; }
        [data-testid="stMetricDelta"] { font-size: 12px !important; }
        </style>
    """, unsafe_allow_html=True)

    # Üst Bilgi Satırı (Çok İnce)
    col_fav, col_main, col_radar = st.columns([0.6, 3, 0.9])

    # 1. SOL: FAVORİLER (Daraltılmış)
    with col_fav:
        st.markdown("### ⭐ FAVORİ")
        for f in st.session_state["favorites"][-6:]:
            if st.button(f"{f}", key=f"f_btn_{f}"):
                st.session_state["last_sorgu"] = f; st.rerun()
        
        y_fav = st.text_input("", key="f_add", placeholder="+Ekle", label_visibility="collapsed").upper().strip()
        if y_fav and len(y_fav) > 2:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()

    # 2. ORTA: ANA PANEL (Full Sıkıştırılmış)
    with col_main:
        # Sorgu ve Skor Yan Yana
        head1, head2 = st.columns([2, 1])
        with head1:
            h_input = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="3mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat, onceki = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-2])
                degisim = ((fiyat - onceki) / onceki) * 100
                
                # Teknik Hesaplama (Hızlı)
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                delta = df['Close'].diff(); gain = (delta.where(delta>0,0)).rolling(14).mean(); loss = (-delta.where(delta<0,0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
                skor = (40 if fiyat > ma20 else 0) + (40 if 45 < rsi < 70 else 0) + (20 if degisim > 0 else 0)

                # Mini Metrik Satırı
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("DEĞİŞİM", f"%{degisim:.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                with m4: st.markdown(f"<div class='skor-box'><span style='font-size:9px;'>GÜVEN</span><br><b style='color:#00ff88;'>%{int(skor)}</b></div>", unsafe_allow_html=True)

                # GÜRKAN AI YORUMU (Daha İnce)
                st.markdown(f"""<div class='asistan-box'><b style='color:#00ff88;'>🤵 AI:</b> {h_input} %{int(skor)} güven puanında. {'Trend pozitif.' if skor > 60 else 'Bekle-gör.'}</div>""", unsafe_allow_html=True)

                # GRAFİK (Yüksekliği Azaltılmış)
                fig = go.Figure(data=[go.Scatter(x=df.tail(35).index, y=df.tail(35)['Close'], fill='tozeroy', line=dict(color='#00ff88', width=2), fillcolor='rgba(0,255,136,0.05)')])
                fig.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, tickfont=dict(size=10)), yaxis=dict(showgrid=True, gridcolor='#1c2128', side='right', tickfont=dict(size=10)))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.error("Bağlantı...")

    # 3. SAĞ: RADAR (Sıkışık)
    with col_radar:
        st.markdown("### 🚀 RADAR")
        tara_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        try:
            r_data = yf.download(tara_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in tara_list:
                name = s.split('.')[0]
                try:
                    c, p = r_data[s].iloc[-1], r_data[s].iloc[-2]
                    pct = ((c - p) / p) * 100
                    if st.button(f"{name} %{pct:.1f}", key=f"r_{name}"):
                        st.session_state["last_sorgu"] = name; st.rerun()
                except: continue
        except: pass

    # Admin (En Alt Gizli)
    if st.session_state.get("role") == "admin":
        if st.button("🔑"): st.code(f"GAI-{int(time.time())}-VIP")
