"""
events.py - Bus de Eventos (Patrón de Diseño: Observador / Publicador-Suscriptor)
================================================================================
Este módulo es el CORAZÓN de la INTEGRACIÓN EMPRESARIAL del proyecto.

¿Cómo funciona?
- Los módulos (ERP, SCM, CRM) se "suscriben" a eventos que les interesan.
- El Sistema Core "publica" eventos cuando algo ocurre (ej. una venta).
- El bus notifica automáticamente a todos los suscriptores, SIN que el Core
  sepa siquiera que existen. Así se evita el acoplamiento y los silos de
  información: una acción en el Sistema A dispara consecuencias en el
  Sistema B sin intervención humana (requisito 2.3 del proyecto).

Eventos definidos en el ecosistema:
- "venta_registrada"  -> lo escucha el ERP (asiento contable) y el CRM (última compra)
- "stock_bajo"        -> lo escucha el SCM (orden de compra automática)
- "cliente_en_riesgo" -> lo escucha la interfaz gerencial (alerta de deserción)
"""


class BusDeEventos:
    """Canal central de comunicación entre el Core y los módulos satélite."""

    def __init__(self):
        # Diccionario: nombre_evento -> lista de funciones suscritas
        self._suscriptores = {}
        # Bitácora de eventos: sirve como evidencia de integración en la demo
        self.bitacora = []

    def suscribir(self, nombre_evento: str, funcion_manejadora):
        """Un módulo registra su interés en un tipo de evento."""
        if nombre_evento not in self._suscriptores:
            self._suscriptores[nombre_evento] = []
        self._suscriptores[nombre_evento].append(funcion_manejadora)

    def publicar(self, nombre_evento: str, datos: dict):
        """El Core emite un evento; el bus notifica a todos los suscriptores."""
        registro = f"[EVENTO] '{nombre_evento}' publicado -> {len(self._suscriptores.get(nombre_evento, []))} módulo(s) notificado(s)"
        self.bitacora.append(registro)
        print(f"  {registro}")
        for funcion in self._suscriptores.get(nombre_evento, []):
            funcion(datos)


# Instancia única compartida por todo el ecosistema (patrón Singleton simple)
bus = BusDeEventos()
