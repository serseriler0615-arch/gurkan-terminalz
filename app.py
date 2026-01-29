import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI : Analyst", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "HUNER", "SMART"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (ESKİ GÜZELLİK + MOBİL ZEKA) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    .login-box { 
        max-width: 400px; margin: 100px auto; padding: 30px; 
        background: #0d1117; border: 2px solid #ffcc00; border-radius: 12px; text-align: center;
    }
    
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; text-align: center; font-size: 16px !important;
    }

    /* Görsel 1 & 2'deki Ana Kart Yapısı */
    .master-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 10px;
        padding: 25px; border-top: 4px solid #00d4ff; margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }
    
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: bold; }
    .price-text { font-size: 42px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; line-height: 1; }
    
    .report-text { color: #ffcc00; font-size: 13px; line-height: 1.6; border-left: 3px solid #ffcc00; padding-left: 15px; margin-top: 15px; font-style: italic; }
    
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important; font-size: 12px !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }

    /* Mobil için kart içi grid ayarı */
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-top: 25px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ ---
if not st.session_state["auth"]:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#ffcc00; letter-spacing:3px;'>🤵 ADMIN GİRİŞİ</h2>", unsafe_allow_html=True)
    pw = st.text_input("GÜVENLİK KODU", type="password")
    if st.button("TERMİNALİ BAŞLAT"):
        if pw == "HEDEF2024!":
            st.session_state["auth"] = True
            st.rerun()
        else: st.error("HATALI ŞİFRE!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. ARAŞTIRMACI ANALİZ MOTORU ---
def get_deep_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        # --- Araştırmacı Zeka: Yorum Oluşturma ---
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        if ch > 1 and vol_r > 1.3:
            yorum = f"Hacimli bir kırılım gözleniyor. {lp:.2f} seviyesindeki güçlenme, {ma20:.2f} desteğinin üzerinde sağlıklı bir trend oluşturdu. Alıcı iştahı yüksek."
        elif lp < ma20:
            yorum = f"Fiyat ana pivot noktası olan {ma20:.2f} altında baskılanıyor. Güvenli bölge için bu seviye üzerinde kalıcılık aranmalı. Negatif momentum sürüyor."
        else:
            yorum = f"Trend kanalı içinde konsolidasyon mevcut. Hacim onayı gelene kadar mevcut pozisyonların korunması mantıklı görünüyor. {ma20:.2f} ana destek."

        return {"p": lp, "ch": ch, "df": df, "ma20": ma20, "target": lp+(atr*2.5), "stop": lp-(atr*1.2), "yorum": yorum}
    except: return None

# --- 5. ANA EKRAN ---
st.markdown("<h2 style='text-align:center; color:#ffcc00; letter-spacing:8px;'>🤵 GÜRKAN AI : INTEL ANALYST</h2>", unsafe_allow_html=True)

# Üst Bar (Arama + Favori Yönetimi)
c_inp, c_search, c_fav = st.columns([3, 1, 1])
with c_inp: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c_search: 
    if st.button("SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c_fav:
    btn_text = "❌ LİSTEDEN ÇIKAR" if s_inp in st.session_state["favorites"] else "⭐ LİSTEYE EKLE"
    if st.button(btn_text):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Yatay Favori Butonları
st.write("")
f_cols = st.columns(len(st.session_state["favorites"]) if st.session_state["favorites"] else 1)
for i, f in enumerate(st.session_state["favorites"]):
    if f_cols[i].button(f"• {f}"): st.session_state["last_sorgu"] = f; st.rerun()

# Ana Analiz Paneli
res = get_deep_analysis(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='master-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;'>
            <div>
                <span class='label-mini'>{st.session_state["last_sorgu"]} TERMİNAL VERİSİ</span><br>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:22px; font-weight:bold;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:#00d4ff; font-weight:bold; font-size:18px;'>POZİSYONU KORU</span><br>
                <span class='label-mini'>GÜVEN ENDEKSİ: YÜKSEK</span>
            </div>
        </div>
        
        <div class='metric-grid'>
            <div style='background:#111418; padding:20px; border-radius:8px; text-align:center;'>
                <p class='label-mini'>MA20 PİVOT</p><p style='font-size:24px; font-weight:bold; color:#8b949e;'>{res['ma20']:.2f}</p>
            </div>
            <div style='background:#111418; padding:20px; border-radius:8px; text-align:center; border: 1px solid #00ff8833;'>
                <p class='label-mini'>TEKNİK HEDEF</p><p style='font-size:24px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p>
            </div>
            <div style='background:#111418; padding:20px; border-radius:8px; text-align:center; border: 1px solid #ff4b4b33;'>
                <p class='label-mini'>ZARAR KES (STOP)</p><p style='font-size:24px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p>
            </div>
        </div>
        
        <div class='report-text'>
            <b style='color:#ffcc00; text-transform:uppercase;'>Stratejik Araştırma Raporu:</b><br>
            "{res['yorum']}"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Profesyonel Grafik
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                      xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Çıkış Paneli
if st.sidebar.button("ADMIN ÇIKIŞI"):
    st.session_state["auth"] = False
    st.rerun()
