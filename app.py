import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. OTURUM VE SİSTEM ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 🔐 GİRİŞ SİSTEMİ ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("SİSTEME GİR", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): 
                        st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            with st.form("a"):
                u = st.text_input("ID")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("ADMİN GİRİŞ", use_container_width=True):
                    if u.strip().upper() == "GURKAN" and p.strip() == "HEDEF2024!": 
                        st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 PRO CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .block-container { max-width: 1250px !important; padding-top: 1rem !important; margin: auto; }
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 18px; 
            border-radius: 10px; color: #ffffff; border-left: 5px solid #ffcc00; margin-bottom: 15px;
        }
        .text-green { color: #00ff88; font-weight: bold; }
        .text-red { color: #ff4b4b; font-weight: bold; }
        .text-blue { color: #00d4ff; font-weight: bold; }
        .strat-badge { padding: 4px 12px; border-radius: 6px; font-weight: bold; color: black; font-size: 14px; }
        .percent-box { background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; border: 1px dashed #30363d; margin-top: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔍 ARAMA & BAŞLIK ---
    st.markdown("<h2 style='color:#ffcc00; text-align:center; font-size:26px;'>★ GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
    _, sc2, sc3, _ = st.columns([2, 2.5, 0.7, 2])
    with sc2:
        h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Hisse Ara...", label_visibility="collapsed").upper().strip()
    with sc3:
        if st.button("➕ EKLE", use_container_width=True):
            if h_input not in st.session_state["favorites"]:
                st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_fav, col_main, col_radar = st.columns([1, 4, 1.2])

    with col_fav:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f"{f}", key=f"f_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with cf2:
                if st.button("×", key=f"d_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()

    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                # --- 🧠 ZEKA MOTORU HESAPLARI ---
                last_p = float(df['Close'].iloc[-1])
                change = ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
                
                # RSI Hesapla
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))

                # --- 📊 YÜZDESEL BEKLENTİ HESABI ---
                # Volatiliteye göre (son 10 günün ortalama hareketi)
                volatility = (df['High'] - df['Low']).tail(10).mean() / last_p * 100
                up_pot = round(volatility * 1.5, 1) # Yükseliş beklentisi
                down_risk = round(volatility * 1.2, 1) # Düşüş riski

                # Strateji & Renk
                if rsi > 75: strat, color, up_pot, down_risk = "KAR AL / DOYUM", "#ff4b4b", up_pot*0.5, down_risk*2.0
                elif rsi < 30: strat, color, up_pot, down_risk = "TEPKİ ALIMI YAKIN", "#00ff88", up_pot*2.5, down_risk*0.5
                elif last_p > ma20: strat, color = "TREND POZİTİF", "#00ff88"
                else: strat, color = "İZLE / NAKİTTE KAL", "#ffcc00"

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("FİYAT", f"{last_p:.2f} ₺")
                m2.metric("GÜNLÜK", f"%{change:+.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                m4.metric("VOLATİLİTE", f"%{volatility:.1f}")

                # --- 🤵 GÜRKAN PRO ANALİZ ---
                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <b style='color:#ffcc00; font-size:20px;'>🤵 GÜRKAN PRO ANALİZ</b><br><br>
                    <p style='font-size:16px;'>
                        Hisse: <span class='text-blue'>{h_input}</span> | Strateji: <span class='strat-badge' style='background:{color};'>{strat}</span><br>
                    </p>
                    <div class='percent-box'>
                        <table style='width:100%; border:none;'>
                            <tr>
                                <td style='text-align:center;'>🚀 <b>OLASI YÜKSELİŞ</b><br><span class='text-green' style='font-size:22px;'>+ %{up_pot}</span></td>
                                <td style='text-align:center; border-left: 1px solid #30363d;'>⚠️ <b>OLASI DÜŞÜŞ</b><br><span class='text-red' style='font-size:22px;'>- %{down_risk}</span></td>
                            </tr>
                        </table>
                    </div>
                    <p style='margin-top:15px; font-size:14px; color:#8b949e;'>
                        *Bu oranlar hissenin son 10 gündeki hareket genliğine ve RSI doygunluğuna göre hesaplanmıştır. 
                        Trendin devamı halinde <span class='text-green'>{last_p * (1 + up_pot/100):.2f} ₺</span> seviyesi teknik hedef, 
                        <span class='text-red'>{last_p * (1 - down_risk/100):.2f} ₺</span> seviyesi ise stop-loss olarak izlenebilir.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.info("Hisse verileri işleniyor...")

    with col_radar:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE"]:
            if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
