
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from database import obtener_conexion

RUTA_PNG = os.path.join(os.path.dirname(__file__), "..", "data", "dashboard.png")

COLORES = ["#2E86AB", "#F18F01", "#A23B72", "#3B8952", "#C73E1D",
           "#6C5B7B", "#17A398", "#8D6A9F"]


def generar_dashboard(mostrar_ruta=True) -> str:
    conexion = obtener_conexion()

    # ---------- Datos 1: ventas por semana --------------------------------
    ventas = pd.read_sql_query(
        "SELECT fecha, total FROM ventas ORDER BY fecha", conexion,
        parse_dates=["fecha"])
    semanal = ventas.set_index("fecha").resample("W")["total"].sum()

    # ---------- Datos 2: segmentos RFM ------------------------------------
    segmentos = pd.read_sql_query(
        "SELECT segmento, COUNT(*) n FROM segmentos_rfm GROUP BY segmento "
        "ORDER BY n DESC", conexion)

    # ---------- Datos 3: KPI ERP (caja) y SCM (top pedidos) ---------------
    caja = pd.read_sql_query(
        """SELECT
             SUM(CASE WHEN cuenta_debe='Caja'  THEN monto ELSE 0 END) AS ingresos,
             SUM(CASE WHEN cuenta_haber='Caja' THEN monto ELSE 0 END) AS gastos
           FROM asientos_contables""", conexion)
    top_pedidos = pd.read_sql_query(
        """SELECT p.nombre, SUM(oc.cantidad) unidades
           FROM ordenes_compra oc JOIN productos p ON p.id_producto=oc.id_producto
           GROUP BY p.nombre ORDER BY unidades DESC LIMIT 5""", conexion)

    # ---------- Datos 4: alertas CRM --------------------------------------
    alertas = pd.read_sql_query(
        """SELECT c.nombre, a.dias_inactivo
           FROM alertas_crm a JOIN clientes c ON c.id_cliente=a.id_cliente
           WHERE a.atendida=0 ORDER BY a.dias_inactivo DESC LIMIT 8""", conexion)
    total_alertas = pd.read_sql_query(
        "SELECT COUNT(*) n FROM alertas_crm WHERE atendida=0", conexion)["n"][0]
    conexion.close()

    # ---------- Construcción del tablero ----------------------------------
    fig, ejes = plt.subplots(2, 2, figsize=(15, 9))
    fig.suptitle(
        f"FitCore Gym - Tablero de Control Gerencial   "
        f"(actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
        fontsize=15, fontweight="bold")

    # (1) Evolución semanal de ventas
    eje = ejes[0][0]
    eje.plot(semanal.index, semanal.values, marker="o", markersize=3.5,
             color=COLORES[0], linewidth=1.8)
    eje.fill_between(semanal.index, semanal.values, alpha=0.15, color=COLORES[0])
    eje.set_title("1. Evolución Semanal de Ventas (USD)", fontweight="bold")
    eje.set_ylabel("USD")
    eje.grid(alpha=0.3)
    eje.tick_params(axis="x", rotation=30, labelsize=8)

    # (2) Segmentación RFM
    eje = ejes[0][1]
    if len(segmentos):
        eje.pie(segmentos["n"], labels=segmentos["segmento"],
                autopct="%1.1f%%", startangle=90,
                colors=COLORES[:len(segmentos)],
                textprops={"fontsize": 9})
        eje.set_title("2. Segmentación de Clientes (RFM)", fontweight="bold")
    else:
        eje.text(0.5, 0.5, "Ejecutar análisis RFM", ha="center")

    # (3) KPI financiero (ERP) + top pedidos (SCM)
    eje = ejes[1][0]
    ingresos = float(caja["ingresos"][0] or 0)
    gastos = float(caja["gastos"][0] or 0)
    barras = eje.bar(["Ingresos", "Gastos", "Saldo"],
                     [ingresos, gastos, ingresos - gastos],
                     color=[COLORES[3], COLORES[4], COLORES[0]])
    for barra in barras:
        eje.text(barra.get_x() + barra.get_width() / 2, barra.get_height(),
                 f"${barra.get_height():,.0f}", ha="center", va="bottom",
                 fontweight="bold", fontsize=9)
    titulo3 = "3. ERP: Ingresos vs Gastos (Caja)"
    if len(top_pedidos):
        mas_pedido = top_pedidos.iloc[0]
        titulo3 += f"\nSCM: más pedido a proveedores = {mas_pedido['nombre']} ({int(mas_pedido['unidades'])} u.)"
    eje.set_title(titulo3, fontweight="bold", fontsize=10)
    eje.grid(alpha=0.3, axis="y")

    # (4) Alertas CRM
    eje = ejes[1][1]
    if len(alertas):
        eje.barh(alertas["nombre"][::-1], alertas["dias_inactivo"][::-1],
                 color=COLORES[4])
        eje.set_xlabel("Días de inactividad")
    else:
        eje.text(0.5, 0.5, "Sin alertas activas", ha="center", fontsize=12)
    eje.set_title(f"4. CRM: Clientes en Riesgo de Deserción "
                  f"(total: {total_alertas})", fontweight="bold")
    eje.grid(alpha=0.3, axis="x")

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    ruta = os.path.abspath(RUTA_PNG)
    plt.savefig(ruta, dpi=110)
    plt.close(fig)
    if mostrar_ruta:
        print(f"  [DASHBOARD] Tablero regenerado -> {ruta}")
    return ruta
