import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Intelligence", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "EREGL", "ISCTR", "AKBNK"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. CSS (ELITE EXECUTIVE STYLE) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; border-radius: 8px !important; }

    .master-card {
        background: linear-gradient(145deg, #0d1117, #080a0d);
        border: 1px solid #1c2128; border-radius: 12px; padding: 25px;
        border-top: 5px solid #ffcc00; margin-bottom: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .price-text { font-size: 45px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; line-height: 1; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
    
    .radar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; margin-top: 20px; }
    .radar-item { background: #111418; padding: 18px; border-radius: 10px; text-align: center; border: 1px solid #1c2128; }
    
    .intel-box { 
        background: rgba(255, 204, 0, 0.03); border-radius: 8px; padding: 20px; margin-top: 20px;
        border-left: 4px solid #ffcc00; border-right: 1px solid #1c2128;
    }
    div.stButton > button { background: #111418 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; width: 100%; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:100px;'><h2 style='color:#ffcc00;'>🤵 ADMIN PANEL</h2>", unsafe_allow_html=True)
        pw = st.text_input("GİRİŞ ŞİFRESİ", type="password", label_visibility="collapsed")
        if st.button("SİSTEMİ BAŞLAT"):
            if pw == "HEDEF2024!": st.session_state["auth"] = True; st.rerun()
            else: st.error("HATALI!")
    st.stop()

# --- 4. KESKİN ANALİZ MOTORU ---
def get_absolute_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # Matematiksel Doğruluk (Safe Margin Stop)
        target = lp + (atr * 2.5)
        stop = lp - (atr * 1.8)
        
        # Zeka Filtresi
        if vol_r < 0.5:
            radar_sig = "İLGİSİZ / LİKİTİDE RİSKİ"; r_col = "#8b949e"
            yorum = f"Dikkat: Hacim ({vol_r:.1f}x) kritik seviyenin altında. Piyasa yapıcılar {symbol} üzerinde henüz aktif değil. {ma20:.2f} pivotu üzerinde olsa dahi düşük hacim bu yükselişi 'fake' kılabilir. Bekle-Gör stratejisi uygun."
        elif lp > ma20 and vol_r > 1.2:
            radar_sig = "GÜÇLÜ BOĞA"; r_col = "#00ff88"
            yorum = f"Trend ve hacim onayı alındı. {lp:.2f} seviyesindeki güçlü duruş, {ma20:.2f} desteğinden alınan güçle {target:.2f} hedefine doğru ivmeleniyor. Pozisyonlar korunabilir."
        else:
            radar_sig = "BASKILI SEYİR"; r_col = "#ff4b4b"
            yorum = f"Fiyat {ma20:.2f} pivotunun altında kalarak zayıf bir profil çiziyor. {stop:.2f} ana destek seviyesine kadar geri çekilme riski masada. Yeni pozisyon için hacim onayı beklenmeli."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "yorum": yorum, "sig": radar_sig, "s_col": r_col, "vol": vol_r}
    except: return None

# --- 5. ANA EKRAN ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:10px; font-weight:bold;'>GÜRKAN AI : ABSOLUTE INTELLIGENCE</p>", unsafe_allow_html=True)

# Kontrol Paneli
c_inp, c_s, c_f = st.columns([3, 1, 1])
with c_inp: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c_s: 
    if st.button("🔍 ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c_f:
    t = "❌ SİL" if s_inp in st.session_state["favorites"] else "⭐ EKLE"
    if st.button(t):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favori Radarı
f_cols = st.columns(len(st.session_state["favorites"]) if st.session_state["favorites"] else 1)
for i, f in enumerate(st.session_state["favorites"]):
    if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Dashboard
res = get_absolute_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
            <div>
                <span class='label-mini'>{st.session_state["last_sorgu"]} ANALİZ MERKEZİ</span><br>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:24px; font-weight:bold;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['s_col']}; font-weight:bold; font-size:18px;'>{res['sig']}</span><br>
                <span class='label-mini'>HACİM GÜCÜ: {res['vol']:.1f}x</span>
            </div>
        </div>
        <div class='radar-grid'>
            <div class='radar-item'><p class='label-mini'>PİVOT (MA20)</p><p style='font-size:22px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 3px solid #00ff88;'><p class='label-mini'>HEDEF</p><p style='font-size:22px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 3px solid #ff4b4b;'><p class='label-mini'>STOP (GÜVENLİ)</p><p style='font-size:22px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        <div class='intel-box'>
            <p class='label-mini' style='color:#ffcc00; margin-bottom:10px;'>🕵️ STRATEJİK ANALİST RAPORU</p>
            <p style='color:#d1d1d1; line-height:1.6; font-style:italic;'>"{res['yorum']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("OTURUMU KAPAT"):
    st.session_state["auth"] = False
    st.rerun()
