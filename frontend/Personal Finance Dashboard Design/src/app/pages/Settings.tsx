import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '../components/ui/dialog';
import { useApp, type RiskAppetite, type GoalStatus } from '../context/AppContext';
import { Moon, Sun, Plus, Pencil, Trash2, LogOut } from 'lucide-react';

export function Settings() {
  const { profile, updateProfile, settings, updateSettings, theme, toggleTheme, goals, addGoal, updateGoal, deleteGoal } = useApp();
  const [isGoalDialogOpen, setIsGoalDialogOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<string | null>(null);
  const [goalForm, setGoalForm] = useState({
    name: '',
    targetAmount: '',
    targetDate: '',
    priority: '1',
    status: 'On Track' as GoalStatus,
  });

  const handleProfileChange = (field: string, value: string | number) => {
    updateProfile({ [field]: value });
  };

  const handleSettingsChange = (field: string, value: boolean | string) => {
    updateSettings({ [field]: value });
  };

  const openGoalDialog = (goalId?: string) => {
    if (goalId) {
      const goal = goals.find(g => g.id === goalId);
      if (goal) {
        setGoalForm({
          name: goal.name,
          targetAmount: goal.targetAmount.toString(),
          targetDate: goal.targetDate,
          priority: goal.priority.toString(),
          status: goal.status,
        });
        setEditingGoal(goalId);
      }
    } else {
      setGoalForm({
        name: '',
        targetAmount: '',
        targetDate: '',
        priority: '1',
        status: 'On Track',
      });
      setEditingGoal(null);
    }
    setIsGoalDialogOpen(true);
  };

  const handleGoalSubmit = () => {
    if (editingGoal) {
      updateGoal(editingGoal, {
        name: goalForm.name,
        targetAmount: parseFloat(goalForm.targetAmount),
        targetDate: goalForm.targetDate,
        priority: parseInt(goalForm.priority),
        status: goalForm.status,
      });
    } else {
      addGoal({
        name: goalForm.name,
        targetAmount: parseFloat(goalForm.targetAmount),
        targetDate: goalForm.targetDate,
        priority: parseInt(goalForm.priority),
        status: goalForm.status,
      });
    }
    setIsGoalDialogOpen(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-2">Settings</h1>
        <p className="text-muted-foreground">Manage your account preferences and application settings</p>
      </div>

      {/* Profile Settings */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Profile Settings</CardTitle>
          <CardDescription>Update your personal information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="displayName">Display Name</Label>
              <Input
                id="displayName"
                value={profile.displayName}
                onChange={(e) => handleProfileChange('displayName', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                value={profile.age}
                onChange={(e) => handleProfileChange('age', parseInt(e.target.value))}
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
                    size="sm"
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

      {/* Goal Settings */}
      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Goal Settings</CardTitle>
              <CardDescription>Create and manage your financial goals</CardDescription>
            </div>
            <Dialog open={isGoalDialogOpen} onOpenChange={setIsGoalDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => openGoalDialog()} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Goal
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{editingGoal ? 'Edit Goal' : 'Create New Goal'}</DialogTitle>
                  <DialogDescription>
                    {editingGoal ? 'Update your financial goal details' : 'Add a new financial goal to track'}
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="goalName">Goal Name</Label>
                    <Input
                      id="goalName"
                      value={goalForm.name}
                      onChange={(e) => setGoalForm({ ...goalForm, name: e.target.value })}
                      placeholder="e.g., Emergency Fund"
                    />
                  </div>
                  <div className="grid gap-4 grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="targetAmount">Target Amount</Label>
                      <Input
                        id="targetAmount"
                        type="number"
                        value={goalForm.targetAmount}
                        onChange={(e) => setGoalForm({ ...goalForm, targetAmount: e.target.value })}
                        placeholder="10000"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="priority">Priority</Label>
                      <Input
                        id="priority"
                        type="number"
                        value={goalForm.priority}
                        onChange={(e) => setGoalForm({ ...goalForm, priority: e.target.value })}
                        placeholder="1"
                        min="1"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="targetDate">Target Date</Label>
                    <Input
                      id="targetDate"
                      type="date"
                      value={goalForm.targetDate}
                      onChange={(e) => setGoalForm({ ...goalForm, targetDate: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select value={goalForm.status} onValueChange={(value: GoalStatus) => setGoalForm({ ...goalForm, status: value })}>
                      <SelectTrigger id="status">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="On Track">On Track</SelectItem>
                        <SelectItem value="At Risk">At Risk</SelectItem>
                        <SelectItem value="Unrealistic">Unrealistic</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsGoalDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleGoalSubmit}>
                    {editingGoal ? 'Update' : 'Create'} Goal
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {goals.map((goal) => (
              <div key={goal.id} className="flex items-center justify-between p-3 rounded-lg border">
                <div>
                  <div className="font-medium">{goal.name}</div>
                  <div className="text-sm text-muted-foreground">
                    ${goal.targetAmount.toLocaleString()} by {new Date(goal.targetDate).toLocaleDateString()}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" onClick={() => openGoalDialog(goal.id)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => deleteGoal(goal.id)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* General Settings */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>General Settings</CardTitle>
          <CardDescription>Customize your application experience</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Theme</Label>
              <div className="text-sm text-muted-foreground">
                Switch between light and dark mode
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleTheme}
              className="gap-2"
            >
              {theme === 'dark' ? (
                <>
                  <Moon className="h-4 w-4" />
                  Dark
                </>
              ) : (
                <>
                  <Sun className="h-4 w-4" />
                  Light
                </>
              )}
            </Button>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="currency-format">Currency Format</Label>
              <div className="text-sm text-muted-foreground">
                Display currency as symbol or code
              </div>
            </div>
            <Select
              value={settings.currencyFormat}
              onValueChange={(value: 'symbol' | 'code') => handleSettingsChange('currencyFormat', value)}
            >
              <SelectTrigger id="currency-format" className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="symbol">Symbol</SelectItem>
                <SelectItem value="code">Code</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notifications">Notifications</Label>
              <div className="text-sm text-muted-foreground">
                Receive updates about your finances
              </div>
            </div>
            <Switch
              id="notifications"
              checked={settings.notifications}
              onCheckedChange={(checked) => handleSettingsChange('notifications', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Logout Button */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>Manage your account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Logout</Label>
              <div className="text-sm text-muted-foreground">
                Sign out of your account
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsLogoutDialogOpen(true)}
              className="gap-2"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Logout Dialog */}
      <Dialog open={isLogoutDialogOpen} onOpenChange={setIsLogoutDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Logout</DialogTitle>
            <DialogDescription>
              Are you sure you want to logout? You will be redirected to the login page.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsLogoutDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => {
              // Add logout logic here
              setIsLogoutDialogOpen(false);
            }}>
              Logout
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}