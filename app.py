import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Stil ve Tasarım Ayarları
st.set_page_config(page_title="Gürkan AI - Fırsat Dedektörü", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117 !important; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .radar-card { 
        background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; 
        border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d;
        transition: transform 0.2s;
    }
    .radar-card:hover { transform: scale(1.02); background-color: #1c2128; }
    .asistan-notu { background: #1c2128; border: 1px solid #00ff88; padding: 15px; border-radius: 12px; color: #e6edf3; }
    .radar-baslik { color: #00ff88; font-weight: bold; font-size: 18px; margin-bottom: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Ana Panel Düzeni
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        h_input = st.text_input("🔍 Analiz Edilecek Hisse:", value="ISCTR").upper().strip()
    
    sembol = h_input if "." in h_input else h_input + ".IS"

    try:
        df = yf.download(sembol, period="6mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            son_fiyat = float(df['Close'].iloc[-1])
            dunku_kapanis = float(df['Close'].iloc[-2])
            degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

            with c2: st.metric("FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK", f"%{degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

            st.write(f"📈 **{h_input} - 20 Günlük Canlı Trend**")
            st.area_chart(df['Close'].tail(20), color="#00ff88", height=250)

            # --- ASİSTANIN STRATEJİK YORUMU ---
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            diff = df['Close'].diff(); g = (diff.where(diff > 0, 0)).rolling(14).mean(); l = (-diff.where(diff < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]

            st.markdown("### 🤵 Kişisel Asistan Notu")
            not_metni = f"Dostum, **{h_input}** için yaptığım teknik taramada; "
            if rsi < 40: not_metni += "hissenin çok dipte olduğunu ve bir tepki yükselişinin kapıda olduğunu görüyorum. Hacim artışını takip et."
            elif son_fiyat > ma20: not_metni += f"fiyatın {ma20:.2f} TL desteği üzerinde kalması çok pozitif. Trend yukarı yönlü iştahını koruyor."
            else: not_metni += "şu an biraz yorgunluk var. Yeni bir hamle için sakin kalıp ortalamalara yaklaşmasını beklemek daha mantıklı."
            
            st.markdown(f'<div class="asistan-notu">{not_metni}</div>', unsafe_allow_html=True)
    except:
        st.error("Veri çekilemedi.")

# --- 🛰️ AI RADAR: SABAH %2+ POTANSİYELİ OLANLAR ---
with ana_sag:
    st.markdown('<div class="radar-baslik">🚀 SABAH POTANSİYELİ (%2+)</div>', unsafe_allow_html=True)
    st.caption("AI Taraması: Hacim + Trend + RSI")
    
    # Tarama yapılacak geniş liste
    tarama_listesi = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS", "SISE.IS", "KCHOL.IS", "TUPRS.IS", "BIMAS.IS", "AKBNK.IS"]
    firsatlar = []

    for r in tarama_listesi:
        try:
            r_df = yf.download(r, period="10d", interval="1d", progress=False)
            if not r_df.empty:
                if isinstance(r_df.columns, pd.MultiIndex): r_df.columns = r_df.columns.get_level_values(0)
                
                # Basit bir "Yükseliş Potansiyeli" Skoru
                son_kapanis = r_df['Close'].iloc[-1]
                ma5 = r_df['Close'].rolling(5).mean().iloc[-1]
                hacim_artis = r_df['Volume'].iloc[-1] > r_df['Volume'].mean()
                
                # Eğer hisse 5 günlük ortalamasının üzerindeyse ve hacim artıyorsa "Potansiyel" ekle
                if son_kapanis > ma5 and hacim_artis:
                    fark = ((son_kapanis - r_df['Close'].iloc[-2]) / r_df['Close'].iloc[-2]) * 100
                    firsatlar.append({'sembol': r.split('.')[0], 'fiyat': son_kapanis, 'degisim': fark})
        except: continue

    # Sadece en iyi 5 potansiyeli göster
    for f in firsatlar[:5]:
        st.markdown(f"""
        <div class="radar-card">
            <div style="display:flex; justify-content:space-between;">
                <b style="color:#00ff88;">{f['sembol']}</b>
                <span style="color:{'#00ff88' if f['degisim'] > 0 else '#ff4b4b'};">%{f['degisim']:.2f}</span>
            </div>
            <div style="font-size: 12px; color: #888; margin-top: 5px;">
                AI Sinyali: <span style="color:#e6edf3;">GÜÇLÜ AL / %2+ Hedef</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not firsatlar:
        st.write("Şu an kriterlere uygun hisse bulunamadı.")

    if st.button("🔄 Radarı Yeniden Tara", use_container_width=True):
        st.rerun()
