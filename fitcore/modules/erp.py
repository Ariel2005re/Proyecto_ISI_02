"""
modules/erp.py - Módulo ERP (Mini-Financiero)
=============================================
Requisito 2.2: "Cada vez que el sistema principal registra una Venta, el
módulo ERP debe registrar automáticamente el Asiento Contable".

El ERP NO es llamado por el Core: se SUSCRIBE al evento 'venta_registrada'
(y a 'orden_generada' del SCM para registrar el gasto). Contabilidad por
partida doble simplificada:
  - Venta:  DEBE Caja            / HABER Ingresos por Ventas
  - Compra: DEBE Inventario      / HABER Caja (pago a proveedor)
"""

from datetime import datetime
from database import obtener_conexion
from events import bus


class ModuloERP:
    """Mini-sistema financiero: libro diario y estado de caja."""

    def __init__(self):
        # Integración: el ERP se suscribe a los eventos que le interesan
        bus.suscribir("venta_registrada", self.registrar_asiento_venta)
        bus.suscribir("orden_generada", self.registrar_asiento_compra)

    # ---------------------------------------------------------------- REACCIONES
    def registrar_asiento_venta(self, datos: dict):
        """Reacción automática al evento 'venta_registrada' del Core."""
        conexion = obtener_conexion()
        conexion.execute(
            """INSERT INTO asientos_contables
                 (fecha, descripcion, cuenta_debe, cuenta_haber, monto, id_venta)
               VALUES (?,?,?,?,?,?)""",
            (datos["fecha"],
             f"Venta #{datos['id_venta']} - {datos['nombre_cliente']}",
             "Caja", "Ingresos por Ventas", datos["total"], datos["id_venta"]),
        )
        conexion.commit()
        conexion.close()
        print(f"  [ERP] Asiento contable creado: DEBE Caja ${datos['total']:.2f} "
              f"/ HABER Ingresos ${datos['total']:.2f}")

    def registrar_asiento_compra(self, datos: dict):
        """Reacción automática al evento 'orden_generada' del SCM."""
        conexion = obtener_conexion()
        conexion.execute(
            """INSERT INTO asientos_contables
                 (fecha, descripcion, cuenta_debe, cuenta_haber, monto, id_orden)
               VALUES (?,?,?,?,?,?)""",
            (datos["fecha"],
             f"Orden de compra #{datos['id_orden']} - {datos['nombre_producto']}",
             "Inventario", "Caja", datos["costo_total"], datos["id_orden"]),
        )
        conexion.commit()
        conexion.close()
        print(f"  [ERP] Asiento contable creado: DEBE Inventario "
              f"${datos['costo_total']:.2f} / HABER Caja (gasto)")

    # ---------------------------------------------------------------- CONSULTAS
    def estado_de_caja(self) -> dict:
        """KPI financiero para el dashboard: ingresos, gastos y saldo."""
        conexion = obtener_conexion()
        ingresos = conexion.execute(
            "SELECT COALESCE(SUM(monto),0) t FROM asientos_contables WHERE cuenta_debe='Caja'"
        ).fetchone()["t"]
        gastos = conexion.execute(
            "SELECT COALESCE(SUM(monto),0) t FROM asientos_contables WHERE cuenta_haber='Caja'"
        ).fetchone()["t"]
        conexion.close()
        return {"ingresos": round(ingresos, 2),
                "gastos": round(gastos, 2),
                "saldo": round(ingresos - gastos, 2)}

    def libro_diario(self, limite: int = 10) -> list:
        conexion = obtener_conexion()
        filas = conexion.execute(
            "SELECT * FROM asientos_contables ORDER BY id_asiento DESC LIMIT ?",
            (limite,),
        ).fetchall()
        conexion.close()
        return filas
