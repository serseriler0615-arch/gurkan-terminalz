# check_status fonksiyonunu şu şekilde güncelliyorum:
@st.cache_data(ttl=300)
def check_status(symbol):
    try:
        d = yf.download(symbol + ".IS", period="1mo", interval="1d", progress=False)
        if d.empty or len(d) < 14: return "🔍" # Veri yetersizse arama simgesi
        
        # RSI Hesapla
        delta = d['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Son değeri güvenli al
        last_gain = gain.iloc[-1]
        last_loss = loss.iloc[-1]
        
        if last_loss == 0: return "🟢" # Kayıp yoksa hisse çok güçlüdür
        
        rs = last_gain / last_loss
        rsi = 100 - (100 / (1 + rs))
        
        if rsi > 70: return "🔴" # RİSKLİ (Aşırı Alım)
        if rsi < 35: return "🟢" # FIRSAT (Aşırı Satım)
        return "🟡" # DENGELİ
    except: 
        return "⏳" # Hata anında bekleme simgesi
