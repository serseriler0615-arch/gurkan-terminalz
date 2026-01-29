import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI : Executive", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (GÖRSEL 1 & 2 DERİNLİĞİ) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Login Paneli */
    .login-box { max-width: 400px; margin: 100px auto; padding: 35px; background: #0d1117; border: 2px solid #ffcc00; border-radius: 15px; text-align: center; box-shadow: 0 0 30px rgba(255, 204, 0, 0.1); }
    
    /* Arama Motoru */
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; border-radius: 8px !important; font-size: 16px !important; }

    /* Ana Terminal Kartı (Görsel 1 Ruhu) */
    .master-card {
        background: linear-gradient(145deg, #0d1117, #080a0d);
        border: 1px solid #1c2128; border-radius: 12px;
        padding: 30px; border-top: 5px solid #ffcc00; margin-bottom: 20px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    }
    
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
    .price-text { font-size: 48px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; line-height: 1; }
    
    /* Metrik Grid (Görsel 2 Ruhu) */
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px; margin-top: 25px; }
    .m-item { background: #111418; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #1c2128; border-bottom: 3px solid #30363d; }
    
    /* Rapor Kutusu */
    .report-box { 
        background: rgba(255, 204, 0, 0.03); border-radius: 8px; padding: 20px; margin-top: 25px;
        border-left: 4px solid #ffcc00; border-bottom: 1px solid #1c2128;
    }
    .report-content { color: #d1d1d1; font-size: 14.5px; line-height: 1.6; font-style: italic; }

    /* Favori Butonları */
    div.stButton > button { background: #111418 !important; color: #8b949e !important; border: 1px solid #30363d !important; border-radius: 6px !important; font-size: 12px !important; height: 32px !important; }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#ffcc00; letter-spacing:5px;'>🤵 GÜRKAN AI</h2><p style='color:#4b525d; font-size:10px;'>EXECUTIVE TERMINAL v200</p>", unsafe_allow_html=True)
    pw = st.text_input("ŞİFRE", type="password")
    if st.button("SİSTEME GİRİŞ"):
        if pw == "HEDEF2024!":
            st.session_state["auth"] = True
            st.rerun()
        else: st.error("HATALI!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. ARAŞTIRMACI ANALİZ MOTORU ---
def get_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        target = lp + (atr * 2.3)
        stop = lp - (atr * 1.4)
        
        if lp > ma20:
            status, color = "POZİTİF (BOĞA)", "#00ff88"
            yorum = f"Fiyat {ma20:.2f} pivot bölgesinin üzerinde güç topluyor. Hacim rasyosu ({vol_r:.1f}x) trenddeki kararlılığı gösteriyor. {target:.2f} direnci ana hedef olarak radarda kalmaya devam ediyor."
        else:
            status, color = "NEGATİF (AYI)", "#ff4b4b"
            yorum = f"Fiyat {ma20:.2f} desteğinin altına sarkarak kısa vadeli momentumu kaybetti. {stop:.2f} seviyesi kritik tampon bölge. Hacimli alımlar gelmedikçe baskı sürebilir."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "yorum": yorum, "status": status, "status_color": color}
    except: return None

# --- 5. DASHBOARD ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:10px; font-size:18px; margin-bottom:20px;'>GÜRKAN AI : ELITE DASHBOARD</h3>", unsafe_allow_html=True)

# Kontrol Barı
c_inp, c_search, c_fav = st.columns([3, 1, 1])
with c_inp: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c_search: 
    if st.button("🔍 SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c_fav:
    txt = "❌ ÇIKAR" if s_inp in st.session_state["favorites"] else "⭐ FAVORİ"
    if st.button(txt):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favoriler
if st.session_state["favorites"]:
    f_cols = st.columns(len(st.session_state["favorites"]))
    for i, f in enumerate(st.session_state["favorites"]):
        if f_cols[i].button(f"• {f}"): st.session_state["last_sorgu"] = f; st.rerun()

# Ana İçerik
res = get_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
            <div>
                <span class='label-mini'>{st.session_state["last_sorgu"]} TERMİNALİ</span><br>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:24px; font-weight:bold;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['status_color']}; font-weight:bold; font-size:18px;'>{res['status']}</span><br>
                <span class='label-mini'>ANLIK SİNYAL DURUMU</span>
            </div>
        </div>
        
        <div class='metric-grid'>
            <div class='m-item'><p class='label-mini'>MA20 PİVOT</p><p style='font-size:24px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='m-item' style='border-bottom-color:#00ff88;'><p class='label-mini'>TEKNİK HEDEF</p><p style='font-size:24px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='m-item' style='border-bottom-color:#ff4b4b;'><p class='label-mini'>ZARAR KES (STOP)</p><p style='font-size:24px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        
        <div class='report-box'>
            <p class='label-mini' style='color:#ffcc00; margin-bottom:10px;'>📊 STRATEJİK ARAŞTIRMA VE YORUM</p>
            <p class='report-content'>"{res['yorum']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("OTURUMU KAPAT"):
    st.session_state["auth"] = False
    st.rerun()
