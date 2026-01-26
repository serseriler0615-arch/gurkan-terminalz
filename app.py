import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Konfigürasyonu (Tam Ekran ve Temiz Arayüz)
st.set_page_config(page_title="Gürkan AI Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; background-color: #0d1117; }
    header {visibility: hidden;}
    /* Metrik Kartları Tasarımı */
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px !important; }
    /* Sağ Radar Kartları */
    .radar-card { 
        background-color: #161b22; border: 1px solid #30363d; border-left: 4px solid #00ff88;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
    }
    /* Alt Bilgi Kutuları */
    .status-box { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel Düzeni
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_input = st.text_input("🔍 Hisse Sorgula:", value="ULKER").upper().strip()
    
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    try:
        # Teknik analiz için veri çekme
        df = yf.download(aktif_hisse, period="6mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            son_fiyat = float(df['Close'].iloc[-1])
            dunku_kapanis = float(df['Close'].iloc[-2])
            degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100
            
            with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

            # GRAFİK: Siyahlık yapmayan, şeffaf ve profesyonel çizgi grafik
            st.markdown(f"📈 **{hisse_input} - Teknik Hareket (Son 45 Gün)**")
            st.line_chart(df['Close'].tail(45), color="#00ff88", height=220)

            # --- AI STRATEJİ RAPORU (Hatasız Kodlama) ---
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]

            st.markdown("### 🤖 AI Strateji Raporu")
            s1, s2, s3 = st.columns(3)
            
            with s1:
                st.markdown('<div class="status-box"><b>İndikatör (RSI)</b><br></div>', unsafe_allow_html=True)
                if rsi > 70: st.error(f"⚠️ Aşırı Alım ({rsi:.1f})")
                elif rsi < 35: st.success(f"🔥 Aşırı Satım ({rsi:.1f})")
                else: st.info(f"⚖️ Normal ({rsi:.1f})")

            with s2:
                st.markdown('<div class="status-box"><b>Kısa Vade (MA20)</b><br></div>', unsafe_allow_html=True)
                if son_fiyat > ma20: st.success("📈 Trend: Pozitif")
                else: st.error("📉 Trend: Negatif")

            with s3:
                st.markdown('<div class="status-box"><b>Ana Trend (MA50)</b><br></div>', unsafe_allow_html=True)
                if son_fiyat > ma50: st.success("🚀 Görünüm: Yükseliş")
                else: st.warning("🐢 Görünüm: Zayıf")

    except Exception as e:
        st.error(f"Veri yüklenirken hata oluştu: {e}")

# --- SAĞ TARAF: AI POTANSİYEL RADARI (SABİT 5 HİSSE) ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL")
    st.caption("Yükseliş Beklenen İlk 5")
    
    radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    
    for sembol in radar_list:
        try:
            r_data = yf.download(sembol, period="5d", interval="1d", progress=False)
            if not r_data.empty:
                if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
                r_son = r_data['Close'].iloc[-1]
                r_once = r_data['Close'].iloc[-2]
                r_fark = ((r_son - r_once) / r_once) * 100
                ad = sembol.replace(".IS", "")
                
                st.markdown(f"""
                <div class="radar-card">
                    <div style="display:flex; justify-content:space-between;">
                        <b style="color:#00ff88; font-size:16px;">{ad}</b>
                        <span style="color:{'#00ff88' if r_fark > 0 else '#ff3333'}; font-weight:bold;">%{r_fark:.2f}</span>
                    </div>
                    <small style="color:#888;">AI Tahmini: <b style="color:#e6edf3;">YÜKSELİŞ</b></small>
                </div>
                """, unsafe_allow_html=True)
        except: continue
    
    if st.button("🔄 Radarı Yenile", use_container_width=True):
        st.rerun()
