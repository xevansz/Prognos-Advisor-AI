import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { useApp, convertToBase } from "../context/AppContext";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { formatCurrency } from "../constants";
import { TrendingUp, TrendingDown, Wallet } from "lucide-react";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "../components/ui/chart";

export function Overview() {
  const { accounts, transactions, profile, settings, fxRates } = useApp();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 400);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return <LoadingSkeleton />;
  }

  const baseCurrency = profile?.base_currency ?? "INR";

  const netWorth = accounts.reduce(
    (sum, acc) =>
      sum + convertToBase(acc.balance, acc.currency, baseCurrency, fxRates),
    0,
  );

  // Compute real monthly income vs spending for last 7 months
  const now = new Date();
  const monthlyData = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - (6 - i), 1);
    const label = d.toLocaleString("default", { month: "short" });
    const yr = d.getFullYear();
    const mo = d.getMonth();
    let income = 0;
    let spending = 0;
    transactions.forEach((t) => {
      const td = new Date(t.date);
      if (td.getFullYear() === yr && td.getMonth() === mo) {
        const converted = convertToBase(
          t.amount,
          t.currency,
          baseCurrency,
          fxRates,
        );
        if (t.type === "credit") income += converted;
        else spending += converted;
      }
    });
    return { month: label, income, spending };
  });

  // Calculate asset distribution (values converted to base currency)
  const assetData = accounts.map((acc) => ({
    name: acc.name,
    value: convertToBase(acc.balance, acc.currency, baseCurrency, fxRates),
  }));

  const COLORS = [
    "var(--chart-1)",
    "var(--chart-2)",
    "var(--chart-3)",
    "var(--chart-4)",
    "var(--chart-5)",
  ];

  const lineChartConfig: ChartConfig = {
    income: { label: "Income", color: "var(--chart-2)" },
    spending: { label: "Spending", color: "var(--chart-3)" },
  };

  const assetChartConfig: ChartConfig = Object.fromEntries(
    assetData.map((d) => [d.name, { label: d.name }]),
  );

  const renderPieLabel = ({
    cx,
    cy,
    midAngle,
    outerRadius,
    name,
    percent,
  }: {
    cx: number;
    cy: number;
    midAngle: number;
    outerRadius: number;
    name: string;
    percent: number;
  }) => {
    const RADIAN = Math.PI / 180;
    const radius = outerRadius + 24;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    return (
      <text
        x={x}
        y={y}
        fill="var(--foreground)"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        fontSize={11}
      >
        {name}: {(percent * 100).toFixed(0)}%
      </text>
    );
  };

  // Current month totals in base currency
  const curMonth = now.getMonth();
  const curYear = now.getFullYear();
  const totalIncome = transactions
    .filter((t) => {
      const d = new Date(t.date);
      return (
        t.type === "credit" &&
        d.getMonth() === curMonth &&
        d.getFullYear() === curYear
      );
    })
    .reduce(
      (sum, t) =>
        sum + convertToBase(t.amount, t.currency, baseCurrency, fxRates),
      0,
    );

  const totalExpenses = transactions
    .filter((t) => {
      const d = new Date(t.date);
      return (
        t.type === "debit" &&
        d.getMonth() === curMonth &&
        d.getFullYear() === curYear
      );
    })
    .reduce(
      (sum, t) =>
        sum + convertToBase(t.amount, t.currency, baseCurrency, fxRates),
      0,
    );

  const savingsRate =
    totalIncome > 0
      ? (((totalIncome - totalExpenses) / totalIncome) * 100).toFixed(1)
      : 0;

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Net Worth</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl sm:text-3xl font-bold">
              {formatCurrency(netWorth, baseCurrency, settings.currencyFormat)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              +12.5% from last month
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Monthly Income
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-[var(--success)]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl sm:text-3xl font-bold text-[var(--success)]">
              {formatCurrency(
                totalIncome,
                baseCurrency,
                settings.currencyFormat,
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">This month</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Monthly Expenses
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-[var(--destructive)]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl sm:text-3xl font-bold text-[var(--destructive)]">
              {formatCurrency(
                totalExpenses,
                baseCurrency,
                settings.currencyFormat,
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Savings rate: {savingsRate}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Income vs Spending</CardTitle>
            <CardDescription>Last 7 months trend</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={lineChartConfig}
              className="h-[300px] w-full"
            >
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <ChartLegend content={<ChartLegendContent />} />
                <Line
                  type="monotone"
                  dataKey="income"
                  stroke="var(--chart-2)"
                  strokeWidth={2}
                  name="Income"
                />
                <Line
                  type="monotone"
                  dataKey="spending"
                  stroke="var(--chart-3)"
                  strokeWidth={2}
                  name="Spending"
                />
              </LineChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Asset Distribution</CardTitle>
            <CardDescription>Current allocation</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={assetChartConfig}
              className="h-[300px] w-full"
            >
              <PieChart>
                <Pie
                  data={assetData}
                  cx="50%"
                  cy="50%"
                  label={renderPieLabel}
                  labelLine={{ stroke: "var(--muted-foreground)" }}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {assetData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <ChartTooltip
                  content={
                    <ChartTooltipContent
                      nameKey="name"
                      formatter={(value) => {
                        const num =
                          typeof value === "number"
                            ? value
                            : Array.isArray(value)
                              ? parseFloat(String(value[0])) || 0
                              : parseFloat(String(value)) || 0;
                        return formatCurrency(
                          num,
                          baseCurrency,
                          settings.currencyFormat,
                        );
                      }}
                    />
                  }
                />
                <ChartLegend content={<ChartLegendContent nameKey="name" />} />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
          <CardDescription>Your latest financial activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...transactions]
              .sort(
                (a, b) =>
                  new Date(b.date).getTime() - new Date(a.date).getTime(),
              )
              .slice(0, 5)
              .map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{transaction.label}</p>
                    <p className="text-xs text-muted-foreground">
                      {transaction.date}
                    </p>
                  </div>
                  <div
                    className={`text-sm font-medium ${
                      transaction.type === "credit"
                        ? "text-[var(--success)]"
                        : "text-[var(--destructive)]"
                    }`}
                  >
                    {transaction.type === "credit" ? "+" : "-"}{" "}
                    {formatCurrency(
                      transaction.amount,
                      transaction.currency,
                      settings.currencyFormat,
                    )}
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
