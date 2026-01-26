import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. VIP GÜVENLİK & LİSANS SİSTEMİ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False

    def login_logic():
        # Admin ID: GURKAN | Şifre: HEDEF2024!
        u_input = st.session_state["username"].strip().upper()
        p_input = st.session_state["password"].strip()
        
        if u_input == "GURKAN" and p_input == "HEDEF2024!":
            st.session_state["password_correct"] = True
            st.session_state["is_admin"] = True
            st.toast("✅ Admin Girişi Başarılı!")
        else:
            st.error("❌ Hatalı Giriş! Bilgilerinizi kontrol edin.")

    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center; color: #00ff88;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #ff4b4b; font-weight: bold;'>⚠️ BU TERMİNAL VIP ÜYELİK GEREKTİRİR</p>", unsafe_allow_html=True)
        
        cols = st.columns([1, 1.5, 1])
        with cols[1]:
            st.text_input("VIP ID", key="username", placeholder="ID Giriniz...")
            st.text_input("VIP Şifre", type="password", key="password", placeholder="Şifre Giriniz...")
            st.checkbox("Beni Hatırla", key="remember_me", value=True)
            st.button("Terminale Güvenli Bağlantı Kur", on_click=login_logic, use_container_width=True)
        return False
    return True

# --- 2. ANA TERMİNAL BAŞLIYOR ---
if check_password():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # Tüm CSS ve Görsel İyileştirmeler
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        header {visibility: hidden;}
        div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; }
        .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
        .asistan-notu { background: #1c2128; border: 1px solid #00ff88; padding: 20px; border-radius: 15px; color: #e6edf3; font-style: italic; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.1); }
        .admin-panel { background: #1e2327; border: 1px dashed #00ff88; padding: 20px; border-radius: 12px; margin-bottom: 25px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔑 YÖNETİCİ PANELİ (KEY ÜRETİCİ) ---
    if st.session_state["is_admin"]:
        with st.expander("🛠️ ADMIN KEY YÖNETİM MERKEZİ"):
            st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
            st.subheader("🔑 Yeni VIP Üye Lisansı Oluştur")
            uye_ismi = st.text_input("Üye Adı Soyadı:")
            if st.button("Lisans Anahtarı Üret"):
                new_key = f"GAI-{int(time.time())}-{uye_ismi[:3].upper()}"
                st.code(new_key, language="text")
                st.success(f"{uye_ismi} için Key üretildi. Bu anahtarı üyeye ileterek terminali satabilirsiniz.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- ANA İÇERİK (SOL VE SAĞ) ---
    ana_sol, ana_sag = st.columns([3, 1])

    with ana_sol:
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            h_input = st.text_input("🔍 İncelemek İstediğiniz VIP Sembol:", value="ISCTR").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"

        try:
            # Veri Çekme
            ticker = yf.Ticker(sembol)
            df = ticker.history(period="6mo", interval="1d")
            
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                son_fiyat = float(df['Close'].iloc[-1])
                dunku_kapanis = float(df['Close'].iloc[-2])
                degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

                with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
                with c3: st.metric("GÜNLÜK FARK", f"%{degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

                # GRAFİK (20 GÜN - SİYAHSIZ)
                st.markdown(f"📈 **{h_input} - VIP 20 Günlük Trend Analizi**")
                st.area_chart(df['Close'].tail(20), color="#00ff88", height=280)

                # TEKNİK HESAPLAMALAR
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                diff = df['Close'].diff(); g = (diff.where(diff > 0, 0)).rolling(14).mean(); l = (-diff.where(diff < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (g/l))).iloc[-1]

                # ASİSTAN ANALİZİ (Kişiselleştirilmiş)
                st.markdown("### 🤵 Gürkan AI Kişisel Analist Notu")
                yorum = f"Dostum, **{h_input}** için yaptığım derin VIP taramada; "
                if rsi < 40:
                    yorum += "hissenin teknik olarak 'Dipte' olduğunu görüyorum. RSI seviyesi bir tepki yükselişini işaret ediyor."
                elif son_fiyat > ma20:
                    yorum += f"fiyatın {ma20:.2f} TL desteği üzerinde kalması harika. Trend iştahı %2+ hedef için uygun görünüyor."
                else:
                    yorum += "şu an biraz dinlenme modunda. MA20 seviyesini aşağı kırmadığı sürece panik yok, izlemeye devam."

                st.markdown(f'<div class="asistan-notu">{yorum}</div>', unsafe_allow_html=True)
        except:
            st.error("Veri hattı meşgul veya sembol hatalı.")

    with ana_sag:
        st.markdown("<h3 style='color:#00ff88; text-align:center;'>🚀 VIP RADAR</h3>", unsafe_allow_html=True)
        st.caption("Sabah %2+ Potansiyeli")
        
        vip_liste = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "TUPRS.IS", "SISE.IS", "KCHOL.IS", "AKBNK.IS"]
        bulunan = 0
        for r in vip_liste:
            if bulunan >= 5: break
            try:
                r_df = yf.download(r, period="10d", interval="1d", progress=False)
                if not r_df.empty:
                    if isinstance(r_df.columns, pd.MultiIndex): r_df.columns = r_df.columns.get_level_values(0)
                    son = r_df['Close'].iloc[-1]
                    if son > r_df['Close'].rolling(5).mean().iloc[-1]:
                        f = ((son - r_df['Close'].iloc[-2]) / r_df['Close'].iloc[-2]) * 100
                        st.markdown(f"""
                        <div class="radar-card">
                            <b style="color:#00ff88;">{r.split('.')[0]}</b> <span style="float:right; color:#00ff88;">%{f:.2f}</span><br>
                            <small style="color:#888;">AI Sinyali: %2+ HEDEF</small>
                        </div>
                        """, unsafe_allow_html=True)
                        bulunan += 1
            except: continue
        
        if st.button("🔄 Radarı Yenile", use_container_width=True): st.rerun()
