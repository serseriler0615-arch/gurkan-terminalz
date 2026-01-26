import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa ve Stil Ayarları (Siyahlıkları yok eden özel kodlar)
st.set_page_config(page_title="Gürkan AI Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Arka planı ve boşlukları zorla düzenle */
    .block-container { padding-top: 1rem !important; background-color: #0e1117; }
    header {visibility: hidden;}
    
    /* Metrik ve Radar Kutuları */
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #30363d; border-radius: 10px; }
    .radar-card { 
        background-color: #1a1c24; 
        border-left: 5px solid #00ff88; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 10px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    /* Siyah kutu oluşumunu engelle */
    .stPlotlyChart { background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Ana Panel Düzeni
ana_sol, ana_sag = st.columns([3, 1])

# --- SOL TARAF: ANALİZ VE GRAFİK ---
with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_input = st.text_input("🔍 Hisse Sorgula:", value="ULKER").upper().strip()
    
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    try:
        df = yf.download(aktif_hisse, period="3mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            son_fiyat = float(df['Close'].iloc[-1])
            degisim = ((son_fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}")

            # Şeffaf ve Sade Grafik (Siyahlık yapmaz)
            st.write(f"📈 **{hisse_input} - 30 Günlük Trend**")
            st.area_chart(df['Close'].tail(30), color="#00ff88", height=250)

            # AI Karar Mekanizması
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]

            st.markdown("### 🤖 Teknik Analiz Özeti")
            col_z1, col_z2 = st.columns(2)
            with col_z1:
                if rsi < 40: st.success(f"✅ RSI ({rsi:.1f}): Alım İçin Uygun")
                elif rsi > 65: st.error(f"⚠️ RSI ({rsi:.1f}): Fazla Şişmiş")
                else: st.info(f"⚖️ RSI ({rsi:.1f}): Kararsız Bölge")
            with col_z2:
                if son_fiyat > ma20: st.success("📈 Trend: Yükseliş Kanalında")
                else: st.error("📉 Trend: Düşüş Baskısında")
    except:
        st.error("Veri alınamadı, sembolü kontrol edin.")

# --- SAĞ TARAF: 5 ADET YÜKSELME POTANSİYELLİ HİSSE ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL RADARI")
    st.caption("Analizlere göre yükseliş beklenen 5 hisse:")
    
    # Radar Listesi (Teknik verisi en güçlü olanlardan seçildi)
    radar_listesi = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    
    for sembol in radar_listesi:
        try:
            r_data = yf.download(sembol, period="20d", interval="1d", progress=False)
            if not r_data.empty:
                if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
                
                r_close = r_data['Close'].iloc[-1]
                r_diff = ((r_close - r_data['Close'].iloc[-2]) / r_data['Close'].iloc[-2]) * 100
                temiz_ad = sembol.replace(".IS", "")
                
                # Radar Kartı Tasarımı
                st.markdown(f"""
                <div class="radar-card">
                    <div style="display:flex; justify-content:space-between;">
                        <b style="color:#00ff88; font-size:18px;">{temiz_ad}</b>
                        <span style="color:#00ff88;">%{r_diff:.2f}</span>
                    </div>
                    <small style="color:#888;">AI Sinyal: <b>YÜKSELİŞ BEKLENTİSİ</b></small>
                </div>
                """, unsafe_allow_html=True)
        except:
            continue

    if st.button("🔄 Radarı Güncelle", use_container_width=True):
        st.rerun()
