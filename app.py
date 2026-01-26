import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Sayfa ve Stil Ayarları
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 98%; background-color: #0e1117; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #30363d; border-radius: 12px; padding: 10px; }
    /* Grafiğin kapladığı alanı zorla temizle */
    .js-plotly-plot, .plot-container { border: none !important; margin-bottom: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with c1:
    hisse_input = st.text_input("", placeholder="🔍 Hisse Kodu...", label_visibility="collapsed").upper().strip()
with c2:
    secilen_fav = st.selectbox("", st.session_state.favoriler, label_visibility="collapsed")

aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Motoru
try:
    # Analiz için günlük veri (Daha doğru RSI için)
    data = yf.download(aktif_hisse, period="3mo", interval="1d", progress=False, auto_adjust=True)
    
    if not data.empty:
        son_fiyat = float(data['Close'].iloc[-1])
        onceki_kapanis = float(data['Close'].iloc[-2])
        fark = son_fiyat - onceki_kapanis
        degisim = (fark / onceki_kapanis) * 100

        with c3: st.metric("FİYAT", f"{son_fiyat:.2f} TL")
        with c4: st.metric("GÜNLÜK %", f"%{degisim:.2f}", f"{fark:+.2f}")

        # 4. Grafik (Hatasız Mod)
        # Eğer veri çok azsa çizgi grafik, yeterliyse mum grafik
        fig = go.Figure()

        if len(data) > 0:
            # Mum grafik yerine daha kararlı olan Alan Grafiği (Siyahlık riskini sıfırlar)
            fig.add_trace(go.Scatter(
                x=data.index, y=data['Close'],
                fill='tozeroy', 
                line=dict(color='#00ff88', width=2),
                fillcolor='rgba(0, 255, 136, 0.1)',
                name="Fiyat"
            ))
        
        fig.update_layout(
            template="plotly_dark",
            height=400,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. NET ANALİZ (RSI 14)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        st.markdown("---")
        a1, a2, a3 = st.columns(3)
        
        with a1:
            if rsi > 70: st.error(f"🔴 SINYAL: SAT (RSI: {rsi:.1f})")
            elif rsi < 30: st.success(f"🟢 SINYAL: AL (RSI: {rsi:.1f})")
            else: st.info(f"🔵 SINYAL: BEKLE (RSI: {rsi:.1f})")
        
        with a2:
            st.warning(f"📊 Trend: {'Yükseliş' if degisim > 0 else 'Düşüş'}")
            
        with a3:
            st.link_button("🚀 HABERLER", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.error("Sembol bulunamadı veya veri çekilemiyor.")

except Exception as e:
    st.error("Veri hatası. Lütfen sayfayı yenileyin.")
