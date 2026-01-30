import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : v232 Final", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "SASA", "SISE", "ISCTR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "SASA"

SCAN_LIST = ["THYAO", "SASA", "SISE", "ISCTR", "TUPRS", "AKBNK", "EREGL", "KCHOL", "ASELS", "BIMAS", "VBTYZ", "HUNER"]

# --- 2. CSS (TAM PAKET) ---
st.markdown("""
<style>
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 25px; border-left: 10px solid #ffcc00; margin-bottom: 20px; }
    .evidence-box { background: rgba(0, 255, 136, 0.05); border: 1px solid #30363d; border-radius: 12px; padding: 15px; margin-bottom: 15px; border-top: 3px solid #00ff88; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 15px; height: 800px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #00ff88; }
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; font-weight: bold; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #ffcc00 !important; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. DERİN ANALİZ MOTORU ---
def deep_inspector(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        vol_avg = df['Volume'].rolling(10).mean().iloc[-1]; vol_now = df['Volume'].iloc[-1]
        
        score = 0; notes = []
        if lp > ma20: 
            score += 40; notes.append("✅ Fiyat pivot (MA20) üzerinde.")
        else: notes.append("❌ Fiyat pivotun altında kalmış.")
        
        if vol_now > vol_avg * 1.1: 
            score += 30; notes.append(f"✅ Hacim güçlü (%{((vol_now/vol_avg)-1)*100:.0f} artış).")
        else: notes.append("⚠️ Hacim zayıf, katılım az.")
        
        if ch > 0: score += 10; notes.append("✅ Günlük momentum pozitif.")
        
        # RSI
        delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = (100 - (100 / (1 + g/l))).iloc[-1]
        if 40 < rsi < 70: score += 20; notes.append("✅ RSI ideal bölgede.")
        elif rsi > 70: notes.append("⚠️ RSI şişmiş (Aşırı alım).")

        decision = "GÜÇLÜ AL" if score >= 80 else ("AL" if score >= 60 else "BEKLE / İZLE")
        dec_col = "#00ff88" if score >= 60 else "#ffcc00"
        
        return {"p": lp, "ch": ch, "score": score, "df": df, "notes": notes, "dec": decision, "col": dec_col}
    except: return None

# --- 4. UI ---
m_col, r_col = st.columns([3, 1])

with m_col:
    # Arama ve Favori
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        is_fav = s_inp in st.session_state["favorites"]
        if st.button("🌟 ÇIKAR" if is_fav else "⭐ EKLE"):
            if is_fav: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Gold Favoriler
    if st.session_state["favorites"]:
        f_cols = st.columns(len(st.session_state["favorites"]))
        for i, fv in enumerate(st.session_state["favorites"]):
            if f_cols[i].button(fv, key=f"f_{fv}"):
                st.session_state["last_sorgu"] = fv; st.rerun()

    # MÜFETTİŞ RAPORU (BURASI GERİ GELDİ)
    res = deep_inspector(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div><p class='label-mini'>{st.session_state["last_sorgu"]}</p><span style='font-size:45px; font-weight:bold;'>{res['p']:.2f}</span><span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:20px;'> {res['ch']:+.2f}%</span></div>
                <div style='text-align:right;'><p class='label-mini'>KARAR</p><h1 style='color:{res['col']};'>{res['dec']}</h1></div>
            </div>
        </div>
        <div class='evidence-box'>
            <p class='label-mini' style='color:#00ff88;'>🕵️ MÜFETTİŞ NOTLARI (GÜVEN: %{res['score']})</p>
            <ul style='list-style-type:none; padding:0; margin:0;'>
                {"".join([f"<li style='margin-bottom:5px;'>{n}</li>" for n in res['notes']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 RADAR SİNYAL</p>", unsafe_allow_html=True)
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    for s in SCAN_LIST:
        r_res = deep_inspector(s)
        if r_res and r_res['score'] >= 50:
            st.markdown(f"""
            <div class='scan-item'>
                <div style='display:flex; justify-content:space-between;'><b>{s}</b><span style='color:#00ff88;'>%{r_res['score']}</span></div>
                <p style='font-size:11px; color:#ffcc00; margin:0;'>{r_res['dec']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"GİT {s}", key=f"r_{s}"):
                st.session_state["last_sorgu"] = s; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
