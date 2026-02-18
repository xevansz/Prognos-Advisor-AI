import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useApp } from '../context/AppContext';
import { Sparkles, AlertTriangle } from 'lucide-react';

export function PrognosisAI() {
  const { prognosisReport, generatePrognosis } = useApp();

  if (!prognosisReport) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="mb-2">Prognosis AI</h1>
          <p className="text-muted-foreground">AI-powered financial insights and forecasting</p>
        </div>

        <Card className="shadow-sm">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-full bg-primary/10 p-4 mb-6">
              <Sparkles className="h-12 w-12 text-primary" />
            </div>
            <h2 className="mb-3">Generate Your Financial Report</h2>
            <p className="text-muted-foreground mb-6 max-w-md">
              Get AI-powered insights, analysis, and recommendations based on your financial data. 
              Our algorithm will analyze your accounts, transactions, and goals to provide personalized guidance.
            </p>
            <Button size="lg" onClick={generatePrognosis}>
              <Sparkles className="h-5 w-5 mr-2" />
              Generate Report
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Parse the mock report to display sections
  const sections = prognosisReport.split('\n\n');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-2">Prognosis AI</h1>
          <p className="text-muted-foreground">Your personalized financial insights</p>
        </div>
        <Button onClick={generatePrognosis}>
          <Sparkles className="h-4 w-4 mr-2" />
          Regenerate Report
        </Button>
      </div>

      <Card className="shadow-sm border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Financial Analysis Report
          </CardTitle>
          <CardDescription>Generated on {new Date().toLocaleDateString()}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {sections.map((section, index) => {
            const lines = section.split('\n');
            const heading = lines[0].replace(/\*\*/g, '');
            const content = lines.slice(1).join('\n');

            return (
              <div key={index}>
                {heading && (
                  <h3 className="mb-3">{heading}</h3>
                )}
                <div className="prose prose-sm max-w-none text-foreground">
                  {content.split('\n').map((line, i) => {
                    if (line.startsWith('•')) {
                      return (
                        <div key={i} className="flex gap-2 mb-2">
                          <span className="text-primary mt-1">•</span>
                          <span>{line.substring(1).trim()}</span>
                        </div>
                      );
                    }
                    if (line.trim().match(/^\d+\./)) {
                      return (
                        <p key={i} className="mb-2 pl-4">
                          {line}
                        </p>
                      );
                    }
                    if (line.trim()) {
                      return <p key={i} className="mb-3">{line}</p>;
                    }
                    return null;
                  })}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <Card className="shadow-sm border-warning/50 bg-warning/5">
        <CardContent className="flex gap-3 py-4">
          <AlertTriangle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-medium mb-1">Disclaimer</p>
            <p className="text-muted-foreground">
              This report is generated using automated algorithms based on your financial data. 
              It should not be considered as professional financial advice. Always consult with a 
              qualified financial advisor before making significant financial decisions. Past 
              performance does not guarantee future results.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
