"""Genera los diagramas del informe: ER, cadena de valor, arquitectura, mockups."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import os

SALIDA = "/home/claude/fitcore/docs"
os.makedirs(SALIDA, exist_ok=True)

AZUL, NARANJA, VERDE, ROJO, MORADO, GRIS = "#2E86AB", "#F18F01", "#3B8952", "#C73E1D", "#6C5B7B", "#4a4a4a"


def caja(ax, x, y, w, h, titulo, lineas, color, fs_titulo=10, fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                facecolor="white", edgecolor=color, linewidth=2))
    ax.add_patch(Rectangle((x, y + h - 0.55), w, 0.55, facecolor=color, edgecolor=color))
    ax.text(x + w / 2, y + h - 0.27, titulo, ha="center", va="center",
            fontsize=fs_titulo, fontweight="bold", color="white")
    for i, linea in enumerate(lineas):
        ax.text(x + 0.15, y + h - 0.85 - i * 0.34, linea, fontsize=fs, va="center",
                family="monospace")


def flecha(ax, x1, y1, x2, y2, texto="", color=GRIS, estilo="-|>", curva=0.0, fs=8):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=estilo,
                                 connectionstyle=f"arc3,rad={curva}",
                                 color=color, linewidth=1.6, mutation_scale=16))
    if texto:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.14, texto, fontsize=fs,
                ha="center", color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))


# ============================================================ 1. DIAGRAMA ER
fig, ax = plt.subplots(figsize=(13, 8.2))
ax.set_xlim(0, 13); ax.set_ylim(0, 8.2); ax.axis("off")
ax.set_title("Diagrama Entidad-Relación — Ecosistema FitCore Gym", fontsize=14, fontweight="bold")

caja(ax, 0.4, 4.9, 2.9, 3.0, "CLIENTES", [
    "PK id_cliente", "   nombre", "   edad / genero", "   meses_contrato",
    "   frecuencia_semanal", "   meses_antiguedad", "   abandono_historico"], AZUL)
caja(ax, 5.0, 5.5, 2.9, 2.4, "VENTAS", [
    "PK id_venta", "FK id_cliente", "   fecha", "   total"], AZUL)
caja(ax, 9.6, 5.5, 3.0, 2.4, "DETALLE_VENTA", [
    "PK id_detalle", "FK id_venta", "FK id_producto", "   cantidad / subtotal"], AZUL)
caja(ax, 9.6, 2.2, 3.0, 2.5, "PRODUCTOS", [
    "PK id_producto", "   nombre / categoria", "   precio / costo",
    "   stock / stock_minimo", "FK id_proveedor"], VERDE)
caja(ax, 5.0, 2.4, 2.9, 2.1, "ORDENES_COMPRA", [
    "PK id_orden", "FK id_producto", "FK id_proveedor", "   cantidad / estado"], VERDE)
caja(ax, 0.4, 2.4, 2.9, 1.9, "PROVEEDORES", [
    "PK id_proveedor", "   nombre", "   dias_entrega"], VERDE)
caja(ax, 0.4, 0.1, 3.4, 1.8, "ALERTAS_CRM  (CRM)", [
    "PK id_alerta", "FK id_cliente", "   tipo / dias_inactivo"], ROJO)
caja(ax, 4.6, 0.1, 3.6, 1.8, "SEGMENTOS_RFM", [
    "PK id_cliente (FK)", "   R / F / M", "   segmento"], MORADO)
caja(ax, 8.9, 0.1, 3.7, 1.8, "ASIENTOS_CONTABLES (ERP)", [
    "PK id_asiento", "FK id_venta / id_orden", "   debe / haber / monto"], NARANJA)

flecha(ax, 3.3, 6.5, 5.0, 6.6, "1:N  realiza", AZUL)
flecha(ax, 7.9, 6.6, 9.6, 6.6, "1:N  contiene", AZUL)
flecha(ax, 11.1, 5.5, 11.1, 4.7, "N:1", VERDE)
flecha(ax, 9.6, 3.4, 7.9, 3.4, "N:1  repone", VERDE)
flecha(ax, 5.0, 3.4, 3.3, 3.4, "N:1  emite a", VERDE)
flecha(ax, 1.8, 2.4, 1.8, 1.9, "1:N", ROJO)
flecha(ax, 4.0, 5.5, 5.5, 1.9, "1:1", MORADO, curva=0.15)
flecha(ax, 6.4, 5.5, 10.0, 1.9, "1:1  genera", NARANJA, curva=-0.1)
plt.tight_layout()
plt.savefig(f"{SALIDA}/diagrama_er.png", dpi=130, bbox_inches="tight")
plt.close()

# ============================================== 2. ARQUITECTURA / INTEGRACIÓN
fig, ax = plt.subplots(figsize=(12.5, 7))
ax.set_xlim(0, 12.5); ax.set_ylim(0, 7); ax.axis("off")
ax.set_title("Arquitectura de Integración por Bus de Eventos (Patrón Observador)",
             fontsize=14, fontweight="bold")

caja(ax, 4.4, 4.9, 3.7, 1.9, "SISTEMA CORE (POS)", [
    "Membresías / Clases", "Productos / Ventas", "PUBLICA eventos"], AZUL, fs=9)
ax.add_patch(FancyBboxPatch((1.0, 3.0), 10.5, 0.85, boxstyle="round,pad=0.02",
                            facecolor="#fff3e0", edgecolor=NARANJA, linewidth=2.5))
ax.text(6.25, 3.42, "BUS DE EVENTOS   —   venta_registrada  ·  stock_bajo  ·  orden_generada  ·  cliente_en_riesgo",
        ha="center", fontsize=10.5, fontweight="bold", color="#7a4a00")

caja(ax, 0.6, 0.3, 3.2, 1.9, "MÓDULO ERP", [
    "Asiento contable", "por cada venta", "y cada compra"], NARANJA, fs=9)
caja(ax, 4.6, 0.3, 3.2, 1.9, "MÓDULO SCM", [
    "Orden de compra", "automática si", "stock <= mínimo"], VERDE, fs=9)
caja(ax, 8.6, 0.3, 3.2, 1.9, "MÓDULO CRM", [
    "Alerta de riesgo", "de deserción por", "inactividad > 30d"], ROJO, fs=9)

flecha(ax, 6.25, 4.9, 6.25, 3.85, "publica", AZUL, fs=9)
flecha(ax, 2.2, 3.0, 2.2, 2.2, "suscrito", NARANJA, fs=9)
flecha(ax, 6.25, 3.0, 6.25, 2.2, "suscrito", VERDE, fs=9)
flecha(ax, 10.2, 3.0, 10.2, 2.2, "suscrito", ROJO, fs=9)
flecha(ax, 6.6, 2.2, 3.4, 2.6, "orden_generada → gasto", GRIS, curva=0.25, fs=8)
ax.text(6.25, 6.85, "", fontsize=1)
plt.tight_layout()
plt.savefig(f"{SALIDA}/arquitectura_integracion.png", dpi=130, bbox_inches="tight")
plt.close()

# ==================================================== 3. CADENA DE VALOR
fig, ax = plt.subplots(figsize=(13, 6.6))
ax.set_xlim(0, 13); ax.set_ylim(0, 6.6); ax.axis("off")
ax.set_title("Cadena de Valor: Situación Actual (manual) vs. Propuesta (con SI integrado)",
             fontsize=13.5, fontweight="bold")

def fila_cadena(ax, y, etiqueta, celdas, color_titulo):
    ax.text(0.15, y + 0.62, etiqueta, fontsize=10, fontweight="bold", color=color_titulo)
    x = 0.15
    ancho = 12.7 / len(celdas)
    for titulo, texto, mejora in celdas:
        color = VERDE if mejora else GRIS
        ax.add_patch(FancyBboxPatch((x + 0.05, y - 0.75), ancho - 0.1, 1.28,
                     boxstyle="round,pad=0.02", facecolor="white",
                     edgecolor=color, linewidth=2.2 if mejora else 1.2))
        ax.text(x + ancho / 2, y + 0.32, titulo, ha="center", fontsize=8.6, fontweight="bold")
        ax.text(x + ancho / 2, y - 0.22, texto, ha="center", fontsize=7.4, wrap=True)
        x += ancho

fila_cadena(ax, 4.9, "ACTUAL (manual):", [
    ("Logística Interna", "Compras por\nintuición, sin registro", False),
    ("Operaciones", "Control de socios\nen cuaderno/Excel", False),
    ("Logística Externa", "Sin control de\nentregas de proveedor", False),
    ("Marketing y Ventas", "Cobros en efectivo\nsin historial", False),
    ("Servicio Postventa", "No se detecta al\nsocio que abandona", False),
], GRIS)

fila_cadena(ax, 2.4, "PROPUESTA (SI):", [
    ("Logística Interna", "SCM: orden de compra\nautomática (stock mín.)", True),
    ("Operaciones", "Core POS: ventas,\nmembresías y clases", True),
    ("Logística Externa", "SCM: seguimiento de\nórdenes por proveedor", True),
    ("Marketing y Ventas", "RFM: segmentación\nVIP/Leal/Recuperable", True),
    ("Servicio Postventa", "CRM: alerta automática\nde riesgo de deserción", True),
], VERDE)

ax.add_patch(FancyBboxPatch((0.15, 0.35), 12.6, 0.8, boxstyle="round,pad=0.02",
             facecolor="#e8f1f7", edgecolor=AZUL, linewidth=1.8))
ax.text(6.45, 0.75, "ACTIVIDADES DE APOYO propuestas:  Infraestructura (BD SQLite única)  ·  "
        "Finanzas (ERP: libro diario automático)  ·  Tecnología (bus de eventos, dashboard BI)",
        ha="center", fontsize=9)
flecha(ax, 6.45, 3.95, 6.45, 3.35, "MARGEN ↑ (transformación digital)", AZUL, fs=9)
plt.tight_layout()
plt.savefig(f"{SALIDA}/cadena_valor.png", dpi=130, bbox_inches="tight")
plt.close()

# ==================================================== 4. MOCKUPS (wireframes)
def wireframe_pos():
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(0, 9); ax.set_ylim(0, 6); ax.axis("off")
    ax.add_patch(Rectangle((0.2, 0.2), 8.6, 5.6, fill=False, linewidth=2))
    ax.add_patch(Rectangle((0.2, 5.15), 8.6, 0.65, facecolor="#2E86AB"))
    ax.text(0.45, 5.47, "FitCore Gym — Punto de Venta", color="white",
            fontsize=12, fontweight="bold", va="center")
    ax.text(8.6, 5.47, "Cajero: A. Pérez  |  24/07/2026", color="white",
            fontsize=8, va="center", ha="right")
    # panel izquierdo: cliente + catálogo
    ax.add_patch(Rectangle((0.45, 4.3), 5.1, 0.55, fill=False))
    ax.text(0.6, 4.57, "Buscar socio:  María Torr|", fontsize=9, va="center", color="#555")
    for i, (nombre, precio) in enumerate([("Membresía Mensual", "45.00"),
                                          ("Clase de Spinning", "6.00"),
                                          ("Proteína Whey 1kg", "38.00"),
                                          ("Bebida Isotónica", "1.80")]):
        y = 3.55 - i * 0.7
        ax.add_patch(Rectangle((0.45, y), 5.1, 0.55, fill=False, linewidth=0.8))
        ax.text(0.6, y + 0.27, nombre, fontsize=9, va="center")
        ax.text(5.4, y + 0.27, f"${precio}  [+]", fontsize=9, va="center", ha="right")
    # panel derecho: carrito
    ax.add_patch(Rectangle((5.8, 1.55), 2.85, 3.3, fill=False))
    ax.text(5.95, 4.6, "CARRITO", fontsize=10, fontweight="bold")
    ax.text(5.95, 4.15, "1x Memb. Mensual   45.00", fontsize=8, family="monospace")
    ax.text(5.95, 3.8, "2x Proteína Whey   76.00", fontsize=8, family="monospace")
    ax.text(5.95, 2.3, "TOTAL:  $121.00", fontsize=11, fontweight="bold")
    ax.add_patch(FancyBboxPatch((5.9, 0.5), 2.6, 0.75, boxstyle="round,pad=0.02",
                 facecolor="#3B8952"))
    ax.text(7.2, 0.87, "REGISTRAR VENTA", color="white", ha="center",
            fontsize=10, fontweight="bold")
    ax.text(0.45, 0.6, "▸ Al registrar: ERP y SCM se actualizan automáticamente",
            fontsize=8, style="italic", color="#555")
    plt.tight_layout()
    plt.savefig(f"{SALIDA}/mockup_pos.png", dpi=130, bbox_inches="tight")
    plt.close()

def wireframe_gerencial():
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(0, 9); ax.set_ylim(0, 6); ax.axis("off")
    ax.add_patch(Rectangle((0.2, 0.2), 8.6, 5.6, fill=False, linewidth=2))
    ax.add_patch(Rectangle((0.2, 5.15), 8.6, 0.65, facecolor="#6C5B7B"))
    ax.text(0.45, 5.47, "FitCore Gym — Panel Gerencial", color="white",
            fontsize=12, fontweight="bold", va="center")
    for x, y, t in [(0.45, 2.9, "Ventas semanales\n(línea)"),
                    (4.6, 2.9, "Segmentos RFM\n(pastel)"),
                    (0.45, 0.5, "Ingresos vs Gastos\n(barras — ERP)"),
                    (4.6, 0.5, "⚠ Clientes en riesgo\n(lista — CRM)")]:
        ax.add_patch(Rectangle((x, y), 3.95, 2.0, fill=False, linewidth=1))
        ax.text(x + 1.97, y + 1.0, t, ha="center", va="center", fontsize=9.5, color="#444")
    plt.tight_layout()
    plt.savefig(f"{SALIDA}/mockup_gerencial.png", dpi=130, bbox_inches="tight")
    plt.close()

wireframe_pos()
wireframe_gerencial()
print("Diagramas generados:", os.listdir(SALIDA))
