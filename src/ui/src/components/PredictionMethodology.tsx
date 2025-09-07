import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, TrendingUp, Shield, Target, Database, Zap, GitBranch, Server } from 'lucide-react';

type Feature = {
  icon: React.ReactNode;
  title: string;
  description: string;
};

const features: Feature[] = [
  {
    icon: <Brain className="h-5 w-5 text-prediction" />,
    title: 'Machine Learning',
    description: 'LSTM neural networks trained on historical data.',
  },
  {
    icon: <TrendingUp className="h-5 w-5 text-bullish" />,
    title: 'Technical Analysis',
    description: 'Multiple indicators for trend identification.',
  },
  {
    icon: <Shield className="h-5 w-5 text-volume" />,
    title: 'Risk Assessment',
    description: 'Confidence intervals and volatility analysis.',
  },
  {
    icon: <Target className="h-5 w-5 text-accent" />,
    title: 'High Accuracy',
    description: '75-85% directional accuracy on predictions.',
  },
];

const FeatureCard: React.FC<{ feature: Feature }> = ({ feature }) => (
  <Card className="bg-secondary/50 border-border hover:border-primary/50 hover:bg-secondary transition-all duration-300 transform hover:-translate-y-1">
    <CardContent className="p-4">
      <div className="flex items-center gap-3 mb-2">
        {feature.icon}
        <h3 className="font-semibold text-foreground">{feature.title}</h3>
      </div>
      <p className="text-sm text-muted-foreground">{feature.description}</p>
    </CardContent>
  </Card>
);

const PredictionMethodology: React.FC = () => {
  const readmeContent = `
RetainAI is a sophisticated, cloud-native pipeline that fully automates stock price prediction for both the **NASDAQ** and **NEPSE** exchanges. Orchestrated by Kubernetes, its architecture combines containerized services to create a robust, end-to-end MLOps workflow designed for scalability and continuous adaptation.

At its core, a **FastAPI** application serves as the operational brain, managing the entire machine learning lifecycle. It is supported by **Redis** for high-speed model and prediction caching, and **PostgreSQL** for persistent, long-term storage of historical stock data. The result is a fully automated and adaptive system for real-time financial forecasting.

`;

  const parseMarkdown = (content: string) => {
    let html = content.trim();

    html = html.replace(/```mermaid([\s\S]*?)```/g, (match, code) => {
        const escapedCode = code.trim().replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return `\n<div class="bg-card border border-border rounded-lg p-4 my-6"><pre class="bg-transparent p-0 m-0"><code class="font-mono text-sm text-secondary-foreground">${escapedCode}</code></pre></div>\n`;
    });

    const blocks = html.split('\n\n');

    return blocks.map(block => {
        if (block.startsWith('<div>')) return block;
        if (block.startsWith('## ')) return `<h2 class="text-2xl font-bold text-foreground border-b border-border pb-2 mb-4 mt-6">${block.substring(3)}</h2>`;
        if (block.startsWith('### ')) return `<h3 class="text-xl font-semibold text-foreground mb-3 mt-4">${block.substring(4)}</h3>`;
        if (block.startsWith('---')) return '<hr class="my-8 border-border" />';

        let processedBlock = block
            .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-primary">$1</strong>');

        if (processedBlock.match(/^(\d+\.|-)\s/m)) {
            const listItems = processedBlock.split('\n').map(item => {
                let content = item.replace(/^(\d+\.|\-)\s/, '');
                return `<li class="text-muted-foreground mb-2 ml-4 flex items-start"><span class="text-primary mr-3 mt-1">•</span><span>${content}</span></li>`;
            }).join('');
            return `<ul class="list-none p-0">${listItems}</ul>`;
        }
        
        return `<p class="text-muted-foreground leading-relaxed">${processedBlock}</p>`;
    }).join('');
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {features.map((feature) => (
          <FeatureCard key={feature.title} feature={feature} />
        ))}
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-foreground flex items-center gap-3">
            {/* <GitBranch className="h-7 w-7 text-primary" /> */}
            {/* Retain AI <Badge className="bg-accent/10 text-accent">v1.0</Badge> */}
          </CardTitle>
           <p className="text-muted-foreground pt-1">An inside look at our automated MLOps pipeline and prediction engine.</p>
        </CardHeader>
        <CardContent>
          <div
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: parseMarkdown(readmeContent) }}
          />
        </CardContent>
      </Card>
    </div>
  );
};

export default PredictionMethodology;
