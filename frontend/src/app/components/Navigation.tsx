import React from 'react'
import { NavLink } from 'react-router'
import { Wallet, Menu, X, Brain } from 'lucide-react'
import { useState } from 'react'
import { Button } from './ui/button'
import { ThemeToggle } from './ThemeToggle'

const pageNavItems = [
  { path: '/dashboard', label: 'Overview' },
  { path: '/dashboard/accounts', label: 'Accounts' },
  { path: '/dashboard/transactions', label: 'Transactions' },
  { path: '/dashboard/profile', label: 'Profile' },
  { path: '/dashboard/settings', label: 'Settings' },
]

export function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Left: Logo + page nav */}
          <div className="flex items-center gap-6">
            {/* Logo — clicking does nothing when logged in (dashboard) */}
            <div className="flex items-center gap-2 select-none">
              <div className="rounded-lg bg-primary p-2">
                <Wallet className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-semibold">Prognosis AI</span>
            </div>

            <div className="hidden md:flex items-center gap-1">
              {pageNavItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/dashboard'}
                  className={({ isActive }) =>
                    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-accent text-accent-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          </div>

          {/* Right: Prognosis AI link + theme toggle + mobile toggle */}
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <NavLink
              to="/dashboard/prognosis"
              className={({ isActive }) =>
                `hidden md:flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                }`
              }
            >
              <Brain className="h-4 w-4" />
              Prognosis Report
            </NavLink>

            <div className="md:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? (
                  <X className="h-5 w-5" />
                ) : (
                  <Menu className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-1 border-t border-border">
            {pageNavItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/dashboard'}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `block px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-accent text-accent-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
            <ThemeToggle />
            <NavLink
              to="/dashboard/prognosis"
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                }`
              }
            >
              <Brain className="h-4 w-4" />
              Prognosis Report
            </NavLink>
            <div className="flex items-center justify-between px-4 py-2">
              <span className="text-sm font-medium text-muted-foreground">
                Theme
              </span>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
