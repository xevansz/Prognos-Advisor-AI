import React, { createContext, useContext, useState, useEffect } from 'react';

export type RiskAppetite = 'Aggressive' | 'Moderate' | 'Conservative';
export type GoalStatus = 'On Track' | 'At Risk' | 'Unrealistic';

export interface Account {
  id: string;
  name: string;
  type: string;
  currency: string;
  balance: number;
}

export interface Transaction {
  id: string;
  date: string;
  label: string;
  description: string;
  accountId: string;
  type: 'Income' | 'Expense';
  amount: number;
  currency: string;
  isRecurring: boolean;
}

export interface Goal {
  id: string;
  name: string;
  targetAmount: number;
  targetDate: string;
  priority: number;
  status: GoalStatus;
}

export interface Profile {
  age: number;
  baseCurrency: string;
  riskAppetite: RiskAppetite;
  displayName: string;
}

interface AppSettings {
  currencyFormat: 'symbol' | 'code';
  notifications: boolean;
}

interface AppContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  profile: Profile;
  updateProfile: (profile: Partial<Profile>) => void;
  goals: Goal[];
  addGoal: (goal: Omit<Goal, 'id'>) => void;
  updateGoal: (id: string, goal: Partial<Goal>) => void;
  deleteGoal: (id: string) => void;
  accounts: Account[];
  addAccount: (account: Omit<Account, 'id'>) => void;
  updateAccount: (id: string, account: Partial<Account>) => void;
  deleteAccount: (id: string) => void;
  transactions: Transaction[];
  addTransaction: (transaction: Omit<Transaction, 'id'>) => void;
  updateTransaction: (id: string, transaction: Partial<Transaction>) => void;
  deleteTransaction: (id: string) => void;
  settings: AppSettings;
  updateSettings: (settings: Partial<AppSettings>) => void;
  prognosisReport: string | null;
  generatePrognosis: () => void;
  isAuthenticated: boolean;
  login: (email: string, password: string) => void;
  signup: (name: string, email: string, password: string) => void;
  logout: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [profile, setProfile] = useState<Profile>({
    age: 30,
    baseCurrency: 'USD',
    riskAppetite: 'Moderate',
    displayName: 'John Doe',
  });

  const [goals, setGoals] = useState<Goal[]>([
    {
      id: '1',
      name: 'Emergency Fund',
      targetAmount: 10000,
      targetDate: '2025-12-31',
      priority: 1,
      status: 'On Track',
    },
    {
      id: '2',
      name: 'Down Payment',
      targetAmount: 50000,
      targetDate: '2027-06-30',
      priority: 2,
      status: 'At Risk',
    },
  ]);

  const [accounts, setAccounts] = useState<Account[]>([
    { id: '1', name: 'Checking Account', type: 'Checking', currency: 'USD', balance: 5234.67 },
    { id: '2', name: 'Savings Account', type: 'Savings', currency: 'USD', balance: 12500.00 },
    { id: '3', name: 'Investment Portfolio', type: 'Investment', currency: 'USD', balance: 28750.50 },
  ]);

  const [transactions, setTransactions] = useState<Transaction[]>([
    {
      id: '1',
      date: '2026-02-10',
      label: 'Salary',
      description: 'Monthly salary',
      accountId: '1',
      type: 'Income',
      amount: 5000,
      currency: 'USD',
      isRecurring: true,
    },
    {
      id: '2',
      date: '2026-02-08',
      label: 'Rent',
      description: 'Monthly rent payment',
      accountId: '1',
      type: 'Expense',
      amount: 1500,
      currency: 'USD',
      isRecurring: true,
    },
    {
      id: '3',
      date: '2026-02-05',
      label: 'Groceries',
      description: 'Weekly groceries',
      accountId: '1',
      type: 'Expense',
      amount: 150,
      currency: 'USD',
      isRecurring: false,
    },
    {
      id: '4',
      date: '2026-02-01',
      label: 'Utilities',
      description: 'Electric and water',
      accountId: '1',
      type: 'Expense',
      amount: 200,
      currency: 'USD',
      isRecurring: true,
    },
  ]);

  const [settings, setSettings] = useState<AppSettings>({
    currencyFormat: 'symbol',
    notifications: true,
  });

  const [prognosisReport, setPrognosisReport] = useState<string | null>(null);

  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const updateProfile = (newProfile: Partial<Profile>) => {
    setProfile(prev => ({ ...prev, ...newProfile }));
  };

  const addGoal = (goal: Omit<Goal, 'id'>) => {
    const newGoal = { ...goal, id: Date.now().toString() };
    setGoals(prev => [...prev, newGoal]);
  };

  const updateGoal = (id: string, goal: Partial<Goal>) => {
    setGoals(prev => prev.map(g => g.id === id ? { ...g, ...goal } : g));
  };

  const deleteGoal = (id: string) => {
    setGoals(prev => prev.filter(g => g.id !== id));
  };

  const addAccount = (account: Omit<Account, 'id'>) => {
    const newAccount = { ...account, id: Date.now().toString() };
    setAccounts(prev => [...prev, newAccount]);
  };

  const updateAccount = (id: string, account: Partial<Account>) => {
    setAccounts(prev => prev.map(a => a.id === id ? { ...a, ...account } : a));
  };

  const deleteAccount = (id: string) => {
    setAccounts(prev => prev.filter(a => a.id !== id));
  };

  const addTransaction = (transaction: Omit<Transaction, 'id'>) => {
    const newTransaction = { ...transaction, id: Date.now().toString() };
    setTransactions(prev => [newTransaction, ...prev]);
  };

  const updateTransaction = (id: string, transaction: Partial<Transaction>) => {
    setTransactions(prev => prev.map(t => t.id === id ? { ...t, ...transaction } : t));
  };

  const deleteTransaction = (id: string) => {
    setTransactions(prev => prev.filter(t => t.id !== id));
  };

  const updateSettings = (newSettings: Partial<AppSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  const generatePrognosis = () => {
    // Mock AI report generation
    const report = `Based on your current financial data analysis (as of ${new Date().toLocaleDateString()}), here are your key insights:

**Summary:**
• Net Worth: $${(accounts.reduce((sum, acc) => sum + acc.balance, 0)).toLocaleString()}
• Monthly Income: $5,000
• Monthly Expenses: $1,850
• Savings Rate: 63%

**Insights:**

Your financial health is strong with a healthy savings rate of 63%. You're currently on track to meet your Emergency Fund goal by the end of 2025. However, your Down Payment goal may need adjustment or increased contributions to stay on schedule.

**Recommendations:**

1. Continue your current savings strategy for the Emergency Fund - you're making excellent progress.

2. Consider increasing monthly contributions to your Down Payment fund by $200-300 to improve your trajectory toward the 2027 target.

3. Your investment portfolio shows solid diversification. Given your Moderate risk appetite, consider reviewing your asset allocation quarterly.

4. You have strong expense discipline. Consider automating an additional 5% of income toward long-term investments to maximize compound growth.

**Next Steps:**

Review and adjust your Down Payment goal timeline or increase monthly contributions. Schedule a quarterly review of your investment portfolio performance.`;

    setPrognosisReport(report);
  };

  const login = (email: string, password: string) => {
    // Mock login logic
    setIsAuthenticated(true);
  };

  const signup = (name: string, email: string, password: string) => {
    // Mock signup logic
    setIsAuthenticated(true);
  };

  const logout = () => {
    // Mock logout logic
    setIsAuthenticated(false);
  };

  return (
    <AppContext.Provider
      value={{
        theme,
        toggleTheme,
        profile,
        updateProfile,
        goals,
        addGoal,
        updateGoal,
        deleteGoal,
        accounts,
        addAccount,
        updateAccount,
        deleteAccount,
        transactions,
        addTransaction,
        updateTransaction,
        deleteTransaction,
        settings,
        updateSettings,
        prognosisReport,
        generatePrognosis,
        isAuthenticated,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}