"use client";
import { useState, useEffect } from "react";
import { getStockData } from "../services/api";
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

interface StockData {
  ticker: string;
  last_price: number;
  prediction: number;
  signal: string;
  change: number;
  history: { value: number }[];
}

export default function StockDashboard() {
  // Gunakan Array untuk menyimpan banyak data saham
  const [allData, setAllData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(false);

  // Daftar 10 Ticker yang ingin ditampilkan sekaligus
  const tickers = ["BBRI.JK", "GOTO.JK", "ANTM.JK", "TLKM.JK", "BMRI.JK", "ADRO.JK", "MEDC.JK", "ASII.JK", "BUKA.JK", "BBNI.JK"];

  const fetchAllPredictions = async () => {
    setLoading(true);
    const results: StockData[] = [];
    
    // Ambil data satu per satu dari API Python
    for (const ticker of tickers) {
      const res = await getStockData(ticker);
      if (res && !res.error) {
        results.push(res);
      }
    }
    setAllData(results);
    setLoading(false);
  };

  // Jalankan otomatis saat web dibuka pertama kali
  useEffect(() => {
    fetchAllPredictions();
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 p-8 text-slate-900">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-slate-800">Market Intelligence AI</h1>
          <button 
            onClick={fetchAllPredictions}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl font-semibold transition-all disabled:opacity-50"
          >
            {loading ? "Analysing All..." : "Update All Predictions"}
          </button>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr className="text-slate-500 text-xs uppercase tracking-wider">
                <th className="px-6 py-4">Asset</th>
                <th className="px-6 py-4">Current Price</th>
                <th className="px-6 py-4">AI Target</th>
                <th className="px-6 py-4">7D Trend</th>
                <th className="px-6 py-4 text-center">Recommendation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {/* Lakukan Map agar semua data di array muncul menjadi baris tabel */}
              {allData.map((item, index) => (
                <tr key={index} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-5 flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                      {item.ticker.substring(0,2)}
                    </div>
                    <span className="font-bold">{item.ticker}</span>
                  </td>
                  <td className="px-6 py-5 font-medium">Rp {item.last_price.toLocaleString('id-ID')}</td>
                  <td className={`px-6 py-5 font-bold ${item.change > 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    Rp {item.prediction.toLocaleString('id-ID')}
                  </td>
                  <td className="px-6 py-5 w-32 h-16">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={item.history}>
                        <Area 
                          type="monotone" 
                          dataKey="value" 
                          stroke={item.change > 0 ? "#10b981" : "#f43f5e"} 
                          fill={item.change > 0 ? "#d1fae5" : "#ffe4e6"} 
                          strokeWidth={2}
                          isAnimationActive={false}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </td>
                  <td className="px-6 py-5 text-center">
                    <span className={`px-4 py-1.5 rounded-lg text-xs font-black tracking-widest ${
                      item.signal === 'BUY' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                    }`}>
                      {item.signal}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {allData.length === 0 && !loading && (
            <div className="p-10 text-center text-slate-400">
              <td>
                Klik &quot;Update All Predictions&quot; untuk memuat data.
            </td>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
