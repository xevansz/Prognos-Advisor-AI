#!/usr/bin/env python3
"""
Seed script to populate database with realistic transactions for a high-income
urban Indian professional.

Profile:
  - Monthly salary: ₹2,50,000 (credited to Salary Account)
  - Accounts: Salary Account (primary), Savings Account (rare transfers), Cash Wallet
  - Cash maintained at ₹5,000; ATM withdrawal only when cash hits ₹0
  - 90% digital (salary account), 10% cash, 5% savings account (rare)
  - Expenses ~55-65% of salary; occasional large spends (travel, shopping, medical)

Usage:
    cd backend
    python seed_data.py
"""

import asyncio
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from db import SessionLocal
from models.enums import AccountType, TransactionType
from schemas.account import AccountCreate
from schemas.transaction import TransactionCreate
from services.account_service import create_account
from services.transaction_service import create_transaction

# ── Configuration ─────────────────────────────────────────────────────────────

USER_ID = ""  # uuid here
CURRENCY = "INR"
MONTHLY_SALARY = Decimal("")  # 250000.00
CASH_RESERVE = Decimal("5000.00")  # Target cash balance; top-up when depleted

# ── Account definitions ────────────────────────────────────────────────────────

ACCOUNTS_CONFIG = [
    {
        "name": "Salary Account",
        "type": AccountType.BANK,
        "initial_balance": Decimal("150000.00"),
    },
    {
        "name": "Savings Account",
        "type": AccountType.BANK,
        "initial_balance": Decimal("500000.00"),
    },
    {
        "name": "Cash Wallet",
        "type": AccountType.CASH,
        "initial_balance": CASH_RESERVE,
    },
]

# ── Expense categories ─────────────────────────────────────────────────────────
# Each entry: (monthly_base_amount, variance_pct, day_range, subtransaction_templates)
# subtransaction_templates: list of (label, description_fmt) for splitting the category
# into multiple realistic line items.  Split amounts are randomised proportionally.

EXPENSE_CATEGORIES = [
    # (base_amount, variance%, (day_start, day_end), [(label, desc), ...])
    (
        Decimal("55000.00"),
        2,
        (1, 3),
        [("House Rent", "Monthly rent payment")],
    ),
    (
        Decimal("4000.00"),
        8,
        (1, 5),
        [("Electricity Bill", "BESCOM electricity bill"), ("Water Bill", "BWSSB water charges")],
    ),
    (
        Decimal("1500.00"),
        5,
        (5, 10),
        [("Internet Bill", "Broadband monthly plan"), ("Mobile Recharge", "Postpaid bill payment")],
    ),
    (
        Decimal("2500.00"),
        10,
        (1, 5),
        [("Term Insurance", "LIC term insurance premium"), ("Health Insurance", "Star Health premium debit")],
    ),
    (
        Decimal("25000.00"),
        12,
        (1, 28),
        [
            ("Big Basket", "Online grocery order"),
            ("Zepto Groceries", "Quick commerce grocery"),
            ("DMart", "Monthly grocery run"),
            ("Nilgiris", "Fresh produce purchase"),
        ],
    ),
    (
        Decimal("8000.00"),
        15,
        (1, 28),
        [
            ("Ola/Uber Ride", "Cab fare"),
            ("Metro Card Recharge", "BMTC/Metro top-up"),
            ("Rapido Auto", "Auto fare"),
            ("Fuel - Shell", "Petrol station"),
        ],
    ),
    (
        Decimal("12000.00"),
        18,
        (1, 28),
        [
            ("Swiggy Order", "Food delivery"),
            ("Zomato Order", "Food delivery"),
            ("Restaurant Dining", "Dine-in meal"),
            ("Cafe Coffee Day", "Coffee & snacks"),
            ("Barbeque Nation", "Dinner outing"),
        ],
    ),
    (
        Decimal("5000.00"),
        20,
        (1, 28),
        [
            ("Netflix", "Monthly subscription"),
            ("Spotify Premium", "Music subscription"),
            ("Amazon Prime", "Prime membership"),
            ("BookMyShow", "Movie tickets"),
            ("Steam / Game Purchase", "Gaming"),
        ],
    ),
    (
        Decimal("3000.00"),
        25,
        (1, 28),
        [
            ("Apollo Pharmacy", "Medicine purchase"),
            ("Lab Test", "Diagnostic test fees"),
            ("Doctor Consultation", "Clinic visit"),
        ],
    ),
    (
        Decimal("4000.00"),
        20,
        (1, 28),
        [
            ("Myntra", "Clothing order"),
            ("Amazon Purchase", "Online shopping"),
            ("Decathlon", "Sports gear"),
            ("Croma", "Electronics accessories"),
        ],
    ),
]

# Occasional large spends — triggered randomly once per few months
OCCASIONAL_EXPENSES = [
    (Decimal("30000.00"), Decimal("60000.00"), "Flight Tickets", "Round trip flight booking"),
    (Decimal("15000.00"), Decimal("35000.00"), "Hotel Stay", "Hotel booking via MMT"),
    (Decimal("8000.00"), Decimal("20000.00"), "Medical Bill", "Hospital / specialist bill"),
    (Decimal("10000.00"), Decimal("30000.00"), "Electronics", "Gadget / appliance purchase"),
    (Decimal("5000.00"), Decimal("15000.00"), "Clothing Haul", "Seasonal wardrobe refresh"),
    (Decimal("20000.00"), Decimal("50000.00"), "Festival Shopping", "Festive season purchases"),
]

# ── Helpers ────────────────────────────────────────────────────────────────────


def rand_amount(base: Decimal, variance_pct: int) -> Decimal:
    factor = 1 + random.uniform(-variance_pct, variance_pct) / 100
    return Decimal(str(round(float(base) * factor, 2)))


def rand_date(year: int, month: int, day_start: int, day_end: int) -> date:
    last_day = (date(year, month % 12 + 1, 1) - timedelta(days=1)).day
    end = min(day_end, last_day)
    start = min(day_start, end)
    return date(year, month, random.randint(start, end))


def split_proportionally(total: Decimal, n: int) -> list[Decimal]:
    """Split total into n random proportions that sum to total."""
    cuts = sorted(random.uniform(0, 1) for _ in range(n - 1))
    cuts = [0.0] + cuts + [1.0]
    parts = [Decimal(str(round(float(total) * (cuts[i + 1] - cuts[i]), 2))) for i in range(n)]
    # Adjust rounding difference on last element
    diff = total - sum(parts)
    parts[-1] += diff
    return parts


async def _tx(
    db: AsyncSession,
    account_id: str,
    label: str,
    description: str,
    tx_date: date,
    amount: Decimal,
    tx_type: TransactionType,
) -> None:
    await create_transaction(
        db,
        USER_ID,
        TransactionCreate(
            account_id=account_id,
            label=label,
            description=description,
            date=tx_date,
            amount=amount,
            type=tx_type,
            currency=CURRENCY,
            is_recurring=False,
        ),
    )


# ── Account creation ───────────────────────────────────────────────────────────


async def create_accounts(db: AsyncSession) -> dict[str, str]:
    account_ids: dict[str, str] = {}
    print("Creating accounts...")
    for config in ACCOUNTS_CONFIG:
        account = await create_account(
            db,
            USER_ID,
            AccountCreate(
                name=config["name"],
                type=config["type"],
                currency=CURRENCY,
                initial_balance=config["initial_balance"],
            ),
        )
        account_ids[config["name"]] = str(account.id)
        print(f"  ✓ {config['name']} ({config['type'].value}) — ID: {account.id}")
    return account_ids


# ── Monthly transaction generator ─────────────────────────────────────────────


async def create_monthly_transactions(
    db: AsyncSession,
    account_ids: dict[str, str],
    year: int,
    month: int,
    cash_balance: Decimal,
) -> tuple[int, Decimal]:
    """
    Create all transactions for one month.
    Returns (transaction_count, updated_cash_balance).
    """
    count = 0
    salary_id = account_ids["Salary Account"]
    savings_id = account_ids["Savings Account"]
    cash_id = account_ids["Cash Wallet"]

    # ── 1. Salary credit (1st–3rd of month) ───────────────────────────────────
    salary_date = rand_date(year, month, 1, 3)
    await _tx(
        db,
        salary_id,
        "Salary Credit",
        f"Monthly salary — {date(year, month, 1).strftime('%B %Y')}",
        salary_date,
        MONTHLY_SALARY,
        TransactionType.CREDIT,
    )
    count += 1

    # ── 2. Fixed / recurring expenses via Salary Account ──────────────────────
    for base_amount, var_pct, (d_start, d_end), templates in EXPENSE_CATEGORIES:
        monthly_total = rand_amount(base_amount, var_pct)
        amounts = split_proportionally(monthly_total, len(templates))

        for (label, desc), amount in zip(templates, amounts, strict=False):
            if amount <= 0:
                continue

            # Payment method selection: 90% salary account, 5% savings, 5% cash
            roll = random.random()
            if roll < 0.05:
                # Rare savings account payment
                account_id = savings_id
                payment_desc = f"{desc} (via Savings Account)"
            elif roll < 0.10:
                # Cash payment — only if cash is sufficient, else use salary account
                if cash_balance >= amount:
                    account_id = cash_id
                    cash_balance -= amount
                    payment_desc = f"{desc} (cash)"
                else:
                    account_id = salary_id
                    payment_desc = f"{desc} (UPI)"
            else:
                account_id = salary_id
                payment_desc = f"{desc} (UPI/card)"

            tx_date = rand_date(year, month, d_start, d_end)
            await _tx(db, account_id, label, payment_desc, tx_date, amount, TransactionType.DEBIT)
            count += 1

    # ── 3. Occasional large expense (≈35% chance per month) ───────────────────
    if random.random() < 0.35:
        lo, hi, label, desc = random.choice(OCCASIONAL_EXPENSES)
        amount = Decimal(str(round(random.uniform(float(lo), float(hi)), 2)))
        tx_date = rand_date(year, month, 5, 28)
        # Large purchases always go via Salary Account
        await _tx(db, salary_id, label, desc, tx_date, amount, TransactionType.DEBIT)
        count += 1

    # ── 4. Cash top-up when wallet is depleted ────────────────────────────────
    if cash_balance <= 0:
        topup = CASH_RESERVE  # Restore to ₹5,000 exactly
        topup_date = rand_date(year, month, 1, 28)
        # Debit salary account (ATM withdrawal)
        await _tx(
            db,
            salary_id,
            "ATM Withdrawal",
            f"Cash withdrawal — {date(year, month, 1).strftime('%B %Y')}",
            topup_date,
            topup,
            TransactionType.DEBIT,
        )
        # Credit cash wallet
        await _tx(
            db,
            cash_id,
            "ATM Cash Received",
            f"Cash top-up — {date(year, month, 1).strftime('%B %Y')}",
            topup_date,
            topup,
            TransactionType.CREDIT,
        )
        cash_balance += topup
        count += 2

    # ── 5. Rare surplus transfer to savings (≈20% chance per month) ──────────
    if random.random() < 0.20:
        transfer_amount = Decimal(str(round(random.uniform(10000, 40000), 2)))
        transfer_date = rand_date(year, month, 20, 28)
        await _tx(
            db,
            salary_id,
            "Transfer to Savings",
            "Monthly surplus savings transfer",
            transfer_date,
            transfer_amount,
            TransactionType.DEBIT,
        )
        await _tx(
            db,
            savings_id,
            "Savings Transfer Received",
            "Surplus transferred from salary account",
            transfer_date,
            transfer_amount,
            TransactionType.CREDIT,
        )
        count += 2

    return count, cash_balance


# ── Main ───────────────────────────────────────────────────────────────────────


async def seed_data() -> None:
    print("=" * 60)
    print("Database Seeding Script")
    print("=" * 60)
    print(f"User ID:  {USER_ID}")
    print(f"Currency: {CURRENCY}")
    print()

    async with SessionLocal() as db:
        try:
            account_ids = await create_accounts(db)
            print()

            print("Generating transactions (Apr 2025 – Apr 2026)...")
            total_transactions = 0
            cash_balance = CASH_RESERVE  # Track cash wallet balance locally
            start_year, start_month = 2025, 4

            for i in range(13):
                year = start_year + (start_month + i - 1) // 12
                month = ((start_month + i - 1) % 12) + 1

                count, cash_balance = await create_monthly_transactions(db, account_ids, year, month, cash_balance)
                total_transactions += count
                print(
                    f"  ✓ {date(year, month, 1).strftime('%B %Y')}: "
                    f"{count} transactions  (cash balance: ₹{cash_balance:,.2f})"
                )

            print()
            print("=" * 60)
            print("Seeding completed successfully!")
            print(f"  Accounts created:     {len(account_ids)}")
            print(f"  Transactions created: {total_transactions}")
            print("=" * 60)

        except Exception as e:
            print(f"\n Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
