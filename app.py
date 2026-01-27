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
        st.title("🤵 Gürkan AI VIP Terminal")
        k = st.text_input("💎 VIP KEY GİRİNİZ", type="password")
        if st.button("SİSTEMİ BAŞLAT"):
            if k.startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 ULTRA DARK & NEON CSS ---
    st.markdown("""
        <style>
        /* Ana Arka Plan */
        .stApp { background-color: #05070a !important; }
        
        /* Tüm Yazıları Beyaz Yap */
        h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Inter', sans-serif !important; }
        
        /* Butonlardaki O Çirkin Beyazlığı Kaldır */
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.05) !important;
            color: #00ff88 !important;
            border: 1px solid #00ff88 !important;
            border-radius: 5px !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button:hover {
            background-color: #00ff88 !important;
            color: #05070a !important;
            box-shadow: 0 0 15px #00ff88 !important;
        }

        /* Gürkan AI Yorum Kutusu */
        .asistan-box { 
            background: #0d1117; 
            border: 1px solid #30363d; 
            border-left: 4px solid #00ff88; 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px;
        }

        /* Skor Kutusu */
        .skor-box { 
            background: #0d1117; 
            border: 2px solid #00ff88; 
            border-radius: 15px; 
            padding: 15px; 
            text-align: center;
            box-shadow: inset 0 0 10px rgba(0,255,136,0.1);
        }

        /* Input Alanlarını Karart */
        .stTextInput > div > div > input {
            background-color: #0d1117 !important;
            color: white !important;
            border: 1px solid #30363d !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.2])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="f_add_v77", label_visibility="collapsed", placeholder="Hisse...").upper().strip()
        if st.button("➕") and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        
        st.markdown("---")
        for f in st.session_state["favorites"][-8:]:
            if st.button(f"🔍 {f}", key=f"f_btn_{f}"):
                st.session_state["last_sorgu"] = f
                st.rerun()

    # 2. ORTA: ANALİZ PANELİ
    with col_main:
        h_input = st.text_input("Hisse Sorgula:", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat, onceki = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-2])
                degisim = ((fiyat - onceki) / onceki) * 100
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
                
                skor = 0
                if fiyat > ma20: skor += 40
                if 45 < rsi < 70: skor += 40
                if degisim > 0: skor += 20

                # ÜST METRİKLER
                m1, m2, m3 = st.columns([1, 1, 1])
                m1.metric("SON FİYAT", f"{fiyat:.2f} TL", f"{degisim:.2f}%")
                with m2: st.markdown(f"<div class='skor-box'><span style='font-size:11px; color:#8b949e;'>VIP GÜVEN SKORU</span><br><b style='font-size:28px; color:#00ff88;'>%{int(skor)}</b></div>", unsafe_allow_html=True)
                m3.metric("RSI GÜCÜ", f"{rsi:.1f}")

                # GÜRKAN AI YORUMU
                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88; font-size:16px;'>🤵 GÜRKAN AI ANALİZ NOTU</b><br>
                    {h_input} hissesi %{int(skor)} teknik güven puanıyla {'pozitif' if skor > 60 else 'temkinli'} bölgede. 
                    RSI {int(rsi)} seviyesinde, {'alım iştahı artıyor.' if rsi > 50 else 'yatay seyir hakim.'}
                </div>
                """, unsafe_allow_html=True)

                # GRAFİK
                fig = go.Figure(data=[go.Scatter(x=df.tail(50).index, y=df.tail(50)['Close'], fill='tozeroy', line=dict(color='#00ff88', width=2), fillcolor='rgba(0,255,136,0.05)')])
                fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1c2128', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.error("Veri bağlantısı kurulamadı.")

    # 3. SAĞ: TIKLANABİLİR RADAR
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        tara_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS"]
        
        try:
            r_data = yf.download(tara_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            
            for s in tara_list:
                name = s.split('.')[0]
                try:
                    c, p = r_data[s].iloc[-1], r_data[s].iloc[-2]
                    pct = ((c - p) / p) * 100
                    # Tıklanabilir Radar
                    if st.button(f"{name} | %{pct:.2f}", key=f"rad_{name}"):
                        st.session_state["last_sorgu"] = name
                        st.rerun()
                except: continue
        except: st.warning("Radar Beklemede...")

        if st.session_state.get("role") == "admin":
            st.markdown("<br>🔐 **ADMIN**", unsafe_allow_html=True)
            if st.button("LİSANS ÜRET"): st.code(f"GAI-{int(time.time())}-VIP")
