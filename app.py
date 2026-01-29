import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI : Quantum", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. ELITE QUANTUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #020408 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    .master-card {
        background: linear-gradient(145deg, #0d1117 0%, #05070a 100%);
        border: 1px solid #1c2128; border-radius: 20px; padding: 30px;
        border-top: 4px solid #ffcc00; margin-bottom: 25px;
        box-shadow: 0 40px 80px rgba(0,0,0,0.9);
    }
    .price-text { font-size: clamp(38px, 6vw, 58px); font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #ffffff; }
    .label-mini { color: #6e7681; font-size: 10px; text-transform: uppercase; letter-spacing: 3px; font-weight: 700; }
    
    .radar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px; margin-top: 25px; }
    .radar-item { background: rgba(255,255,255,0.02); padding: 22px; border-radius: 15px; border: 1px solid #1c2128; text-align: center; }
    
    .intel-box { 
        background: rgba(255, 204, 0, 0.03); border-radius: 15px; padding: 25px; margin-top: 25px;
        border-left: 6px solid #ffcc00; border-right: 1px solid #1c2128;
    }
    .plus-badge { background: #ffcc00; color: #000; padding: 3px 10px; border-radius: 5px; font-size: 11px; font-weight: 800; margin-bottom: 12px; display: inline-block; }
    .report-content { color: #cfd6e0; font-size: 15.5px; line-height: 1.8; }

    div.stButton > button { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 10px; font-weight: 600; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; }

    @media (max-width: 600px) { .radar-grid { grid-template-columns: 1fr 1fr; } }
</style>
""", unsafe_allow_html=True)

# --- 3. QUANTUM ANALİZ MOTORU ---
def get_quantum_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # --- KESKİN HESAPLAMA: SAFE-ZONE ---
        target = lp + (atr * 2.8)
        stop = lp - (atr * 1.9) # Stop mesafesi daha profesyonel bir marja çekildi.
        rr_ratio = (target - lp) / (lp - stop)
        
        # --- ZEKA KATMANI ---
        intel = []
        if vol_r < 0.6:
            sig, col = "LİKİTİDE EKSİKLİĞİ", "#6e7681"
            intel.append(f"Piyasada {symbol} için ilgi kaybı (Volume Decay) mevcut. Hacim rasyosu ({vol_r:.1f}x) teknik formasyonları geçersiz kılabilir. Patlama beklemek yerine, kurumsal giriş onayı aranmalı.")
        elif lp > ma20 and vol_r > 1.4:
            sig, col = "HACİMLİ TREND", "#00ff88"
            intel.append(f"Sinyal Onaylandı: {ma20:.2f} pivotu üzerinde hacimli bir kopuş mevcut. Alıcı iştahı (Buy Pressure) yüksek. {target:.2f} seviyesine kadar ivme sürebilir.")
        elif lp < ma20:
            sig, col = "AYI DOMİNASYONU", "#ff4b4b"
            intel.append(f"Pivot altı kapanışlar zayıflığı teyit ediyor. {ma20:.2f} direnci aşılamadıkça risk masada. {stop:.2f} bölgesi ana savunma hattıdır.")
        else:
            sig, col = "DARALAN VOLATİLİTE", "#ffcc00"
            intel.append(f"Fiyat {ma20:.2f} pivotu etrafında yatayda (Squeeze). Enerji birikimi mevcut; ancak hacim girişi ({vol_r:.1f}x) henüz yön teyidi vermedi.")

        if rr_ratio > 1.4: intel.append(f"Risk/Ödül Oranı ({rr_ratio:.2f}) 'Yüksek Verimli' sınıfında.")

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "intel": " ".join(intel), "sig": sig, "col": col, "vol": vol_r}
    except: return None

# --- 4. DASHBOARD ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#ffcc00;'>🤵 GÜRKAN AI</h1></div>", unsafe_allow_html=True)
        pw = st.text_input("ŞİFRE", type="password", label_visibility="collapsed")
        if st.button("TERMİNALİ BAŞLAT"):
            if pw == "HEDEF2024!": st.session_state["auth"] = True; st.rerun()
    st.stop()

# Üst Bar
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:10px; font-weight:bold; font-size:12px;'>QUANTUM RESEARCH TERMINAL</p>", unsafe_allow_html=True)

# Kontrol
c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 TARAMA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c3:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favori Barı
f_cols = st.columns(len(st.session_state["favorites"]) if st.session_state["favorites"] else 1)
for i, f in enumerate(st.session_state["favorites"]):
    if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Analiz Raporu
res = get_quantum_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;'>
            <div>
                <p class='label-mini'>{st.session_state["last_sorgu"]} // QUANTUM CORE</p>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:26px; font-weight:700;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['col']}; font-weight:bold; font-size:20px;'>{res['sig']}</span><br>
                <span class='label-mini'>INTENSITY: {res['vol']:.1f}x</span>
            </div>
        </div>
        
        <div class='radar-grid'>
            <div class='radar-item'><p class='label-mini'>PİVOT (MA20)</p><p style='font-size:24px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 4px solid #00ff88;'><p class='label-mini'>HEDEF (PRO)</p><p style='font-size:24px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 4px solid #ff4b4b;'><p class='label-mini'>STOP (SAFE)</p><p style='font-size:24px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        
        <div class='intel-box'>
            <span class='plus-badge'>GÜRKAN AI STRATEGY (+)</span>
            <p class='report-content'>"{res['intel']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(color='#484f58')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("OTURUMU KAPAT"):
    st.session_state["auth"] = False
    st.rerun()
