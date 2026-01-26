import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. VIP GİRİŞ SİSTEMİ ---
def check_password():
    def password_entered():
        # Belirlediğimiz yeni bilgiler: ID: GURKAN | Şifre: Hedef2024!
        if st.session_state["username"].upper() == "GURKAN" and st.session_state["password"] == "Hedef2024!":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Profesyonel Giriş Ekranı
        st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: #00ff88; margin-bottom: 0;'>Gürkan AI VIP Terminal</h1>
                <p style='color: #888; font-size: 18px;'>⚠️ Bu Terminal Gürkan AI VIP Üyelik Gerektirir</p>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 1.5, 1])
        with cols[1]:
            st.text_input("VIP Kullanıcı Kimliği", key="username")
            st.text_input("Erişim Şifresi", type="password", key="password")
            st.button("Sisteme Güvenli Giriş Yap", on_click=password_entered, use_container_width=True)
            st.markdown("<p style='text-align: center; color: #555; font-size: 12px; margin-top: 20px;'>© 2024 Gürkan AI Financial Systems. Tüm Hakları Saklıdır.</p>", unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌ Yetkisiz Erişim! Lütfen VIP bilgilerinizi kontrol edin.")
        return False
    else:
        return True

# Giriş başarılıysa ana uygulamayı çalıştır
if check_password():
    st.set_page_config(page_title="Gürkan AI - VIP Terminal", layout="wide", initial_sidebar_state="collapsed")

    # Stil Ayarları
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        header {visibility: hidden;}
        div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
        .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; }
        .vip-box { background: linear-gradient(90deg, #1c2128 0%, #0d1117 100%); border: 1px solid #00ff88; padding: 15px; border-radius: 12px; color: #e6edf3; }
        </style>
        """, unsafe_allow_html=True)

    ana_sol, ana_sag = st.columns([3, 1])

    with ana_sol:
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            h_input = st.text_input("🔍 VIP Sembol Sorgula:", value="ISCTR").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"

        try:
            df = yf.download(sembol, period="3mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                son_fiyat = float(df['Close'].iloc[-1])
                with c2: st.metric("CANLI FİYAT", f"{son_fiyat:.2f} TL")
                with c3: st.metric("GÜNLÜK FARK", f"%{((son_fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100:.2f}")

                st.write(f"📈 **{h_input} VIP Teknik Projeksiyon**")
                st.area_chart(df['Close'].tail(20), color="#00ff88", height=250)

                # ASİSTAN YORUMU
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                st.markdown(f'<div class="vip-box">🤵 <b>VIP Analist Notu:</b> {h_input} analizi tamamlandı. Hisse şu an {son_fiyat:.2f} seviyesinde dengeleniyor. Kısa vadeli güven bölgesi {ma20:.2f} TL üzeridir.</div>', unsafe_allow_html=True)
        except: st.error("VIP Veri Hattı Bağlantı Hatası.")

    with ana_sag:
        st.markdown("<h3 style='color:#00ff88; text-align:center;'>🚀 VIP POTANSİYEL</h3>", unsafe_allow_html=True)
        # Genişletilmiş VIP Tarama Listesi
        vip_liste = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS", "SISE.IS", "KCHOL.IS", "TUPRS.IS", "AKBNK.IS", "GARAN.IS", "EKGYO.IS", "PETKM.IS"]
        bulunan = 0
        
        for r in vip_liste:
            if bulunan >= 5: break
            try:
                r_df = yf.download(r, period="10d", interval="1d", progress=False)
                if not r_df.empty:
                    if isinstance(r_df.columns, pd.MultiIndex): r_df.columns = r_df.columns.get_level_values(0)
                    if r_df['Close'].iloc[-1] > r_df['Close'].rolling(5).mean().iloc[-1]:
                        fark = ((r_df['Close'].iloc[-1] - r_df['Close'].iloc[-2]) / r_df['Close'].iloc[-2]) * 100
                        st.markdown(f"""<div class="radar-card"><b style='color:#00ff88;'>{r.split('.')[0]}</b> <span style='float:right;'>%{fark:.2f}</span><br><small>Sinyal: %2+ POTANSİYEL</small></div>""", unsafe_allow_html=True)
                        bulunan += 1
            except: continue
        
        if st.button("🔄 VIP Radarı Güncelle", use_container_width=True): st.rerun()
