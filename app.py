import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. SÜRE VE KEY KONTROL SİSTEMİ ---
def validate_key(key_input):
    try:
        # Key formatı: GAI-URETIM-GUN-ISIM
        parts = key_input.split("-")
        if len(parts) < 4: return False, None
        
        gun_sayisi = int(parts[2])
        
        # Eğer bu key ilk kez giriliyorsa bitiş tarihini şimdi tanımla
        if "bitis_tarihi" not in st.session_state:
            st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=gun_sayisi)
        
        simdi = datetime.now()
        if simdi < st.session_state["bitis_tarihi"]:
            return True, st.session_state["bitis_tarihi"]
        else:
            return "expired", None
    except:
        return False, None

# --- 2. GİRİŞ EKRANI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP Giriş", layout="centered")
    st.markdown("<h1 style='text-align:center; color:#00ff88;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💎 VIP KEY AKTİVASYON", "🔐 ADMIN GİRİŞİ"])
    
    with tab1:
        v_key = st.text_input("VIP Lisans Anahtarınız", placeholder="GAI-XXXX-XXXX")
        st.caption("Keyinizi girdiğiniz an süreniz otomatik olarak başlar.")
        if st.button("Sistemi Aktive Et"):
            status, bitis = validate_key(v_key)
            if status == True:
                st.session_state["access_granted"] = True
                st.session_state["role"] = "user"
                st.success(f"Hoş geldiniz! Süreniz Başladı. Bitiş: {bitis.strftime('%d/%m/%Y %H:%M')}")
                time.sleep(1.5)
                st.rerun()
            elif status == "expired":
                st.error("❌ Bu lisansın süresi dolmuş!")
            else:
                st.error("❌ Geçersiz Key!")

    with tab2:
        u = st.text_input("Yönetici ID")
        p = st.text_input("Yönetici Şifre", type="password")
        if st.button("Yönetici Girişi"):
            if u.upper() == "GURKAN" and p == "HEDEF2024!":
                st.session_state["access_granted"] = True
                st.session_state["role"] = "admin"
                st.rerun()
            else:
                st.error("Hatalı Bilgi!")
    st.stop()

# --- 3. ANA TERMİNAL (BURASI TÜM GÖRSELLERİ İÇERİR) ---
st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide")

# CSS: Tüm Siyahlık ve Renk Sorunlarını Çözer
st.markdown("""
    <style>
    .stApp { background-color: #0d1117 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .radar-card { background-color: #161b22; border-left: 5px solid #00ff88; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #30363d; }
    .asistan-box { background: #1c2128; border: 1px solid #00ff88; padding: 20px; border-radius: 15px; margin-top: 10px; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# ÜST BİLGİ VE ADMIN PANELİ
if st.session_state["role"] == "admin":
    with st.expander("🛠️ ADMIN KEY MERKEZİ"):
        c1, c2 = st.columns(2)
        u_ad = c1.text_input("Üye Adı:")
        l_sure = c2.selectbox("Süre:", [1, 7, 30, 365], format_func=lambda x: f"{x} Gün")
        if st.button("Bekleyen Key Üret"):
            generated = f"GAI-{int(time.time())}-{l_sure}-{u_ad[:3].upper()}"
            st.code(generated)
            st.info("Bu key girildiği an süreyi başlatacaktır.")

# --- TERMİNAL İÇERİĞİ ---
sol, sag = st.columns([3, 1])

with sol:
    if st.session_state["role"] == "user":
        st.warning(f"🔔 VIP Üyeliğiniz Aktif. Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    
    st.title("📈 VIP Analiz Paneli")
    h_input = st.text_input("🔍 Hisse Sembolü (Örn: THYAO):", value="ISCTR").upper()
    
    try:
        sembol = h_input if "." in h_input else h_input + ".IS"
        df = yf.download(sembol, period="1mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            fiyat = float(df['Close'].iloc[-1])
            
            # Metrikler
            m1, m2 = st.columns(2)
            m1.metric("GÜNCEL FİYAT", f"{fiyat:.2f} TL")
            m2.metric("GÜNLÜK DEĞİŞİM", f"%{((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100:.2f}")
            
            # Grafik
            st.area_chart(df['Close'].tail(20), color="#00ff88")
            
            # Asistan Notu
            st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88;'>🤵 VIP Asistan Notu:</b><br>
                    {h_input} analizi tamamlandı. Teknik radar {fiyat:.2f} seviyesini destekliyor.
                </div>
            """, unsafe_allow_html=True)
    except: st.error("Veri alınamadı.")

with sag:
    st.markdown("<h3 style='color:#00ff88; text-align:center;'>🚀 VIP RADAR</h3>", unsafe_allow_html=True)
    for r in ["THYAO.IS", "ASELS.IS", "EREGL.IS", "SASA.IS", "TUPRS.IS"]:
        st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{r.split('.')[0]}</b><br>Sinyal: %2+ Potansiyel</div>", unsafe_allow_html=True)

if st.button("Sistemden Güvenli Çıkış"):
    st.session_state.clear()
    st.rerun()
