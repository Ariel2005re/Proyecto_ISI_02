from core.modelos import Venta
from core.sistema_core import SistemaCore
from modules.erp import ModuloERP
from modules.scm import ModuloSCM
from modules.crm import ModuloCRM
from analytics.rfm import calcular_rfm, resumen_segmentos
from dashboard.tablero import generar_dashboard
from database import obtener_conexion
from events import bus


def titulo(texto):
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70)


# ---------------------------------------------------------------- 1. Arranque
titulo("1) ARRANQUE DEL ECOSISTEMA")
core = SistemaCore()
erp = ModuloERP()
scm = ModuloSCM()
crm = ModuloCRM(umbral_dias=30)
bus.suscribir("cliente_en_riesgo",
              lambda d: print(f"  [GERENCIA] ALERTA: {d['nombre']} en riesgo "
                              f"de deserción ({d['dias_inactivo']} días inactivo)"))
print("Core listo; ERP, SCM y CRM suscritos al bus de eventos.")

# ------------------------------------------------------------ 2. Analítica
titulo("2) SEGMENTACIÓN RFM (Fase 3)")
rfm = calcular_rfm()
print(f"{len(rfm)} clientes clasificados:")
print(resumen_segmentos().to_string(index=False))

titulo("3) ANÁLISIS CRM DE INACTIVIDAD")
crm.analizar_inactividad(silencioso=True)
alertas = crm.alertas_activas()
print(f"Alertas activas: {len(alertas)}. Primeras 5:")
for alerta in alertas[:5]:
    print(f"  [ALERTA] {alerta['nombre']:<26} {alerta['dias_inactivo']:>4} días - {alerta['detalle']}")

# ------------------------------------------------------------ 3. Dashboard antes
titulo("4) DASHBOARD INICIAL")
generar_dashboard()
estado = erp.estado_de_caja()
print(f"[ERP] Caja antes de la venta en vivo: ingresos ${estado['ingresos']:,.2f} "
      f"| gastos ${estado['gastos']:,.2f}")

# ------------------------------------------------------------ 4. Venta en vivo
titulo("5) VENTA EN VIVO -> INTEGRACIÓN AUTOMÁTICA")
# Forzar escenario didáctico: dejar la Proteína Whey al borde del stock mínimo
# (y cerrar órdenes pendientes previas para que la demo sea re-ejecutable)
conexion = obtener_conexion()
conexion.execute("UPDATE productos SET stock = 16 WHERE nombre = 'Proteína Whey 1kg'")
conexion.execute("UPDATE ordenes_compra SET estado='RECIBIDA' "
                 "WHERE estado='PENDIENTE' AND id_producto=8")
conexion.commit()
conexion.close()
print("(Escenario: 'Proteína Whey 1kg' con stock=16, mínimo=15)\n")

cliente = core.buscar_clientes("a")[0]           # cualquier cliente
venta = Venta(cliente)
venta.agregar_item(core.obtener_producto(8), 2)  # 2 x Proteína Whey -> stock 14 < 15
venta.agregar_item(core.obtener_producto(1), 1)  # 1 x Membresía Mensual
core.registrar_venta(venta)

estado = erp.estado_de_caja()
print(f"\n[ERP] Caja después: ingresos ${estado['ingresos']:,.2f} "
      f"| gastos ${estado['gastos']:,.2f} | saldo ${estado['saldo']:,.2f}")
print("[SCM] Órdenes pendientes:")
for orden in scm.ordenes(solo_pendientes=True):
    print(f"  Orden #{orden['id_orden']} {orden['producto']} x{orden['cantidad']} "
          f"-> {orden['proveedor']} (${orden['costo_total']:.2f})")

# ------------------------------------------------------------ 5. Dashboard después
titulo("6) DASHBOARD ACTUALIZADO TRAS LA VENTA")
generar_dashboard()

titulo("BITÁCORA DE EVENTOS (evidencia de integración, requisito 2.3)")
for registro in bus.bitacora[-8:]:
    print(f"  {registro}")
