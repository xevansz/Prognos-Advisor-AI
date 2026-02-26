import { Link } from "react-router";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Wallet,
  TrendingUp,
  PieChart,
  Target,
  Shield,
  ArrowRight,
  ClipboardList,
  BarChart2,
  BrainCircuit,
} from "lucide-react";

export function Landing() {
  const features = [
    {
      icon: PieChart,
      title: "Smart Analytics",
      description: "Visualize spending patterns with beautiful charts",
    },
    {
      icon: Target,
      title: "Goal Tracking",
      description: "Set and achieve financial goals with progress tracking",
    },
    {
      icon: TrendingUp,
      title: "AI Prognosis",
      description: "Personalized financial recommendations powered by AI",
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your financial data is encrypted and protected",
    },
  ];

  const steps = [
    {
      icon: ClipboardList,
      step: "01",
      title: "Add your accounts",
      description:
        "Connect your bank accounts, savings, and investments in one place.",
    },
    {
      icon: BarChart2,
      step: "02",
      title: "Track transactions",
      description: "Log income and expenses. Set budgets and financial goals.",
    },
    {
      icon: BrainCircuit,
      step: "03",
      title: "Get AI insights",
      description:
        "Prognosis AI analyses your data and recommends your next move.",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 w-full border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-primary p-2">
                <Wallet className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-semibold">Prognosis AI</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm tracking-wide text-muted-foreground hidden sm:block">
                Live • Work • Build
              </span>
              <Button size="sm" asChild>
                <Link to="/login">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex items-center min-h-[calc(100vh-4rem)]">
        <div className="mx-auto max-w-6xl w-full px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center space-y-7 max-w-3xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.1]">
              Your finances,{" "}
              <span className="bg-gradient-to-r from-primary to-chart-2 bg-clip-text text-transparent">
                finally clear.
              </span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Prognosis AI combines smart tracking, goal planning, and
              AI-powered insights — so you always know where you stand.
            </p>
            <div className="flex items-center justify-center gap-3 pt-2">
              <Button size="lg" asChild>
                <Link to="/signup">
                  Start for free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link to="/login">Sign in</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-border bg-card/40 py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-2xl font-semibold mb-12 text-muted-foreground tracking-wide uppercase text-sm">
            How it works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {steps.map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.step} className="flex flex-col items-start gap-3">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-muted-foreground/60">
                      {s.step}
                    </span>
                    <div className="h-9 w-9 rounded-md bg-primary/10 flex items-center justify-center">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <h3 className="font-semibold text-lg">{s.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {s.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-3 mb-14">
            <h2 className="text-3xl md:text-4xl font-bold">
              Built for clarity
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Every feature is designed to reduce noise and help you focus on
              what matters.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card
                  key={index}
                  className="shadow-sm hover:shadow-md transition-shadow border-border/60"
                >
                  <CardHeader className="space-y-3 pb-3">
                    <div className="h-10 w-10 rounded-md bg-primary/10 flex items-center justify-center">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-base">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <CardDescription className="text-sm leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="justify-center gap-4">
            <p className="text-xs text-muted-foreground">
              © 2026 Prognosis AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
