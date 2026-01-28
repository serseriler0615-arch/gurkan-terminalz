import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & HAFIZA ---
st.set_page_config(page_title="Gürkan AI v178", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "AKBNK"

# --- 2. CSS (Mükemmel Obsidian & Mikro Buton) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #1c2128 !important; text-align: center; }
    
    .analysis-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 8px;
        padding: 20px; margin-bottom: 10px; border-left: 5px solid #ffcc00;
    }
    
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 2px !important;
        font-size: 10px !important; padding: 2px 5px !important; height: 22px !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. DERİN ANALİZ MOTORU (Eksiksiz Yorum) ---
def get_full_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Göstergeler
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / 
                                      -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean())))
        
        lp = float(df['Close'].iloc[-1])
        pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        rsi = float(df['RSI'].iloc[-1])
        ma20 = float(df['MA20'].iloc[-1])
        ma50 = float(df['MA50'].iloc[-1])
        
        # AI YORUM MANTIĞI
        if lp > ma20 and lp > ma50:
            status = "BOĞA PİYASASI"; clr = "#00ff88"
            comment = f"Fiyat hem 20 hem 50 günlük ortalamanın üzerinde. Piyasa yapıcı malı yukarı sürüyor. RSI ({rsi:.1f}) hala yükseliş alanı tanıyor. Güçlü trend devam edebilir."
        elif rsi > 70:
            status = "AŞIRI ŞİŞME"; clr = "#ffcc00"
            comment = f"RSI {rsi:.1f} seviyesinde. Kağıt teknik olarak doygunluğa ulaştı. Akbank örneğindeki gibi ani bir 'Joker' hacim gelmezse kar satışı kapıda."
        elif lp < ma20 and lp < ma50:
            status = "AYI BASKISI"; clr = "#ff4b4b"
            comment = "Ana destekler kırılmış. Satıcılar tahtaya hakim. Yeni alım için 20 günlük ortalamanın (MA20) üzerine atmasını beklemek en güvenlisi."
        else:
            status = "KARARSIZ BÖLGE"; clr = "#8b949e"
            comment = "Kısa ve uzun vade ortalamalar arasında sıkışma var. Büyük bir kırılım (Hacim patlaması) olmadan yön tayini yapmak kumar olur."
            
        return {"p": lp, "ch": ch, "status": status, "clr": clr, "com": comment, "df": df, "rsi": rsi}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:5px;'>GÜRKAN AI : TERMINAL v178</h3>", unsafe_allow_html=True)

# ARAMA VE FAVORİ YÖNETİMİ
_, mid_search, _ = st.columns([1, 2, 1])
with mid_search:
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        # EKLE / ÇIKAR MANTIĞI
        if st.session_state["last_sorgu"] in st.session_state["favorites"]:
            if st.button("🔴 SİL"):
                st.session_state["favorites"].remove(st.session_state["last_sorgu"])
                st.rerun()
        else:
            if st.button("🟢 EKLE"):
                st.session_state["favorites"].append(st.session_state["last_sorgu"])
                st.rerun()

l, m, r = st.columns([0.7, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>FAVORİ LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"• {f}", key=f"fav_{f}"):
            st.session_state["last_sorgu"] = f; st.rerun()

with m:
    res = get_full_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='analysis-card' style='border-left-color: {res['clr']}'>
            <div style='display:flex; justify-content:space-between;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} DETAYLI ANALİZ</span><br>
                    <span style='font-size:36px; font-weight:bold;'>{res['p']:.2f}</span>
                    <span style='color:{res['clr']}; font-size:20px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:{res['clr']}; font-weight:bold; font-size:16px;'>{res['status']}</span>
                    <p class='label-mini' style='margin-top:10px;'>GÜNCEL RSI: {res['rsi']:.1f}</p>
                </div>
            </div>
            <div style='margin-top:15px; padding-top:10px; border-top:1px solid #1c2128;'>
                <p style='color:#ffcc00; font-size:12px; font-weight:bold; margin-bottom:5px;'>🤵 GÜRKAN AI STRATEJİK YORUMU:</p>
                <p style='color:#e1e1e1; font-style:italic; font-size:14px; line-height:1.6;'>"{res['com']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=500, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>PİYASA RADARI</p>", unsafe_allow_html=True)
    for rs in ["TUPRS", "KCHOL", "SAHOL", "PGSUS", "SISE", "BIMAS"]:
        st.markdown(f"<p style='color:#ffcc00; font-size:11px; margin-bottom:2px;'>{rs}</p>", unsafe_allow_html=True)
        if st.button("İncele", key=f"rad_{rs}"):
            st.session_state["last_sorgu"] = rs; st.rerun()
