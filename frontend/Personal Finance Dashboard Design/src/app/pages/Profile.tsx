import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useApp } from '../context/AppContext';
import { Calendar, Target, TrendingUp } from 'lucide-react';

export function Profile() {
  const { profile, updateProfile, goals } = useApp();

  const handleProfileChange = (field: string, value: string | number) => {
    updateProfile({ [field]: value });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'On Track':
        return 'bg-[hsl(var(--success))] text-[hsl(var(--success-foreground))]';
      case 'At Risk':
        return 'bg-[hsl(var(--warning))] text-[hsl(var(--warning-foreground))]';
      case 'Unrealistic':
        return 'bg-[hsl(var(--destructive))] text-[hsl(var(--destructive-foreground))]';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-2">Profile</h1>
        <p className="text-muted-foreground">Manage your personal information and financial goals</p>
      </div>

      {/* Profile Form */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>Update your profile details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="displayName">Display Name</Label>
              <Input
                id="displayName"
                value={profile.displayName}
                onChange={(e) => handleProfileChange('displayName', e.target.value)}
                placeholder="Enter your name"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                value={profile.age}
                onChange={(e) => handleProfileChange('age', parseInt(e.target.value))}
                placeholder="Enter your age"
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="currency">Base Currency</Label>
              <Select value={profile.baseCurrency} onValueChange={(value) => handleProfileChange('baseCurrency', value)}>
                <SelectTrigger id="currency">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="USD">USD ($)</SelectItem>
                  <SelectItem value="EUR">EUR (€)</SelectItem>
                  <SelectItem value="GBP">GBP (£)</SelectItem>
                  <SelectItem value="JPY">JPY (¥)</SelectItem>
                  <SelectItem value="AUD">AUD (A$)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Risk Appetite</Label>
              <div className="flex gap-2">
                {(['Aggressive', 'Moderate', 'Conservative'] as const).map((risk) => (
                  <Button
                    key={risk}
                    variant={profile.riskAppetite === risk ? 'default' : 'outline'}
                    className="flex-1"
                    onClick={() => handleProfileChange('riskAppetite', risk)}
                  >
                    {risk}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Goals List */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Financial Goals</CardTitle>
          <CardDescription>Track your progress toward your financial objectives</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {goals.map((goal) => (
              <Card key={goal.id} className="border-2">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Target className="h-4 w-4 text-primary" />
                        <h4 className="font-semibold">{goal.name}</h4>
                      </div>
                      <Badge className={getStatusColor(goal.status)}>
                        {goal.status}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">Priority</div>
                      <div className="text-lg font-bold">{goal.priority}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground mb-1">Target Amount</div>
                      <div className="font-semibold flex items-center gap-1">
                        <TrendingUp className="h-3 w-3" />
                        ${goal.targetAmount.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-1">Target Date</div>
                      <div className="font-semibold flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(goal.targetDate).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
