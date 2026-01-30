import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Müfettiş v228", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS (PREMIUM GÜVEN TEMASI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 25px; border-left: 8px solid #ffcc00; margin-bottom: 20px; }
    .evidence-box { background: rgba(0, 255, 136, 0.03); border: 1px solid #1e2329; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-top: 3px solid #00ff88; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 15px; height: 850px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; border-left: 5px solid #00ff88; }
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: bold; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border-radius: 8px; font-weight: bold; height: 40px; }
</style>
""", unsafe_allow_html=True)

# --- 3. MÜFETTİŞ ANALİZ MOTORU ---
def deep_inspector(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean(); ma50 = df['Close'].rolling(50).mean()
        vol_avg = df['Volume'].rolling(10).mean().iloc[-1]
        vol_now = df['Volume'].iloc[-1]
        
        # RSI
        delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = (100 - (100 / (1 + g/l))).iloc[-1]
        
        # Gürkan'ın Kanıtları
        evidences = []
        confidence = 0
        
        if lp > ma20.iloc[-1]: 
            evidences.append("✅ Fiyat kısa vadeli pivotun (MA20) üzerinde; trend güvende.")
            confidence += 35
        else: evidences.append("❌ Fiyat pivotun altında; baskı sürüyor.")
            
        if vol_now > vol_avg * 1.2: 
            evidences.append(f"✅ Hacim ortalamanın %{( (vol_now/vol_avg)-1)*100:.0f} üzerinde; kurumsal ilgi var.")
            confidence += 35
        else: evidences.append("⚠️ Hacim zayıf; hareket henüz onaylanmadı.")

        if 40 < rsi < 65: 
            evidences.append("✅ RSI 'tatlı noktada'; ne çok ucuz ne de şişmiş, yol açık.")
            confidence += 30
        elif rsi > 70: evidences.append("⚠️ RSI aşırı alımda; kısa süreli düzeltme kapıda."); confidence += 10
        
        decision = "GÜÇLÜ AL" if confidence >= 80 else ("BEKLE / GÖZLE" if confidence >= 50 else "UZAK DUR")
        dec_col = "#00ff88" if confidence >= 80 else ("#ffcc00" if confidence >= 50 else "#ff4b4b")

        return {"p": lp, "ch": ch, "rsi": rsi, "conf": confidence, "ev": evidences, "dec": decision, "col": dec_col, "df": df, "ma20": ma20.iloc[-1]}
    except: return None

# --- 4. UI ---
m_col, r_col = st.columns([3, 1])

with m_col:
    # Arama
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("MÜFETTİŞ SORGUSU", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 İNCELE"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("⭐ FAVORİ"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favori Çubukları
    if st.session_state["favorites"]:
        fav_cols = st.columns(len(st.session_state["favorites"]))
        for i, fv in enumerate(st.session_state["favorites"]):
            if fav_cols[i].button(fv): st.session_state["last_sorgu"] = fv; st.rerun()

    # Müfettiş Raporu
    res = deep_inspector(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]} // DOSYA NO: {pd.Timestamp.now().strftime('%Y%m%d')}</p>
                    <span style='font-size:45px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:22px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini'>GÜVEN SKORU</p>
                    <h1 style='color:{res['col']}; margin:0;'>%{res['conf']}</h1>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='evidence-box'>
            <p class='label-mini' style='color:#00ff88;'>🕵️ MÜFETTİŞ GÜRKAN'IN ANALİZ NOTLARI</p>
            <h3 style='color:{res['col']}; margin-bottom:15px;'>KARAR: {res['dec']}</h3>
            <ul style='list-style-type: none; padding:0;'>
                {''.join([f"<li style='margin-bottom:8px;'>{e}</li>" for e in res['ev']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 RADAR (GÜÇLÜ SİNYALLER)</p>", unsafe_allow_html=True)
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    
    # Radarda sadece müfettiş onayı %70 üstü olanlar
    for s in SCAN_LIST:
        r_res = deep_inspector(s)
        if r_res and r_res['conf'] >= 70:
            st.markdown(f"""
            <div class='scan-item'>
                <div style='display:flex; justify-content:space-between;'><b>{s}</b><span style='color:#00ff88;'>%{r_res['conf']} GÜVEN</span></div>
                <p style='font-size:11px; color:#8b949e; margin-top:5px;'>Fiyat: {r_res['p']:.2f} | RSI: {r_res['rsi']:.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"DETAY: {s}", key=f"r_{s}"):
                st.session_state["last_sorgu"] = s
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
