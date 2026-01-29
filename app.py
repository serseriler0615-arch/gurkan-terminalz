import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI : Supreme", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (MÜKEMMEL DENGELENMİŞ ARAYÜZ) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; border-radius: 8px !important; }

    .master-card {
        background: linear-gradient(145deg, #0d1117, #080a0d);
        border: 1px solid #1c2128; border-radius: 12px;
        padding: 30px; border-top: 5px solid #ffcc00; margin-bottom: 20px;
    }
    .price-text { font-size: 48px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; line-height: 1; }
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px; margin-top: 25px; }
    .m-item { background: #111418; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #1c2128; border-bottom: 3px solid #30363d; }
    .report-box { background: rgba(255, 204, 0, 0.02); border-radius: 8px; padding: 20px; margin-top: 25px; border-left: 4px solid #ffcc00; border-right: 1px solid #1c2128; }
    .report-content { color: #d1d1d1; font-size: 14.5px; line-height: 1.6; }
    div.stButton > button { background: #111418 !important; color: #8b949e !important; border: 1px solid #30363d !important; width: 100%; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:100px;'><h2 style='color:#ffcc00;'>🤵 ADMIN LOGIN</h2>", unsafe_allow_html=True)
        pw = st.text_input("ŞİFRE", type="password", label_visibility="collapsed")
        if st.button("SİSTEMİ AÇ"):
            if pw == "HEDEF2024!":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("HATALI!")
    st.stop()

# --- 4. AKILLI ANALİZ MOTORU ---
def get_supreme_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # --- MANTIKSAL DÜZELTME BÖLGESİ ---
        target = lp + (atr * 2.2)
        stop = lp - (atr * 1.3) # Stop her zaman fiyattan düşüktür.
        
        # Hacim ve Trend Yorumu
        hacim_notu = "güçlü bir katılımla" if vol_r > 1.2 else "zayıf bir hacimle"
        trend_notu = f"{ma20:.2f} pivotunun üzerinde güven tazeledi" if lp > ma20 else f"{ma20:.2f} altında baskı hissediyor"
        
        if lp > ma20 and vol_r > 1: status = "GÜÇLÜ BOĞA"
        elif lp > ma20: status = "TEMKİNLİ POZİTİF"
        else: status = "AYI BASKISI"
        
        yorum = f"Fiyat şu an {trend_notu}. İşlemler {hacim_notu} ilerliyor. Teknik olarak {target:.2f} seviyesi hedef konumundayken, {stop:.2f} seviyesi risk yönetimi için ana destek hattıdır."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "yorum": yorum, "status": status, "vol": vol_r}
    except: return None

# --- 5. DASHBOARD ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:10px; font-weight:bold;'>GÜRKAN AI : SUPREME TERMINAL</p>", unsafe_allow_html=True)

# Arama & Kontrol
c_inp, c_search, c_fav = st.columns([3, 1, 1])
with c_inp: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c_search: 
    if st.button("🔍 SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c_fav:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favoriler
if st.session_state["favorites"]:
    f_cols = st.columns(len(st.session_state["favorites"]))
    for i, f in enumerate(st.session_state["favorites"]):
        if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Analiz Panel
res = get_supreme_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <span style='color:#8b949e; font-size:11px;'>{st.session_state["last_sorgu"]} ANALİZİ</span><br>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:22px; font-weight:bold;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:#ffcc00; font-weight:bold; font-size:18px;'>{res['status']}</span><br>
                <span style='color:#8b949e; font-size:10px;'>HACİM RASYOSU: {res['vol']:.1f}x</span>
            </div>
        </div>
        <div class='metric-grid'>
            <div class='m-item'><p class='label-mini'>MA20 PİVOT</p><p style='font-size:22px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='m-item' style='border-bottom-color:#00ff88;'><p class='label-mini'>HEDEF</p><p style='font-size:22px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='m-item' style='border-bottom-color:#ff4b4b;'><p class='label-mini'>STOP (ZARAR KES)</p><p style='font-size:22px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        <div class='report-box'>
            <p style='color:#ffcc00; font-size:11px; font-weight:bold; margin-bottom:8px;'>📊 STRATEJİK ANALİST YORUMU</p>
            <p class='report-content'>"{res['yorum']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("OTURUMU KAPAT"):
    st.session_state["auth"] = False
    st.rerun()
