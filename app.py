import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Terminal Stil Ayarları
st.set_page_config(page_title="Gürkan AI - Kişisel Asistan", layout="wide", initial_sidebar_state="collapsed")

tr_aylar = {"Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisan", "May": "Mayıs", "Jun": "Haziran",
            "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"}

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; }
    .personal-assistant { 
        background: linear-gradient(135deg, #1c2128 0%, #0d1117 100%); 
        border: 1px solid #00ff88; padding: 20px; border-radius: 15px; 
        color: #e6edf3; font-style: italic; line-height: 1.6;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_kod = st.text_input("🔍 Hangi hisseyi inceleyelim?", value="ISCTR").upper().strip()
    
    sembol = hisse_kod if "." in hisse_kod else hisse_kod + ".IS"

    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period="6mo", interval="1d")
        
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # Anlık Veriler
            son_fiyat = ticker.fast_info['last_price']
            dunku_kapanis = df['Close'].iloc[-2]
            yuzde_degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

            with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{yuzde_degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

            # --- 20 GÜNLÜK TÜRKÇE GRAFİK ---
            plot_df = df[['Close']].tail(20).copy()
            tr_eks = []
            for d in plot_df.index:
                t = d.strftime("%d %b")
                for e, tr in tr_aylar.items(): t = t.replace(e, tr)
                tr_eks.append(t)
            plot_df.index = tr_eks
            
            st.write(f"📈 **{hisse_kod} - Son 20 İş Günü Trend Analizi**")
            st.area_chart(plot_df, color="#00ff88", height=250)

            # --- 🧠 STRATEJİ VERİLERİ ---
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            ma50 = df['Close'].rolling(50).mean().iloc[-1]
            diff = df['Close'].diff(); g = (diff.where(diff > 0, 0)).rolling(14).mean(); l = (-diff.where(diff < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]

            st.markdown("### 🛰️ Teknik Sinyal Merkezi")
            s1, s2, s3 = st.columns(3)
            
            # Hatasız Sinyal Kutuları
            with s1:
                if rsi > 70: st.error(f"🚨 RSI: Aşırı Alım ({rsi:.1f})")
                elif rsi < 35: st.success(f"🔥 RSI: Fırsat ({rsi:.1f})")
                else: st.info(f"⚖️ RSI: Dengeli ({rsi:.1f})")
            with s2:
                if son_fiyat > ma20: st.success(f"📈 MA20: Üstünde")
                else: st.error(f"📉 MA20: Altında")
            with s3:
                if ma20 > ma50: st.success(f"🚀 Trend: Yükseliş")
                else: st.warning(f"⚠️ Trend: Zayıf")

            # --- 🤵 KİŞİSEL ASİSTANIN YORUMU ---
            asistan_mesaji = f"Dostum, {hisse_kod} için tabloyu inceledim. "
            if rsi < 40 and son_fiyat > ma20:
                asistan_mesaji += f"Şu an teknik olarak harika bir yerde. RSI {rsi:.1f} ile henüz yorulmamış ve 20 günlük ortalamanın ({ma20:.2f} TL) üzerinde güç topluyor. Yukarı yönlü bir ivme beklenebilir."
            elif rsi > 65:
                asistan_mesaji += f"Dikkatli olmanı öneririm; hisse biraz şişmiş (RSI: {rsi:.1f}). Buralardan bir miktar kar satışı gelmesi normal olur, yeni alım için {ma20:.2f} TL seviyelerine çekilmeyi beklemek daha zekice olabilir."
            else:
                asistan_mesaji += f"Şu an tam bir 'bekle-gör' evresinde. Fiyat {ma20:.2f} TL olan kısa vade desteğinin {'üzerinde' if son_fiyat > ma20 else 'altında'}. Net bir yön tayini için hacimli bir kırılım beklemelisin."

            st.markdown(f"""
            <div class="personal-assistant">
                <b>🤵 Gürkan AI Kişisel Analist Notu:</b><br>
                "{asistan_mesaji}"
            </div>
            """, unsafe_allow_html=True)

    except: st.error("Hisse bilgisi alınırken bir sorun oluştu.")

# --- SAĞ RADAR (5 HİSSE) ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL RADARI")
    radar = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    for r in radar:
        try:
            rd = yf.download(r, period="2d", interval="1d", progress=False)
            if not rd.empty:
                if isinstance(rd.columns, pd.MultiIndex): rd.columns = rd.columns.get_level_values(0)
                f = ((rd['Close'].iloc[-1] - rd['Close'].iloc[-2]) / rd['Close'].iloc[-2]) * 100
                st.markdown(f"""
                <div class="radar-card">
                    <b style="color:#00ff88;">{r.split(".")[0]}</b> : %{f:.2f}
                </div>
                """, unsafe_allow_html=True)
        except: continue
    st.button("🔄 Radarı Yenile", use_container_width=True)
