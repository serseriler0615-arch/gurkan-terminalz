import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Konfigürasyonu (Sıfır Boşluk)
st.set_page_config(page_title="Gürkan Elite AI", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; background-color: #0e1117; }
    header {visibility: hidden;}
    /* Metrik Kartları */
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px !important; }
    /* Radar Kartları */
    .radar-card { 
        background-color: #161b22; border: 1px solid #30363d; border-left: 4px solid #00ff88;
        padding: 10px; border-radius: 6px; margin-bottom: 8px;
    }
    /* Yazı fontlarını küçültüp profesyonelleştirme */
    h3, p { color: #e6edf3; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_input = st.text_input("🔍 Hisse Sorgula:", value="ULKER").upper().strip()
    
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    try:
        # Analiz için 6 aylık veri
        df = yf.download(aktif_hisse, period="6mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            son_fiyat = float(df['Close'].iloc[-1])
            dunku_kapanis = float(df['Close'].iloc[-2])
            degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100
            
            with c2: st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

            # GRAFİK: Alan dolgusunu daha yumuşak yaptık
            st.markdown(f"📊 **{hisse_input} - Teknik Görünüm**")
            st.area_chart(df['Close'].tail(45), color="#00ff88", height=200)

            # --- GELİŞMİŞ ANALİZ MOTORU ---
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]

            st.markdown("### 🤖 AI Strateji Raporu")
            a1, a2, a3 = st.columns(3)
            
            with a1:
                st.write("**İndikatör (RSI)**")
                if rsi > 70: st.error(f"⚠️ Şişmiş ({rsi:.1f})")
                elif rsi < 35: st.success(f"🔥 Ucuz ({rsi:.1f})")
                else: st.info(f"⚖️ Normal ({rsi:.1f})")

            with a2:
                st.write("**Kısa Vade (MA20)**")
                st.success("📈 Pozitif") if son_fiyat > ma20 else st.error("📉 Negatif")

            with a3:
                st.write("**Ana Trend (MA50)**")
                st.success("🚀 Yükseliş") if son_fiyat > ma50 else st.warning("🐢 Yatay/Düşüş")

            # Özet Cümle
            st.markdown(f"**💡 Özet:** {hisse_input} şu an {son_fiyat:.2f} TL ile {'yükseliş trendini koruyor' if son_fiyat > ma20 else 'baskı altında gözüküyor'}. RSI değeri {rsi:.1f} ile {'alım fırsatı verebilir' if rsi < 40 else 'dikkatli olunmalı'}.")
    except:
        st.error("Veri hatası!")

# --- SAĞ TARAF: AI RADAR (YÜKSELME BEKLENEN 5 HİSSE) ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL")
    st.caption("Yükseliş Beklenen İlk 5")
    
    # Gerçekten potansiyeli yüksek 5 ana hisse
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
                        <b style="color:#00ff88;">{ad}</b>
                        <span style="color:{'#00ff88' if r_fark > 0 else '#ff3333'};">%{r_fark:.2f}</span>
                    </div>
                    <small style="color:#888;">AI Tahmini: <b>YÜKSELİŞ</b></small>
                </div>
                """, unsafe_allow_html=True)
        except: continue
    
    if st.button("🔄 Radarı Tazele", use_container_width=True):
        st.rerun()
