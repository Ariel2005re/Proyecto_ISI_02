"""
main.py - FitCore Gym: Ecosistema Integrado de Sistemas de Información
======================================================================
Proyecto Final ISID223 - Transformación Digital Empresarial

Punto de entrada del sistema. Al iniciar, se instancian los módulos ERP,
SCM y CRM, que quedan "escuchando" los eventos del Core. Todo lo que se
haga desde el menú (una venta, por ejemplo) dispara automáticamente las
reacciones de los demás sistemas: esa es la evidencia de integración.

Cómo correr la demo de la defensa:
  1. python preparar_datos.py     (una sola vez: carga clientes + histórico)
  2. python main.py
  3. Opción 5 (RFM) y opción 4 (CRM) para poblar la analítica
  4. Opción 7 para generar el dashboard inicial
  5. Opción 1: registrar una venta en vivo -> ver cómo ERP/SCM/CRM
     reaccionan en consola, y regenerar el dashboard (opción 7).
"""

from core.modelos import Venta, Cliente
from core.sistema_core import SistemaCore
from modules.erp import ModuloERP
from modules.scm import ModuloSCM
from modules.crm import ModuloCRM
from analytics.rfm import calcular_rfm, resumen_segmentos
from dashboard.tablero import generar_dashboard


def linea(caracter="=", ancho=64):
    print(caracter * ancho)


def registrar_venta_interactiva(core: SistemaCore):
    texto = input("  Buscar cliente por nombre: ").strip()
    candidatos = core.buscar_clientes(texto)
    if not candidatos:
        print("  No se encontraron clientes.")
        return
    for cliente in candidatos:
        print(f"   {cliente}")
    try:
        id_cliente = int(input("  ID del cliente: "))
    except ValueError:
        print("  ID inválido.")
        return
    cliente = core.obtener_cliente(id_cliente)
    if not cliente:
        print("  Cliente no existe.")
        return

    print("\n  CATÁLOGO:")
    for producto in core.listar_catalogo():
        print(f"   {producto}")

    venta = Venta(cliente)
    while True:
        entrada = input("  ID producto (ENTER para terminar): ").strip()
        if not entrada:
            break
        try:
            producto = core.obtener_producto(int(entrada))
            cantidad = int(input("  Cantidad: ") or "1")
        except ValueError:
            print("  Entrada inválida.")
            continue
        if producto:
            venta.agregar_item(producto, cantidad)
            print(f"   + {cantidad} x {producto.nombre}")
        else:
            print("  Producto no existe.")
    if not venta.detalles:
        print("  Venta vacía; cancelada.")
        return

    print("\n  --- Registrando venta: observar la reacción de los módulos ---")
    core.registrar_venta(venta)
    print("  --- Fin de la cadena de integración ---")


def registrar_cliente_interactivo(core: SistemaCore):
    nombre = input("  Nombre completo: ").strip()
    if not nombre:
        return
    try:
        edad = int(input("  Edad: ") or "25")
        meses = int(input("  Meses de contrato (1/6/12): ") or "1")
    except ValueError:
        edad, meses = 25, 1
    nuevo = Cliente(None, nombre, edad=edad, meses_contrato=meses)
    nuevo_id = core.registrar_cliente(nuevo)
    print(f"  Cliente registrado con ID {nuevo_id}.")


def main():
    linea()
    print("   FITCORE GYM - Ecosistema Integrado (Core + ERP + SCM + CRM)")
    linea()

    core = SistemaCore()
    erp = ModuloERP()      # al instanciarse se suscriben al bus de eventos
    scm = ModuloSCM()
    crm = ModuloCRM(umbral_dias=30)
    print("Módulos ERP, SCM y CRM suscritos al bus de eventos.\n")

    opciones = """
  1) Registrar VENTA (Core)  ->  dispara ERP/SCM/CRM automáticamente
  2) Registrar cliente nuevo (Core)
  3) Ver estado de caja y libro diario (ERP)
  4) Analizar clientes inactivos (CRM)
  5) Calcular segmentación RFM (Analítica)
  6) Ver órdenes de compra / recibir orden (SCM)
  7) Generar/actualizar DASHBOARD gerencial
  0) Salir
"""
    while True:
        print(opciones)
        eleccion = input("Opción: ").strip()

        if eleccion == "1":
            registrar_venta_interactiva(core)

        elif eleccion == "2":
            registrar_cliente_interactivo(core)

        elif eleccion == "3":
            estado = erp.estado_de_caja()
            print(f"\n  [ERP] Ingresos: ${estado['ingresos']:,.2f} | "
                  f"Gastos: ${estado['gastos']:,.2f} | Saldo: ${estado['saldo']:,.2f}")
            print("  Últimos asientos del libro diario:")
            for asiento in erp.libro_diario(8):
                print(f"   #{asiento['id_asiento']:>4} {asiento['fecha'][:10]} "
                      f"{asiento['descripcion'][:38]:<38} "
                      f"DEBE {asiento['cuenta_debe']:<10} / "
                      f"HABER {asiento['cuenta_haber']:<20} ${asiento['monto']:>9.2f}")

        elif eleccion == "4":
            crm.analizar_inactividad()
            print("  Alertas activas (top 10):")
            for alerta in crm.alertas_activas()[:10]:
                print(f"   [ALERTA] {alerta['nombre']:<26} "
                      f"{alerta['dias_inactivo']:>4} días inactivo - {alerta['detalle']}")

        elif eleccion == "5":
            print("  Calculando RFM sobre el histórico de transacciones...")
            rfm = calcular_rfm()
            print(f"  {len(rfm)} clientes clasificados.\n")
            print(resumen_segmentos().to_string(index=False))

        elif eleccion == "6":
            for orden in scm.ordenes()[:10]:
                print(f"   Orden #{orden['id_orden']:>3} [{orden['estado']:<9}] "
                      f"{orden['producto']:<26} x{orden['cantidad']} "
                      f"-> {orden['proveedor']} (${orden['costo_total']:.2f})")
            entrada = input("  ID de orden a recibir (ENTER para omitir): ").strip()
            if entrada:
                try:
                    scm.recibir_orden(int(entrada))
                except ValueError:
                    print("  ID inválido.")

        elif eleccion == "7":
            generar_dashboard()

        elif eleccion == "0":
            print("Hasta luego.")
            break

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
