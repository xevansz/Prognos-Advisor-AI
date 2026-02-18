import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Switch } from '../components/ui/switch';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { useApp } from '../context/AppContext';
import { Plus, Pencil, Trash2, Filter, RepeatIcon } from 'lucide-react';

export function Transactions() {
  const { transactions, accounts, addTransaction, updateTransaction, deleteTransaction } = useApp();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    accountId: 'all',
    type: 'all',
    recurring: 'all',
  });
  const [transactionForm, setTransactionForm] = useState({
    accountId: accounts[0]?.id || '',
    label: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    amount: '',
    type: 'Expense' as 'Income' | 'Expense',
    currency: 'USD',
    isRecurring: false,
  });

  const openDialog = (transactionId?: string) => {
    if (transactionId) {
      const transaction = transactions.find(t => t.id === transactionId);
      if (transaction) {
        setTransactionForm({
          accountId: transaction.accountId,
          label: transaction.label,
          description: transaction.description,
          date: transaction.date,
          amount: transaction.amount.toString(),
          type: transaction.type,
          currency: transaction.currency,
          isRecurring: transaction.isRecurring,
        });
        setEditingTransaction(transactionId);
      }
    } else {
      setTransactionForm({
        accountId: accounts[0]?.id || '',
        label: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        amount: '',
        type: 'Expense',
        currency: 'USD',
        isRecurring: false,
      });
      setEditingTransaction(null);
    }
    setIsDialogOpen(true);
  };

  const handleSubmit = () => {
    if (editingTransaction) {
      updateTransaction(editingTransaction, {
        accountId: transactionForm.accountId,
        label: transactionForm.label,
        description: transactionForm.description,
        date: transactionForm.date,
        amount: parseFloat(transactionForm.amount),
        type: transactionForm.type,
        currency: transactionForm.currency,
        isRecurring: transactionForm.isRecurring,
      });
    } else {
      addTransaction({
        accountId: transactionForm.accountId,
        label: transactionForm.label,
        description: transactionForm.description,
        date: transactionForm.date,
        amount: parseFloat(transactionForm.amount),
        type: transactionForm.type,
        currency: transactionForm.currency,
        isRecurring: transactionForm.isRecurring,
      });
    }
    setIsDialogOpen(false);
  };

  const filteredTransactions = transactions.filter(transaction => {
    if (filters.accountId !== 'all' && transaction.accountId !== filters.accountId) return false;
    if (filters.type !== 'all' && transaction.type !== filters.type) return false;
    if (filters.recurring !== 'all') {
      const isRecurring = filters.recurring === 'true';
      if (transaction.isRecurring !== isRecurring) return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-2">Transactions</h1>
          <p className="text-muted-foreground">Track your income and expenses</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => openDialog()}>
                <Plus className="h-4 w-4 mr-2" />
                Create Transaction
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{editingTransaction ? 'Edit Transaction' : 'Create Transaction'}</DialogTitle>
                <DialogDescription>
                  {editingTransaction ? 'Update transaction details' : 'Add a new transaction to your account'}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="account">Account</Label>
                  <Select value={transactionForm.accountId} onValueChange={(value) => setTransactionForm({ ...transactionForm, accountId: value })}>
                    <SelectTrigger id="account">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {accounts.map(account => (
                        <SelectItem key={account.id} value={account.id}>
                          {account.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="label">Label</Label>
                  <Input
                    id="label"
                    value={transactionForm.label}
                    onChange={(e) => setTransactionForm({ ...transactionForm, label: e.target.value })}
                    placeholder="e.g., Groceries"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={transactionForm.description}
                    onChange={(e) => setTransactionForm({ ...transactionForm, description: e.target.value })}
                    placeholder="Optional details..."
                    rows={2}
                  />
                </div>
                <div className="grid gap-4 grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      value={transactionForm.date}
                      onChange={(e) => setTransactionForm({ ...transactionForm, date: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount</Label>
                    <Input
                      id="amount"
                      type="number"
                      step="0.01"
                      value={transactionForm.amount}
                      onChange={(e) => setTransactionForm({ ...transactionForm, amount: e.target.value })}
                      placeholder="0.00"
                    />
                  </div>
                </div>
                <div className="grid gap-4 grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="type">Type</Label>
                    <Select value={transactionForm.type} onValueChange={(value: 'Income' | 'Expense') => setTransactionForm({ ...transactionForm, type: value })}>
                      <SelectTrigger id="type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Income">Income</SelectItem>
                        <SelectItem value="Expense">Expense</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="currency">Currency</Label>
                    <Select value={transactionForm.currency} onValueChange={(value) => setTransactionForm({ ...transactionForm, currency: value })}>
                      <SelectTrigger id="currency">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD">USD</SelectItem>
                        <SelectItem value="EUR">EUR</SelectItem>
                        <SelectItem value="GBP">GBP</SelectItem>
                        <SelectItem value="JPY">JPY</SelectItem>
                        <SelectItem value="AUD">AUD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="recurring">Recurring (Monthly)</Label>
                    <div className="text-sm text-muted-foreground">
                      This transaction repeats monthly
                    </div>
                  </div>
                  <Switch
                    id="recurring"
                    checked={transactionForm.isRecurring}
                    onCheckedChange={(checked) => setTransactionForm({ ...transactionForm, isRecurring: checked })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSubmit}>
                  {editingTransaction ? 'Update' : 'Create'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {showFilters && (
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="filterAccount">Account</Label>
                <Select value={filters.accountId} onValueChange={(value) => setFilters({ ...filters, accountId: value })}>
                  <SelectTrigger id="filterAccount">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Accounts</SelectItem>
                    {accounts.map(account => (
                      <SelectItem key={account.id} value={account.id}>
                        {account.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="filterType">Type</Label>
                <Select value={filters.type} onValueChange={(value) => setFilters({ ...filters, type: value })}>
                  <SelectTrigger id="filterType">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="Income">Income</SelectItem>
                    <SelectItem value="Expense">Expense</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="filterRecurring">Recurring</Label>
                <Select value={filters.recurring} onValueChange={(value) => setFilters({ ...filters, recurring: value })}>
                  <SelectTrigger id="filterRecurring">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="true">Recurring Only</SelectItem>
                    <SelectItem value="false">One-time Only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Transaction History</CardTitle>
          <CardDescription>All your financial transactions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="min-w-[100px]">Date</TableHead>
                  <TableHead className="min-w-[120px]">Label</TableHead>
                  <TableHead className="min-w-[120px]">Account</TableHead>
                  <TableHead className="min-w-[80px]">Type</TableHead>
                  <TableHead className="text-right min-w-[100px]">Amount</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTransactions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                      No transactions found.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredTransactions.map((transaction) => {
                    const account = accounts.find(a => a.id === transaction.accountId);
                    return (
                      <TableRow key={transaction.id}>
                        <TableCell className="font-medium">{transaction.date}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span className="truncate max-w-[150px]">{transaction.label}</span>
                            {transaction.isRecurring && (
                              <Badge variant="outline" className="text-xs whitespace-nowrap">
                                <RepeatIcon className="h-3 w-3 mr-1" />
                                Recurring
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>{account?.name || 'Unknown'}</TableCell>
                        <TableCell>
                          <Badge
                            variant={transaction.type === 'Income' ? 'default' : 'secondary'}
                            className={transaction.type === 'Income' ? 'bg-[hsl(var(--success))]' : ''}
                          >
                            {transaction.type}
                          </Badge>
                        </TableCell>
                        <TableCell className={`text-right font-mono font-semibold whitespace-nowrap ${
                          transaction.type === 'Income' 
                            ? 'text-[hsl(var(--success))]' 
                            : 'text-[hsl(var(--destructive))]'
                        }`}>
                          {transaction.type === 'Income' ? '+' : '-'}${transaction.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openDialog(transaction.id)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteTransaction(transaction.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}