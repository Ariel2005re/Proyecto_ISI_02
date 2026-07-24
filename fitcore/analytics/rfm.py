"""
analytics/rfm.py - Segmentación RFM (Fase 3.1)
==============================================
RFM clasifica a los clientes según su comportamiento de compra:
  R (Recencia):   días desde la última compra   (menos días = mejor)
  F (Frecuencia): número de compras históricas  (más compras = mejor)
  M (Monetario):  total gastado                 (más gasto = mejor)

Cada dimensión se puntúa de 1 a 5 usando quintiles (pandas.qcut) y con la
combinación de puntajes se asigna una ETIQUETA ESTRATÉGICA accionable para
la gerencia (VIP, Leal, Recuperable, En Riesgo, Perdido...).
"""

from datetime import datetime
import pandas as pd
from database import obtener_conexion


def calcular_rfm(fecha_referencia: str | None = None) -> pd.DataFrame:
    """Calcula R, F, M por cliente desde el histórico de ventas y lo persiste."""
    fecha_referencia = fecha_referencia or datetime.now().strftime("%Y-%m-%d")
    conexion = obtener_conexion()

    # 1) Métricas base por cliente (una sola consulta SQL)
    rfm = pd.read_sql_query(
        """
        SELECT c.id_cliente,
               c.nombre,
               CAST(julianday(:hoy) - julianday(MAX(v.fecha)) AS INTEGER) AS recencia,
               COUNT(v.id_venta)                                          AS frecuencia,
               ROUND(SUM(v.total), 2)                                     AS monetario
        FROM clientes c
        JOIN ventas v ON v.id_cliente = c.id_cliente
        GROUP BY c.id_cliente
        """,
        conexion, params={"hoy": fecha_referencia},
    )

    # 2) Puntajes 1-5 por quintiles.
    #    Recencia se invierte: MENOS días => puntaje MÁS alto.
    rfm["R"] = pd.qcut(rfm["recencia"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frecuencia"].rank(method="first"), 5,
                       labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetario"].rank(method="first"), 5,
                       labels=[1, 2, 3, 4, 5]).astype(int)

    # 3) Etiqueta estratégica
    rfm["segmento"] = rfm.apply(_asignar_segmento, axis=1)

    # 4) Persistir para que el dashboard y el CRM lo consuman
    fecha_calculo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conexion.execute("DELETE FROM segmentos_rfm")
    conexion.executemany(
        """INSERT INTO segmentos_rfm
             (id_cliente, recencia_dias, frecuencia, monetario,
              puntaje_r, puntaje_f, puntaje_m, segmento, fecha_calculo)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        [(int(f.id_cliente), int(f.recencia), int(f.frecuencia), float(f.monetario),
          int(f.R), int(f.F), int(f.M), f.segmento, fecha_calculo)
         for f in rfm.itertuples()],
    )
    conexion.commit()
    conexion.close()
    return rfm


def _asignar_segmento(fila) -> str:
    """Reglas de negocio para traducir puntajes en etiquetas estratégicas."""
    r, f, m = fila["R"], fila["F"], fila["M"]
    if r >= 4 and f >= 4 and m >= 4:
        return "VIP"                    # compran seguido, hace poco y gastan mucho
    if r >= 4 and f >= 3:
        return "Leal"                   # activos y constantes
    if r >= 4 and f <= 2:
        return "Nuevo / Prometedor"     # compraron hace poco pero pocas veces
    if r == 3:
        return "Necesita Atención"      # se están enfriando
    if r <= 2 and (f >= 3 or m >= 4):
        return "Recuperable"            # eran buenos clientes y se alejaron
    if r <= 2 and f <= 2:
        return "Perdido"                # inactivos y de poco valor histórico
    return "En Riesgo"


def resumen_segmentos() -> pd.DataFrame:
    """Distribución de clientes por segmento (insumo del dashboard)."""
    conexion = obtener_conexion()
    df = pd.read_sql_query(
        """SELECT segmento, COUNT(*) AS clientes,
                  ROUND(AVG(monetario),2) AS gasto_promedio
           FROM segmentos_rfm GROUP BY segmento ORDER BY clientes DESC""",
        conexion,
    )
    conexion.close()
    return df
