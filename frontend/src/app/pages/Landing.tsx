import { Link } from 'react-router';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Wallet, TrendingUp, PieChart, Target, Shield, Sparkles, ArrowRight } from 'lucide-react';
import { useApp } from '../context/AppContext';

export function Landing() {
  const { theme, toggleTheme } = useApp();

  const features = [
    {
      icon: PieChart,
      title: 'Smart Analytics',
      description: 'Visualize your spending patterns with beautiful charts and insights',
    },
    {
      icon: Target,
      title: 'Goal Tracking',
      description: 'Set and achieve your financial goals with intelligent progress tracking',
    },
    {
      icon: TrendingUp,
      title: 'AI Prognosis',
      description: 'Get personalized financial recommendations powered by AI',
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description: 'Your financial data is encrypted and protected at all times',
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 w-full border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-primary p-2">
                <Wallet className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-semibold">FinanceHub</span>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" asChild>
                <Link to="/login">Login</Link>
              </Button>
              <Button size="sm" asChild>
                <Link to="/signup">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/50 text-sm font-medium">
            <Sparkles className="h-4 w-4" />
            Modern Finance Management
          </div>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight max-w-4xl mx-auto">
            Take Control of Your{' '}
            <span className="bg-gradient-to-r from-primary to-chart-2 bg-clip-text text-transparent">
              Financial Future
            </span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Track expenses, manage accounts, and achieve your financial goals with FinanceHub's 
            intelligent dashboard and AI-powered insights.
          </p>
          <div className="flex items-center justify-center gap-4 pt-4">
            <Button size="lg" asChild>
              <Link to="/signup">
                Start Free Trial
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/login">Sign In</Link>
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-20">
          <div className="text-center space-y-2">
            <div className="text-4xl font-bold text-primary">10K+</div>
            <div className="text-muted-foreground">Active Users</div>
          </div>
          <div className="text-center space-y-2">
            <div className="text-4xl font-bold text-primary">$50M+</div>
            <div className="text-muted-foreground">Money Managed</div>
          </div>
          <div className="text-center space-y-2">
            <div className="text-4xl font-bold text-primary">99.9%</div>
            <div className="text-muted-foreground">Uptime</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-accent/20 py-20 md:py-32">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-5xl font-bold">
              Everything You Need to Succeed
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed to help you manage your finances efficiently
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="shadow-sm hover:shadow-md transition-shadow border-border/50">
                  <CardHeader className="space-y-3">
                    <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
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

      {/* CTA Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <Card className="shadow-lg bg-gradient-to-br from-primary/10 to-chart-2/10 border-primary/20">
          <CardContent className="p-12 md:p-16 text-center space-y-6">
            <h2 className="text-3xl md:text-5xl font-bold">
              Ready to Get Started?
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Join thousands of users who are already managing their finances smarter with FinanceHub
            </p>
            <div className="flex items-center justify-center gap-4 pt-4">
              <Button size="lg" asChild>
                <Link to="/signup">
                  Create Free Account
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-primary p-1.5">
                <Wallet className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="font-semibold">FinanceHub</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2026 FinanceHub. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}