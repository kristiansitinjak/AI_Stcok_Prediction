from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import yfinance as yf
import pandas as pd
import os
import numpy as np

app = FastAPI()

# 1. Konfigurasi CORS agar bisa diakses oleh Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder tempat menyimpan 10 model .pkl Anda
MODEL_DIR = "Models"

@app.get("/predict/{ticker}")
def get_prediction(ticker: str):
    try:
        # A. Validasi keberadaan file model
        model_path = f"{MODEL_DIR}/model_{ticker}.pkl"
        if not os.path.exists(model_path):
            return {"error": f"Model untuk {ticker} tidak ditemukan di folder {MODEL_DIR}"}

        # B. Load Model & Scaler sesuai Ticker
        model = joblib.load(model_path)
        scaler_x = joblib.load(f"{MODEL_DIR}/scaler_x_{ticker}.pkl")
        scaler_y = joblib.load(f"{MODEL_DIR}/scaler_y_{ticker}.pkl")
        
        # C. Ambil data pasar terbaru (60 hari terakhir)
        data = yf.download(ticker, period="60d", interval="1d", auto_adjust=True, timeout=20)
        
        if data.empty:
            return {"error": f"Gagal mengambil data pasar untuk {ticker}"}

        # Bersihkan MultiIndex jika ada (fitur yfinance terbaru)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        # D. Feature Engineering (Sama dengan saat training)
        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        
        # Ambil baris terakhir yang sudah lengkap datanya
        df_clean = data.dropna()
        if df_clean.empty:
            return {"error": "Data historis tidak cukup untuk menghitung indikator (MA5/MA20)"}
            
        last_row = df_clean.iloc[-1:][['Open', 'High', 'Low', 'Close', 'Volume', 'MA5', 'MA20']]
        
        # E. Prediksi
        input_scaled = scaler_x.transform(last_row)
        pred_scaled = model.predict(input_scaled)
        pred_real = scaler_y.inverse_transform(pred_scaled.reshape(-1, 1))
        
        last_close = float(data['Close'].iloc[-1])
        predicted_val = float(pred_real[0][0])
        
        # F. Ambil 7 Data Terakhir untuk Grafik (Sparkline)
        # Kita ambil harga 'Close' 7 hari terakhir untuk ditampilkan di web
        history_data = data['Close'].tail(7).tolist()
        formatted_history = [{"value": round(h, 2)} for h in history_data]
        
        # G. Hitung Persentase Perubahan
        price_change_pct = ((predicted_val - last_close) / last_close) * 100
        
        return {
            "ticker": ticker,
            "last_price": round(last_close, 2),
            "prediction": round(predicted_val, 2),
            "change": round(predicted_val - last_close, 2),
            "change_pct": round(price_change_pct, 2),
            "signal": "BUY" if predicted_val > last_close else "SELL",
            "history": formatted_history
        }

    except Exception as e:
        return {"error": f"Terjadi kesalahan internal: {str(e)}"}

@app.get("/")
def root():
    return {"message": "AI Stock API is Running and Ready!"}
