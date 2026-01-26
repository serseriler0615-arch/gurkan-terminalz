import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI Pro Radar", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    header {visibility: hidden;}
    .stMetric { background-color: #1a1c24; border: 1px solid #30363d; border-radius: 10px; padding: 10px !important; }
    .radar-box { background-color: #0e1117; border: 1px solid #00ff88; padding: 10px; border-radius: 10px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Ana Panel Düzeni (Sol: Analiz, Sağ: Radar)
ana_sol, ana_sag = st.columns([3, 1])

# --- SOL TARAF: DETAYLI ANALİZ ---
with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_input = st.text_input("", value="ULKER", label_visibility="collapsed").upper().strip()
    
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    try:
        df_raw = yf.download(aktif_hisse, period="6mo", interval="1d", progress=False)
        if not df_raw.empty:
            df = df_raw.copy()
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            son_fiyat = float(df['Close'].iloc[-1])
            degisim = ((son_fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            with c2: st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("DEĞİŞİM", f"%{degisim:.2f}")

            # Grafik
            st.line_chart(df['Close'].tail(30), color="#00ff88", height=250)

            # AI Karar Motoru
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]

            st.subheader("🤖 AI Teknik Raporu")
            r1, r2, r3 = st.columns(3)
            with r1: st.info(f"RSI: {rsi:.1f}")
            with r2: st.success("Trend: Pozitif") if son_fiyat > ma20 else st.error("Trend: Negatif")
            with r3: 
                if rsi < 35: st.success("Sinyal: GÜÇLÜ AL")
                elif rsi > 65: st.error("Sinyal: SATIŞ YAKIN")
                else: st.warning("Sinyal: BEKLE")
    except:
        st.error("Veri hatası!")

# --- SAĞ TARAF: AI RADAR (YÜKSELME POTANSİYELİ) ---
with ana_sag:
    st.markdown("### 🛰️ AI RADAR")
    st.caption("Yükseliş Potansiyeli Yüksekler")
    
    # Taramak istediğimiz ana hisseler
    tarama_listesi = ["THYAO.IS", "ASELS.IS", "SASA.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS", "SISE.IS"]
    
    for sembol in tarama_listesi:
        try:
            t_data = yf.download(sembol, period="20d", interval="1d", progress=False)
            if not t_data.empty:
                t_close = t_data['Close']
                if isinstance(t_close, pd.DataFrame): t_close = t_close.iloc[:, 0]
                
                # Basit bir puanlama: Son 3 gün yükselmiş mi? RSI dipte mi?
                t_rsi = 50 # Varsayılan
                diff = t_close.diff()
                g = (diff.where(diff > 0, 0)).tail(14).mean()
                l = (-diff.where(diff < 0, 0)).tail(14).mean()
                if l != 0: t_rsi = 100 - (100 / (1 + (g/l)))
                
                temiz_ad = sembol.replace(".IS", "")
                
                # Radar Sinyali: RSI 45'ten küçük ve fiyat toparlıyorsa göster
                if t_rsi < 50:
                    with st.container():
                        st.markdown(f"""
                        <div class="radar-box">
                            <b style="color:#00ff88;">{temiz_ad}</b><br>
                            <small>RSI: {t_rsi:.1f} | Sinyal: Potansiyel 🔥</small>
                        </div>
                        """, unsafe_allow_html=True)
        except:
            continue
    
    st.divider()
    if st.button("🔄 Radarı Yenile"):
        st.rerun()
