import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Button } from "../components/ui/button";
import { Switch } from "../components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "../components/ui/dialog";
import {
  useApp,
  type RiskAppetite,
  type GoalStatus,
} from "../context/AppContext";
import { CURRENCIES } from "../constants";
import {
  Moon,
  Sun,
  Plus,
  Pencil,
  Trash2,
  LogOut,
  User,
  Target,
  Settings2,
  Shield,
  ChevronRight,
} from "lucide-react";

type SettingsTab = "profile" | "goals" | "general" | "account";

const sidebarItems: {
  id: SettingsTab;
  label: string;
  icon: React.ElementType;
  description: string;
}[] = [
  {
    id: "profile",
    label: "Personal Info",
    icon: User,
    description: "Name, age, currency, risk",
  },
  {
    id: "goals",
    label: "Goals",
    icon: Target,
    description: "Financial goals & targets",
  },
  {
    id: "general",
    label: "General",
    icon: Settings2,
    description: "Theme, format, notifications",
  },
  {
    id: "account",
    label: "Account",
    icon: Shield,
    description: "Email, security, data",
  },
];

export function Settings() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const {
    profile,
    updateProfile,
    settings,
    updateSettings,
    theme,
    toggleTheme,
    goals,
    addGoal,
    updateGoal,
    deleteGoal,
    logout,
  } = useApp();

  const initialTab = (searchParams.get("tab") as SettingsTab) || "profile";
  const [activeTab, setActiveTab] = useState<SettingsTab>(initialTab);
  const [isGoalDialogOpen, setIsGoalDialogOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<string | null>(null);
  const [profileError, setProfileError] = useState("");
  const [profileSuccess, setProfileSuccess] = useState("");
  const [goalError, setGoalError] = useState("");
  const [goalForm, setGoalForm] = useState({
    name: "",
    targetAmount: "",
    targetDate: "",
    priority: "1",
    status: "On Track" as GoalStatus,
  });

  useEffect(() => {
    const tab = searchParams.get("tab") as SettingsTab;
    if (tab && sidebarItems.some((i) => i.id === tab)) {
      setActiveTab(tab);
    }
  }, [searchParams]);

  const handleTabChange = (tab: SettingsTab) => {
    setActiveTab(tab);
    setSearchParams({ tab });
    setProfileError("");
    setProfileSuccess("");
    setGoalError("");
  };

  const handleProfileChange = (field: string, value: string | number) => {
    setProfileSuccess("");
    setProfileError("");
    updateProfile({ [field]: value });
  };

  const handleProfileSave = () => {
    if (!profile.displayName.trim()) {
      setProfileError("Display name cannot be empty.");
      return;
    }
    if (!profile.email.trim()) {
      setProfileError("Email cannot be empty.");
      return;
    }
    if (profile.age < 1 || profile.age > 120) {
      setProfileError("Please enter a valid age.");
      return;
    }
    setProfileSuccess("Profile saved successfully.");
    setTimeout(() => setProfileSuccess(""), 3000);
  };

  const handleSettingsChange = (field: string, value: boolean | string) => {
    updateSettings({ [field]: value });
  };

  const openGoalDialog = (goalId?: string) => {
    setGoalError("");
    if (goalId) {
      const goal = goals.find((g) => g.id === goalId);
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
        name: "",
        targetAmount: "",
        targetDate: "",
        priority: "1",
        status: "On Track",
      });
      setEditingGoal(null);
    }
    setIsGoalDialogOpen(true);
  };

  const handleGoalSubmit = () => {
    setGoalError("");
    if (!goalForm.name.trim()) {
      setGoalError("Goal name is required.");
      return;
    }
    if (!goalForm.targetAmount || isNaN(parseFloat(goalForm.targetAmount))) {
      setGoalError("Enter a valid target amount.");
      return;
    }
    if (!goalForm.targetDate) {
      setGoalError("Target date is required.");
      return;
    }
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
        <h1 className="mb-1">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account preferences and application settings
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Sidebar */}
        <aside className="md:w-56 shrink-0">
          <nav className="rounded-lg border bg-card overflow-hidden">
            {sidebarItems.map((item, idx) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleTabChange(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors
                    ${idx !== 0 ? "border-t border-border" : ""}
                    ${
                      isActive
                        ? "bg-accent text-accent-foreground"
                        : "hover:bg-accent/50 text-foreground"
                    }`}
                >
                  <Icon
                    className={`h-4 w-4 shrink-0 ${isActive ? "text-accent-foreground" : "text-muted-foreground"}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium">{item.label}</div>
                    <div className="text-xs text-muted-foreground truncate">
                      {item.description}
                    </div>
                  </div>
                  <ChevronRight
                    className={`h-3 w-3 shrink-0 ${isActive ? "opacity-70" : "opacity-0"}`}
                  />
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-4">
          {/* Personal Info */}
          {activeTab === "profile" && (
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
                <CardDescription>
                  Update the details shown on your profile page
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="displayName">Display Name</Label>
                    <Input
                      id="displayName"
                      value={profile.displayName}
                      onChange={(e) =>
                        handleProfileChange("displayName", e.target.value)
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profile.email}
                      onChange={(e) =>
                        handleProfileChange("email", e.target.value)
                      }
                    />
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="age">Age</Label>
                    <Input
                      id="age"
                      type="number"
                      value={profile.age}
                      onChange={(e) =>
                        handleProfileChange(
                          "age",
                          parseInt(e.target.value) || 0,
                        )
                      }
                      min={1}
                      max={120}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="currency">Base Currency</Label>
                    <Select
                      value={profile.baseCurrency}
                      onValueChange={(v) =>
                        handleProfileChange("baseCurrency", v)
                      }
                    >
                      <SelectTrigger id="currency">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="max-h-60">
                        {CURRENCIES.map((c) => (
                          <SelectItem key={c.code} value={c.code}>
                            {c.code} ({c.symbol}) — {c.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Risk Appetite</Label>
                  <div className="flex gap-2">
                    {(["Aggressive", "Moderate", "Conservative"] as const).map(
                      (risk) => (
                        <Button
                          key={risk}
                          variant={
                            profile.riskAppetite === risk
                              ? "default"
                              : "outline"
                          }
                          size="sm"
                          className="flex-1"
                          onClick={() =>
                            handleProfileChange("riskAppetite", risk)
                          }
                        >
                          {risk}
                        </Button>
                      ),
                    )}
                  </div>
                </div>
                {profileError && (
                  <p className="text-sm text-destructive">{profileError}</p>
                )}
                {profileSuccess && (
                  <p className="text-sm text-success">{profileSuccess}</p>
                )}
                <Button onClick={handleProfileSave}>Save Changes</Button>
              </CardContent>
            </Card>
          )}

          {/* Goals */}
          {activeTab === "goals" && (
            <Card className="shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Financial Goals</CardTitle>
                    <CardDescription>
                      Create and manage goals shown on your profile
                    </CardDescription>
                  </div>
                  <Dialog
                    open={isGoalDialogOpen}
                    onOpenChange={setIsGoalDialogOpen}
                  >
                    <DialogTrigger asChild>
                      <Button onClick={() => openGoalDialog()} size="sm">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Goal
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>
                          {editingGoal ? "Edit Goal" : "Create New Goal"}
                        </DialogTitle>
                        <DialogDescription>
                          {editingGoal
                            ? "Update your financial goal details"
                            : "Add a new financial goal to track"}
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="goalName">Goal Name</Label>
                          <Input
                            id="goalName"
                            value={goalForm.name}
                            onChange={(e) =>
                              setGoalForm({ ...goalForm, name: e.target.value })
                            }
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
                              onChange={(e) =>
                                setGoalForm({
                                  ...goalForm,
                                  targetAmount: e.target.value,
                                })
                              }
                              placeholder="10000"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="priority">Priority</Label>
                            <Input
                              id="priority"
                              type="number"
                              value={goalForm.priority}
                              onChange={(e) =>
                                setGoalForm({
                                  ...goalForm,
                                  priority: e.target.value,
                                })
                              }
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
                            onChange={(e) =>
                              setGoalForm({
                                ...goalForm,
                                targetDate: e.target.value,
                              })
                            }
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="goalStatus">Status</Label>
                          <Select
                            value={goalForm.status}
                            onValueChange={(v: GoalStatus) =>
                              setGoalForm({ ...goalForm, status: v })
                            }
                          >
                            <SelectTrigger id="goalStatus">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="On Track">On Track</SelectItem>
                              <SelectItem value="At Risk">At Risk</SelectItem>
                              <SelectItem value="Unrealistic">
                                Unrealistic
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        {goalError && (
                          <p className="text-sm text-destructive">
                            {goalError}
                          </p>
                        )}
                      </div>
                      <DialogFooter>
                        <Button
                          variant="outline"
                          onClick={() => setIsGoalDialogOpen(false)}
                        >
                          Cancel
                        </Button>
                        <Button onClick={handleGoalSubmit}>
                          {editingGoal ? "Update" : "Create"} Goal
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                {goals.length === 0 ? (
                  <div className="text-center py-10 text-muted-foreground">
                    <Target className="h-10 w-10 mx-auto mb-3 opacity-30" />
                    <p className="text-sm">
                      No goals yet. Add your first goal.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {goals.map((goal) => (
                      <div
                        key={goal.id}
                        className="flex items-center justify-between p-3 rounded-lg border"
                      >
                        <div>
                          <div className="font-medium">{goal.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {goal.targetAmount.toLocaleString()} by{" "}
                            {new Date(goal.targetDate).toLocaleDateString()} ·
                            Priority {goal.priority}
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openGoalDialog(goal.id)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteGoal(goal.id)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* General */}
          {activeTab === "general" && (
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle>General Settings</CardTitle>
                <CardDescription>
                  Customize your application experience
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-0 divide-y divide-border">
                <div className="flex items-center justify-between py-4">
                  <div className="space-y-0.5">
                    <Label>Theme</Label>
                    <p className="text-sm text-muted-foreground">
                      Switch between light and dark mode
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={toggleTheme}
                    className="gap-2 min-w-24"
                  >
                    {theme === "dark" ? (
                      <>
                        <Moon className="h-4 w-4" /> Dark
                      </>
                    ) : (
                      <>
                        <Sun className="h-4 w-4" /> Light
                      </>
                    )}
                  </Button>
                </div>

                <div className="flex items-center justify-between py-4">
                  <div className="space-y-0.5">
                    <Label htmlFor="currency-format">Currency Format</Label>
                    <p className="text-sm text-muted-foreground">
                      Display currency as symbol or code
                    </p>
                  </div>
                  <Select
                    value={settings.currencyFormat}
                    onValueChange={(v: "symbol" | "code") =>
                      handleSettingsChange("currencyFormat", v)
                    }
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

                <div className="flex items-center justify-between py-4">
                  <div className="space-y-0.5">
                    <Label htmlFor="notifications">Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive updates about your finances
                    </p>
                  </div>
                  <Switch
                    id="notifications"
                    checked={settings.notifications}
                    onCheckedChange={(v) =>
                      handleSettingsChange("notifications", v)
                    }
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Account */}
          {activeTab === "account" && (
            <div className="space-y-4">
              <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle>Change Email</CardTitle>
                  <CardDescription>
                    Update the email address for your account
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="newEmail">New Email Address</Label>
                    <div className="flex gap-2">
                      <Input
                        id="newEmail"
                        type="email"
                        placeholder={profile.email}
                        className="flex-1"
                      />
                      <Button variant="outline">Update Email</Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Get Your Data — future feature, commented out in UI */}
              {/* <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle>Export Your Data</CardTitle>
                  <CardDescription>
                    Download a copy of all your financial data
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline">Request Data Export</Button>
                </CardContent>
              </Card> */}

              <Card className="shadow-sm border-destructive/30">
                <CardHeader>
                  <CardTitle className="text-destructive">Sign Out</CardTitle>
                  <CardDescription>
                    Sign out of your Prognosis AI account
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="gap-2 border-destructive/50 text-destructive hover:bg-destructive hover:text-destructive-foreground"
                    onClick={() => setIsLogoutDialogOpen(true)}
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </Button>
                </CardContent>
              </Card>

              <Card className="shadow-sm border-destructive/30">
                <CardHeader>
                  <CardTitle className="text-destructive">
                    Delete Account
                  </CardTitle>
                  <CardDescription>
                    Permanently delete your account and all associated data.
                    This action cannot be undone.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="destructive"
                    onClick={() => setIsDeleteDialogOpen(true)}
                  >
                    Delete Account
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>

      {/* Logout Dialog */}
      <Dialog open={isLogoutDialogOpen} onOpenChange={setIsLogoutDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Sign Out</DialogTitle>
            <DialogDescription>
              Are you sure you want to sign out?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsLogoutDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                logout();
                navigate("/");
                setIsLogoutDialogOpen(false);
              }}
            >
              Sign Out
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Account Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Account</DialogTitle>
            <DialogDescription>
              This will permanently delete your account and all data. This
              action <strong>cannot be undone</strong>.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                logout();
                navigate("/");
                setIsDeleteDialogOpen(false);
              }}
            >
              Delete My Account
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
