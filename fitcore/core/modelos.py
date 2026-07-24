"""
core/modelos.py - Clases del Dominio (Programación Orientada a Objetos)
=======================================================================
Cumple el requisito 2.1: el Core usa POO.
Conceptos de POO demostrados:
  - Encapsulamiento: atributos privados con propiedades (ej. Producto._stock).
  - Herencia: Membresia y Clase heredan de Producto (son "productos-servicio").
  - Polimorfismo: es_servicio() se comporta distinto según la subclase.
  - Composición: una Venta CONTIENE una lista de DetalleVenta.
"""

from datetime import datetime


class Cliente:
    """Representa a un socio del gimnasio (fila de la tabla 'clientes')."""

    def __init__(self, id_cliente, nombre, genero="F", edad=30, telefono="",
                 vive_cerca=1, empresa_convenio=0, promo_amigos=0,
                 meses_contrato=1, clases_grupales=0, frecuencia_semanal=2.0,
                 meses_antiguedad=0, abandono_historico=0, fecha_registro=None):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.genero = genero
        self.edad = edad
        self.telefono = telefono
        self.vive_cerca = vive_cerca
        self.empresa_convenio = empresa_convenio
        self.promo_amigos = promo_amigos
        self.meses_contrato = meses_contrato
        self.clases_grupales = clases_grupales
        self.frecuencia_semanal = frecuencia_semanal
        self.meses_antiguedad = meses_antiguedad
        self.abandono_historico = abandono_historico
        self.fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d")

    def __str__(self):
        return f"[{self.id_cliente:>4}] {self.nombre} ({self.edad} años)"


class Producto:
    """Clase base para todo lo que el gimnasio vende (bienes físicos)."""

    def __init__(self, id_producto, nombre, precio, costo,
                 stock=None, stock_minimo=None, id_proveedor=None,
                 categoria="Producto"):
        self.id_producto = id_producto
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.costo = costo
        self._stock = stock                # Encapsulado: se modifica solo por métodos
        self.stock_minimo = stock_minimo
        self.id_proveedor = id_proveedor

    # ----- Encapsulamiento del stock -----
    @property
    def stock(self):
        return self._stock

    def descontar_stock(self, cantidad: int) -> bool:
        """Descuenta stock y devuelve True si quedó por debajo del mínimo
        (esa señal es la que el Core convierte en evento 'stock_bajo')."""
        if self._stock is None:            # los servicios no tienen stock
            return False
        self._stock -= cantidad
        return self.stock_minimo is not None and self._stock <= self.stock_minimo

    def reponer_stock(self, cantidad: int):
        if self._stock is not None:
            self._stock += cantidad

    def es_servicio(self) -> bool:
        """Polimorfismo: la clase base representa bienes físicos."""
        return False

    def __str__(self):
        stock_txt = f"stock={self._stock}" if self._stock is not None else "servicio"
        return f"[{self.id_producto:>3}] {self.nombre} (${self.precio:.2f}, {stock_txt})"


class Membresia(Producto):
    """Herencia: una membresía es un producto-servicio sin inventario."""

    def __init__(self, id_producto, nombre, precio, costo, duracion_meses=1):
        super().__init__(id_producto, nombre, precio, costo,
                         stock=None, categoria="Membresía")
        self.duracion_meses = duracion_meses

    def es_servicio(self) -> bool:
        return True


class ClaseDirigida(Producto):
    """Herencia: una clase dirigida (spinning, crossfit...) también es servicio."""

    def __init__(self, id_producto, nombre, precio, costo, cupo=20):
        super().__init__(id_producto, nombre, precio, costo,
                         stock=None, categoria="Clase")
        self.cupo = cupo

    def es_servicio(self) -> bool:
        return True


class DetalleVenta:
    """Una línea de la factura: producto x cantidad."""

    def __init__(self, producto: Producto, cantidad: int):
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = producto.precio
        self.subtotal = round(producto.precio * cantidad, 2)


class Venta:
    """Composición: la Venta agrupa varios DetalleVenta de un Cliente."""

    def __init__(self, cliente: Cliente, fecha=None):
        self.id_venta = None               # lo asigna la BD al persistir
        self.cliente = cliente
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.detalles: list[DetalleVenta] = []

    def agregar_item(self, producto: Producto, cantidad: int = 1):
        self.detalles.append(DetalleVenta(producto, cantidad))

    @property
    def total(self) -> float:
        return round(sum(d.subtotal for d in self.detalles), 2)

    def __str__(self):
        lineas = [f"Venta #{self.id_venta} | {self.cliente.nombre} | {self.fecha}"]
        for d in self.detalles:
            lineas.append(f"   {d.cantidad} x {d.producto.nombre:<28} ${d.subtotal:>7.2f}")
        lineas.append(f"   {'TOTAL':>33} ${self.total:>7.2f}")
        return "\n".join(lineas)
