import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["AKBNK", "THYAO", "ASELS"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. MOMENTUM UI CSS ---
st.set_page_config(page_title="Gürkan AI v166", layout="wide")
st.markdown("""
<style>
    .stApp { background: #05070a !important; color: #e1e1e1 !important; }
    .exec-card {
        background: #0d1117; border: 1px solid #30363d; border-radius: 12px;
        padding: 20px; margin-bottom: 10px; border-top: 4px solid #ffcc00;
    }
    .price-big { font-size: 42px; font-weight: bold; margin: 0; color: #fff; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; }
    .momentum-badge { padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    div.stButton > button { background: #161b22 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. MOMENTUM ANALİZ MOTORU ---
def get_momentum_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # 🧠 MOMENTUM FİLTRESİ (Hata Payını Azaltan Katman)
        rets = df['Close'].pct_change().dropna()
        vol_avg = df['Volume'].tail(10).mean()
        cur_vol = df['Volume'].iloc[-1]
        
        # Eğer hacim ortalamanın %20 üzerindeyse ve fiyat artıyorsa "Eksi" beklentisini iptal et
        hacim_onayi = cur_vol > vol_avg * 1.2
        
        # Tahmin Aralığı (Volatilite tabanlı)
        std_dev = rets.tail(20).std()
        plus = (rets.tail(5).mean() + (std_dev * 2)) * 100
        minus = (rets.tail(5).mean() - (std_dev * 2)) * 100
        
        # KARAR (Momentum ve Hacim Birleşik)
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        if lp > ma20 and hacim_onayi:
            dec = "GÜÇLÜ POZİTİF"; clr = "#00ff88"; note = "Hacimli Alış: Trend yukarı evriliyor."
        elif lp < ma20 and not hacim_onayi:
            dec = "BASKILI / NEGATİF"; clr = "#ff4b4b"; note = "Hacimsiz Düşüş / Zayıflık."
        else:
            dec = "NÖTR / KARARSIZ"; clr = "#ffcc00"; note = "Yön netleşmedi, hacim takibi gerekli."
            
        return {"p": lp, "ch": ch, "plus": plus, "minus": minus, "dec": dec, "clr": clr, "note": note, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00; margin-bottom:0;'>🤵 GÜRKAN AI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:10px; color:#555;'>MOMENTUM ENGINE v166</p>", unsafe_allow_html=True)

# Arama
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"):
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

l, m, r = st.columns([0.8, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_momentum_data(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='exec-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]} ANLIK</p>
                    <p class='price-big'>{res['p']:.2f}</p>
                    <p style='color:{res['clr']}; font-weight:bold; font-size:18px;'>{res['ch']:+.2f}%</p>
                </div>
                <div style='text-align:right;'>
                    <div class='momentum-badge' style='background:{res['clr']}22; color:{res['clr']}; border:1px solid {res['clr']};'>
                        {res['dec']}
                    </div>
                    <div style='margin-top:15px;'>
                        <p class='label-mini'>POTANSİYEL ARALIK</p>
                        <p style='color:#00ff88; font-weight:bold; margin:0;'>+%{res['plus']:.2f}</p>
                        <p style='color:#ff4b4b; font-weight:bold; margin:0;'>-%{abs(res['minus']):.2f}</p>
                    </div>
                </div>
            </div>
            <p style='font-size:12px; color:#8b949e; margin-top:10px; font-style:italic;'>"{res['note']}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for rd in ["AKBNK", "ISCTR", "THYAO", "TUPRS", "EREGL"]:
        if st.button(f"⚡ {rd}", key=f"r_{rd}", use_container_width=True): st.session_state["last_sorgu"] = rd; st.rerun()
