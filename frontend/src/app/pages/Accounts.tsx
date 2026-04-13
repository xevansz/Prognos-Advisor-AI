import React from 'react'
import { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import { useApp, convertToBase, type AccountType } from '../context/AppContext'
import { CURRENCIES, formatCurrency } from '../constants'
import { Plus, Trash2 } from 'lucide-react'

export function Accounts() {
  const { accounts, addAccount, deleteAccount, profile, fxRates } = useApp()
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [accountForm, setAccountForm] = useState({
    name: '',
    type: 'bank' as AccountType,
    currency: profile?.base_currency ?? 'INR',
    balance: '',
  })

  const handleSubmit = async () => {
    setSubmitError('')
    try {
      await addAccount({
        name: accountForm.name,
        type: accountForm.type,
        currency: accountForm.currency,
        initial_balance: accountForm.balance
          ? parseFloat(accountForm.balance)
          : undefined,
      })
      setAccountForm({
        name: '',
        type: 'checking',
        currency: profile?.base_currency ?? 'INR',
        balance: '',
      })
      setIsDialogOpen(false)
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : 'Failed to add account.'
      )
    }
  }

  const baseCurrency = profile?.base_currency ?? 'INR'
  const totalBalance = accounts.reduce(
    (sum, acc) =>
      sum + convertToBase(acc.balance, acc.currency, baseCurrency, fxRates),
    0
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-2">Accounts</h1>
          <p className="text-muted-foreground">
            Manage your financial accounts
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Account
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Account</DialogTitle>
              <DialogDescription>
                Create a new account to track your finances
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="accountName">Account Name</Label>
                <Input
                  id="accountName"
                  value={accountForm.name}
                  onChange={(e) =>
                    setAccountForm({ ...accountForm, name: e.target.value })
                  }
                  placeholder="e.g., Primary Checking"
                />
              </div>
              <div className="grid gap-4 grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="accountType">Account Type</Label>
                  <Select
                    value={accountForm.type}
                    onValueChange={(value) =>
                      setAccountForm({
                        ...accountForm,
                        type: value as AccountType,
                      })
                    }
                  >
                    <SelectTrigger id="accountType">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bank">Bank</SelectItem>
                      <SelectItem value="cash">Cash</SelectItem>
                      <SelectItem value="holdings">Holdings</SelectItem>
                      <SelectItem value="crypto">Crypto</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="accountCurrency">Currency</Label>
                  <Select
                    value={accountForm.currency}
                    onValueChange={(value) =>
                      setAccountForm({ ...accountForm, currency: value })
                    }
                  >
                    <SelectTrigger id="accountCurrency">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="max-h-60">
                      {CURRENCIES.map((c) => (
                        <SelectItem key={c.code} value={c.code}>
                          {c.code} ({c.symbol})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="initialBalance">Initial Balance</Label>
                <Input
                  id="initialBalance"
                  inputMode="decimal"
                  type="text"
                  step="0.01"
                  value={accountForm.balance}
                  onChange={(e) =>
                    setAccountForm({ ...accountForm, balance: e.target.value })
                  }
                  placeholder="0.00"
                />
              </div>
            </div>
            <DialogFooter>
              {submitError && (
                <p className="text-sm text-destructive w-full">{submitError}</p>
              )}
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSubmit}>Add Account</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Total Balance</CardTitle>
          <CardDescription>Across all accounts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {formatCurrency(totalBalance, baseCurrency)}
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Your Accounts</CardTitle>
          <CardDescription>
            View and manage all your financial accounts
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Desktop table view */}
          <div className="hidden md:block rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Currency</TableHead>
                  <TableHead className="text-right">Balance</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {accounts.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={5}
                      className="text-center text-muted-foreground py-8"
                    >
                      No accounts yet. Add your first account to get started.
                    </TableCell>
                  </TableRow>
                ) : (
                  accounts.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell className="font-medium">
                        {account.name}
                      </TableCell>
                      <TableCell>{account.type}</TableCell>
                      <TableCell>{account.currency}</TableCell>
                      <TableCell className="text-right font-mono">
                        {formatCurrency(account.balance, account.currency)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteAccount(account.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* Mobile card view */}
          <div className="md:hidden space-y-3">
            {accounts.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No accounts yet. Add your first account to get started.
              </div>
            ) : (
              accounts.map((account) => (
                <div
                  key={account.id}
                  className="border rounded-lg p-4 space-y-2"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-medium">{account.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {account.type} • {account.currency}
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteAccount(account.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                  <div className="text-xl font-bold font-mono">
                    {formatCurrency(account.balance, account.currency)}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
