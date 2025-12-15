import React from 'react';
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Bar
} from 'recharts';
import { StockData } from '@/data/mockData';

interface StockChartProps {
  data: StockData[];
  indicators?: {
    sma?: boolean;
    rsi?: boolean;
    macd?: boolean;
    volume?: boolean;
  };
}

const calculateEMA = (data: number[], period: number): (number | null)[] => {
  const k = 2 / (period + 1);
  const emaArray: (number | null)[] = new Array(data.length).fill(null);
  if (data.length < period) return emaArray;
  let sum = 0;
  for (let i = 0; i < period; i++) sum += data[i];
  emaArray[period - 1] = sum / period;
  for (let i = period; i < data.length; i++) {
    emaArray[i] = (data[i] * k) + (emaArray[i - 1]! * (1 - k));
  }
  return emaArray;
};

const calculateRSI = (data: number[], period = 14): (number | null)[] => {
  const rsiArray: (number | null)[] = new Array(data.length).fill(null);
  if (data.length < period) return rsiArray;
  let gains = 0, losses = 0;
  for (let i = 1; i <= period; i++) {
    const diff = data[i] - data[i - 1];
    if (diff >= 0) gains += diff;
    else losses -= diff;
  }
  let avgGain = gains / period;
  let avgLoss = losses / period;
  rsiArray[period] = 100 - (100 / (1 + (avgGain / avgLoss)));
  for (let i = period + 1; i < data.length; i++) {
    const diff = data[i] - data[i - 1];
    const currentGain = diff >= 0 ? diff : 0;
    const currentLoss = diff < 0 ? -diff : 0;
    avgGain = ((avgGain * (period - 1)) + currentGain) / period;
    avgLoss = ((avgLoss * (period - 1)) + currentLoss) / period;
    rsiArray[i] = avgLoss === 0 ? 100 : 100 - (100 / (1 + avgGain / avgLoss));
  }
  return rsiArray;
};

const calculateMACD = (data: number[]) => {
  const ema12 = calculateEMA(data, 12);
  const ema26 = calculateEMA(data, 26);
  return ema12.map((val, i) => (val !== null && ema26[i] !== null ? val - ema26[i]! : null));
};

const StockChart: React.FC<StockChartProps> = ({ data, indicators = {} }) => {
  const { sma = false, rsi = false, macd = false, volume = false } = indicators;

  const processedData = React.useMemo(() => {
    const closePrices = data.map(d => d.close);
    const rsiValues = calculateRSI(closePrices);
    const macdValues = calculateMACD(closePrices);

    return data.map((item, index) => {
      let smaValue = null;
      if (index >= 19) {
        const sum = data.slice(index - 19, index + 1).reduce((acc, curr) => acc + curr.close, 0);
        smaValue = sum / 20;
      }
      return {
        ...item,
        sma: smaValue,
        rsi: rsiValues[index],
        macd: macdValues[index]
      };
    });
  }, [data]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;
    
    const date = new Date(label);
    const formattedDate = date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
    });

    const priceData = payload.filter((entry: any) => entry.dataKey !== 'volume');
    return (
      <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
        <p className="font-medium text-foreground">{formattedDate}</p>
        {priceData.map((entry: any, i: number) => {
          const displayName = entry.dataKey === 'close' ? 'Price' :
                                entry.dataKey === 'sma' ? 'SMA' :
                                entry.dataKey === 'rsi' ? 'RSI' :
                                entry.dataKey === 'macd' ? 'MACD' :
                                entry.dataKey === 'prediction' ? 'Prediction' : entry.dataKey;
          return <p key={i} style={{ color: entry.color }} className="text-sm">{`${displayName}: ${entry.value?.toFixed(2)}`}</p>;
        })}
      </div>
    );
  };

  const formatXAxis = (tickItem: string) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatYAxis = (tickItem: number) => {
    if (tickItem >= 1000000) return `${(tickItem / 1000000).toFixed(1)}M`;
    if (tickItem >= 1000) return `${(tickItem / 1000).toFixed(1)}k`;
    return tickItem.toString();
  };

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
          <XAxis 
            dataKey="timestamp" 
            stroke="hsl(var(--muted-foreground))" 
            fontSize={12}
            tickFormatter={formatXAxis} 
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))" 
            fontSize={12}
            domain={[dataMin => Math.floor(dataMin * 0.95), dataMax => Math.ceil(dataMax * 1.05)]}
            tickFormatter={formatYAxis}
          />
          <YAxis yAxisId="volume" orientation="right" hide={true} domain={[0, 'dataMax']} />
          <Tooltip content={<CustomTooltip />} />

          {volume && <Bar dataKey="volume" fill="hsl(var(--volume))" opacity={0.3} yAxisId="volume" />}
          <Line type="monotone" dataKey="close" stroke="hsl(var(--foreground))" strokeWidth={2} dot={false} activeDot={{ r: 4, stroke: "hsl(var(--primary))", strokeWidth: 2 }} />
          <Line type="monotone" dataKey="prediction" stroke="hsl(var(--prediction))" strokeWidth={2} strokeDasharray="5 5" dot={false} activeDot={{ r: 4, stroke: "hsl(var(--prediction))", strokeWidth: 2 }} />
          {sma && <Line type="monotone" dataKey="sma" stroke="hsl(var(--bullish))" strokeWidth={1.5} dot={false} connectNulls={false} />}
          {rsi && <Line type="monotone" dataKey="rsi" stroke="hsl(var(--accent))" strokeWidth={1.5} dot={false} connectNulls={false} />}
          {macd && <Line type="monotone" dataKey="macd" stroke="hsl(var(--prediction))" strokeWidth={1.5} dot={false} connectNulls={false} />}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockChart;
