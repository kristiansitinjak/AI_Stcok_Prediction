import streamlit as st
import yfinance as yf
import pandas as pd
import joblib
import os
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="AI Day Trading Predictor", layout="wide")
st.title("🚀 AI Multi-Stock Day Trading Predictor (2026)")

# 1. Daftar 10 Saham Day Trading
dict_saham = {
    "Bank Rakyat Indonesia (BBRI)": "BBRI.JK",
    "GoTo Gojek Tokopedia (GOTO)": "GOTO.JK",
    "Aneka Tambang (ANTM)": "ANTM.JK",
    "Adaro Energy (ADRO)": "ADRO.JK",
    "Telkom Indonesia (TLKM)": "TLKM.JK",
    "Medco Energi (MEDC)": "MEDC.JK",
    "Bank Mandiri (BMRI)": "BMRI.JK",
    "Astra International (ASII)": "ASII.JK",
    "Bukalapak (BUKA)": "BUKA.JK",
    "Bank Negara Indonesia (BBNI)": "BBNI.JK"
}

# 2. Sidebar untuk Pilih Saham
st.sidebar.header("Pilih Saham Trading")
selected_stock = st.sidebar.selectbox("Pilih Emiten:", list(dict_saham.keys()))
ticker = dict_saham[selected_stock]

# 3. Fungsi Load Model & Scaler Secara Dinamis
@st.cache_resource
def load_stock_assets(ticker_code):
    model_path = f"Models/model_{ticker_code}.pkl"
    sx_path = f"Models/scaler_x_{ticker_code}.pkl"
    sy_path = f"Models/scaler_y_{ticker_code}.pkl"
    
    # Cek apakah file ada
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        scaler_x = joblib.load(sx_path)
        scaler_y = joblib.load(sy_path)
        return model, scaler_x, scaler_y
    else:
        return None, None, None

model, scaler_x, scaler_y = load_stock_assets(ticker)

# 4. Ambil Data Pasar Terbaru (Real-Time 2026)
if model:
    with st.spinner(f'Mengambil data {ticker}...'):
        data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

    # Preprocessing (Sesuai dengan Step 1 di Colab)
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data_clean = data.dropna()

    # Tampilan Dashboard
    last_price = data_clean['Close'].iloc[-1]
    st.subheader(f"Analisis Teknikal: {selected_stock}")
    
    col1, col2 = st.columns(2)
    col1.metric("Harga Terakhir", f"Rp {last_price:,.0f}")
    col2.write(f"Waktu Lokal: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.line_chart(data_clean['Close'])

    # 5. Eksekusi Prediksi
    if st.button(f"Prediksi Harga {ticker} Besok"):
        # Ambil fitur terakhir: Open, High, Low, Close, Volume, MA5, MA20
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA5', 'MA20']
        input_data = data_clean.iloc[-1:][features]
        
        # Scaling & Predict
        input_scaled = scaler_x.transform(input_data)
        pred_scaled = model.predict(input_scaled)
        pred_real = scaler_y.inverse_transform(pred_scaled.reshape(-1, 1))
        
        # Hasil
        predicted_price = pred_real[0][0]
        diff = predicted_price - last_price
        
        st.divider()
        res1, res2 = st.columns(2)
        res1.metric("Target Harga Besok", f"Rp {predicted_price:,.0f}", f"{diff:,.0f}")
        
        if diff > 0:
            st.success(f"Sinyal {ticker}: POTENSI NAIK (Bullish)")
        else:
            st.warning(f"Sinyal {ticker}: POTENSI TURUN (Bearish)")
else:
    st.error(f"Model untuk {ticker} belum ditemukan di folder Models!")

st.info("Disclaimer: Gunakan prediksi AI ini hanya sebagai referensi tambahan, bukan satu-satunya dasar keputusan trading.")
