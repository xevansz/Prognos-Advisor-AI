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
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function getSectionTitle(key: string): string {
  const titleMap: Record<string, string> = {
    summary_bullets: 'Key Insights',
    cashflow_section: 'Cash Flow Analysis',
    goals_section: 'Goal Progress',
    allocation_section: 'Investment Strategy',
    changes_since_last: 'Changes Since Last Report',
    markdown_body: 'Detailed Analysis',
    disclaimer: 'Disclaimer',
  }
  return titleMap[key] || key.replace(/_/g, ' ')
}

function renderValue(value: unknown, sectionKey: string): React.ReactNode {
  if (value === null || value === undefined) return null

  // Render markdown for text sections
  if (typeof value === 'string') {
    return (
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h2: ({ children }) => (
              <h2 className="text-xl font-semibold mt-6 mb-3">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg font-semibold mt-4 mb-2">{children}</h3>
            ),
            p: ({ children }) => (
              <p className="mb-3 leading-relaxed">{children}</p>
            ),
            ul: ({ children }) => (
              <ul className="list-disc pl-5 space-y-1 mb-3">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal pl-5 space-y-1 mb-3">{children}</ol>
            ),
            li: ({ children }) => (
              <li className="leading-relaxed">{children}</li>
            ),
            strong: ({ children }) => (
              <strong className="font-semibold text-foreground">
                {children}
              </strong>
            ),
            em: ({ children }) => <em className="italic">{children}</em>,
          }}
        >
          {value}
        </ReactMarkdown>
      </div>
    )
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return <span>{String(value)}</span>
  }

  if (Array.isArray(value)) {
    return (
      <ul className="list-disc pl-5 space-y-2">
        {value.map((item, i) => (
          <li key={i} className="leading-relaxed">
            {renderValue(item, sectionKey)}
          </li>
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
            {renderValue(v, k)}
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
  const generatedAt = new Date(
    prognosisReport.generated_at
  ).toLocaleDateString()

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
        <CardContent className="space-y-8">
          {Object.entries(report)
            .filter(([key]) => {
              // Exclude disclaimer (shown separately) and markdown_body (contains duplicates)
              return key !== 'disclaimer' && key !== 'markdown_body'
            })
            .map(([sectionKey, sectionValue]) => (
              <div
                key={sectionKey}
                className="border-b border-border/50 pb-6 last:border-0 last:pb-0"
              >
                <h3 className="text-lg font-semibold mb-4 text-foreground">
                  {getSectionTitle(sectionKey)}
                </h3>
                <div className="text-foreground/90">
                  {renderValue(sectionValue, sectionKey)}
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
