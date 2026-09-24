import React from 'react';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Activity, Zap, BarChart3 } from 'lucide-react';

interface ChartControlsProps {
  indicators: {
    sma: boolean;
    rsi: boolean;
    macd: boolean;
    volume: boolean;
  };
  onIndicatorChange: (indicator: keyof ChartControlsProps['indicators'], value: boolean) => void;
}

const ChartControls: React.FC<ChartControlsProps> = ({ indicators, onIndicatorChange }) => {
  const indicatorsList = [
    {
      key: 'sma' as const,
      label: 'Simple Moving Average',
      description: '20-period SMA for trend analysis',
      icon: <TrendingUp className="h-4 w-4" />,
      color: 'hsl(var(--bullish))'
    },
    {
      key: 'rsi' as const,
      label: 'RSI',
      description: 'Relative Strength Index (14-period)',
      icon: <Zap className="h-4 w-4" />,
      color: 'hsl(var(--accent))'
    },
    {
      key: 'macd' as const,
      label: 'MACD',
      description: 'Moving Average Convergence Divergence',
      icon: <Activity className="h-4 w-4" />,
      color: 'hsl(var(--prediction))'
    },
    {
      key: 'volume' as const,
      label: 'Volume',
      description: 'Trading volume overlay',
      icon: <BarChart3 className="h-4 w-4" />,
      color: 'hsl(var(--volume))'
    }
  ];

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-foreground flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          Technical Indicators
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {indicatorsList.map((indicator) => (
          <div key={indicator.key} className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors">
            <div className="flex items-center gap-3">
              <div style={{ color: indicator.color }}>
                {indicator.icon}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-foreground">{indicator.label}</span>
                  {indicators[indicator.key] && (
                    <Badge variant="secondary" className="text-xs bg-primary/20 text-primary">
                      Active
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{indicator.description}</p>
              </div>
            </div>
            <Switch
              checked={indicators[indicator.key]}
              onCheckedChange={(value) => onIndicatorChange(indicator.key, value)}
            />
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

export default ChartControls;
