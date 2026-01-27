import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM VE OTURUM ---
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
        .asistan-box { background: #1c2128; border-left: 4px solid #00ff88; padding: 12px; border-radius: 8px; margin-bottom: 10px; font-size: 14px; }
        .skor-box { font-size: 26px !important; color: #00ff88 !important; font-weight: 900 !important; text-align: center; border: 1px solid #333; border-radius: 10px; padding: 10px; background: #161b22; }
        .radar-card-btn { width: 100%; text-align: left; background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 8px; margin-bottom: 5px; cursor: pointer; }
        .radar-card-btn:hover { border-color: #00ff88; background: #161b22; }
        .pct-up { color: #00ff88; float: right; font-weight: bold; }
        .pct-down { color: #ff4b4b; float: right; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.2])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="f_add_v76", label_visibility="collapsed", placeholder="Hisse...").upper().strip()
        if st.button("➕", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        for f in st.session_state["favorites"][-8:]:
            if st.button(f"🔍 {f}", key=f"f_btn_{f}", use_container_width=True):
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
                
                # SKOR VE ANALİZ NOTU
                skor = 0
                if fiyat > ma20: skor += 40
                if 45 < rsi < 70: skor += 40
                if degisim > 0: skor += 20
                analiz_notu = f"{h_input} şu an teknik olarak %{int(skor)} güven veriyor. {'Trend güçlü, dirençler izlenmeli.' if skor > 60 else 'Hacim onayı ve destek takibi önemli.'}"

                # ÜST PANEL: METRİKLER
                m1, m2, m3 = st.columns([1, 1, 1])
                m1.metric("FİYAT", f"{fiyat:.2f} TL", f"{degisim:.2f}%")
                with m2: st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>GÜVEN SKORU</span><br>%{int(skor)}</div>", unsafe_allow_html=True)
                m3.metric("RSI (14G)", f"{rsi:.1f}")

                # GÜRKAN AI YORUMU (ÇİZELGE ÜZERİNDE)
                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 GÜRKAN AI YORUMU:</b><br>{analiz_notu}</div>", unsafe_allow_html=True)

                # ÇİZELGE
                fig = go.Figure(data=[go.Scatter(x=df.tail(45).index, y=df.tail(45)['Close'], fill='tozeroy', line=dict(color='#00ff88', width=3), fillcolor='rgba(0,255,136,0.1)')])
                fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.error("Bağlantı hatası, lütfen sembolü kontrol edin.")

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
                    color_cls = "pct-up" if pct >= 0 else "pct-down"
                    
                    # Tıklanabilir Radar Butonu
                    if st.button(f"{name} {'+' if pct>=0 else ''}{pct:.2f}%", key=f"rad_{name}", use_container_width=True):
                        st.session_state["last_sorgu"] = name
                        st.rerun()
                except: continue
        except: st.warning("Radar yüklenemedi.")

        if st.session_state.get("role") == "admin":
            st.markdown("<br>🔑 **KEY ÜRET**", unsafe_allow_html=True)
            if st.button("LİSANS OLUŞTUR"): st.code(f"GAI-{int(time.time())}-30-VIP")
