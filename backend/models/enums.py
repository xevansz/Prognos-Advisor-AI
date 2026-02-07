import enum


class RiskAppetite(str, enum.Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class AccountType(str, enum.Enum):
    BANK = "bank"
    CASH = "cash"
    HOLDINGS = "holdings"
    CRYPTO = "crypto"
    OTHER = "other"


class TransactionType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class RecurrenceFrequency(str, enum.Enum):
    MONTHLY = "monthly"


class GoalPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalStatus(str, enum.Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    UNREALISTIC = "unrealistic"
