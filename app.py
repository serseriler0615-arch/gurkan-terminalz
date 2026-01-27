import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. OTURUM VE GİRİŞ SİSTEMİ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]
if "role" not in st.session_state:
    st.session_state["role"] = None

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI Giriş", layout="centered")
        st.markdown("<style>.stApp{background-color:#0d1117;} h1,p,label{color:white !important;}</style>", unsafe_allow_html=True)
        st.title("🤵 Gürkan AI Terminal")
        
        tab1, tab2 = st.tabs(["💎 VIP KEY GİRİŞİ", "🔐 ADMIN PANELİ"])
        
        with tab1:
            key = st.text_input("Lisans Anahtarınızı Giriniz", key="v_key_input")
            if st.button("Sistemi Aktive Et"):
                if key.startswith("GAI-"): 
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "user"
                    st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=30)
                    st.rerun()
                else: st.error("Geçersiz Anahtar!")
        
        with tab2:
            u = st.text_input("Yönetici ID")
            p = st.text_input("Yönetici Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!":
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
                else: st.error("Bilgiler Hatalı!")
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- GELİŞMİŞ CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; box-shadow: 0 0 15px rgba(0,255,136,0.1); }
        .radar-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 8px 12px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; }
        .radar-name { color: #00ff88 !important; font-size: 14px !important; }
        .radar-pct { font-size: 13px !important; padding: 3px 8px; border-radius: 5px; min-width: 60px; text-align: right; }
        .pct-up { color: #00ff88 !important; background: rgba(0, 255, 136, 0.1); border: 1px solid #00ff88; }
        .pct-down { color: #ff4b4b !important; background: rgba(255, 75, 75, 0.1); border: 1px solid #ff4b4b; }
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 20px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST PANEL ---
    c_st1, c_st2, c_st3 = st.columns([3, 1, 1])
    with c_st1: st.markdown(f"🚀 **GÜRKAN AI | VIP TÜRKÇE TERMİNAL**")
    with c_st2: 
        if st.session_state["role"] == "admin": st.warning("🛠️ MOD: YÖNETİCİ")
        elif "bitis_tarihi" in st.session_state: st.markdown(f"⏳ Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    with c_st3: 
        if st.button("Güvenli Çıkış", use_container_width=True): 
            st.session_state.clear()
            st.rerun()

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

    # 2. ORTA: ANALİZ & ÇİZELGE OKUMA YETENEĞİ
    with col_main:
        h_input = st.text_input("Hisse Sorgu:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            # Teknik analiz için biraz daha fazla veri çekiyoruz (60 gün) ama 20 gün gösteriyoruz
            df_raw = yf.download(sembol, period="3mo", interval="1d", progress=False)
            if not df_raw.empty:
                if isinstance(df_raw.columns, pd.MultiIndex): df_raw.columns = df_raw.columns.get_level_values(0)
                
                # --- ÇİZELGE OKUMA ALGORİTMASI (TEKNİK ANALİZ) ---
                df_raw['MA20'] = df_raw['Close'].rolling(window=20).mean()
                df_raw['MA5'] = df_raw['Close'].rolling(window=5).mean()
                
                # RSI Hesaplama (Basit)
                delta = df_raw['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                current_rsi = rsi.iloc[-1]
                fiyat = float(df_raw['Close'].iloc[-1])
                ma20_val = df_raw['MA20'].iloc[-1]
                
                # Görselleştirme için son 20 gün
                df = df_raw.tail(20)
                h1, h2, stop = fiyat*1.05, fiyat*1.12, fiyat*0.96

                m1, m2, m3 = st.columns(3)
                m1.metric("FİYAT", f"{fiyat:.2f} TL")
                m2.metric("RSI (GÜÇ)", f"{current_rsi:.1f}")
                m3.metric("STOP", f"{stop:.2f}")

                # ÇİZELGE
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', line=dict(color='#00ff88', width=2), fillcolor='rgba(0, 255, 136, 0.1)'))
                fig.update_layout(height=180, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, color='#8b949e'), yaxis=dict(showgrid=True, gridcolor='#222', side='right', color='#8b949e'), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # --- YENİ: ÇİZELGE OKUMA YETENEĞİ (VIP YORUM) ---
                rsi_yorum = "Aşırı Alım (Riskli)" if current_rsi > 70 else "Normal (Dengeli)" if current_rsi > 30 else "Aşırı Satım (Fırsat)"
                trend_yorum = "Ortalama Üstü (Pozitif)" if fiyat > ma20_val else "Ortalama Altı (Negatif)"
                
                st.markdown(f"""
                    <div class='asistan-box'>
                        <b style='color:#00ff88;'>🤵 VIP ÇİZELGE ANALİZİ: {h_input}</b><br>
                        📈 <b>Trend Okuması:</b> {trend_yorum} | 📉 <b>RSI Durumu:</b> {rsi_yorum}<br>
                        🎯 <b>Hedefler:</b> <span style='color:#00ff88;'>{h1:.2f} / {h2:.2f}</span> | 🛡️ <b>Zarar Kes:</b> <span style='color:#ff4b4b;'>{stop:.2f}</span><br>
                        <b>Asistan Notu:</b> Grafikte {h_input} için {'yukarı yönlü iştah korunuyor.' if fiyat > ma20_val else 'satış baskısı hissediliyor, temkinli olunmalı.'}
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Analiz yapılamadı.")

    # 3. SAĞ: RADAR & KEY ÜRETİCİ
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
                hacim = f"{int(val * 1.6)}M"
                cls = "pct-up" if pct >= 0 else "pct-down"
                st.markdown(f"<div class='radar-card'><div><span class='radar-name'>{h_name}</span><br><span style='font-size:10px; color:#8b949e;'>Hacim: {hacim} TL</span></div><div class='radar-pct {cls}'>%{pct:.2f}</div></div>", unsafe_allow_html=True)
            except: continue
        
        # --- ADMIN KEY ÜRETİCİ (SAĞ ALTA SABİTLENDİ) ---
        if st.session_state["role"] == "admin":
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("### 🔑 ADMIN PANELİ")
            if st.button("YENİ LİSANS ÜRET", use_container_width=True):
                new_key = f"GAI-{int(time.time())}-30-VIP"
                st.success("Key Üretildi!")
                st.code(new_key)
