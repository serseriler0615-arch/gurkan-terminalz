import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI Master Pro", layout="wide", initial_sidebar_state="collapsed")

# Türkçe Ay Sözlüğü (Kesin Çözüm)
tr_aylar = {"Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisan", "May": "Mayıs", "Jun": "Haziran",
            "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"}

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    header {visibility: hidden;}
    /* Siyah kutuları engellemek için arka planı şeffaflaştır */
    .stApp { background: #0d1117; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; }
    /* Asistan yorum metnini beyaz yap */
    .asistan-yorum { color: #e6edf3; background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; font-size: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Panel Düzeni
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        h_input = st.text_input("🔍 Hisse Yaz:", value="ISCTR").upper().strip()
    
    sembol = h_input if "." in h_input else h_input + ".IS"

    try:
        # VERİ: Zeka için 6 aylık veri, Görsel için 20 gün
        ticker = yf.Ticker(sembol)
        full_df = ticker.history(period="6mo", interval="1d")
        
        if not full_df.empty:
            if isinstance(full_df.columns, pd.MultiIndex): full_df.columns = full_df.columns.get_level_values(0)
            
            # Gecikmeyi önlemek için fast_info
            curr_price = ticker.fast_info['last_price']
            prev_close = full_df['Close'].iloc[-2]
            change = ((curr_price - prev_close) / prev_close) * 100

            with c2: st.metric("SON FİYAT", f"{curr_price:.2f} TL")
            with c3: st.metric("GÜNLÜK %", f"%{change:.2f}", f"{curr_price-prev_close:+.2f}")

            # --- GRAFİK: 20 GÜN + TÜRKÇE + SİYAHSIZ ---
            plot_df = full_df[['Close']].tail(20).copy()
            tr_idx = []
            for d in plot_df.index:
                s = d.strftime("%d %b")
                for e, t in tr_aylar.items(): s = s.replace(e, t)
                tr_idx.append(s)
            plot_df.index = tr_idx
            
            st.markdown(f"📈 **{h_input} - Son 20 Günlük Trendy Görünüm**")
            st.area_chart(plot_df, color="#00ff88", height=280)

            # --- 🧠 SUPER AI ASİSTAN MOTORU ---
            ma20 = full_df['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = full_df['Close'].rolling(window=50).mean().iloc[-1]
            # RSI
            diff = full_df['Close'].diff()
            g = (diff.where(diff > 0, 0)).rolling(14).mean()
            l = (-diff.where(diff < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]

            st.markdown("### 🤖 Gürkan AI Strateji Raporu")
            s1, s2, s3 = st.columns(3)
            
            with s1:
                st.write("**RSI (GÜÇ)**")
                if rsi > 70: st.error(f"🚨 Aşırı Alım ({rsi:.1f})")
                elif rsi < 30: st.success(f"🔥 Aşırı Satım ({rsi:.1f})")
                else: st.info(f"⚖️ Dengeli ({rsi:.1f})")
            
            with s2:
                st.write("**TREND (MA20)**")
                st.success("🟢 Pozitif (Ort. Üstü)") if curr_price > ma20 else st.error("🔴 Negatif (Ort. Altı)")
            
            with s3:
                st.write("**ANA YÖN (MA50)**")
                st.success("🚀 YÜKSELİŞ") if ma20 > ma50 else st.warning("⚠️ ZAYIF TREND")

            # Zeki Yorum Alanı
            yorum = f"**Hisse Analizi:** {h_input} hissesi şu an {curr_price:.2f} TL seviyesinde. "
            if curr_price > ma20 and rsi < 65:
                yorum += "Teknik olarak 'Yükseliş Trendi' destekleniyor, RSI henüz doygunluğa ulaşmamış. Olumlu."
            elif rsi > 70:
                yorum += "Dikkat! RSI 70 üzerine çıkarak hissenin aşırı primlendiğini gösteriyor, düzeltme gelebilir."
            else:
                yorum += "Fiyat ortalamaların altında baskılanıyor. Yeni bir alım için MA20 ( {ma20:.2f} ) üzerine çıkması beklenmeli."
            
            st.markdown(f'<div class="asistan-yorum">{yorum}</div>', unsafe_allow_html=True)

    except: st.error("Sembol hatası veya veri çekilemedi.")

# --- SAĞ RADAR ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL")
    radar = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    for r in radar:
        try:
            rd = yf.download(r, period="2d", interval="1d", progress=False)
            if not rd.empty:
                f = ((rd['Close'].iloc[-1] - rd['Close'].iloc[-2]) / rd['Close'].iloc[-2]) * 100
                st.markdown(f'<div class="radar-card"><b>{r.split(".")[0]}</b> : %{f:.2f}</div>', unsafe_allow_html=True)
        except: continue
    if st.button("🔄 Radarı Yenile", use_container_width=True): st.rerun()
