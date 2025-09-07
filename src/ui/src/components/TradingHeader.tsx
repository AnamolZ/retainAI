import React from 'react';
import { Card } from '@/components/ui/card';
import { TrendingUp } from 'lucide-react';

const TradingHeader: React.FC = () => {
  return (
    <Card className="bg-card border-border p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-muted-foreground mt-2">
            Professional stock analysis with advanced prediction algorithms
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 bg-bullish rounded-full animate-pulse"></div>
            </div>
          </div>
          
          <div className="text-right">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-prediction" />
              <span className="text-sm font-medium text-prediction">Active</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default TradingHeader;