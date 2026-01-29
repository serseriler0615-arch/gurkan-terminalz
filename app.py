import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Omniscient", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "ASTOR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. PREMIUM CSS (ULTRA-RESPONSIVE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@500&display=swap');
    
    .stApp { background-color: #030508 !important; color: #e1e1e1 !important; font-family: 'Inter', sans-serif; }
    header { visibility: hidden; }
    
    /* Master Card: Görsel 1'deki Derinlik */
    .master-card {
        background: linear-gradient(165deg, #0d1117 0%, #05070a 100%);
        border: 1px solid #1c2128; border-radius: 20px; padding: 30px;
        border-top: 4px solid #ffcc00; margin-bottom: 25px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
    }
    
    .price-text { font-size: clamp(35px, 6vw, 55px); font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #ffffff; letter-spacing: -2px; }
    .label-mini { color: #6e7681; font-size: 10px; text-transform: uppercase; letter-spacing: 2.5px; font-weight: 700; margin-bottom: 5px; }
    
    /* Radar Grid */
    .radar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 30px; }
    .radar-item { 
        background: rgba(255,255,255,0.02); padding: 20px; border-radius: 12px; 
        border: 1px solid #1c2128; text-align: center; transition: 0.3s;
    }
    .radar-item:hover { border-color: #ffcc0044; background: rgba(255,255,255,0.04); }

    /* Zeka Rapor Kutusu (+) */
    .intel-box { 
        background: rgba(255, 204, 0, 0.03); border-radius: 15px; padding: 25px; margin-top: 30px;
        border: 1px solid rgba(255,204,0,0.1); border-left: 6px solid #ffcc00;
    }
    .report-content { color: #d1d5db; font-size: 15px; line-height: 1.8; font-style: normal; }
    .plus-badge { background: #ffcc00; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-bottom: 10px; display: inline-block; }

    /* Butonlar */
    div.stButton > button { 
        background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important;
        border-radius: 10px; height: 40px; font-weight: 600; font-size: 12px;
    }
    
    @media (max-width: 600px) {
        .price-text { font-size: 38px; }
        .radar-grid { grid-template-columns: 1fr 1fr; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU (OMNISCIENT ENGINE) ---
def get_omniscient_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_avg = df['Volume'].rolling(10).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / vol_avg
        
        # Keskin Seviyeler
        target = lp + (atr * 2.6)
        stop = lp - (atr * 1.6)
        rr_ratio = (target - lp) / (lp - stop)
        
        # --- DERİN ARAŞTIRMACI ZEKA (PLUS) ---
        intelligence = []
        if ch > 0 and vol_r < 0.7:
            status, col = "YORGUN YÜKSELİŞ", "#ff9f1c"
            intelligence.append("Fiyat yükselirken hacmin ortalamanın altında kalması, 'Smart Money'nin bu hareketi desteklemediğini gösteriyor. Fake bir kırılım olabilir.")
        elif lp > ma20 and vol_r > 1.5:
            status, col = "KURUMSAL ALIM", "#00ff88"
            intelligence.append("Yüksek hacimli pivot kırılımı tespit edildi. Trend gücü (Momentum) maksimum seviyede. Pozisyon eklemek için uygun bir zemin.")
        elif lp < ma20:
            status, col = "AYI BASKISI", "#ff4b4b"
            intelligence.append(f"Fiyat {ma20:.2f} altındaki dağıtım evresinde. Satıcılar kontrolü elinde tutuyor. Stop seviyesi olan {stop:.2f} mutlaka takip edilmeli.")
        else:
            status, col = "DENGELENME", "#00d4ff"
            intelligence.append("Hissede yön arayışı sürüyor. Pivot noktası etrafında kümelenme var, patlama yakındır.")

        if rr_ratio > 1.5: intelligence.append(f"Risk/Ödül oranı ({rr_ratio:.2f}) pozitif. Teknik olarak iştah kabartıcı.")
        
        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "intel": intelligence, "sig": status, "col": col, "vol": vol_r}
    except: return None

# --- 4. ANA EKRAN ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#ffcc00; letter-spacing:5px;'>GÜRKAN AI</h1><p style='color:#6e7681;'>OMNISCIENT v205</p></div>", unsafe_allow_html=True)
        pw = st.text_input("GİRİŞ", type="password", label_visibility="collapsed")
        if st.button("SİSTEME BAĞLAN"):
            if pw == "HEDEF2024!": st.session_state["auth"] = True; st.rerun()
    st.stop()

st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:10px; font-size:12px; font-weight:bold;'>STRATEJİK İSTİHBARAT TERMİNALİ</p>", unsafe_allow_html=True)

# Arama Barı
c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c3:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favori Barı
f_cols = st.columns(len(st.session_state["favorites"]) if st.session_state["favorites"] else 1)
for i, f in enumerate(st.session_state["favorites"]):
    if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Dashboard
res = get_omniscient_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;'>
            <div>
                <p class='label-mini'>{st.session_state["last_sorgu"]} ANALİZİ</p>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:26px; font-weight:700; margin-left:10px;'>{res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['col']}; font-weight:bold; font-size:20px;'>{res['sig']}</span><br>
                <span class='label-mini'>HACİM GÜCÜ: {res['vol']:.1f}x</span>
            </div>
        </div>
        
        <div class='radar-grid'>
            <div class='radar-item'><p class='label-mini'>PİVOT (20G)</p><p style='font-size:24px; font-weight:bold;'>{res['ma']:.2f}</p></div>
            <div class='radar-item'><p class='label-mini' style='color:#00ff88;'>TEKNİK HEDEF</p><p style='font-size:24px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item'><p class='label-mini' style='color:#ff4b4b;'>STOP LOSS</p><p style='font-size:24px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        
        <div class='intel-box'>
            <span class='plus-badge'>GÜRKAN AI RESEARCH (+)</span>
            <p class='report-content'>{' '.join(res['intel'])}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(color='#484f58')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("OTURUMU SONLANDIR"):
    st.session_state["auth"] = False
    st.rerun()
