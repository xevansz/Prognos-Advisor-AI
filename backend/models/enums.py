from enum import StrEnum


class RiskAppetite(StrEnum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class AccountType(StrEnum):
    BANK = "bank"
    CASH = "cash"
    HOLDINGS = "holdings"
    CRYPTO = "crypto"
    OTHER = "other"


class TransactionType(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class RecurrenceFrequency(StrEnum):
    MONTHLY = "monthly"


class GoalPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalStatus(StrEnum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    UNREALISTIC = "unrealistic"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditResourceType(StrEnum):
    ACCOUNT = "account"
    TRANSACTION = "transaction"
    GOAL = "goal"
    PROFILE = "profile"
