import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Stock } from '@/data/mockData';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StockSelectorProps {
  stocks: Stock[];
  selectedExchange: 'NASDAQ' | 'NEPSE';
  selectedStock: string;
  onExchangeChange: (exchange: 'NASDAQ' | 'NEPSE') => void;
  onStockChange: (symbol: string) => void;
  isLoading: boolean;
  prediction: number | null;
  lastClosePrice: number | null;
}

const StockSelector: React.FC<StockSelectorProps> = ({
  stocks,
  selectedExchange,
  selectedStock,
  onExchangeChange,
  onStockChange,
  isLoading,
  prediction,
  lastClosePrice
}) => {
  const filteredStocks = stocks.filter(stock => stock.exchange === selectedExchange);

  const isTrendingUp = prediction !== null && lastClosePrice !== null && prediction > lastClosePrice;
  const isTrendingDown = prediction !== null && lastClosePrice !== null && prediction < lastClosePrice;

  return (
    <div className="flex flex-wrap items-center gap-6">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-muted-foreground">Exchange:</span>
        <Select value={selectedExchange} onValueChange={onExchangeChange}>
          <SelectTrigger className="w-32 bg-secondary border-border">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="NASDAQ">NASDAQ</SelectItem>
            <SelectItem value="NEPSE">NEPSE</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-muted-foreground">Stock:</span>
        <Select value={selectedStock} onValueChange={onStockChange}>
          <SelectTrigger className="w-48 bg-secondary border-border">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {filteredStocks.map(stock => (
              <SelectItem key={stock.symbol} value={stock.symbol}>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{stock.symbol}</span>
                  <span className="text-xs text-muted-foreground truncate max-w-32">
                    {stock.name}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-6 ml-auto">
        {isLoading ? (
          <div className="text-right">
            <Skeleton className="h-7 w-24 mb-1" />
            <Skeleton className="h-5 w-32" />
          </div>
        ) : (
          <>
            {prediction !== null && (
              <div className="text-right">
                <div className="text-xs text-muted-foreground">Prediction</div>
                <div className={`flex items-center justify-end gap-1 text-lg font-bold ${
                  isTrendingUp ? 'text-bullish' : isTrendingDown ? 'text-bearish' : 'text-foreground'
                }`}>
                  {isTrendingUp && <TrendingUp className="h-4 w-4" />}
                  {isTrendingDown && <TrendingDown className="h-4 w-4" />}
                  <span>{prediction.toFixed(2)}</span>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default StockSelector;