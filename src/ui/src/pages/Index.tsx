import { useState, useEffect } from 'react';
import TradingHeader from '@/components/TradingHeader';
import StockSelector from '@/components/StockSelector';
import StockChart from '@/components/StockChart';
import ChartControls from '@/components/ChartControls';
import PredictionMethodology from '@/components/PredictionMethodology';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  stocks,
  fetchStockDetails,
  StockData,
  Stock,
  technicalIndicators as defaultIndicators
} from '@/data/mockData';
import { Activity } from 'lucide-react';

const Index = () => {
  const [selectedExchange, setSelectedExchange] = useState<'NASDAQ' | 'NEPSE'>('NASDAQ');
  const [selectedStock, setSelectedStock] = useState<string>('AAPL');
  const [indicators, setIndicators] = useState(defaultIndicators);
  const [chartData, setChartData] = useState<StockData[]>([]);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [currentStockDetails, setCurrentStockDetails] = useState<Stock | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStockData = async () => {
      if (!selectedStock) return;
      setIsLoading(true);
      const { chartData: data, prediction: pred } = await fetchStockDetails(selectedStock);
      setChartData(data);
      setPrediction(pred);

      if (data && data.length >= 2) {
        const latestData = data[data.length - 1];
        const previousData = data[data.length - 2];
        const staticInfo = stocks.find(s => s.symbol === selectedStock);
        const change = latestData.close - previousData.close;
        const changePercent = (change / previousData.close) * 100;
        setCurrentStockDetails({
          symbol: selectedStock,
          name: staticInfo?.name || '',
          exchange: staticInfo?.exchange || 'NASDAQ',
          currentPrice: latestData.close,
          change: change,
          changePercent: changePercent,
        });
      } else if (data && data.length === 1) {
        const staticInfo = stocks.find(s => s.symbol === selectedStock);
        setCurrentStockDetails({
           symbol: selectedStock,
           name: staticInfo?.name || '',
           exchange: staticInfo?.exchange || 'NASDAQ',
           currentPrice: data[0].close,
           change: 0,
           changePercent: 0,
       });
      }
      setIsLoading(false);
    };
    loadStockData();
  }, [selectedStock]);

  const handleIndicatorChange = (indicator: string, value: boolean) => {
    setIndicators(prev => ({ ...prev, [indicator]: value }));
  };

  const handleStockChange = (symbol: string) => {
    setSelectedStock(symbol);
  };

  const handleExchangeChange = (exchange: 'NASDAQ' | 'NEPSE') => {
    setSelectedExchange(exchange);
    const firstStock = stocks.find(s => s.exchange === exchange);
    if (firstStock) {
      setSelectedStock(firstStock.symbol);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6 space-y-6">
        <TradingHeader />
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <StockSelector
              stocks={stocks}
              selectedExchange={selectedExchange}
              selectedStock={selectedStock}
              onExchangeChange={handleExchangeChange}
              onStockChange={handleStockChange}
              isLoading={isLoading}
              prediction={prediction}
              lastClosePrice={currentStockDetails ? currentStockDetails.currentPrice : null}
            />
          </CardContent>
        </Card>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-foreground flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  Price Chart with AI Predictions
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center h-96 text-muted-foreground">
                    <p>Loading chart data for {selectedStock}...</p>
                  </div>
                ) : (
                  <StockChart data={chartData} indicators={indicators} />
                )}
              </CardContent>
            </Card>
          </div>
          <div className="lg:col-span-1">
            <ChartControls
              indicators={indicators}
              onIndicatorChange={handleIndicatorChange}
            />
          </div>
        </div>
        <PredictionMethodology />
      </div>
    </div>
  );
};

export default Index;