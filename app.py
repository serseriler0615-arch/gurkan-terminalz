import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Elite", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (ESTETİK & MOBİL UYUM) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .login-box { max-width: 400px; margin: 100px auto; padding: 30px; background: #0d1117; border: 2px solid #ffcc00; border-radius: 12px; text-align: center; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; font-size: 16px !important; }

    .master-card {
        background: linear-gradient(145deg, #0d1117, #080a0d);
        border: 1px solid #1c2128; border-radius: 12px;
        padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px;
    }
    .price-text { font-size: 42px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; line-height: 1; }
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; margin-top: 20px; }
    .m-item { background: #111418; padding: 18px; border-radius: 10px; text-align: center; border: 1px solid #1c2128; }
    .report-box { background: #111418; border-radius: 8px; padding: 20px; margin-top: 20px; border-left: 4px solid #ffcc00; }
    div.stButton > button { background: #111418 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#ffcc00;'>GÜRKAN AI ADMIN</h2>", unsafe_allow_html=True)
    pw = st.text_input("ŞİFRE", type="password")
    if st.button("SİSTEMİ BAŞLAT"):
        if pw == "HEDEF2024!":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("HATALI ŞİFRE!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. ANALİZ MOTORU ---
def get_elite_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        pc = float(df['Close'].iloc[-2])
        ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        # Matematiksel Doğrulama
        target = lp + (atr * 2.2)
        stop = lp - (atr * 1.5)
        
        # Araştırmacı Yorum Zekası
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        if lp > ma20:
            status = "BOĞA GÖRÜNÜMÜ"
            yorum = f"Fiyat {ma20:.2f} pivotunun üzerinde. Hacim rasyosu ({vol_r:.1f}x) trendin gücünü teyit ediyor. {target:.2f} seviyesi ana hedef konumunda."
        else:
            status = "AYI BASKISI"
            yorum = f"Fiyat {ma20:.2f} pivotunun altında. Satış baskısı hissediliyor. {stop:.2f} desteği kırılırsa temkinli olunmalı."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "yorum": yorum, "status": status}
    except:
        return None

# --- 5. DASHBOARD ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:8px; font-weight:bold;'>GÜRKAN AI : ELITE ANALYST</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 SORGULA"): 
        st.session_state["last_sorgu"] = s_inp
        st.rerun()
with c3:
    txt = "❌ ÇIKAR" if s_inp in st.session_state["favorites"] else "⭐ EKLE"
    if st.button(txt):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favoriler
f_cols = st.columns(len(st.session_state
