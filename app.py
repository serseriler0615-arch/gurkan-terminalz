import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa ve Stil Ayarları
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 98%; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #30363d; border-radius: 12px; }
    /* Siyahlık oluşmasını engelleyen arka plan ayarı */
    .js-plotly-plot { background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with c1:
    hisse_input = st.text_input("", placeholder="🔍 Hisse Kodu (Örn: SASA)", label_visibility="collapsed").upper().strip()
with c2:
    secilen_fav = st.selectbox("", st.session_state.favoriler, label_visibility="collapsed")

aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Motoru (Doğruluk Odaklı)
try:
    # Veriyi daha kararlı olması için 1 saatlik aralıklarla son 1 ay için çekiyoruz (Analiz tutarlılığı için)
    df = yf.download(aktif_hisse, period="1mo", interval="1h", progress=False, auto_adjust=True)
    
    if not df.empty and len(df) > 20:
        son_fiyat = float(df['Close'].iloc[-1])
        onceki_kapanis = float(df['Close'].iloc[-2])
        fark = son_fiyat - onceki_kapanis
        degisim = (fark / onceki_kapanis) * 100

        with c3: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
        with c4: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{fark:+.2f}")

        # 4. Siyahlığı Yok Eden Şeffaf Grafik
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.8])
        
        # Mum Grafik
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00ff88', decreasing_line_color='#ff3333',
            name="Fiyat"
        ), row=1, col=1)

        # Hacim Barları
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color='#30363d', opacity=0.5, name="Hacim"), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=450,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)', # Siyahlığı bitiren şeffaflık
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        # Eksenleri düzeltiyoruz ki mumlar tam otursun
        fig.update_yaxes(gridcolor='#222')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. NET VE DOĞRU ANALİZ MOTORU
        # RSI 14 Periyot (Standart Analiz)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])

        st.markdown("---")
        a1, a2 = st.columns([1, 1])
        
        with a1:
            if rsi > 70:
                st.error(f"🔴 AI SİNYAL: SAT (RSI: {rsi:.1f})")
                st.write("Teknik Uyarı: Hisse aşırı alım bölgesinde. Düzeltme gelebilir.")
            elif rsi < 30:
                st.success(f"🟢 AI SİNYAL: AL (RSI: {rsi:.1f})")
                st.write("Teknik Fırsat: Hisse aşırı satım bölgesinde. Tepki alımı beklenebilir.")
            else:
                st.info(f"🔵 AI SİNYAL: BEKLE (RSI: {rsi:.1f})")
                st.write("Durum: Hisse nötr bölgede. Trendin kırılımı beklenmeli.")

        with a2:
            st.link_button("🚀 GÜNCEL KAP VE HABERLER", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.error("Veri doğrulanamadı. Lütfen interneti veya kodu kontrol edin.")

except Exception as e:
    st.error("Terminal yüklenirken bir hata oluştu.")
