import { Link } from "react-router";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { useApp } from "../context/AppContext";
import {
  Calendar,
  Target,
  TrendingUp,
  User,
  Wallet,
  ShieldAlert,
  Settings,
  Mail,
} from "lucide-react";
import { getCurrencySymbol, formatCurrency } from "../constants";

export function Profile() {
  const { profile, goals, userEmail } = useApp();

  if (!profile) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        <p className="text-sm">Loading profile…</p>
      </div>
    );
  }

  const riskColor =
    {
      aggressive: "text-destructive",
      moderate: "text-warning",
      conservative: "text-success",
    }[profile.risk_appetite] ?? "";

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="mb-1">Profile</h1>
          <p className="text-muted-foreground">
            Your personal information and financial goals
          </p>
        </div>
        <Button variant="outline" size="sm" asChild className="gap-2">
          <Link to="/dashboard/settings">
            <Settings className="h-4 w-4" />
            Edit in Settings
          </Link>
        </Button>
      </div>

      {/* Personal Information */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-4 w-4 text-primary" />
            Personal Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
            <div className="space-y-1">
              <dt className="text-xs text-muted-foreground uppercase tracking-wide flex items-center gap-1">
                <User className="h-3 w-3" /> Display Name
              </dt>
              <dd className="text-base font-medium">
                {profile.display_name ?? "—"}
              </dd>
            </div>
            <div className="space-y-1">
              <dt className="text-xs text-muted-foreground uppercase tracking-wide flex items-center gap-1">
                <Mail className="h-3 w-3" /> Email
              </dt>
              <dd className="text-base font-medium">{userEmail ?? "—"}</dd>
            </div>
            <div className="space-y-1">
              <dt className="text-xs text-muted-foreground uppercase tracking-wide">
                Age
              </dt>
              <dd className="text-base font-medium">{profile.age} years</dd>
            </div>
            <div className="space-y-1">
              <dt className="text-xs text-muted-foreground uppercase tracking-wide flex items-center gap-1">
                <Wallet className="h-3 w-3" /> Base Currency
              </dt>
              <dd className="text-base font-medium">
                {profile.base_currency} (
                {getCurrencySymbol(profile.base_currency)})
              </dd>
            </div>
            <div className="space-y-1">
              <dt className="text-xs text-muted-foreground uppercase tracking-wide flex items-center gap-1">
                <ShieldAlert className="h-3 w-3" /> Risk Appetite
              </dt>
              <dd className={`text-base font-semibold capitalize ${riskColor}`}>
                {profile.risk_appetite}
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      {/* Financial Goals */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" />
            Financial Goals
          </CardTitle>
        </CardHeader>
        <CardContent>
          {goals.length === 0 ? (
            <div className="text-center py-10 text-muted-foreground">
              <Target className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm">No goals yet.</p>
              <Button variant="link" size="sm" asChild className="mt-1">
                <Link to="/dashboard/settings?tab=goals">
                  Add a goal in Settings
                </Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {goals.map((goal) => (
                <div
                  key={goal.id}
                  className="rounded-lg border bg-background p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-primary" />
                      <span className="font-semibold">{goal.name}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-muted-foreground">
                        Priority
                      </div>
                      <div className="text-sm font-semibold capitalize">
                        {goal.priority}
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground mb-1">
                        Target Amount
                      </div>
                      <div className="font-semibold flex items-center gap-1">
                        <TrendingUp className="h-3 w-3" />
                        {formatCurrency(
                          goal.target_amount,
                          goal.target_currency,
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-1">
                        Target Date
                      </div>
                      <div className="font-semibold flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(goal.target_date).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
