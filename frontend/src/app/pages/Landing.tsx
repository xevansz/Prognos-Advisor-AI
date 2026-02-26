import { Link } from "react-router";
import { ReactNode } from "react";
import { Button } from "../components/ui/button";
import { ThemeToggle } from "../components/ThemeToggle";
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
import { useEffect, useRef, useState } from "react";

// Scroll-triggered fade-in hook
function useFadeIn(): [React.RefObject<HTMLDivElement | null>, boolean] {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setVisible(true);
      },
      { threshold: 0.15 },
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);
  return [ref, visible];
}

function FadeIn({
  children,
  delay = 0,
  className = "",
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const [ref, visible] = useFadeIn();
  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(28px)",
        transition: `opacity 0.65s ease ${delay}ms, transform 0.65s ease ${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}

export function Landing() {
  // To detect dark theme
  const [isDark, setIsDark] = useState(
    document.documentElement.classList.contains("dark"),
  );

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains("dark"));
    });
    observer.observe(document.documentElement, { attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);
  const steps = [
    {
      icon: ClipboardList,
      step: "01",
      title: "Add your accounts",
      description:
        "Connect your bank accounts, savings, and investments in one place.",
      badge: "Secure & encrypted",
      badgeIcon: Shield,
    },
    {
      icon: BarChart2,
      step: "02",
      title: "Track transactions",
      description: "Log income and expenses. Set budgets and financial goals.",
      badge: "Beautiful analytics",
      badgeIcon: PieChart,
    },
    {
      icon: BrainCircuit,
      step: "03",
      title: "Get AI insights",
      description:
        "Prognosis AI analyses your data and recommends your next move.",
      badge: "Personalized for you",
      badgeIcon: TrendingUp,
    },
  ];

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
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
              <ThemeToggle />
              <Button size="sm" asChild>
                <Link to="/login">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative flex items-center min-h-[calc(100vh-4rem)] overflow-hidden">
        {/* Gradient background */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 80% 60% at 50% -10%, hsl(var(--primary) / 0.12) 0%, transparent 70%)",
          }}
        />
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 40% 40% at 80% 60%, hsl(var(--chart-2) / 0.07) 0%, transparent 60%)",
          }}
        />

        <div className="mx-auto max-w-6xl w-full px-4 sm:px-6 lg:px-8 py-16 relative z-10">
          <div className="text-center space-y-7 max-w-3xl mx-auto">
            <div
              style={{
                opacity: 1,
                animation: "heroFadeUp 0.8s ease both",
              }}
            >
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.1]">
                Your finances,{" "}
                <span className="bg-gradient-to-r from-primary to-chart-2 bg-clip-text text-transparent">
                  finally clear.
                </span>
              </h1>
            </div>
            <div style={{ animation: "heroFadeUp 0.8s ease 0.15s both" }}>
              <p className="text-lg text-muted-foreground">
                Prognosis AI combines smart tracking, goal planning, and
                AI-powered insights — so you always know where you stand.
              </p>
            </div>
            <div
              className="flex items-center justify-center gap-3 pt-2"
              style={{ animation: "heroFadeUp 0.8s ease 0.3s both" }}
            >
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

          {/* Dashboard screenshot */}
          <div
            className="mt-16 relative mx-auto max-w-5xl"
            style={{ animation: "heroFadeUp 1s ease 0.45s both" }}
          >
            {/* Glow behind screenshot */}
            <div
              className="absolute inset-0 rounded-2xl pointer-events-none"
              style={{
                background:
                  "radial-gradient(ellipse 60% 40% at 50% 100%, hsl(var(--primary) / 0.2) 0%, transparent 70%)",
                filter: "blur(24px)",
                transform: "translateY(8px)",
              }}
            />
            {/* Browser chrome frame */}
            <div className="relative rounded-2xl border border-border/60 bg-card/80 shadow-2xl overflow-hidden">
              {/* Chrome bar */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-border/40 bg-muted/30">
                <div className="h-3 w-3 rounded-full bg-red-400/70" />
                <div className="h-3 w-3 rounded-full bg-yellow-400/70" />
                <div className="h-3 w-3 rounded-full bg-green-400/70" />
                <div className="mx-auto flex items-center gap-2 bg-background/60 rounded-md px-4 py-1 text-xs text-muted-foreground/60 w-56 justify-center">
                  <span>app.prognosisai.com/overview</span>
                </div>
              </div>
              <img
                src={isDark ? "/dashboard.png" : "/dashboard-light.png"}
                alt="Prognosis AI Dashboard"
                className="w-full block"
              />
            </div>
          </div>
        </div>
      </section>

      {/* How it works + Features merged */}
      <section className="border-y border-border bg-card/40 py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="text-center space-y-3 mb-16">
            <p className="text-xs font-mono text-muted-foreground/60 uppercase tracking-widest">
              How it works
            </p>
            <h2 className="text-3xl md:text-4xl font-bold">
              Built for clarity
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Every feature is designed to reduce noise and help you focus on
              what matters.
            </p>
          </FadeIn>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {steps.map((s, i) => {
              const Icon = s.icon;
              const BadgeIcon = s.badgeIcon;
              return (
                <FadeIn key={s.step} delay={i * 120}>
                  <Card className="h-full shadow-sm hover:shadow-md transition-all hover:-translate-y-1 border-border/60 bg-card/60">
                    <CardHeader className="space-y-4 pb-3">
                      <div className="flex items-center justify-between">
                        <div className="h-10 w-10 rounded-md bg-primary/10 flex items-center justify-center">
                          <Icon className="h-5 w-5 text-primary" />
                        </div>
                        <span className="text-xs font-mono text-muted-foreground/40">
                          {s.step}
                        </span>
                      </div>
                      <CardTitle className="text-lg">{s.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0 space-y-4">
                      <CardDescription className="text-sm leading-relaxed">
                        {s.description}
                      </CardDescription>
                      <div className="flex items-center gap-2 text-xs text-primary/80 bg-primary/8 rounded-md px-3 py-2 w-fit">
                        <BadgeIcon className="h-3.5 w-3.5" />
                        <span>{s.badge}</span>
                      </div>
                    </CardContent>
                  </Card>
                </FadeIn>
              );
            })}
          </div>
        </div>
      </section>

      {/* AI Insights section */}
      <section className="py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <FadeIn>
              <div className="space-y-6">
                <p className="text-xs font-mono text-muted-foreground/60 uppercase tracking-widest">
                  AI-Powered
                </p>
                <h2 className="text-3xl md:text-4xl font-bold leading-tight">
                  Your personal{" "}
                  <span className="bg-gradient-to-r from-primary to-chart-2 bg-clip-text text-transparent">
                    financial advisor
                  </span>
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  Prognosis AI analyses your spending patterns, income trends,
                  and goals — then delivers actionable recommendations tailored
                  specifically to your financial situation.
                </p>
                <ul className="space-y-3">
                  {[
                    "Net worth tracking across all accounts",
                    "Goal progress with timeline projections",
                    "Spending pattern analysis & alerts",
                    "Personalized investment recommendations",
                  ].map((item) => (
                    <li
                      key={item}
                      className="flex items-center gap-3 text-sm text-muted-foreground"
                    >
                      <div className="h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
                <Button asChild>
                  <Link to="/signup">
                    Try it free <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </FadeIn>

            <FadeIn delay={150}>
              <div className="relative">
                <div
                  className="absolute inset-0 rounded-2xl pointer-events-none"
                  style={{
                    background:
                      "radial-gradient(ellipse 60% 60% at 50% 50%, hsl(var(--chart-2) / 0.15) 0%, transparent 70%)",
                    filter: "blur(20px)",
                  }}
                />
                <div className="relative rounded-2xl border border-border/60 bg-card/80 shadow-2xl overflow-hidden">
                  <div className="flex items-center gap-2 px-4 py-3 border-b border-border/40 bg-muted/30">
                    <div className="h-3 w-3 rounded-full bg-red-400/70" />
                    <div className="h-3 w-3 rounded-full bg-yellow-400/70" />
                    <div className="h-3 w-3 rounded-full bg-green-400/70" />
                    <div className="mx-auto flex items-center gap-2 bg-background/60 rounded-md px-4 py-1 text-xs text-muted-foreground/60 w-56 justify-center">
                      <span>app.prognosisai.com/report</span>
                    </div>
                  </div>
                  <img
                    src={isDark ? "/aireport.png" : "/aireport-light.png"}
                    alt="Prognosis AI Report"
                    className="w-full block"
                  />
                </div>
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="border-t border-border py-24 relative overflow-hidden">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 60% 80% at 50% 50%, hsl(var(--primary) / 0.08) 0%, transparent 70%)",
          }}
        />
        <FadeIn>
          <div className="mx-auto max-w-2xl px-4 text-center space-y-6 relative z-10">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
              Ready to take control?
            </h2>
            <p className="text-muted-foreground text-lg">
              Join thousands of people who finally understand their finances.
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
            <p className="text-xs text-muted-foreground/50">
              No credit card required
            </p>
          </div>
        </FadeIn>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-xs text-muted-foreground">
            © 2026 Prognosis AI. All rights reserved.
          </p>
        </div>
      </footer>

      <style>{`
        @keyframes heroFadeUp {
          from { opacity: 0; transform: translateY(32px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
