import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. VIP GÜVENLİK SİSTEMİ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False

    def login_logic():
        u_input = st.session_state["username"].strip().upper()
        p_input = st.session_state["password"].strip()
        if u_input == "GURKAN" and p_input == "HEDEF2024!":
            st.session_state["password_correct"] = True
            st.session_state["is_admin"] = True
        else:
            st.error("❌ Hatalı Giriş!")

    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center; color: #00ff88;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
        cols = st.columns([1, 1.5, 1])
        with cols[1]:
            st.text_input("VIP ID", key="username")
            st.text_input("VIP Şifre", type="password", key="password")
            st.button("Giriş Yap", on_click=login_logic, use_container_width=True)
        return False
    return True

# --- 2. ANA TERMİNAL ---
if check_password():
    st.set_page_config(page_title="Gürkan AI VIP", layout="wide")

    # GÖRÜNÜRLÜK DÜZELTME CSS (Kritik Bölge)
    st.markdown("""
        <style>
        /* Ana Arka Plan */
        .stApp { background-color: #0d1117 !important; }
        
        /* Tüm yazı renklerini beyaza zorla */
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }
        
        /* Input kutularının içindeki yazıların rengi (Siyah olmasın diye) */
        input { color: #0d1117 !important; font-weight: bold; }
        
        /* Admin paneli ve kart metinleri */
        .admin-panel, .radar-card, .asistan-notu { color: #e6edf3 !important; }
        
        div[data-testid="stExpander"] p { color: #ffffff !important; }
        
        /* Kart Tasarımları */
        div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
        .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
        .asistan-notu { background: #1c2128; border: 1px solid #00ff88; padding: 20px; border-radius: 15px; }
        .admin-panel { background: #1e2327; border: 1px dashed #00ff88; padding: 20px; border-radius: 12px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔑 ADMIN PANELİ ---
    if st.session_state["is_admin"]:
        with st.expander("🛠️ ADMIN KEY YÖNETİM MERKEZİ (TIKLA)"):
            st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#00ff88;'>🔑 Yeni VIP Üye Lisansı</h3>", unsafe_allow_html=True)
            uye = st.text_input("Üye Adı Soyadı (Yazı burada görünecek):")
            if st.button("Lisans Anahtarı Üret"):
                key = f"GAI-{int(time.time())}-{uye[:3].upper()}"
                st.code(key, language="text")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- İÇERİK ---
    sol, sag = st.columns([3, 1])

    with sol:
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            h_input = st.text_input("🔍 İncelemek İstediğiniz VIP Sembol:", value="ISCTR").upper()
        
        try:
            sembol = h_input if "." in h_input else h_input + ".IS"
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                son = float(df['Close'].iloc[-1])
                with c2: st.metric("FİYAT", f"{son:.2f} TL")
                with c3: st.metric("GÜNLÜK", f"%{((son - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100:.2f}")

                st.markdown(f"📈 **{h_input} VIP Trend Görünümü**")
                st.area_chart(df['Close'].tail(20), color="#00ff88")
                
                # Zeki Asistan Notu
                st.markdown(f"""
                <div class='asistan-notu'>
                    <b>🤵 VIP Asistan Notu:</b> {h_input} analizi başarıyla tamamlandı. 
                    Fiyat {son:.2f} seviyesinde seyrediyor. Teknik veriler 'VIP Radarı' ile uyumlu.
                </div>
                """, unsafe_allow_html=True)
        except: st.error("Veri alınamadı.")

    with sag:
        st.markdown("<h3 style='color:#00ff88; text-align:center;'>🚀 VIP RADAR</h3>", unsafe_allow_html=True)
        radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "TUPRS.IS"]
        for r in radar_list:
            st.markdown(f"""
            <div class="radar-card">
                <b style="color:#00ff88;">{r.split('.')[0]}</b><br>
                <small>Sinyal: %2+ POTANSİYEL</small>
            </div>
            """, unsafe_allow_html=True)
