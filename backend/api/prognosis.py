from fastapi import APIRouter, status

from api.deps import CurrentUserDep, DbDep
from schemas.prognosis import PrognosisReportOut
from services import prognosis_service

router = APIRouter(prefix="/api/prognosis", tags=["prognosis"])


@router.post("/refresh", response_model=PrognosisReportOut)
async def refresh_prognosis(
    db: DbDep,
    current_user: CurrentUserDep,
) -> PrognosisReportOut:
    """
    Generate a new prognosis report for the current user.
    """
    result = await prognosis_service.generate_prognosis(db, current_user.user_id)
    return result


@router.get("/current", response_model=PrognosisReportOut | None)
async def get_current_prognosis(
    db: DbDep,
    current_user: CurrentUserDep,
) -> PrognosisReportOut | None:
    """
    Get the last cached prognosis report for the current user.
    """
    result = await prognosis_service.get_cached_report(db, current_user.user_id)
    return result
