export interface StockData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockDetails {
  chartData: StockData[];
  prediction: number | null;
}

export interface Stock {
  symbol: string;
  name: string;
  exchange: 'NASDAQ' | 'NEPSE';
  currentPrice: number;
  change: number;
  changePercent: number;
}

export const stocks: Stock[] = [
  { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ', currentPrice: 185.23, change: 2.45, changePercent: 1.34 },
  { symbol: 'TSLA', name: 'Tesla Inc.', exchange: 'NASDAQ', currentPrice: 248.67, change: -5.12, changePercent: -2.02 },
  { symbol: 'NVDA', name: 'NVIDIA Corporation', exchange: 'NASDAQ', currentPrice: 875.45, change: 15.23, changePercent: 1.77 },
  { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ', currentPrice: 412.58, change: 3.67, changePercent: 0.90 },
  { symbol: 'NABIL', name: 'Nabil Bank Limited', exchange: 'NEPSE', currentPrice: 1250.00, change: 25.00, changePercent: 2.04 },
  { symbol: 'CIT', name: 'Citizen Investment Trust', exchange: 'NEPSE', currentPrice: 2200.00, change: -15.00, changePercent: -0.68 },
  { symbol: 'GBIME', name: 'Global IME Bank Ltd.', exchange: 'NEPSE', currentPrice: 550.00, change: 5.50, changePercent: 1.01 },
  { symbol: 'EBL', name: 'Everest Bank Limited', exchange: 'NEPSE', currentPrice: 780.00, change: -10.00, changePercent: -1.27 },
  { symbol: 'HIDCL', name: 'Hydropower Investment & Dev.', exchange: 'NEPSE', currentPrice: 210.00, change: 2.10, changePercent: 1.01 }
];

export const fetchStockDetails = async (symbol: string): Promise<StockDetails> => {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:30080';

  try {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol.toUpperCase()}`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to fetch data: ${response.statusText}`);
    }

    const data = await response.json();

    return {
      chartData: data.chartData as StockData[],
      prediction: data.prediction as number | null,
    };

  } catch (error) {
    console.error(`Failed to fetch details for ${symbol}:`, error);
    return {
      chartData: [],
      prediction: null,
    };
  }
};

export const technicalIndicators = {
  sma: true,
  rsi: false,
  macd: false,
  volume: false, // default OFF
};