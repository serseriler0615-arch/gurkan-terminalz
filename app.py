import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Neural", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "EREGL", "ISCTR", "AKBNK"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. CSS (ELITE RESPONSIVE DESIGN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Input & Buttons */
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; text-align: center; border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace;
    }
    div.stButton > button { 
        background: #111418 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; width: 100%; border-radius: 8px;
        transition: 0.3s; font-weight: bold;
    }
    div.stButton > button:hover { border-color: #ffcc00; box-shadow: 0 0 10px rgba(255,204,0,0.2); }

    /* Ana Kart Yapısı */
    .master-card {
        background: linear-gradient(160deg, #0d1117 0%, #07090c 100%);
        border: 1px solid #1c2128; border-radius: 16px; padding: 25px;
        border-top: 6px solid #ffcc00; margin-bottom: 20px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.7);
    }
    
    .price-text { font-size: clamp(32px, 5vw, 52px); font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; line-height: 1; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
    
    /* Radar Grid & Items */
    .radar-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); 
        gap: 15px; margin-top: 25px; 
    }
    .radar-item { 
        background: rgba(255,255,255,0.03); padding: 18px; border-radius: 12px; 
        text-align: center; border: 1px solid #1c2128;
    }
    
    /* Araştırmacı Rapor Kutusu */
    .intel-box { 
        background: rgba(255, 204, 0, 0.05); border-radius: 12px; padding: 22px; margin-top: 25px;
        border: 1px solid rgba(255,204,0,0.1); border-left: 5px solid #ffcc00;
    }
    .report-content { color: #d1d1d1; font-size: 15px; line-height: 1.7; font-style: italic; font-family: sans-serif; }

    /* Mobil Ayarı */
    @media (max-width: 600px) {
        .master-card { padding: 15px; }
        .radar-grid { grid-template-columns: 1fr 1fr; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:80px;'><h1 style='color:#ffcc00; letter-spacing:8px;'>🤵 GÜRKAN AI</h1><p style='color:#4b525d;'>NEURAL STRATEGIST v204</p></div>", unsafe_allow_html=True)
        pw = st.text_input("GİRİŞ ANALAHTARI", type="password", label_visibility="collapsed")
        if st.button("SİSTEMİ UYANDIR"):
            if pw == "HEDEF2024!": st.session_state["auth"] = True; st.rerun()
            else: st.error("ERİŞİM REDDEDİLDİ.")
    st.stop()

# --- 4. NEURAL ANALİZ MOTORU (KESKİN RADAR) ---
def get_neural_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # Keskin Radar Hesaplamaları
        target = lp + (atr * 2.5)
        stop = lp - (atr * 1.6)
        
        # Araştırmacı Zeka Motoru
        if vol_r < 0.4:
            sig, col = "DÜŞÜK LİKİTİDE", "#8b949e"
            yorum = f"Analiz Sonucu: {symbol} üzerinde işlem hacmi ({vol_r:.1f}x) alarm verici düzeyde düşük. Piyasa bu fiyat seviyelerini onaylamıyor. Ciddi bir 'Likitide Tuzağı' riski var. Teknik seviyelerden ziyade hacim girişi beklenmeli."
        elif lp > ma20 and vol_r > 1.3:
            sig, col = "GÜÇLÜ AKÜMÜLASYON", "#00ff88"
            yorum = f"Stratejik Rapor: Hissede kurumsal toplama (akümülasyon) emareleri var. Hacim desteği ({vol_r:.1f}x) yükselişi perçinliyor. {ma20:.2f} pivotunun üzerinde kalındığı sürece {target:.2f} teknik hedefi geçerliliğini korur."
        elif lp < ma20:
            sig, col = "NEGATİF MOMENTUM", "#ff4b4b"
            yorum = f"Dikkat: Ayı baskısı hakim. {ma20:.2f} pivot bölgesi sert direnç haline gelmiş durumda. Satışların hacimli olması düşüşün devam edebileceğine işaret ediyor. {stop:.2f} desteği son kale."
        else:
            sig, col = "NÖTR / İZLEME", "#00d4ff"
            yorum = f"Fiyat konsolide oluyor. Büyük oyuncuların yön kararı vermesi bekleniyor. Hacim ({vol_r:.1f}x) patlama için yetersiz. Güvenli giriş için pivot üstü hacimli kapanış aranmalı."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "yorum": yorum, "sig": sig, "col": col, "vol": vol_r}
    except: return None

# --- 5. ANA TERMİNAL ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:12px; font-weight:bold; margin-bottom:20px;'>NEURAL INTELLIGENCE TERMINAL</p>", unsafe_allow_html=True)

# Smart Control Bar
c1, c2, c3 = st.columns([3, 1, 1])
with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c2: 
    if st.button("🔍 SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c3:
    fav_text = "❌ SİL" if s_inp in st.session_state["favorites"] else "⭐ EKLE"
    if st.button(fav_text):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Favori Radar Barı
if st.session_state["favorites"]:
    f_cols = st.columns(len(st.session_state["favorites"]))
    for i, f in enumerate(st.session_state["favorites"]):
        if f_cols[i].button(f): st.session_state["last_sorgu"] = f; st.rerun()

# Analiz Dashboard
res = get_neural_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;'>
            <div>
                <span class='label-mini'>{st.session_state["last_sorgu"]} // ANALİZ MERKEZİ</span><br>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:24px; font-weight:bold;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['col']}; font-weight:bold; font-size:20px; letter-spacing:1px;'>{res['sig']}</span><br>
                <span class='label-mini'>HACİM GÜCÜ: {res['vol']:.1f}x</span>
            </div>
        </div>
        
        <div class='radar-grid'>
            <div class='radar-item'><p class='label-mini'>PİVOT (MA20)</p><p style='font-size:24px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 4px solid #00ff88;'><p class='label-mini'>POZİTİF HEDEF</p><p style='font-size:24px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 4px solid #ff4b4b;'><p class='label-mini'>KRİTİK STOP</p><p style='font-size:24px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        
        <div class='intel-box'>
            <p class='label-mini' style='color:#ffcc00; margin-bottom:12px;'>🕵️ ARAŞTIRMACI STRATEJİ RAPORU (+)</p>
            <p class='report-content'>"{res['yorum']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pro Grafik
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("TERMİNALİ KAPAT"):
    st.session_state["auth"] = False
    st.rerun()
