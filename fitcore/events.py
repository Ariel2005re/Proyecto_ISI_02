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
