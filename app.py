import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Oracle", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. ELITE ORACLE CSS (CAM EFEKTLİ & KESKİN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    .master-card {
        background: linear-gradient(145deg, #0d1117 0%, #05070a 100%);
        border: 1px solid #1c2128; border-radius: 24px; padding: 35px;
        border-top: 5px solid #ffcc00; margin-bottom: 25px;
        box-shadow: 0 50px 100px rgba(0,0,0,0.9);
    }
    .price-text { font-size: clamp(40px, 7vw, 62px); font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #ffffff; letter-spacing: -3px; }
    .label-mini { color: #484f58; font-size: 10px; text-transform: uppercase; letter-spacing: 4px; font-weight: 800; }
    
    .radar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 20px; margin-top: 30px; }
    .radar-item { 
        background: rgba(255,255,255,0.01); padding: 25px; border-radius: 18px; 
        border: 1px solid #1c2128; text-align: center; transition: all 0.4s ease;
    }
    .radar-item:hover { background: rgba(255,204,0,0.02); border-color: #ffcc0044; transform: translateY(-5px); }
    
    .intel-box { 
        background: rgba(255, 204, 0, 0.02); border-radius: 20px; padding: 30px; margin-top: 30px;
        border-left: 8px solid #ffcc00; border-right: 1px solid #1c2128;
    }
    .plus-badge { background: #ffcc00; color: #000; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 900; margin-bottom: 15px; display: inline-block; }
    .report-content { color: #d1d5db; font-size: 16px; line-height: 1.9; font-family: 'Inter', sans-serif; }

    div.stButton > button { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 12px; height: 45px; font-weight: 700; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 10px !important; text-align: center; }

    @media (max-width: 600px) { .radar-grid { grid-template-columns: 1fr 1fr; } .master-card { padding: 20px; } }
</style>
""", unsafe_allow_html=True)

# --- 3. ORACLE ANALİZ MOTORU ---
def get_oracle_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        low_20 = df['Low'].rolling(20).min().iloc[-1] # Son 20 günün dibi
        
        # --- STRATEJİK HESAPLAMA ---
        target = lp + (atr * 2.7)
        # Stop, pivotun %4 altı ile son 20 günün dibi arasındaki en güvenli noktadır.
        stop = min(ma20 * 0.96, low_20 * 0.99)
        
        # --- DERİN ZEKA (+) ---
        intel = []
        if vol_r < 0.5:
            sig, col = "İLGİ KAYBI / ZAYIF", "#484f58"
            intel.append(f"Araştırma Notu: {symbol} şu an kurumsal radardan çıkmış durumda. Hacim rasyosu ({vol_r:.1f}x) teknik formasyonları 'aldatıcı' kılabilir. {ma20:.2f} pivotu üzerinde olsa dahi aksiyon için hacim onayı şart.")
        elif lp > ma20 and 0.8 <= vol_r <= 1.2:
            sig, col = "SESSİZ AKÜMÜLASYON", "#00d4ff"
            intel.append(f"Stratejik Tespit: Fiyat {ma20:.2f} pivotunda 'dip çalışması' yapıyor. Hacmin stabil kalması, büyük oyuncuların sessizce pozisyon biriktirdiğine (Accumulation) işaret edebilir. {target:.2f} hedefi için enerji toplanıyor.")
        elif lp > ma20 and vol_r > 1.5:
            sig, col = "AGRESİF ALIM", "#00ff88"
            intel.append(f"Sinyal Onayı: Hacimli kopuş başladı! {lp:.2f} seviyesindeki güç, {target:.2f} hedefine giden yolu temizliyor. Trend takibi (Trend Following) stratejisi uygun.")
        else:
            sig, col = "RİSKLİ BÖLGE", "#ff4b4b"
            intel.append(f"Ayı Baskısı: Fiyat pivot altında dağıtım (Distribution) evresinde. {stop:.2f} desteği kırılırsa satış derinleşebilir.")

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "intel": " ".join(intel), "sig": sig, "col": col, "vol": vol_r}
    except: return None

# --- 4. ANA DASHBOARD ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#ffcc00; letter-spacing:5px;'>GÜRKAN AI</h1><p style='font-size:10px; color:#484f58;'>ELITE ORACLE v208</p></div>", unsafe_allow_html=True)
        pw = st.text_input("GİRİŞ ANAHTARI", type="password", label_visibility="collapsed")
        if st.button("TERMİNALİ UYANDIR"):
            if pw == "HEDEF2024!": st.session_state["auth"] = True; st.rerun()
    st.stop()

# Dashboard UI
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:12px; font-weight:bold; font-size:13px;'>ELITE RESEARCH TERMINAL</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 ANALİZ ET"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c3:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favori Barı
f_cols = st.columns(len(st.session_state["favorites"]) if st.session_state["favorites"] else 1)
for i, f in enumerate(st.session_state["favorites"]):
    if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

res = get_oracle_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;'>
            <div>
                <p class='label-mini'>{st.session_state["last_sorgu"]} // ORACLE CORE</p>
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
            <div class='radar-item' style='border-bottom: 5px solid #00ff88;'><p class='label-mini'>TARGET (PRO)</p><p style='font-size:26px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 5px solid #ff4b4b;'><p class='label-mini'>SAFEZONE STOP</p><p style='font-size:26px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
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
