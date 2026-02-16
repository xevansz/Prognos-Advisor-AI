from datetime import datetime, timedelta
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.logging import get_logger
from models import FXRate

logger = get_logger(__name__)


async def fetch_latest_rates(base_currency: str = "USD") -> dict[str, float]:
    """
    Fetch latest FX rates from external API.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.fx_api_url}/{base_currency}",
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("rates", {})
    except Exception as e:
        logger.error(f"Failed to fetch FX rates: {e}")
        raise


async def get_cached_rates(db: AsyncSession, base_currency: str = "USD") -> dict[str, float]:
    """
    Get cached FX rates, fetching new ones if cache is stale (>3 days).
    """
    stmt = (
        select(FXRate)
        .where(FXRate.base_currency == base_currency)
        .order_by(FXRate.fetched_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    cached = result.scalar_one_or_none()

    now = datetime.utcnow()
    if cached and (now - cached.fetched_at) < timedelta(days=3):
        return cached.rates

    rates = await fetch_latest_rates(base_currency)

    fx_rate = FXRate(
        base_currency=base_currency,
        rates=rates,
        fetched_at=now,
    )
    db.add(fx_rate)
    await db.commit()

    return rates


async def convert_currency(
    db: AsyncSession,
    amount: Decimal,
    from_currency: str,
    to_currency: str,
) -> Decimal:
    """
    Convert amount from one currency to another using cached rates.
    """
    if from_currency == to_currency:
        return amount

    rates = await get_cached_rates(db, from_currency)

    if to_currency not in rates:
        raise ValueError(f"Currency {to_currency} not found in rates")

    rate = Decimal(str(rates[to_currency]))
    return amount * rate
