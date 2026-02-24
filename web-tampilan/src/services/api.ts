const API_BASE_URL = "http://127.0.0.1:8000";

export const getStockData = async (ticker: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/predict/${ticker}`);
    if (!response.ok) throw new Error("Gagal mengambil data");
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};
