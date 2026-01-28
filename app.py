import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Admin", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GÜVENLİK VE HAFIZA ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 3. CSS (SİYAH ADMIN & MOBİL KOKPİT) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Login Paneli */
    .login-card { 
        background: #0d1117; border: 2px solid #ffcc00; border-radius: 12px; 
        padding: 30px; max-width: 350px; margin: 80px auto; text-align: center;
        box-shadow: 0 0 20px rgba(255, 204, 0, 0.2);
    }
    
    /* Mobil Input ve Kartlar */
    .stTextInput>div>div>input { 
        background: #111418 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; text-align: center; font-size: 16px; 
    }
    .metric-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 8px;
        padding: 12px; margin-bottom: 8px; border-left: 4px solid #ffcc00;
    }
    .price-val { font-size: 32px; font-weight: bold; font-family: monospace; }
    
    /* Butonlar */
    div.stButton > button {
        background: #111418 !important; color: #ffcc00 !important;
        border: 1px solid #30363d !important; width: 100% !important; border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. ADMIN GİRİŞİ (HEDEF2024!) ---
if not st.session_state["auth"]:
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#ffcc00; letter-spacing:3px;'>🤵 ADMIN LOGIN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:#4b525d;'>GÜRKAN AI TERMINAL v193</p>", unsafe_allow_html=True)
    
    pw_input = st.text_input("SİSTEM ŞİFRESİ", type="password")
    if st.button("SİSTEME GİRİŞ YAP"):
        if pw_input == "HEDEF2024!":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("ŞİFRE HATALI!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Şifre doğru değilse geri kalan kodu çalıştırma

# --- 5. ANALİZ MOTORU ---
def get_pro_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # Akıllı Sinyal
        signal = "AL" if ch > 0 and vol_r > 1.1 else "SAT" if ch < -1 else "BEKLE"
        
        return {"p": lp, "ch": ch, "df": df, "target": lp+(atr*2.2), "stop": lp-(atr*1.2), "sig": signal, "vr": vol_r}
    except: return None

# --- 6. TERMİNAL EKRANI (ŞİFRE SONRASI) ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:5px; font-size:12px;'>🤵 GÜRKAN AI SECURE TERMINAL</p>", unsafe_allow_html=True)

# Arama ve Favori Ekleme (Telefonda yan yana durur)
c_search, c_fav = st.columns([3, 1])
with c_search:
    s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c_fav:
    if st.button("🔍 SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()

# Hızlı Favori Butonları
fav_cols = st.columns(len(st.session_state["favorites"]) + 1)
for i, f in enumerate(st.session_state["favorites"]):
    if fav_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Ana İçerik
res = get_pro_analysis(st.session_state["last_sorgu"])
if res:
    m_col, g_col = st.columns([1, 2.5])
    
    with m_col:
        st.markdown(f"""
        <div class='metric-card'>
            <p class='label-mini'>{st.session_state["last_sorgu"]} FİYAT</p>
            <p class='price-val'>{res['p']:.2f} <span style='font-size:14px; color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}'>{res['ch']:+.2f}%</span></p>
        </div>
        <div class='metric-card' style='border-left-color:#00ff88'>
            <p class='label-mini'>HEDEF</p><p style='font-size:20px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p>
        </div>
        <div class='metric-card' style='border-left-color:#ff4b4b'>
            <p class='label-mini'>STOP</p><p style='font-size:20px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p>
        </div>
        <div class='metric-card' style='border-left-color:#00d4ff'>
            <p class='label-mini'>SİNYAL / HACİM</p><p style='font-size:18px; font-weight:bold;'>{res['sig']} / {res['vr']:.1f}x</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⭐ LİSTEYE EKLE / SİL"):
            if st.session_state["last_sorgu"] in st.session_state["favorites"]:
                st.session_state["favorites"].remove(st.session_state["last_sorgu"])
            else:
                st.session_state["favorites"].append(st.session_state["last_sorgu"])
            st.rerun()

    with g_col:
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d', size=10)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Çıkış Butonu
if st.sidebar.button("ADMIN ÇIKIŞI"):
    st.session_state["auth"] = False
    st.rerun()
