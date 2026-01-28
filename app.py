import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Admin", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ADMIN GİRİŞ KONTROLÜ ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 3. CSS (TELEFON UYUMLU & ADMIN TEMASI) ---
st.markdown("""
<style>
    /* Global Reset */
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Mobil İçin Esnek Yapı */
    @media (max-width: 600px) {
        .main-container { padding: 10px !important; }
        .price-main { font-size: 24px !important; }
        .stPlotlyChart { height: 300px !important; }
    }

    /* Admin Giriş Paneli */
    .admin-box { background: #0d1117; border: 1px solid #ffcc00; border-radius: 8px; padding: 20px; text-align: center; max-width: 400px; margin: 100px auto; }
    
    /* Arama Motoru Küçültme */
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; font-size: 14px !important; 
        height: 35px !important; border-radius: 4px !important;
    }

    /* Şık Kartlar */
    .admin-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 4px;
        padding: 12px; border-left: 3px solid #ffcc00; margin-bottom: 8px;
    }
    
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; font-weight: bold; }
    
    /* Butonlar */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
        font-size: 10px !important; height: 28px !important; width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. ADMIN LOGIN ---
if not st.session_state["authenticated"]:
    with st.container():
        st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#ffcc00;'>🤵 ADMIN GİRİŞİ</h3>", unsafe_allow_html=True)
        pw = st.text_input("Sistem Şifresi", type="password")
        if st.button("SİSTEMİ AÇ"):
            if pw == "gurkan123": # Buradan şifreni değiştirebilirsin
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Hatalı Kod.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. ANALİZ MOTORU ---
def get_admin_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="3mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        return {"p": lp, "ch": ch, "df": df, "target": lp+(atr*2), "stop": lp-(atr*1.2)}
    except: return None

# --- 6. ANA DASHBOARD (TELEFON & WEB) ---
st.markdown("<p style='text-align:center; color:#ffcc00; font-size:12px; letter-spacing:3px;'>GÜRKAN AI : ENCRYPTED TERMINAL</p>", unsafe_allow_html=True)

# Kontroller
c_search, c_actions = st.columns([3, 1])
with c_search:
    s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c_actions:
    if st.button("SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()

# Favoriler (Mobil Uyumlu Scroll)
fav_list = st.columns(len(st.session_state["favorites"]) + 1)
for i, f in enumerate(st.session_state["favorites"]):
    if fav_list[i].button(f"{f}"): st.session_state["last_sorgu"] = f; st.rerun()

# Ana İçerik
res = get_admin_data(st.session_state["last_sorgu"])
if res:
    # Mobilde alt alta, Webde yan yana
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.markdown(f"""
        <div class='admin-card'>
            <span class='label-mini'>{st.session_state["last_sorgu"]} VERİSİ</span><br>
            <span style='font-size:28px; font-weight:bold;'>{res['p']:.2f}</span>
            <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:14px;'> {res['ch']:+.2f}%</span>
        </div>
        <div class='admin-card' style='border-left-color:#00ff88'>
            <span class='label-mini'>TEKNİK HEDEF</span><br>
            <span style='font-size:18px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</span>
        </div>
        <div class='admin-card' style='border-left-color:#ff4b4b'>
            <span class='label-mini'>STOP LOSS</span><br>
            <span style='font-size:18px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⭐ FAVORİ EKLE/SİL"):
            if st.session_state["last_sorgu"] in st.session_state["favorites"]:
                st.session_state["favorites"].remove(st.session_state["last_sorgu"])
            else:
                st.session_state["favorites"].append(st.session_state["last_sorgu"])
            st.rerun()

    with col2:
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d', size=10)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Çıkış
if st.sidebar.button("OTURUMU KAPAT"):
    st.session_state["authenticated"] = False
    st.rerun()
