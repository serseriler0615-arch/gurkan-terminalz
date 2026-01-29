import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI : Absolute Zero", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. ABSOLUTE ZERO CSS (KESKİN & PROFESYONEL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    .master-card {
        background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 35px;
        border-top: 6px solid #ffcc00; margin-bottom: 25px; box-shadow: 0 50px 100px rgba(0,0,0,0.5);
    }
    .price-text { font-size: 60px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #ffffff; letter-spacing: -2px; }
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; }
    
    /* Radar Grid: Artık daha ferah */
    .radar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }
    .radar-item { background: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    
    /* Araştırmacı Rapor Kutusu */
    .intel-box { 
        background: rgba(255, 204, 0, 0.03); border-radius: 15px; padding: 25px; margin-top: 30px;
        border-left: 8px solid #ffcc00; border: 1px solid #30363d; border-left: 8px solid #ffcc00;
    }
    .plus-badge { background: #ffcc00; color: #000; padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: 900; margin-bottom: 12px; display: inline-block; }
    .report-content { color: #d1d5db; font-size: 16px; line-height: 1.8; }

    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 10px; height: 45px; font-weight: 700; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. MEKANİK ANALİZ MOTORU (SIFIR HATA) ---
def get_absolute_zero_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # --- MEKANİK HESAPLAMA ---
        target = lp + (atr * 3.0) # Hedef marjı genişletildi
        
        # STOP: Pivotun %5 altı veya ATR*2.5 marjından en uzağı (Güvenlik Odaklı)
        safe_stop = ma20 * 0.95
        atr_stop = lp - (atr * 2.5)
        stop = min(safe_stop, atr_stop)
        
        # --- KESKİN ZEKA MOTORU ---
        intel = []
        if vol_r < 0.8:
            sig, col = "HACİM ONAYI YOK", "#8b949e"
            intel.append(f"KRİTİK UYARI: {symbol} üzerinde işlem hacmi yetersiz ({vol_r:.1f}x). Fiyatın {ma20:.2f} pivotu üzerinde olması 'fake' bir harekettir. Hacim rasyosu 1.5x üzerine çıkmadan pozisyon almak likidite tuzağı yaratabilir.")
        elif lp > ma20 and vol_r >= 1.2:
            sig, col = "GÜÇLÜ TREND", "#00ff88"
            intel.append(f"STRATEJİ: Trend onayı alındı. Hacimli bir şekilde pivotun üzerinde kalıcılık sağlanıyor. {target:.2f} hedefi masada, {stop:.2f} seviyesi ana savunma hattı olarak güncellendi.")
        elif lp < ma20:
            sig, col = "AYI BASKISI", "#ff4b4b"
            intel.append(f"DİKKAT: Ayı piyasası hakimiyeti sürüyor. Fiyat {ma20:.2f} altında kaldığı sürece her yükseliş 'satış fırsatı' olarak görülecektir. Güvenli bölgeye dönüş için pivot üstü kapanış şart.")
        else:
            sig, col = "BELİRSİZLİK", "#ffcc00"
            intel.append(f"ANALİZ: Fiyat kararsız bölgede. {ma20:.2f} pivot noktası etrafında testere piyasası (Chop) hakim. Net bir hacim girişi görülene kadar izlemede kalınmalı.")

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "intel": " ".join(intel), "sig": sig, "col": col, "vol": vol_r}
    except: return None

# --- 4. ANA DASHBOARD ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#ffcc00;'>🤵 GÜRKAN AI</h1><p style='color:#8b949e;'>ABSOLUTE ZERO v209</p></div>", unsafe_allow_html=True)
        pw = st.text_input("ŞİFRE", type="password", label_visibility="collapsed")
        if st.button("TERMİNALİ AÇ"):
            if pw == "HEDEF2024!": st.session_state["auth"] = True; st.rerun()
    st.stop()

# Üst Bar
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:12px; font-weight:bold; font-size:12px;'>STRATEJİK ARAŞTIRMA MERKEZİ (+)</p>", unsafe_allow_html=True)

# Sorgu
c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c3:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favoriler
f_cols = st.columns(len(st.session_state["favorites"]) if st.session_state["favorites"] else 1)
for i, f in enumerate(st.session_state["favorites"]):
    if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Dashboard
res = get_absolute_zero_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;'>
            <div>
                <p class='label-mini'>{st.session_state["last_sorgu"]} // TERMINAL CORE</p>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:28px; font-weight:700;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['col']}; font-weight:bold; font-size:22px;'>{res['sig']}</span><br>
                <span class='label-mini'>INTENSITY: {res['vol']:.1f}x</span>
            </div>
        </div>
        
        <div class='radar-grid'>
            <div class='radar-item'><p class='label-mini'>PİVOT (MA20)</p><p style='font-size:26px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 5px solid #00ff88;'><p class='label-mini'>PRO TARGET (+)</p><p style='font-size:26px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 5px solid #ff4b4b;'><p class='label-mini'>SAFE STOP LOSS</p><p style='font-size:26px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        
        <div class='intel-box'>
            <span class='plus-badge'>GÜRKAN AI RESEARCH (+)</span>
            <p class='report-content'>"{res['intel']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=480, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(color='#484f58')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
