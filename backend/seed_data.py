#!/usr/bin/env python3
"""
Seed script to populate database with test accounts and transactions.
Uses the service layer to maintain data integrity and audit trails.

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

# Configuration
USER_ID = ""
CURRENCY = "INR"

# Base expense pattern from example (monthly amounts)
BASE_PATTERN = {
    "income": Decimal("44637.25"),
    "rent": Decimal("13391.17"),
    "loan_repayment": Decimal("0.00"),
    "insurance": Decimal("2206.49"),
    "groceries": Decimal("6658.77"),
    "transport": Decimal("2636.97"),
    "eating_out": Decimal("1651.80"),
    "entertainment": Decimal("1536.18"),
    "utilities": Decimal("2911.79"),
    "healthcare": Decimal("1546.91"),
    "education": Decimal("0.00"),
    "miscellaneous": Decimal("831.53"),
}

# Account configuration
ACCOUNTS_CONFIG = [
    {"name": "HDFC Bank", "type": AccountType.BANK, "initial_balance": Decimal("50000.00")},
    {"name": "ICICI Bank", "type": AccountType.BANK, "initial_balance": Decimal("25000.00")},
    {"name": "Cash Wallet", "type": AccountType.CASH, "initial_balance": Decimal("5000.00")},
]

# Expense distribution across accounts (percentages)
EXPENSE_DISTRIBUTION = {
    "income": [("HDFC Bank", 1.0)],  # Salary goes to primary bank
    "rent": [("HDFC Bank", 1.0)],
    "loan_repayment": [("HDFC Bank", 1.0)],
    "insurance": [("HDFC Bank", 1.0)],
    "groceries": [("Cash Wallet", 0.7), ("HDFC Bank", 0.3)],
    "transport": [("Cash Wallet", 0.8), ("ICICI Bank", 0.2)],
    "eating_out": [("Cash Wallet", 0.9), ("ICICI Bank", 0.1)],
    "entertainment": [("Cash Wallet", 0.8), ("ICICI Bank", 0.2)],
    "utilities": [("HDFC Bank", 1.0)],
    "healthcare": [("Cash Wallet", 0.6), ("HDFC Bank", 0.4)],
    "education": [("HDFC Bank", 1.0)],
    "miscellaneous": [("Cash Wallet", 0.7), ("ICICI Bank", 0.3)],
}


def add_variance(amount: Decimal, variance_percent: float = 15.0) -> Decimal:
    """Add random variance to amount (±variance_percent%)."""
    variance = random.uniform(-variance_percent, variance_percent) / 100
    new_amount = float(amount) * (1 + variance)
    return Decimal(str(round(new_amount, 2)))


def get_transaction_date(year: int, month: int, category: str) -> date:
    """Generate a realistic date for the transaction within the month."""
    # Different categories have different typical dates
    day_ranges = {
        "income": (1, 5),  # Salary at start of month
        "rent": (1, 3),  # Rent beginning of month
        "loan_repayment": (5, 10),
        "insurance": (5, 15),
        "utilities": (20, 30),  # End of month
        "groceries": (1, 28),  # Throughout month
        "transport": (1, 28),
        "eating_out": (1, 28),
        "entertainment": (1, 28),
        "healthcare": (1, 28),
        "education": (1, 10),
        "miscellaneous": (1, 28),
    }

    start_day, end_day = day_ranges.get(category, (1, 28))
    # Ensure valid day for the month
    last_day = (date(year, month % 12 + 1, 1) - timedelta(days=1)).day
    end_day = min(end_day, last_day)
    start_day = min(start_day, end_day)

    day = random.randint(start_day, end_day)
    return date(year, month, day)


async def create_accounts(db: AsyncSession) -> dict[str, str]:
    """Create accounts and return mapping of name -> id."""
    account_ids = {}

    print("Creating accounts...")
    for config in ACCOUNTS_CONFIG:
        payload = AccountCreate(
            name=config["name"],
            type=config["type"],
            currency=CURRENCY,
            initial_balance=config["initial_balance"],
        )
        account = await create_account(db, USER_ID, payload)
        account_ids[config["name"]] = str(account.id)
        print(f"  ✓ Created {config['name']} ({config['type'].value}) - ID: {account.id}")

    return account_ids


async def create_monthly_transactions(db: AsyncSession, account_ids: dict[str, str], year: int, month: int) -> int:
    """Create transactions for one month. Returns count of transactions created."""
    count = 0

    for category, base_amount in BASE_PATTERN.items():
        if base_amount == 0:
            continue

        # Add variance to amount
        amount = add_variance(base_amount, 15.0)

        # Determine transaction type and label
        if category == "income":
            tx_type = TransactionType.CREDIT
            label = "Monthly Salary"
            description = f"Salary deposit for {date(year, month, 1).strftime('%B %Y')}"
        else:
            tx_type = TransactionType.DEBIT
            label = category.replace("_", " ").title()
            description = f"{label} expense for {date(year, month, 1).strftime('%B %Y')}"

        # Get distribution for this category
        distribution = EXPENSE_DISTRIBUTION.get(category, [("HDFC Bank", 1.0)])

        # Create transactions according to distribution
        for account_name, ratio in distribution:
            if ratio == 0:
                continue

            split_amount = Decimal(str(float(amount) * ratio))
            split_amount = Decimal(str(round(float(split_amount), 2)))

            if split_amount <= 0:
                continue

            account_id = account_ids[account_name]
            tx_date = get_transaction_date(year, month, category)

            payload = TransactionCreate(
                account_id=account_id,
                label=label,
                description=description,
                date=tx_date,
                amount=split_amount,
                type=tx_type,
                currency=CURRENCY,
                is_recurring=False,
            )

            await create_transaction(db, USER_ID, payload)
            count += 1

    return count


async def seed_data():
    """Main seeding function."""
    print("=" * 60)
    print("Database Seeding Script")
    print("=" * 60)
    print(f"User ID: {USER_ID}")
    print(f"Currency: {CURRENCY}")
    print()

    async with SessionLocal() as db:
        try:
            # Step 1: Create accounts
            account_ids = await create_accounts(db)
            print()

            # Step 2: Generate 12 months of transactions (April 2025 - March 2026)
            print("Generating transactions...")
            total_transactions = 0

            start_year, start_month = 2025, 4

            for i in range(12):
                year = start_year + (start_month + i - 1) // 12
                month = ((start_month + i - 1) % 12) + 1

                count = await create_monthly_transactions(db, account_ids, year, month)
                total_transactions += count
                print(f"  ✓ {date(year, month, 1).strftime('%B %Y')}: {count} transactions")

            print()
            print("=" * 60)
            print("Seeding completed successfully!")
            print(f"Total accounts created: {len(account_ids)}")
            print(f"Total transactions created: {total_transactions}")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
