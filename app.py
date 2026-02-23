import streamlit as st
import yfinance as yf
import pandas as pd
import joblib

# 1. Judul Aplikasi
st.title("📈 AI Saham Predictor (BBCA)")

# 2. Fungsi Load Model
@st.cache_resource
def load_model():
    model = joblib.load("model_saham_bbca.pkl")
    scaler_x = joblib.load("scaler_x.pkl")
    scaler_y = joblib.load("scaler_y.pkl")
    return model, scaler_x, scaler_y

model, scaler_x, scaler_y = load_model()

# 3. Ambil Data Real-Time
ticker = "BBCA.JK"
data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)

# Jika kolom bertingkat (fitur yfinance 2026), ratakan:
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# 4. Feature Engineering (Minimalis)
data['MA5'] = data['Close'].rolling(window=5).mean()
data['MA20'] = data['Close'].rolling(window=20).mean()
data_clean = data.dropna()

# 5. Tampilan Dashboard
st.write(f"Harga Terakhir: **Rp {data_clean['Close'].iloc[-1]:,.0f}**")
st.line_chart(data_clean['Close'])

if st.button("Prediksi Harga Besok"):
    # Ambil baris terakhir sebagai input
    input_data = data_clean.iloc[-1:][['Open', 'High', 'Low', 'Close', 'Volume', 'MA5', 'MA20']]
    
    # Scaling & Predict
    input_scaled = scaler_x.transform(input_data)
    pred_scaled = model.predict(input_scaled)
    pred_real = scaler_y.inverse_transform(pred_scaled.reshape(-1, 1))
    
    st.metric("Estimasi Harga Besok", f"Rp {pred_real[0][0]:,.0f}")
