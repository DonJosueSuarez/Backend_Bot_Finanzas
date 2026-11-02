from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

# Los usuarios piensan en días de Ecuador; la base guarda en UTC
LOCAL_TZ = ZoneInfo("America/Guayaquil")
UTC = ZoneInfo("UTC")


def hoy_local() -> date:
    return datetime.now(LOCAL_TZ).date()


def inicio_dia_utc(dia: date) -> datetime:
    """00:00 de ese día en Ecuador, expresado en UTC."""
    return datetime.combine(dia, time.min, LOCAL_TZ).astimezone(UTC)


def fin_dia_utc(dia: date) -> datetime:
    """Límite exclusivo: 00:00 del día siguiente en Ecuador, en UTC."""
    return inicio_dia_utc(dia + timedelta(days=1))


def fecha_local(momento: datetime) -> date:
    # Postgres devuelve la fecha con zona; si llega sin ella (SQLite), está en UTC
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=UTC)
    return momento.astimezone(LOCAL_TZ).date()
