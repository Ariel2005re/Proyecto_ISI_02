"""
core/sistema_core.py - Sistema Principal (Core Business)
========================================================
El negocio del cliente es un GIMNASIO. Su proceso core es la VENTA:
membresías, clases dirigidas y productos (suplementos, bebidas).

Este módulo implementa el punto de venta (POS). Fíjense en registrar_venta():
tras guardar la transacción, PUBLICA eventos en el bus. El Core NO llama
directamente al ERP ni al SCM (no los conoce): la integración ocurre por
eventos. Eso es lo que se demuestra en vivo en la defensa.
"""

from database import obtener_conexion
from core.modelos import Cliente, Producto, Membresia, ClaseDirigida, Venta
from events import bus


class SistemaCore:
    """Fachada del sistema principal: clientes, catálogo y ventas."""

    # ------------------------------------------------------------------ CLIENTES
    def obtener_cliente(self, id_cliente: int) -> Cliente | None:
        conexion = obtener_conexion()
        fila = conexion.execute(
            "SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,)
        ).fetchone()
        conexion.close()
        return self._fila_a_cliente(fila) if fila else None

    def buscar_clientes(self, texto: str) -> list[Cliente]:
        conexion = obtener_conexion()
        filas = conexion.execute(
            "SELECT * FROM clientes WHERE nombre LIKE ? ORDER BY nombre LIMIT 15",
            (f"%{texto}%",),
        ).fetchall()
        conexion.close()
        return [self._fila_a_cliente(f) for f in filas]

    def registrar_cliente(self, cliente: Cliente) -> int:
        conexion = obtener_conexion()
        cursor = conexion.execute(
            """INSERT INTO clientes (nombre, genero, edad, telefono, vive_cerca,
                 empresa_convenio, promo_amigos, meses_contrato, clases_grupales,
                 frecuencia_semanal, meses_antiguedad, abandono_historico, fecha_registro)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (cliente.nombre, cliente.genero, cliente.edad, cliente.telefono,
             cliente.vive_cerca, cliente.empresa_convenio, cliente.promo_amigos,
             cliente.meses_contrato, cliente.clases_grupales, cliente.frecuencia_semanal,
             cliente.meses_antiguedad, cliente.abandono_historico, cliente.fecha_registro),
        )
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return nuevo_id

    # ------------------------------------------------------------------ CATÁLOGO
    def obtener_producto(self, id_producto: int) -> Producto | None:
        conexion = obtener_conexion()
        fila = conexion.execute(
            "SELECT * FROM productos WHERE id_producto = ?", (id_producto,)
        ).fetchone()
        conexion.close()
        return self._fila_a_producto(fila) if fila else None

    def listar_catalogo(self) -> list[Producto]:
        conexion = obtener_conexion()
        filas = conexion.execute(
            "SELECT * FROM productos ORDER BY categoria, id_producto"
        ).fetchall()
        conexion.close()
        return [self._fila_a_producto(f) for f in filas]

    # ------------------------------------------------------------------ VENTAS
    def registrar_venta(self, venta: Venta, silencioso=False) -> int:
        """Persiste la venta, actualiza stock y PUBLICA los eventos de integración.

        Flujo de integración (requisito 2.3):
          1. INSERT en ventas + detalle_venta          (Sistema Core)
          2. UPDATE stock de productos físicos          (Sistema Core)
          3. bus.publicar('venta_registrada') ---------> ERP crea asiento contable
                                              ---------> CRM actualiza última compra
          4. si stock <= mínimo:
             bus.publicar('stock_bajo') ---------------> SCM genera orden de compra
        """
        conexion = obtener_conexion()
        cursor = conexion.execute(
            "INSERT INTO ventas (id_cliente, fecha, total) VALUES (?,?,?)",
            (venta.cliente.id_cliente, venta.fecha, venta.total),
        )
        venta.id_venta = cursor.lastrowid

        productos_con_stock_bajo = []
        for detalle in venta.detalles:
            conexion.execute(
                """INSERT INTO detalle_venta
                     (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                   VALUES (?,?,?,?,?)""",
                (venta.id_venta, detalle.producto.id_producto, detalle.cantidad,
                 detalle.precio_unitario, detalle.subtotal),
            )
            # Descuento de stock solo para bienes físicos (polimorfismo)
            if not detalle.producto.es_servicio():
                quedo_bajo = detalle.producto.descontar_stock(detalle.cantidad)
                conexion.execute(
                    "UPDATE productos SET stock = ? WHERE id_producto = ?",
                    (detalle.producto.stock, detalle.producto.id_producto),
                )
                if quedo_bajo:
                    productos_con_stock_bajo.append(detalle.producto)

        conexion.commit()
        conexion.close()

        if not silencioso:
            print(f"\n{venta}")

        # -------- INTEGRACIÓN: el Core solo publica; los módulos reaccionan ----
        bus.publicar("venta_registrada", {
            "id_venta": venta.id_venta,
            "id_cliente": venta.cliente.id_cliente,
            "nombre_cliente": venta.cliente.nombre,
            "fecha": venta.fecha,
            "total": venta.total,
            "detalles": [(d.producto.nombre, d.cantidad, d.subtotal)
                         for d in venta.detalles],
        })
        for producto in productos_con_stock_bajo:
            bus.publicar("stock_bajo", {
                "id_producto": producto.id_producto,
                "nombre": producto.nombre,
                "stock_actual": producto.stock,
                "stock_minimo": producto.stock_minimo,
                "id_proveedor": producto.id_proveedor,
            })
        return venta.id_venta

    # ------------------------------------------------------------------ MAPEOS
    @staticmethod
    def _fila_a_cliente(fila) -> Cliente:
        return Cliente(
            id_cliente=fila["id_cliente"], nombre=fila["nombre"],
            genero=fila["genero"], edad=fila["edad"], telefono=fila["telefono"],
            vive_cerca=fila["vive_cerca"], empresa_convenio=fila["empresa_convenio"],
            promo_amigos=fila["promo_amigos"], meses_contrato=fila["meses_contrato"],
            clases_grupales=fila["clases_grupales"],
            frecuencia_semanal=fila["frecuencia_semanal"],
            meses_antiguedad=fila["meses_antiguedad"],
            abandono_historico=fila["abandono_historico"],
            fecha_registro=fila["fecha_registro"],
        )

    @staticmethod
    def _fila_a_producto(fila) -> Producto:
        """Reconstruye la subclase correcta según la categoría (polimorfismo)."""
        if fila["categoria"] == "Membresía":
            return Membresia(fila["id_producto"], fila["nombre"],
                             fila["precio"], fila["costo"])
        if fila["categoria"] == "Clase":
            return ClaseDirigida(fila["id_producto"], fila["nombre"],
                                 fila["precio"], fila["costo"])
        return Producto(fila["id_producto"], fila["nombre"], fila["precio"],
                        fila["costo"], stock=fila["stock"],
                        stock_minimo=fila["stock_minimo"],
                        id_proveedor=fila["id_proveedor"])
