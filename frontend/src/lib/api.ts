import { supabase } from './supabase'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function authHeaders(): Promise<Record<string, string>> {
  const {
    data: { session },
  } = await supabase.auth.getSession()
  if (!session) throw new Error('Not authenticated')
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${session.access_token}`,
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const headers = await authHeaders()
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (res.status === 204) return undefined as T
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText)
    throw new Error(detail || `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

// ─── Enums / literal types ────────────────────────────────────────────────────

export type AccountType = 'bank' | 'cash' | 'holdings' | 'crypto' | 'other'
export type TransactionType = 'debit' | 'credit'
export type GoalPriority = 'high' | 'medium' | 'low'
export type RiskAppetite = 'conservative' | 'moderate' | 'aggressive'

// ─── Accounts ────────────────────────────────────────────────────────────────

export interface AccountCreate {
  name: string
  type: AccountType
  currency: string
  initial_balance?: number
}

export interface AccountOut {
  id: string
  user_id: string
  name: string
  type: AccountType
  currency: string
  balance: number
  generated_at: string
  updated_at: string
}

export const accountsApi = {
  list: () => request<AccountOut[]>('GET', '/api/accounts'),
  get: (id: string) => request<AccountOut>('GET', `/api/accounts/${id}`),
  create: (payload: AccountCreate) =>
    request<AccountOut>('POST', '/api/accounts', payload),
  delete: (id: string) => request<void>('DELETE', `/api/accounts/${id}`),
}

// ─── Transactions ─────────────────────────────────────────────────────────────

export interface TransactionCreate {
  account_id: string
  label: string
  description?: string | null
  date: string
  amount: number
  type: TransactionType
  currency?: string
  is_recurring?: boolean
}

export interface TransactionUpdate {
  label?: string | null
  description?: string | null
  date?: string | null
  amount?: number | null
  type?: TransactionType | null
  account_id?: string | null
}

export interface TransactionOut {
  id: string
  user_id: string
  account_id: string
  label: string
  description: string | null
  date: string
  amount: number
  type: TransactionType
  currency: string
  is_recurring: boolean
  recurrence_rule_id: string | null
  generated_at: string
  updated_at: string
}

export const transactionsApi = {
  list: () => request<TransactionOut[]>('GET', '/api/transactions?limit=1000'),
  get: (id: string) =>
    request<TransactionOut>('GET', `/api/transactions/${id}`),
  create: (payload: TransactionCreate) =>
    request<TransactionOut>('POST', '/api/transactions', payload),
  update: (id: string, payload: TransactionUpdate) =>
    request<TransactionOut>('PUT', `/api/transactions/${id}`, payload),
  delete: (id: string) => request<void>('DELETE', `/api/transactions/${id}`),
}

// ─── Goals ────────────────────────────────────────────────────────────────────

export interface GoalCreate {
  name: string
  target_amount: number
  target_currency: string
  target_date: string
  priority: GoalPriority
}

export interface GoalUpdate {
  name?: string | null
  target_amount?: number | null
  target_currency?: string | null
  target_date?: string | null
  priority?: GoalPriority | null
}

export interface GoalOut {
  id: string
  user_id: string
  name: string
  target_amount: number
  target_currency: string
  target_date: string
  priority: GoalPriority
  generated_at: string
  updated_at: string
}

export const goalsApi = {
  list: () => request<GoalOut[]>('GET', '/api/goals'),
  get: (id: string) => request<GoalOut>('GET', `/api/goals/${id}`),
  create: (payload: GoalCreate) =>
    request<GoalOut>('POST', '/api/goals', payload),
  update: (id: string, payload: GoalUpdate) =>
    request<GoalOut>('PUT', `/api/goals/${id}`, payload),
  delete: (id: string) => request<void>('DELETE', `/api/goals/${id}`),
}

// ─── Profile ──────────────────────────────────────────────────────────────────

export interface ProfileUpsert {
  age: number
  display_name?: string | null
  gender?: string | null
  base_currency: string
  risk_appetite: RiskAppetite
}

export interface ProfileOut {
  id: string
  user_id: string
  age: number
  display_name: string | null
  gender: string | null
  base_currency: string
  risk_appetite: RiskAppetite
  generated_at: string
  updated_at: string
}

export const profileApi = {
  get: () => request<ProfileOut | null>('GET', '/api/profile'),
  upsert: (payload: ProfileUpsert) =>
    request<ProfileOut>('PUT', '/api/profile', payload),
}

// ─── Prognosis ────────────────────────────────────────────────────────────────

export interface PrognosisReport {
  report_json: Record<string, unknown>
  generated_at: string
  rate_limited: boolean
}

export const prognosisApi = {
  current: () =>
    request<PrognosisReport | null>('GET', '/api/prognosis/current'),
  generate: () => request<PrognosisReport>('POST', '/api/prognosis/refresh'),
}

// ─── FX Rates ─────────────────────────────────────────────────────────────────

export interface FxRatesResponse {
  base: string
  rates: Record<string, number>
}

export const fxApi = {
  getRates: (base: string) =>
    request<FxRatesResponse>('GET', `/api/fx-rates?base=${base}`),
}
