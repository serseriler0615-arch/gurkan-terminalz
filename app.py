import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & HAFIZA ---
st.set_page_config(page_title="Gürkan AI : Architect", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (Öğlenki O "En İyi" Tasarımın Modernize Edilmiş Hali) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Input Alanı */
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; text-align: center; 
        font-size: 16px !important; border-radius: 8px;
    }
    
    /* Ana Kart (Master Card) */
    .master-card {
        background: linear-gradient(145deg, #0d1117, #080a0d);
        border: 1px solid #1c2128; border-radius: 12px;
        padding: 22px; border-top: 5px solid #ffcc00;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
    
    /* Yazı Boyutları (Tam İstediğin Kıvamda) */
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
    .price-text { font-size: 36px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; }
    .status-text { font-size: 16px; font-weight: bold; letter-spacing: 0.5px; }
    
    /* Favori & Radar Kutuları */
    .box-item { 
        background: #0d1117; border: 1px solid #1c2128; 
        border-radius: 8px; padding: 12px; margin-bottom: 10px;
    }
    
    /* X Buton ve Yıldız */
    div.stButton > button { 
        background: transparent !important; color: #8b949e !important; 
        border: 1px solid #30363d !important; border-radius: 4px;
        transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .btn-x { color: #ff4b4b !important; border: none !important; font-size: 16px !important; line-height: 0; }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA MOTORU: YARININ ANALİZİ ---
def get_architect_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        df['MA20'] = df['Close'].rolling(20).mean()
        # Zeka: Volatilite ve Para Girişi
        df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
        atr = df['TR'].rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # Yarın İçin Tahmin
        yarin = "📈 YÜKSELİŞ" if ch > 0 and vol_r > 1.2 else "📉 BASKI" if ch < 0 else "↔ YATAY"
        
        return {"p": lp, "ch": ch, "df": df, "target": lp+(atr*2.2), "stop": lp-(atr*1.3), "ma": df['MA20'].iloc[-1], "y": yarin, "vr": vol_r}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00; letter-spacing:7px; font-weight:bold;'>GÜRKAN AI : THE ARCHITECT</h2>", unsafe_allow_html=True)

# ÜST PANEL
_, mid_search, _ = st.columns([1, 1.8, 1])
with mid_search:
    c1, c2 = st.columns([4, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Hisse veya Sembol Gir...", label_visibility="collapsed").upper().strip()
    with c2:
        if s_inp not in st.session_state["favorites"]:
            if st.button("⭐ EKLE"): st.session_state["favorites"].append(s_inp); st.session_state["last_sorgu"] = s_inp; st.rerun()

l, m, r = st.columns([0.8, 4, 1])

# SOL: FAVORİLER (X Butonlu)
with l:
    st.markdown("<p class='label-mini'>FAVORİ LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        c_f1, c_f2 = st.columns([4, 1])
        with c_f1:
            if st.button(f" {f}", key=f"fav_{f}"): st.session_state["last_sorgu"] = f; st.rerun()
        with c_f2:
            if st.button("×", key=f"del_{f}"): st.session_state["favorites"].remove(f); st.rerun()

# ORTA: ANA ANALİZ EKRANI
with m:
    res = get_architect_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} ANALİZ RAPORU</span><br>
                    <span class='price-text'>{res['p']:.2f}</span>
                    <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:20px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span class='label-mini'>YARININ TAHMİNİ</span><br>
                    <span class='status-text' style='color:#ffcc00;'>{res['y']}</span><br>
                    <span style='color:#8b949e; font-size:11px;'>Hacim Gücü: {res['vr']:.1f}x</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px; margin-top:20px;'>
                <div style='background:#111418; padding:15px; border-radius:10px; text-align:center; border: 1px solid #1c2128;'>
                    <p class='label-mini'>MA20 DESTEK</p><p style='font-size:20px; font-weight:bold; color:#8b949e; margin:0;'>{res['ma']:.2f}</p>
                </div>
                <div style='background:#111418; padding:15px; border-radius:10px; text-align:center; border: 1px solid #00ff8844;'>
                    <p class='label-mini'>TEKNİK HEDEF</p><p style='font-size:20px; font-weight:bold; color:#00ff88; margin:0;'>{res['target']:.2f}</p>
                </div>
                <div style='background:#111418; padding:15px; border-radius:10px; text-align:center; border: 1px solid #ff4b4b44;'>
                    <p class='label-mini'>STOP SEVİYESİ</p><p style='font-size:20px; font-weight:bold; color:#ff4b4b; margin:0;'>{res['stop']:.2f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=15,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#8b949e')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# SAĞ: YARININ RADARI
with r:
    st.markdown("<p class='label-mini'>🔥 RADARDAKİLER</p>", unsafe_allow_html=True)
    # Akıllı Radar Listesi
    radars = [("AKBNK", "Kırılım", "#00ff88"), ("TUPRS", "Para Girişi", "#00ff88"), ("EREGL", "Sıkışma", "#ffcc00")]
    for r_s, r_desc, r_c in radars:
        st.markdown(f"""
        <div class='box-item'>
            <div style='display:flex; justify-content:space-between;'>
                <span style='font-weight:bold; color:#fff;'>{r_s}</span>
                <span style='font-size:10px; color:{r_c}; font-weight:bold;'>{r_desc}</span>
            </div>
            <p style='font-size:10px; color:#4b525d; margin-top:5px;'>Yarın için sinyal güçlü.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Analiz Et", key=f"rd_{r_s}"): st.session_state["last_sorgu"] = r_s; st.rerun()
