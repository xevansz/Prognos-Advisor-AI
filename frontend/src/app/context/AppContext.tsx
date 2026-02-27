import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { supabase } from "../../lib/supabase";
import {
  accountsApi,
  fxApi,
  goalsApi,
  prognosisApi,
  profileApi,
  transactionsApi,
  type AccountCreate,
  type AccountOut,
  type AccountType,
  type GoalCreate,
  type GoalOut,
  type GoalPriority,
  type GoalUpdate,
  type ProfileOut,
  type ProfileUpsert,
  type PrognosisReport,
  type TransactionCreate,
  type TransactionOut,
  type TransactionType,
  type TransactionUpdate,
} from "../../lib/api";

// ── Re-export types used by pages ────────────────────────────────────────────
export type RiskAppetite = "conservative" | "moderate" | "aggressive";
export type { AccountType, GoalPriority, TransactionType };
export type { AccountOut as Account };
export type { TransactionOut as Transaction };
export type { GoalOut as Goal };
export type { ProfileOut as Profile };

// ── FX helper ────────────────────────────────────────────────────────────────
export function convertToBase(
  amount: number,
  fromCurrency: string,
  baseCurrency: string,
  rates: Record<string, number>,
): number {
  if (fromCurrency === baseCurrency) return amount;
  const toBase = rates[baseCurrency];
  const fromBase = rates[fromCurrency];
  if (!toBase || !fromBase) return amount;
  return (amount / fromBase) * toBase;
}

// ── Settings ─────────────────────────────────────────────────────────────────
interface AppSettings {
  currencyFormat: "symbol" | "code";
  notifications: boolean;
}

// ── Context type ──────────────────────────────────────────────────────────────
interface AppContextType {
  theme: "light" | "dark";
  toggleTheme: () => void;

  isAuthenticated: boolean;
  authLoading: boolean;
  userEmail: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;

  profile: ProfileOut | null;
  profileLoading: boolean;
  saveProfile: (data: ProfileUpsert) => Promise<void>;

  goals: GoalOut[];
  goalsLoading: boolean;
  addGoal: (goal: GoalCreate) => Promise<void>;
  updateGoal: (id: string, goal: GoalUpdate) => Promise<void>;
  deleteGoal: (id: string) => Promise<void>;

  accounts: AccountOut[];
  accountsLoading: boolean;
  addAccount: (account: AccountCreate) => Promise<void>;
  deleteAccount: (id: string) => Promise<void>;

  transactions: TransactionOut[];
  transactionsLoading: boolean;
  addTransaction: (transaction: TransactionCreate) => Promise<void>;
  updateTransaction: (
    id: string,
    transaction: TransactionUpdate,
  ) => Promise<void>;
  deleteTransaction: (id: string) => Promise<void>;

  settings: AppSettings;
  updateSettings: (settings: Partial<AppSettings>) => void;

  fxRates: Record<string, number>;

  prognosisReport: PrognosisReport | null;
  prognosisLoading: boolean;
  generatePrognosis: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  // ── Theme ──────────────────────────────────────────────────────────────────
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    try {
      return (
        (localStorage.getItem("prognosis-theme") as "light" | "dark") || "dark"
      );
    } catch {
      return "dark";
    }
  });

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => {
      const next = prev === "light" ? "dark" : "light";
      try {
        localStorage.setItem("prognosis-theme", next);
      } catch {}
      return next;
    });
  };

  // ── Auth ───────────────────────────────────────────────────────────────────
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      const session = data.session;
      setIsAuthenticated(!!session);
      setUserEmail(session?.user.email ?? null);
      setAuthLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setIsAuthenticated(!!session);
        setUserEmail(session?.user.email ?? null);
      },
    );
    return () => listener.subscription.unsubscribe();
  }, []);

  const login = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw new Error(error.message);
  };

  const signup = async (name: string, email: string, password: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { display_name: name } },
    });
    if (error) throw new Error(error.message);
  };

  const logout = async () => {
    await supabase.auth.signOut();
  };

  // ── Profile ────────────────────────────────────────────────────────────────
  const [profile, setProfile] = useState<ProfileOut | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const fetchProfile = useCallback(async () => {
    setProfileLoading(true);
    try {
      const data = await profileApi.get();
      setProfile(data);
    } catch {
      setProfile(null);
    } finally {
      setProfileLoading(false);
    }
  }, []);

  const saveProfile = async (data: ProfileUpsert) => {
    const updated = await profileApi.upsert(data);
    setProfile(updated);
  };

  // ── Goals ──────────────────────────────────────────────────────────────────
  const [goals, setGoals] = useState<GoalOut[]>([]);
  const [goalsLoading, setGoalsLoading] = useState(false);

  const fetchGoals = useCallback(async () => {
    setGoalsLoading(true);
    try {
      const data = await goalsApi.list();
      setGoals(data);
    } catch {
      setGoals([]);
    } finally {
      setGoalsLoading(false);
    }
  }, []);

  const addGoal = async (goal: GoalCreate) => {
    const created = await goalsApi.create(goal);
    setGoals((prev) => [...prev, created]);
  };

  const updateGoal = async (id: string, goal: GoalUpdate) => {
    const updated = await goalsApi.update(id, goal);
    setGoals((prev) => prev.map((g) => (g.id === id ? updated : g)));
  };

  const deleteGoal = async (id: string) => {
    await goalsApi.delete(id);
    setGoals((prev) => prev.filter((g) => g.id !== id));
  };

  // ── Accounts ───────────────────────────────────────────────────────────────
  const [accounts, setAccounts] = useState<AccountOut[]>([]);
  const [accountsLoading, setAccountsLoading] = useState(false);

  const fetchAccounts = useCallback(async () => {
    setAccountsLoading(true);
    try {
      const data = await accountsApi.list();
      setAccounts(data);
    } catch {
      setAccounts([]);
    } finally {
      setAccountsLoading(false);
    }
  }, []);

  const addAccount = async (account: AccountCreate) => {
    const created = await accountsApi.create(account);
    setAccounts((prev) => [...prev, created]);
  };

  const deleteAccount = async (id: string) => {
    await accountsApi.delete(id);
    setAccounts((prev) => prev.filter((a) => a.id !== id));
  };

  // ── Transactions ───────────────────────────────────────────────────────────
  const [transactions, setTransactions] = useState<TransactionOut[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);

  const fetchTransactions = useCallback(async () => {
    setTransactionsLoading(true);
    try {
      const data = await transactionsApi.list();
      setTransactions(data);
    } catch {
      setTransactions([]);
    } finally {
      setTransactionsLoading(false);
    }
  }, []);

  const addTransaction = async (transaction: TransactionCreate) => {
    const created = await transactionsApi.create(transaction);
    setTransactions((prev) => [created, ...prev]);
  };

  const updateTransaction = async (
    id: string,
    transaction: TransactionUpdate,
  ) => {
    const updated = await transactionsApi.update(id, transaction);
    setTransactions((prev) => prev.map((t) => (t.id === id ? updated : t)));
  };

  const deleteTransaction = async (id: string) => {
    await transactionsApi.delete(id);
    setTransactions((prev) => prev.filter((t) => t.id !== id));
  };

  // ── FX Rates ───────────────────────────────────────────────────────────────
  const [fxRates, setFxRates] = useState<Record<string, number>>({});

  const fetchFxRates = useCallback(async (baseCurrency: string) => {
    try {
      const data = await fxApi.getRates(baseCurrency);
      setFxRates(data.rates);
    } catch {
      setFxRates({});
    }
  }, []);

  // ── Prognosis ──────────────────────────────────────────────────────────────
  const [prognosisReport, setPrognosisReport] =
    useState<PrognosisReport | null>(null);
  const [prognosisLoading, setPrognosisLoading] = useState(false);

  const fetchLatestPrognosis = useCallback(async () => {
    try {
      const data = await prognosisApi.current();
      setPrognosisReport(data);
    } catch {
      setPrognosisReport(null);
    }
  }, []);

  const generatePrognosis = async () => {
    setPrognosisLoading(true);
    try {
      const report = await prognosisApi.generate();
      setPrognosisReport(report);
    } finally {
      setPrognosisLoading(false);
    }
  };

  // ── Settings ───────────────────────────────────────────────────────────────
  const [settings, setSettings] = useState<AppSettings>({
    currencyFormat: "symbol",
    notifications: true,
  });

  const updateSettings = (newSettings: Partial<AppSettings>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  };

  // ── Load data when authenticated ───────────────────────────────────────────
  useEffect(() => {
    if (!isAuthenticated) {
      setProfile(null);
      setGoals([]);
      setAccounts([]);
      setTransactions([]);
      setPrognosisReport(null);
      setFxRates({});
      return;
    }
    fetchProfile();
    fetchGoals();
    fetchAccounts();
    fetchTransactions();
    fetchLatestPrognosis();
  }, [
    isAuthenticated,
    fetchProfile,
    fetchGoals,
    fetchAccounts,
    fetchTransactions,
    fetchLatestPrognosis,
  ]);

  // Fetch FX rates when profile (and thus baseCurrency) is known
  useEffect(() => {
    if (profile?.base_currency) {
      fetchFxRates(profile.base_currency);
    }
  }, [profile?.base_currency, fetchFxRates]);

  return (
    <AppContext.Provider
      value={{
        theme,
        toggleTheme,
        isAuthenticated,
        authLoading,
        userEmail,
        login,
        signup,
        logout,
        profile,
        profileLoading,
        saveProfile,
        goals,
        goalsLoading,
        addGoal,
        updateGoal,
        deleteGoal,
        accounts,
        accountsLoading,
        addAccount,
        deleteAccount,
        transactions,
        transactionsLoading,
        addTransaction,
        updateTransaction,
        deleteTransaction,
        settings,
        updateSettings,
        fxRates,
        prognosisReport,
        prognosisLoading,
        generatePrognosis,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within AppProvider");
  }
  return context;
}
