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
        .skor-box { font-size: 26px !important; color: #00ff88 !important; font-weight: 900 !important; text-align: center; border: 1px solid #333; border-radius: 10px; padding: 12px; background: #161b22; }
        .radar-card { background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 10px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
        .pct-label { padding: 4px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
        .up { color: #00ff88; background: rgba(0, 255, 136, 0.1); border: 1px solid #00ff88; }
        .down { color: #ff4b4b; background: rgba(255, 75, 75, 0.1); border: 1px solid #ff4b4b; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.2])

    # 1. SOL: FAVORİLER (TIKLANABİLİR)
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="f_add_v75", label_visibility="collapsed", placeholder="Hisse...").upper().strip()
        if st.button("➕", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        
        for f in st.session_state["favorites"][-8:]:
            if st.button(f"🔍 {f}", key=f"btn_{f}", use_container_width=True):
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
                
                fiyat = float(df['Close'].iloc[-1])
                onceki = float(df['Close'].iloc[-2])
                degisim = ((fiyat - onceki) / onceki) * 100
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                
                # RSI 
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
                
                # VIP SKOR
                skor = 0
                if fiyat > ma20: skor += 40
                if 45 < rsi < 70: skor += 40
                if degisim > 0: skor += 20

                # UI
                m1, m2, m3 = st.columns([1, 1, 1])
                m1.metric("FİYAT", f"{fiyat:.2f} TL", f"{degisim:.2f}%")
                with m2: st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>VIP GÜVEN SKORU</span><br>%{int(skor)}</div>", unsafe_allow_html=True)
                m3.metric("RSI GÜCÜ", f"{rsi:.1f}")

                fig = go.Figure(data=[go.Scatter(x=df.tail(40).index, y=df.tail(40)['Close'], fill='tozeroy', line=dict(color='#00ff88', width=3), fillcolor='rgba(0,255,136,0.1)')])
                fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                st.markdown(f"<div class='asistan-box'><b style='color:#00ff88;'>🤵 GÜRKAN AI:</b> {h_input} için teknik analiz tamamlandı. Güven skoru %{skor}. { 'Kuvvetli trend devam ediyor.' if skor > 70 else 'Hissede hacimli bir kırılım veya destek onayı beklenmeli.' }</div>", unsafe_allow_html=True)
        except:
            st.error("Veri çekilemedi, lütfen sembolü kontrol edin.")

    # 3. SAĞ: AKILLI RADAR (OTOMATİK TARAYICI)
    with col_radar:
        st.markdown("### 🚀 AKILLI RADAR")
        # Tarama yapılacak BIST listesi
        tara_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "SISE.IS", "KCHOL.IS", "BIMAS.IS", "SASA.IS", "EKGYO.IS"]
        
        @st.cache_data(ttl=600) # 10 dakikada bir tarar
        def vip_tara(liste):
            results = []
            data = yf.download(liste, period="5d", interval="1d", progress=False)['Close']
            for s in liste:
                try:
                    c = data[s].iloc[-1]
                    p = data[s].iloc[-2]
                    pct = ((c - p) / p) * 100
                    results.append({'s': s.split('.')[0], 'p': c, 'ch': pct})
                except: continue
            return sorted(results, key=lambda x: x['ch'], reverse=True)[:5]

        radar_data = vip_tara(tara_list)
        for r in radar_data:
            cls = "up" if r['ch'] >= 0 else "down"
            st.markdown(f"""
                <div class='radar-card'>
                    <div><b>{r['s']}</b><br><span style='font-size:10px; color:#8b949e;'>{r['p']:.2f} TL</span></div>
                    <div class='pct-label {cls}'>{"+" if r['ch']>=0 else ""}{r['ch']:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

        if st.session_state.get("role") == "admin":
            st.markdown("<div style='margin-top:20px; border-top:1px dashed #333; padding-top:10px;'>🔑 **KEY ÜRET**", unsafe_allow_html=True)
            if st.button("LİSANS OLUŞTUR"): st.code(f"GAI-{int(time.time())}-30-VIP")
