import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Elite", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .login-box { max-width: 400px; margin: 100px auto; padding: 30px; background: #0d1117; border: 2px solid #ffcc00; border-radius: 12px; text-align: center; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; }
    .master-card { background: #0d1117; border: 1px solid #1c2128; border-radius: 12px; padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px; }
    .price-text { font-size: 42px; font-weight: bold; font-family: monospace; color: #fff; }
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; margin-top: 20px; }
    .m-item { background: #111418; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #1c2128; }
    .report-box { background: #111418; border-radius: 8px; padding: 20px; margin-top: 20px; border-left: 4px solid #ffcc00; }
    div.stButton > button { background: #111418 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; width: 100%; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#ffcc00;'>GÜRKAN AI ADMIN</h2>", unsafe_allow_html=True)
    pw = st.text_input("ŞİFRE", type="password")
    if st.button("TERMİNALİ AÇ"):
        if pw == "HEDEF2024!":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("HATALI!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. ANALİZ MOTORU ---
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
        
        target = lp + (atr * 2.2)
        stop = lp - (atr * 1.5)
        
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        if lp > ma20:
            status, yorum = "BOĞA GÖRÜNÜMÜ", f"Fiyat {ma20:.2f} pivotunun üzerinde. Hacim rasyosu ({vol_r:.1f}x) trendi teyit ediyor. {target:.2f} ana hedef."
        else:
            status, yorum = "AYI BASKISI", f"Fiyat {ma20:.2f} pivotunun altında. Satış baskısı hissediliyor. {stop:.2f} desteği önemli."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "yorum": yorum, "status": status}
    except:
        return None

# --- 5. DASHBOARD ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:8px; font-weight:bold;'>GÜRKAN AI : ELITE ANALYST</p>", unsafe_allow_html=True)

# Arama
c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 GİT"): 
        st.session_state["last_sorgu"] = s_inp
        st.rerun()
with c3:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favori Butonları
if st.session_state["favorites"]:
    f_cols = st.columns(len(st.session_state["favorites"]))
    for i, f in enumerate(st.session_state["favorites"]):
        if f_cols[i].button(f):
            st.session_state["last_sorgu"] = f
            st.rerun()

# Veri Ekranı
res = get_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div><span style='color:#8b949e; font-size:12px;'>{st.session_state["last_sorgu"]}</span><br><span class='price-text'>{res['p']:.2f}</span> <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:20px;'>{res['ch']:+.2f}%</span></div>
            <div style='text-align:right;'><span style='color:#ffcc00; font-weight:bold;'>{res['status']}</span></div>
        </div>
        <div class='metric-grid'>
            <div class='m-item'><p style='color:#8b949e; font-size:10px;'>MA20 PİVOT</p><p style='font-size:22px; font-weight:bold;'>{res['ma']:.2f}</p></div>
            <div class='m-item' style='border-top:3px solid #00ff88;'><p style='color:#8b949e; font-size:10px;'>HEDEF</p><p style='font-size:22px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='m-item' style='border-top:3px solid #ff4b4b;'><p style='color:#8b949e; font-size:10px;'>STOP LOSS</p><p style='font-size:22px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        <div class='report-box'>
            <p style='color:#ffcc00; font-size:11px; font-weight:bold; margin-bottom:8px;'>📊 STRATEJİK ARAŞTIRMA RAPORU</p>
            <p style='color:#d1d1d1; font-size:14px;'>"{res['yorum']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("LOGOUT"):
    st.session_state["auth"] = False
    st.rerun()
