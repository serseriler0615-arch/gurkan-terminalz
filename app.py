import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. Terminal Stil Ayarları (Tam Kontrol)
st.set_page_config(page_title="Gürkan AI - Kişisel Asistan", layout="wide", initial_sidebar_state="collapsed")

tr_aylar = {"Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisan", "May": "Mayıs", "Jun": "Haziran",
            "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"}

st.markdown("""
    <style>
    /* Arka planı ve tüm konteynerları aynı renge sabitliyoruz */
    .stApp, .block-container, .main { background-color: #0d1117 !important; }
    header {visibility: hidden;}
    
    /* Plotly grafiğinin dışındaki tüm olası siyah çerçeveleri kaldır */
    div[data-testid="stPlotlyChart"] { background-color: transparent !important; border: none !important; }
    iframe { background-color: transparent !important; }
    
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; }
    .personal-assistant { 
        background: #1c2128; border: 1px solid #00ff88; padding: 20px; border-radius: 15px; 
        color: #e6edf3; font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        h_input = st.text_input("🔍 Hangi hisseyi inceleyelim?", value="ISCTR").upper().strip()
    
    sembol = h_input if "." in h_input else h_input + ".IS"

    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period="6mo", interval="1d")
        
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            son_fiyat = ticker.fast_info['last_price']
            dunku_kapanis = df['Close'].iloc[-2]
            yuzde_degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

            with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{yuzde_degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

            # --- SİYAHSIZ PLOTLY GRAFİK ---
            plot_df = df[['Close']].tail(20).copy()
            tr_eks = [d.strftime("%d %b").replace(d.strftime("%b"), tr_aylar.get(d.strftime("%b"), d.strftime("%b"))) for d in plot_df.index]
            
            fig = px.area(x=tr_eks, y=plot_df['Close'])
            # Çizgi ve dolgu rengini neon yeşil yapıyoruz
            fig.update_traces(line_color='#00ff88', fillcolor='rgba(0, 255, 136, 0.15)')
            
            # BURASI KRİTİK: Tüm arka planları sayfa rengiyle (0d1117) eşitliyoruz
            fig.update_layout(
                paper_bgcolor='#0d1117', 
                plot_bgcolor='#0d1117',
                font_color='#e6edf3', 
                margin=dict(l=0, r=0, t=10, b=0), 
                height=280,
                xaxis=dict(showgrid=False, color='#888'), 
                yaxis=dict(showgrid=True, gridcolor='#1c2128', color='#888', position=0)
            )
            
            st.write(f"📈 **{h_input} - Trend Analizi**")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # --- TEKNİK ANALİZ VE ASİSTAN ---
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            diff = df['Close'].diff(); g = (diff.where(diff > 0, 0)).rolling(14).mean(); l = (-diff.where(diff < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]

            st.markdown("### 🛰️ Teknik Sinyal Merkezi")
            s1, s2 = st.columns(2)
            with s1:
                if rsi > 70: st.error(f"🚨 RSI: Aşırı Alım ({rsi:.1f})")
                elif rsi < 35: st.success(f"🔥 RSI: Fırsat ({rsi:.1f})")
                else: st.info(f"⚖️ RSI: Dengeli ({rsi:.1f})")
            with s2:
                if son_fiyat > ma20: st.success(f"📈 MA20: Üstünde")
                else: st.error(f"📉 MA20: Altında")

            # --- KİŞİSEL ASİSTAN ---
            asistan_notu = f"Dostum, {h_input} için durumu süzdüm. "
            if rsi < 45 and son_fiyat > ma20: asistan_notu += "Teknik olarak çok diri duruyor. 20 günlük desteğin üzerinde kalması güven verici."
            elif rsi > 68: asistan_notu += "Hisse biraz nefessiz kalmış gibi, buralardan girmek riskli olabilir."
            else: asistan_notu += "Yatay seyir hakim, yön tayini için biraz daha izlemekte fayda var."

            st.markdown(f'<div class="personal-assistant"><b>🤵 Gürkan AI Notu:</b><br>"{asistan_notu}"</div>', unsafe_allow_html=True)

    except: st.error("Veri çekilemedi.")

with ana_sag:
    st.markdown("### 🛰️ AI RADAR")
    radar = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    for r in radar:
        try:
            rd = yf.download(r, period="2d", interval="1d", progress=False)
            if not rd.empty:
                f = ((rd['Close'].iloc[-1] - rd['Close'].iloc[-2]) / rd['Close'].iloc[-2]) * 100
                st.markdown(f'<div class="radar-card"><b>{r.split(".")[0]}</b> : %{f:.2f}</div>', unsafe_allow_html=True)
        except: continue
