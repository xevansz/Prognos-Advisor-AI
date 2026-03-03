import React from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Button } from '../components/ui/button'
import { useApp } from '../context/AppContext'
import { Sparkles, AlertTriangle, Loader2 } from 'lucide-react'

function renderValue(value: unknown): React.ReactNode {
  if (value === null || value === undefined) return null
  if (
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return <span>{String(value)}</span>
  }
  if (Array.isArray(value)) {
    return (
      <ul className="list-disc pl-5 space-y-1">
        {value.map((item, i) => (
          <li key={i}>{renderValue(item)}</li>
        ))}
      </ul>
    )
  }
  if (typeof value === 'object') {
    return (
      <div className="space-y-2">
        {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
          <div key={k}>
            <span className="font-medium capitalize">
              {k.replace(/_/g, ' ')}:{' '}
            </span>
            {renderValue(v)}
          </div>
        ))}
      </div>
    )
  }
  return null
}

export function PrognosisAI() {
  const { prognosisReport, generatePrognosis, prognosisLoading } = useApp()
  const [genError, setGenError] = React.useState('')

  const handleGenerate = async () => {
    setGenError('')
    try {
      await generatePrognosis()
    } catch (err) {
      setGenError(
        err instanceof Error ? err.message : 'Failed to generate report.'
      )
    }
  }

  if (!prognosisReport) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="mb-2">Prognosis AI</h1>
          <p className="text-muted-foreground">
            AI-powered financial insights and forecasting
          </p>
        </div>

        <Card className="shadow-sm">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-full bg-primary/10 p-4 mb-6">
              <Sparkles className="h-12 w-12 text-primary" />
            </div>
            <h2 className="mb-3">Generate Your Financial Report</h2>
            <p className="text-muted-foreground mb-6 max-w-md">
              Get AI-powered insights, analysis, and recommendations based on
              your financial data. Our algorithm will analyze your accounts,
              transactions, and goals to provide personalized guidance.
            </p>
            {genError && (
              <p className="text-sm text-destructive mb-4">{genError}</p>
            )}
            <Button
              size="lg"
              onClick={handleGenerate}
              disabled={prognosisLoading}
            >
              {prognosisLoading ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Generating…
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5 mr-2" />
                  Generate Report
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const report = prognosisReport.report_json
  const generatedAt = new Date(prognosisReport.created_at).toLocaleDateString()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-2">Prognosis AI</h1>
          <p className="text-muted-foreground">
            Your personalized financial insights
          </p>
        </div>
        <Button onClick={handleGenerate} disabled={prognosisLoading}>
          {prognosisLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating…
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4 mr-2" />
              Regenerate Report
            </>
          )}
        </Button>
      </div>

      {genError && <p className="text-sm text-destructive">{genError}</p>}

      <Card className="shadow-sm border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Financial Analysis Report
          </CardTitle>
          <CardDescription>Generated on {generatedAt}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {Object.entries(report).map(([sectionKey, sectionValue]) => (
            <div key={sectionKey}>
              <h3 className="mb-3 capitalize">
                {sectionKey.replace(/_/g, ' ')}
              </h3>
              <div className="prose prose-sm max-w-none text-foreground">
                {renderValue(sectionValue)}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <Card className="shadow-sm border-warning/50 bg-warning/5">
        <CardContent className="flex gap-3 py-4">
          <AlertTriangle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-medium mb-1">Disclaimer</p>
            <p className="text-muted-foreground">
              This report is generated using automated algorithms based on your
              financial data. It should not be considered as professional
              financial advice. Always consult with a qualified financial
              advisor before making significant financial decisions. Past
              performance does not guarantee future results.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
