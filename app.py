import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI : Secure", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "HUNER", "SMART"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (MÜKEMMEL MOBİL & WEB DENGESİ) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Login Ekranı */
    .login-container { 
        max-width: 400px; margin: 100px auto; padding: 30px; 
        background: #0d1117; border: 2px solid #ffcc00; border-radius: 15px; text-align: center;
    }
    
    /* Arama Motoru ve Inputlar */
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; text-align: center; font-size: 16px !important;
        border-radius: 8px !important;
    }
    
    /* Ana Kart (Görsel 1 ve 2'deki gibi) */
    .master-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 12px;
        padding: 20px; border-top: 4px solid #00d4ff; margin-bottom: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: bold; }
    .price-text { font-size: 38px; font-weight: bold; font-family: monospace; color: #fff; line-height: 1; }
    
    /* Butonlar */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 6px !important;
        font-size: 12px !important; width: 100% !important; transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    
    /* Mobil Düzenleme */
    @media (max-width: 600px) {
        .price-text { font-size: 28px !important; }
        .master-card { padding: 15px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#ffcc00;'>🤵 ADMIN PANEL</h2>", unsafe_allow_html=True)
    pw = st.text_input("SİSTEM ŞİFRESİ", type="password")
    if st.button("TERMİNALİ AKTİF ET"):
        if pw == "HEDEF2024!":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("HATALI ŞİFRE!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. ZEKA VE ANALİZ ---
def get_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        # Yarın İçin Zeka
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        tahmin = "YÜKSELİŞ BEKLENİYOR" if ch > 0 and vol_ratio > 1.2 else "YATAY/İZLE"
        
        return {"p": lp, "ch": ch, "df": df, "ma20": ma20, "target": lp+(atr*2.2), "stop": lp-(atr*1.3), "tahmin": tahmin}
    except: return None

# --- 5. DASHBOARD ---
st.markdown(f"<h3 style='text-align:center; color:#ffcc00; letter-spacing:6px;'>🤵 GÜRKAN AI : SECURE TERMINAL</h3>", unsafe_allow_html=True)

# Arama ve Aksiyon Barı
c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c3:
    label = "ÇIKAR" if s_inp in st.session_state["favorites"] else "EKLE"
    if st.button(label):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favori Listesi (Mobil Uyumlu)
fav_cols = st.columns(len(st.session_state["favorites"]) if len(st.session_state["favorites"]) > 0 else 1)
for i, f in enumerate(st.session_state["favorites"]):
    if fav_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Ana Panel
res = get_analysis(st.session_state["last_sorgu"])
if res:
    # Mobilde alt alta, Web'de yan yana (Görsel 3'teki hata burada düzeltildi)
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
            <div>
                <span class='label-mini'>{st.session_state["last_sorgu"]} TERMİNAL VERİSİ</span><br>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:18px; font-weight:bold;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:#00d4ff; font-weight:bold;'>POZİSYONU KORU</span><br>
                <span class='label-mini'>YARIN: {res['tahmin']}</span>
            </div>
        </div>
        <div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap:15px; margin-top:20px;'>
            <div style='background:#111418; padding:15px; border-radius:8px; text-align:center;'>
                <p class='label-mini'>MA20 PİVOT</p><p style='font-size:18px; font-weight:bold; color:#8b949e;'>{res['ma20']:.2f}</p>
            </div>
            <div style='background:#111418; padding:15px; border-radius:8px; text-align:center; border: 1px solid #00ff8844;'>
                <p class='label-mini'>TEKNİK HEDEF</p><p style='font-size:18px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p>
            </div>
            <div style='background:#111418; padding:15px; border-radius:8px; text-align:center; border: 1px solid #ff4b4b44;'>
                <p class='label-mini'>ZARAR KES</p><p style='font-size:18px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Grafik (Görsel 1'deki profesyonellik)
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                      xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Çıkış
if st.sidebar.button("OTURUMU KAPAT"):
    st.session_state["auth"] = False
    st.rerun()
