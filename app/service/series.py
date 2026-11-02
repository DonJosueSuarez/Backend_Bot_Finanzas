from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

# Hasta este número de días la evolución va por día; con más, por mes
MAX_DIAS_DETALLE = 62


def evolucion(movimientos: List[Dict], desde: date, hasta: date) -> Dict:
    """Ingresos y egresos por día (o por mes en rangos largos). La usan el Excel y el dashboard web.

    Cada movimiento necesita "fecha" (date local), "tipo_movimiento" y "monto".
    """
    por_dia = (hasta - desde).days + 1 <= MAX_DIAS_DETALLE
    clave = (lambda d: d) if por_dia else (lambda d: date(d.year, d.month, 1))

    # Todos los periodos del rango, aunque no tengan movimientos, para que la línea sea continua
    periodos, actual = [], desde
    while actual <= hasta:
        if not periodos or periodos[-1] != clave(actual):
            periodos.append(clave(actual))
        actual += timedelta(days=1)

    totales = defaultdict(lambda: {"INGRESO": Decimal(0), "EGRESO": Decimal(0)})
    for m in movimientos:
        totales[clave(m["fecha"])][m["tipo_movimiento"]] += m["monto"]

    def etiqueta(p: date) -> str:
        return f"{p.day:02d}/{p.month:02d}" if por_dia else f"{MESES[p.month - 1]} {p.year}"

    return {
        "agrupacion": "dia" if por_dia else "mes",
        "puntos": [
            {
                "periodo": p,
                "etiqueta": etiqueta(p),
                "ingresos": totales[p]["INGRESO"],
                "egresos": totales[p]["EGRESO"],
            }
            for p in periodos
        ],
    }
