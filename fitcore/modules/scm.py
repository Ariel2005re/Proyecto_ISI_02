"""
modules/scm.py - Módulo SCM (Inventario / Proveedores)
======================================================
Requisito 2.2: "Si el sistema principal detecta stock bajo al vender, el
módulo SCM debe generar una Orden de Compra automática al proveedor simulado".

El SCM se SUSCRIBE al evento 'stock_bajo'. Al reaccionar:
  1. Genera la orden de compra al proveedor del producto.
  2. Publica a su vez 'orden_generada' (que el ERP escucha para registrar
     el gasto) -> cadena de integración Core -> SCM -> ERP.
"""

from datetime import datetime
from database import obtener_conexion
from events import bus

LOTE_DE_REPOSICION = 50   # unidades que se piden al proveedor por orden


class ModuloSCM:
    """Gestión simplificada de abastecimiento."""

    def __init__(self):
        bus.suscribir("stock_bajo", self.generar_orden_compra)

    # ---------------------------------------------------------------- REACCIÓN
    def generar_orden_compra(self, datos: dict):
        """Reacción automática al evento 'stock_bajo' del Core."""
        conexion = obtener_conexion()

        # Evitar duplicados: si ya hay una orden PENDIENTE de ese producto, no repetir
        pendiente = conexion.execute(
            "SELECT id_orden FROM ordenes_compra WHERE id_producto=? AND estado='PENDIENTE'",
            (datos["id_producto"],),
        ).fetchone()
        if pendiente:
            conexion.close()
            print(f"  [SCM] Ya existe orden PENDIENTE para {datos['nombre']} "
                  f"(#{pendiente['id_orden']}); no se duplica.")
            return

        producto = conexion.execute(
            "SELECT costo, id_proveedor FROM productos WHERE id_producto=?",
            (datos["id_producto"],),
        ).fetchone()
        proveedor = conexion.execute(
            "SELECT * FROM proveedores WHERE id_proveedor=?",
            (producto["id_proveedor"],),
        ).fetchone()

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        costo_total = round(producto["costo"] * LOTE_DE_REPOSICION, 2)
        cursor = conexion.execute(
            """INSERT INTO ordenes_compra
                 (fecha, id_proveedor, id_producto, cantidad, costo_total, estado)
               VALUES (?,?,?,?,?, 'PENDIENTE')""",
            (fecha, producto["id_proveedor"], datos["id_producto"],
             LOTE_DE_REPOSICION, costo_total),
        )
        id_orden = cursor.lastrowid
        conexion.commit()
        conexion.close()

        print(f"  [SCM] Stock bajo de '{datos['nombre']}' "
              f"({datos['stock_actual']} <= mínimo {datos['stock_minimo']}). "
              f"Orden #{id_orden} generada a {proveedor['nombre']}: "
              f"{LOTE_DE_REPOSICION} unidades por ${costo_total:.2f}")

        # Cadena de integración: SCM -> ERP
        bus.publicar("orden_generada", {
            "id_orden": id_orden,
            "fecha": fecha,
            "nombre_producto": datos["nombre"],
            "costo_total": costo_total,
        })

    # ---------------------------------------------------------------- OPERACIÓN
    def recibir_orden(self, id_orden: int):
        """Simula la llegada de la mercadería: repone stock y cierra la orden."""
        conexion = obtener_conexion()
        orden = conexion.execute(
            "SELECT * FROM ordenes_compra WHERE id_orden=? AND estado='PENDIENTE'",
            (id_orden,),
        ).fetchone()
        if not orden:
            conexion.close()
            print("  [SCM] Orden no encontrada o ya recibida.")
            return
        conexion.execute(
            "UPDATE productos SET stock = stock + ? WHERE id_producto = ?",
            (orden["cantidad"], orden["id_producto"]),
        )
        conexion.execute(
            "UPDATE ordenes_compra SET estado='RECIBIDA' WHERE id_orden=?",
            (id_orden,),
        )
        conexion.commit()
        conexion.close()
        print(f"  [SCM] Orden #{id_orden} recibida: stock repuesto (+{orden['cantidad']}).")

    def ordenes(self, solo_pendientes=False) -> list:
        conexion = obtener_conexion()
        sql = """SELECT oc.*, p.nombre AS producto, pr.nombre AS proveedor
                 FROM ordenes_compra oc
                 JOIN productos p   ON p.id_producto  = oc.id_producto
                 JOIN proveedores pr ON pr.id_proveedor = oc.id_proveedor"""
        if solo_pendientes:
            sql += " WHERE oc.estado='PENDIENTE'"
        sql += " ORDER BY oc.id_orden DESC"
        filas = conexion.execute(sql).fetchall()
        conexion.close()
        return filas
