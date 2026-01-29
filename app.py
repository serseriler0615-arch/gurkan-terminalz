import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI : Intelligence", layout="wide", initial_sidebar_state="collapsed")

# Favori ve Hafıza Ayarları
if "auth" not in st.session_state: st.session_state["auth"] = False
if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO", "EREGL"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (RADAR VE ZEKİ TASARIM) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Radar Kartları */
    .radar-box {
        background: linear-gradient(145deg, #0d1117, #0b0e14);
        border: 1px solid #1c2128; border-radius: 12px;
        padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
    }
    
    .price-text { font-size: 45px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #fff; }
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
    
    /* Zeka Kutusu (Görsel 1 Ruhu) */
    .intel-box { 
        background: rgba(255, 204, 0, 0.04); border-radius: 10px; padding: 20px; 
        border: 1px solid #30363d; border-left: 5px solid #ffcc00; margin-top: 20px;
    }
    
    /* Mobil Uyumlu Grid */
    .radar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-top: 20px; }
    .radar-item { background: #111418; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #1c2128; }

    /* Butonlar ve Girişler */
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; }
    div.stButton > button { background: #111418 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; width: 100%; height: 35px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN GİRİŞİ (HEDEF2024!) ---
if not st.session_state["auth"]:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#ffcc00; letter-spacing:5px;'>GÜRKAN AI</h1><p style='color:#8b949e;'>SECURE ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)
        pw = st.text_input("Giriş Şifresi", type="password", label_visibility="collapsed")
        if st.button("TERMİNALİ ÇALIŞTIR"):
            if pw == "HEDEF2024!":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("ŞİFRE REDDEDİLDİ.")
    st.stop()

# --- 4. DERİN ZEKA VE RADAR ANALİZİ ---
def get_intel_report(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # Matematiksel Doğruluk
        target = lp + (atr * 2.2)
        stop = lp - (atr * 1.5)
        
        # Radar Analizi (Zeka)
        if lp > ma20 and vol_r > 1.2:
            radar_sig = "GÜÇLÜ RADAR"; r_col = "#00ff88"
            yorum = f"Sistem, {symbol} üzerinde güçlü bir 'Accumulation' (Toplama) evresi tespit etti. {lp:.2f} seviyesindeki hacimli kapanış, {ma20:.2f} pivotunun üzerinde kalıcı bir boğa trendini müjdeliyor. Hedef {target:.2f}."
        elif lp < ma20 and vol_r > 1.2:
            radar_sig = "TEHLİKE (SAT)"; r_col = "#ff4b4b"
            yorum = f"Dikkat! Yüksek hacimli satış baskısı mevcut. Fiyat {ma20:.2f} pivotunun altında kalarak zayıf bir profil çiziyor. {stop:.2f} desteği kırılırsa düşüş derinleşebilir."
        else:
            radar_sig = "KONSOLİDASYON"; r_col = "#00d4ff"
            yorum = f"Fiyat şu an dengelenme bölgesinde. Hacim rasyosu ({vol_r:.1f}x) patlama öncesi sessizliği andırıyor. {ma20:.2f} pivotu üzerinde kalıcılık aranmalı."

        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": target, "stop": stop, "yorum": yorum, "sig": radar_sig, "s_col": r_col, "vol": vol_r}
    except: return None

# --- 5. ANA TERMİNAL ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:10px; font-weight:bold; margin-bottom:20px;'>GÜRKAN AI : INTELLIGENCE DASHBOARD</p>", unsafe_allow_html=True)

# Arama ve Favori Yönetimi (Radar Kontrol)
c_inp, c_search, c_fav = st.columns([3, 1, 1])
with c_inp: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
with c_search: 
    if st.button("🔍 ANALİZ ET"): st.session_state["last_sorgu"] = s_inp; st.rerun()
with c_fav:
    if st.button("⭐ FAVORİ"):
        if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
        else: st.session_state["favorites"].append(s_inp)
        st.rerun()

# Aktif Favori Radarı
if st.session_state["favorites"]:
    f_cols = st.columns(len(st.session_state["favorites"]))
    for i, f in enumerate(st.session_state["favorites"]):
        if f_cols[i].button(f"{f}"): st.session_state["last_sorgu"] = f; st.rerun()

# Radar Sonuçları
res = get_intel_report(st.session_state["last_sorgu"])
if res:
    st.markdown(f"""
    <div class='radar-box'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <span class='label-mini'>{st.session_state["last_sorgu"]} ANALİZ MERKEZİ</span><br>
                <span class='price-text'>{res['p']:.2f}</span>
                <span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:24px; font-weight:bold;'> {res['ch']:+.2f}%</span>
            </div>
            <div style='text-align:right;'>
                <span style='color:{res['s_col']}; font-weight:bold; font-size:20px;'>{res['sig']}</span><br>
                <span class='label-mini'>HACİM GÜCÜ: {res['vol']:.1f}x</span>
            </div>
        </div>
        
        <div class='radar-grid'>
            <div class='radar-item'><p class='label-mini'>PİVOT (MA20)</p><p style='font-size:22px; font-weight:bold; color:#8b949e;'>{res['ma']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 3px solid #00ff88;'><p class='label-mini'>TEKNİK HEDEF</p><p style='font-size:22px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p></div>
            <div class='radar-item' style='border-bottom: 3px solid #ff4b4b;'><p class='label-mini'>ZARAR KES</p><p style='font-size:22px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p></div>
        </div>
        
        <div class='intel-box'>
            <p class='label-mini' style='color:#ffcc00; margin-bottom:10px;'>🕵️ ANALİST STRATEJİ RAPORU</p>
            <p style='color:#d1d1d1; line-height:1.6; font-style:italic;'>"{res['yorum']}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Grafik (Görsel 1 Tarzı)
    fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

if st.sidebar.button("OTURUMU KAPAT"):
    st.session_state["auth"] = False
    st.rerun()
