import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI v182", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "AKBNK"

# --- 2. CSS (Hatasız ve Keskin Karanlık Tema) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; }
    
    .terminal-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 8px;
        padding: 20px; border-left: 5px solid #ffcc00; margin-bottom: 15px;
    }
    
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 2px !important;
        font-size: 10px !important; height: 22px !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

# --- 3. HIZLI VE AKILLI ANALİZ MOTORU ---
def get_clean_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Temel Zeka Göstergeleri
        df['MA20'] = df['Close'].rolling(20).mean()
        # Para Akışı (Basit ama Etkili MFI)
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        rmf = tp * df['Volume']
        pos = rmf.where(tp > tp.shift(1), 0).rolling(14).sum()
        neg = rmf.where(tp < tp.shift(1), 0).rolling(14).sum()
        mfi = 100 - (100 / (1 + pos / neg))
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        cur_mfi = mfi.iloc[-1]; vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # GERÇEKÇİ ANALİZ YORUMLARI
        if vol_ratio > 2 and ch > 1:
            sig, clr, com = "JOKER GİRİŞİ", "#00ff88", "Tahtaya dev bir para girişi oldu. Hacim patlaması trendin kalıcı olacağını gösteriyor. Akbank benzeri kopuş kapıda."
        elif cur_mfi > 80:
            sig, clr, com = "ŞİŞME VAR / SAT", "#ffcc00", "Para akışı doyuma ulaştı. Kağıt teknik olarak çok ısındı, realizasyon gelmesi an meselesi. Yeni alım riskli."
        elif ch < -1 and vol_ratio > 1.5:
            sig, clr, com = "MAL BOŞALTMA", "#ff4b4b", "Hacimli düşüş var. Büyük eller çıkış yapıyor olabilir. Destek seviyelerini beklemek en doğrusu."
        elif lp > df['MA20'].iloc[-1]:
            sig, clr, com = "TREND DESTEĞİ", "#00d4ff", "Fiyat ortalamanın üzerinde sakin güç topluyor. Paniğe gerek yok, yön hala yukarı."
        else:
            sig, clr, com = "İZLE / NÖTR", "#8b949e", "Belirgin bir para girişi veya haber etkisi yok. Tahtacı şu an kağıdı serbest bırakmış görünüyor."
            
        return {"p": lp, "ch": ch, "sig": sig, "clr": clr, "com": com, "df": df, "mfi": cur_mfi}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:5px;'>GÜRKAN AI : TERMINAL v182</h3>", unsafe_allow_html=True)

# KONTROL PANELİ
_, mid_search, _ = st.columns([1, 2, 1])
with mid_search:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.session_state["last_sorgu"] in st.session_state["favorites"]:
            if st.button("🔴 SİL"): st.session_state["favorites"].remove(st.session_state["last_sorgu"]); st.rerun()
        else:
            if st.button("🟢 EKLE"): st.session_state["favorites"].append(st.session_state["last_sorgu"]); st.rerun()

l, m, r = st.columns([0.7, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_clean_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='terminal-card' style='border-left-color: {res['clr']}'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} ANALİZ</span><br>
                    <span style='font-size:38px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:20px;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:{res['clr']}; font-weight:bold; font-size:16px;'>{res['sig']}</span><br>
                    <span style='color:#4b525d; font-size:11px;'>MFI (Para Akışı): {res['mfi']:.1f}</span>
                </div>
            </div>
            <div style='margin-top:15px; padding-top:10px; border-top:1px solid #1c2128;'>
                <p style='color:#ffcc00; font-size:11px; font-weight:bold; margin-bottom:5px;'>🤵 AI STRATEJİ:</p>
                <p style='color:#e1e1e1; font-style:italic; font-size:14px;'>"{res['com']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=500, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "KCHOL", "SAHOL", "EREGL", "SISE"]:
        st.write(f"<span style='color:#ffcc00; font-size:11px;'>{rs}</span>", unsafe_allow_html=True)
        if st.button("İncele", key=f"r_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
