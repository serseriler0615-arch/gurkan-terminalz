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

    # --- VIP CSS TASARIM ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-size: 13px !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 15px; border-radius: 12px; }
        .skor-box { font-size: 22px !important; color: #00ff88 !important; font-weight: 900 !important; text-align: center; border: 1px solid #333; border-radius: 10px; padding: 10px; background: #161b22; }
        .haber-card { background: #161b22; border-left: 3px solid #0088ff; padding: 10px; margin-bottom: 8px; border-radius: 6px; font-size: 12px !important; }
        .radar-card { background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 10px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
        .pct-up { color: #00ff88 !important; background: rgba(0, 255, 136, 0.1); padding: 4px 8px; border-radius: 5px; }
        .pct-down { color: #ff4b4b !important; background: rgba(255, 75, 75, 0.1); padding: 4px 8px; border-radius: 5px; }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", key="f_add_v70", label_visibility="collapsed").upper()
        if st.button("➕") and y_fav:
            if y_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(y_fav); st.rerun()
        for f in st.session_state["favorites"][-5:]:
            st.markdown(f"<div style='color:#00ff88; border-bottom:1px solid #222; padding:5px;'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ VE HABERLER
    with col_main:
        h_input = st.text_input("Hisse Sorgula:", value="THYAO", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            ticker = yf.Ticker(sembol)
            df = ticker.history(period="6mo", interval="1d")
            
            if not df.empty:
                # --- TEKNİK ANALİZ VERİLERİ ---
                fiyat = df['Close'].iloc[-1]
                onceki = df['Close'].iloc[-2]
                degisim = ((fiyat - onceki) / onceki) * 100
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                
                # RSI Hesapla
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
                
                # GÜVEN SKORU
                skor = 0
                if fiyat > ma20: skor += 35
                if 45 < rsi < 70: skor += 35
                elif rsi < 45: skor += 20 # Aşırı satım potansiyeli
                if degisim > 0: skor += 30

                # Üst Panel
                m1, m2, m3 = st.columns([1, 1, 1])
                m1.metric("SON FİYAT", f"{fiyat:.2f} TL", f"{degisim:.2f}%")
                with m2: st.markdown(f"<div class='skor-box'><span style='font-size:10px; color:#8b949e;'>VIP GÜVEN SKORU</span><br>%{min(skor, 100)}</div>", unsafe_allow_html=True)
                m3.metric("RSI GÜCÜ", f"{rsi:.1f}")

                # Çizelge (Son 20 Gün)
                fig = go.Figure(data=[go.Scatter(x=df.tail(20).index, y=df.tail(20)['Close'], fill='tozeroy', line=dict(color='#00ff88', width=3), fillcolor='rgba(0,255,136,0.1)')])
                fig.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222', side='right'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # --- HABERLER (HATA KORUMALI) ---
                st.markdown("### 📢 SON GELİŞMELER & KAP")
                try:
                    news = ticker.news[:3]
                    if news:
                        for n in news:
                            # Zaman verisini güvenli bir şekilde al (Yoksa 'Bilgi Yok' yaz)
                            dt_raw = n.get('providerPublishTime', None)
                            dt = datetime.fromtimestamp(dt_raw).strftime('%H:%M') if dt_raw else "Sinyal"
                            st.markdown(f"<div class='haber-card'><b>[{dt}]</b> {n.get('title', 'Başlıksız Haber')}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='haber-card'>⚠️ Şirkete dair güncel haber akışı şu an sessiz.</div>", unsafe_allow_html=True)
                except:
                    st.markdown("<div class='haber-card'>⚠️ Haber servisine şu an ulaşılamıyor.</div>", unsafe_allow_html=True)

                # VIP Analiz
                st.markdown(f"""<div class='asistan-box'><b style='color:#00ff88;'>🤵 VIP ANALİZ:</b> Teknik skor %{skor}. { 'Trend alıcılı, pozisyon korunabilir.' if skor > 65 else 'Kararsız bölge, hacim artışı beklenmeli.' }</div>""", unsafe_allow_html=True)
            else:
                st.warning("Bu hisse kodu için veri bulunamadı. Lütfen doğru yazdığınızdan emin olun (Örn: THYAO).")
        except Exception as e:
            st.error(f"Bağlantı Hatası: Lütfen internetinizi ve hisse kodunu kontrol edin.")

    # 3. SAĞ: RADAR & ADMIN
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        r_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "SASA.IS"]
        try:
            r_data = yf.download(r_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(1)
            for s in r_list:
                c, p = r_data[s].iloc[-1], r_data[s].iloc[-2]
                pct = ((c - p) / p) * 100
                st.markdown(f"<div class='radar-card'><div>{s.split('.')[0]}<br><span style='font-size:10px; color:#8b949e;'>Vol: {int(c*1.5)}M</span></div><div class='{'pct-up' if pct>=0 else 'pct-down'}'>{pct:.2f}%</div></div>", unsafe_allow_html=True)
        except: pass

        if st.session_state.get("role") == "admin":
            st.markdown("<div style='background:#161b22; border:1px dashed #00ff88; padding:10px; border-radius:10px; margin-top:30px;'>🔑 **KEY ÜRET**", unsafe_allow_html=True)
            if st.button("ÜRET"): st.code(f"GAI-{int(time.time())}-30-VIP")
            st.markdown("</div>", unsafe_allow_html=True)
