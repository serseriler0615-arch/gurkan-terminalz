import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# --- 1. OTURUM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]
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
                if k.startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Admin Giriş"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- VIP TASARIM ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 15px; border-radius: 12px; }
        .skor-box { font-size: 24px !important; color: #00ff88 !important; font-weight: 900 !important; text-align: center; border: 1px solid #333; border-radius: 10px; padding: 12px; background: #161b22; }
        .radar-card { background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 10px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
        .pct-up { color: #00ff88 !important; background: rgba(0, 255, 136, 0.1); padding: 4px 8px; border-radius: 5px; }
        .pct-down { color: #ff4b4b !important; background: rgba(255, 75, 75, 0.1); padding: 4px 8px; border-radius: 5px; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.2])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="f_add_v74", label_visibility="collapsed", placeholder="Hisse...").upper().strip()
        if st.button("➕", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        for f in st.session_state["favorites"][-5:]:
            if st.button(f"🔍 {f}", key=f"btn_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f
                st.rerun()

    # 2. ORTA: ANALİZ
    with col_main:
        h_input = st.text_input("Hisse Sorgula:", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            # En kararlı veri çekme yöntemi
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            
            if not df.empty and len(df) > 5:
                # Kolonları temizle (MultiIndex hatasını önler)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                onceki = float(df['Close'].iloc[-2])
                degisim = ((fiyat - onceki) / onceki) * 100
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                
                # RSI
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
                
                # SKOR
                skor = 0
                if fiyat > ma20: skor += 40
                if 45 < rsi < 70: skor += 40
                if degisim > 0: skor += 20

                # DASHBOARD
                m1, m2, m3 = st.columns([1, 1, 1])
                m1.metric("FİYAT", f"{fiyat:.2f} TL", f"{degisim:.2f}%")
                with m2: st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>VIP GÜVEN SKORU</span><br>%{min(skor, 100)}</div>", unsafe_allow_html=True)
                m3.metric("RSI GÜCÜ", f"{rsi:.1f}")

                fig = go.Figure(data=[go.Scatter(x=df.tail(30).index, y=df.tail(30)['Close'], fill='tozeroy', line=dict(color='#00ff88', width=3), fillcolor='rgba(0,255,136,0.1)')])
                fig.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 GÜRKAN AI:</b> {h_input} teknik skoru %{skor}. { 'Trend alıcılı seyrediyor.' if skor > 60 else 'Hissede güç toplanması bekleniyor.' }</div>", unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ {sembol} verisi şu an Yahoo tarafından sağlanamıyor.")
        except Exception as e:
            st.error(f"Sistem Hatası: Lütfen sembolü kontrol edin.")

    # 3. SAĞ: RADAR & ADMIN
    with col_radar:
        st.markdown("### 🚀 RADAR (EN GÜÇLÜLER)")
        r_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS"]
        try:
            r_data = yf.download(r_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
            for s in r_list:
                try:
                    c, p = r_data[s].iloc[-1], r_data[s].iloc[-2]
                    pct = ((c - p) / p) * 100
                    st.markdown(f"<div class='radar-card'><div>{s.split('.')[0]}<br><span style='font-size:10px; color:#8b949e;'>{c:.2f}</span></div><div class='{'pct-up' if pct>=0 else 'pct-down'}'>{pct:.2f}%</div></div>", unsafe_allow_html=True)
                except: continue
        except: st.warning("Radar şu an kısıtlı.")

        if st.session_state.get("role") == "admin":
            st.markdown("<div style='background:#161b22; border:1px dashed #00ff88; padding:10px; border-radius:10px; margin-top:30px;'>🔑 **KEY ÜRET**", unsafe_allow_html=True)
            if st.button("LİSANS ÜRET"): st.code(f"GAI-{int(time.time())}-30-VIP")
            st.markdown("</div>", unsafe_allow_html=True)
