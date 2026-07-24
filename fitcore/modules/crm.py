"""
modules/crm.py - Módulo CRM (Relación con el Cliente)
=====================================================
Requisito 2.2: "Si el módulo detecta mediante una consulta automatizada que
un cliente no ha realizado compras dentro de un umbral de tiempo, el sistema
debe aislar su registro y disparar una alerta de 'Cliente en Riesgo de
Deserción' en la interfaz gerencial".

Diseño:
  - analizar_inactividad(): consulta SQL automatizada que calcula los días
    desde la última compra de CADA cliente y aísla a los que superan el
    umbral (por defecto 30 días), generando alertas persistentes.
  - Además se suscribe a 'venta_registrada': si un cliente con alerta activa
    vuelve a comprar, la alerta se marca como atendida (cliente recuperado).
"""

from datetime import datetime
from database import obtener_conexion
from events import bus

UMBRAL_DIAS_DEFECTO = 30


class ModuloCRM:
    """Monitoreo activo de la relación con los socios del gimnasio."""

    def __init__(self, umbral_dias: int = UMBRAL_DIAS_DEFECTO):
        self.umbral_dias = umbral_dias
        # Integración: si el cliente en riesgo vuelve a comprar, se recupera solo
        bus.suscribir("venta_registrada", self.marcar_cliente_recuperado)

    # ---------------------------------------------------------------- ANÁLISIS
    def analizar_inactividad(self, silencioso=False) -> list:
        """Consulta automatizada: aísla clientes sin compras en el umbral."""
        conexion = obtener_conexion()
        hoy = datetime.now().strftime("%Y-%m-%d")
        filas = conexion.execute(
            """
            SELECT c.id_cliente, c.nombre,
                   MAX(v.fecha)                                  AS ultima_compra,
                   CAST(julianday(?) - julianday(MAX(v.fecha)) AS INTEGER) AS dias_inactivo
            FROM clientes c
            JOIN ventas v ON v.id_cliente = c.id_cliente
            GROUP BY c.id_cliente
            HAVING dias_inactivo > ?
            ORDER BY dias_inactivo DESC
            """,
            (hoy, self.umbral_dias),
        ).fetchall()

        nuevas_alertas = 0
        for fila in filas:
            # Aislar el registro: solo una alerta activa por cliente
            existe = conexion.execute(
                "SELECT 1 FROM alertas_crm WHERE id_cliente=? AND atendida=0",
                (fila["id_cliente"],),
            ).fetchone()
            if existe:
                continue
            conexion.execute(
                """INSERT INTO alertas_crm
                     (id_cliente, fecha_alerta, tipo, detalle, dias_inactivo)
                   VALUES (?,?,?,?,?)""",
                (fila["id_cliente"], hoy, "RIESGO_DESERCION",
                 f"Sin compras desde {fila['ultima_compra'][:10]}",
                 fila["dias_inactivo"]),
            )
            nuevas_alertas += 1
            # Alerta hacia la interfaz gerencial
            bus.publicar("cliente_en_riesgo", {
                "id_cliente": fila["id_cliente"],
                "nombre": fila["nombre"],
                "dias_inactivo": fila["dias_inactivo"],
            })

        conexion.commit()
        conexion.close()
        if not silencioso:
            print(f"  [CRM] Análisis completado: {len(filas)} cliente(s) inactivos "
                  f"> {self.umbral_dias} días; {nuevas_alertas} alerta(s) nueva(s).")
        return filas

    # ---------------------------------------------------------------- REACCIÓN
    def marcar_cliente_recuperado(self, datos: dict):
        """Si un cliente con alerta activa compra, la alerta se cierra sola."""
        conexion = obtener_conexion()
        activa = conexion.execute(
            "SELECT id_alerta FROM alertas_crm WHERE id_cliente=? AND atendida=0",
            (datos["id_cliente"],),
        ).fetchone()
        if activa:
            conexion.execute(
                "UPDATE alertas_crm SET atendida=1 WHERE id_alerta=?",
                (activa["id_alerta"],),
            )
            conexion.commit()
            print(f"  [CRM] Cliente '{datos['nombre_cliente']}' RECUPERADO: "
                  f"tenía alerta de deserción y volvió a comprar.")
        conexion.close()

    # ---------------------------------------------------------------- CONSULTAS
    def alertas_activas(self) -> list:
        conexion = obtener_conexion()
        filas = conexion.execute(
            """SELECT a.*, c.nombre
               FROM alertas_crm a JOIN clientes c ON c.id_cliente = a.id_cliente
               WHERE a.atendida = 0
               ORDER BY a.dias_inactivo DESC""",
        ).fetchall()
        conexion.close()
        return filas
