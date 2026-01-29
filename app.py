import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Stability", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "THYAO", "EREGL", "TUPRS"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. MASTER CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 30px; border-top: 6px solid #ffcc00; margin-bottom: 25px; }
    .price-text { font-size: clamp(35px, 5vw, 55px); font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #ffffff; }
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; margin-bottom: 5px; }
    .radar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-top: 25px; }
    .radar-item { background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
    .intel-box { background: rgba(255, 204, 0, 0.03); border-radius: 12px; padding: 20px; margin-top: 25px; border-left: 6px solid #ffcc00; border: 1px solid #30363d; border-left: 6px solid #ffcc00; }
    .plus-badge { background: #ffcc00; color: #000; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 900; display: inline-block; margin-bottom: 10px; }
    .report-content { color: #d1d5db; font-size: 15px; line-height: 1.6; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; border-radius: 8px !important; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
def get_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        pc = float(df['Close'].iloc[-2])
        ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        target = lp + (atr * 2.6)
        stop = min(lp - (atr * 2.2), ma20 * 0.95)
        
        # Değişkenleri f-string dışında hazırlayalım ki hata almayalım
        if vol_r < 1.0:
            sig, col = "HACİM ONAYI YOK", "#8b949e"
            rep = f"KRİTİK UYARI: {symbol} üzerinde işlem hacmi yetersiz ({vol_r:.1f}x). Fiyatın {ma20:.2f} pivotu üzerinde olması yanıltıcı (Fake) olabilir."
        else:
            sig, col = "TREND ONAYLANDI", "#00ff88"
            rep = f"Hacim desteği ({vol_r:.1f}x) ile trend güçleniyor. {ma20:.2f} pivotu üzerinde kalındıkça {target:.2f} hedefi aktiftir."
            
        if lp < ma20:
            sig, col = "AYI BASKISI", "#ff4b4b"
            rep = f"Negatif bölge. {ma20:.2f} pivotu direnç olarak çalışıyor. {stop:.2f} desteğine geri çekilme riski mevcut."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "report": rep, "sig": sig, "col": col, "vol": vol_r}
    except: return None

# --- 4. DASHBOARD ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:5px;'>GÜRKAN AI : STRATEJİ MERKEZİ</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c3:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

f_cols = st.columns(len(st.session_state["favorites"]))
for i, f in enumerate(st.session_state["favorites"]):
    if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

res = get_analysis(st.session_state["last_sorgu"])
if res:
    # Değişkenleri güvenli bir şekilde HTML içine gömelim
    color_val = "#00ff88" if res['ch'] > 0 else "#ff4b4b"
    
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;'>
            <div>
                <p class='label-mini'>{st.session_state["last_sorgu"]} // TERMINAL CORE</p>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{color_val}; font-size:24px; font-weight:700;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['col']}; font-weight:bold; font-size:20px;'>{res['sig']}</span><br>
                <span class='label-mini'>INTENSITY: {res['vol']:.1f}x</span>
            </div>
        </div>
        <div class='radar-grid'>
            <div class='radar-item'><p class='label-mini'>PİVOT (MA20)</p><p style='font-size:26px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 5px solid #00ff88;'><p class='label-mini'>PRO TARGET (+)</p><p style='font-size:26px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 5px solid #ff4b4b;'><p class='label-mini'>SAFE STOP LOSS</p><p style='font-size:26px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        <div class='intel-box'>
            <span class='plus-badge'>GÜRKAN AI RESEARCH (+)</span>
            <p class='report-content'>"{res['report']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
